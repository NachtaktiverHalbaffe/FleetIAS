"""
Filename: guimanager.py
Version name: 1.0, 2021-07-22
Short description: callback functions for button presses. These are defined here so it wont get deleted
if mainwindow.py is regenerated by pyqt5-tools

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

import sys
import time

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox  # nopep8
sys.path.append('.')  # nopep8
sys.path.append('..')  # nopep8

from robotinomanager.robotinomanager import RobotinoManager  # nopep8
from commandserver.commandserver import CommandServer  # nopep8
from mescommunicator.mesclient import MESClient  # nopep8
from threading import Thread
from conf import errLogger


class GUIManager(object):

    def __init__(self, ui):
        # ui instance
        self.ui = ui
        # setup instances of all servers and managers
        self.commandServer = CommandServer()
        self.mesClient = MESClient()
        self.robotinoManager = RobotinoManager(
            commandServer=self.commandServer, mesClient=self.mesClient, guiManager=self)
        self.commandServer.setRobotinoManager(self.robotinoManager)
        # data which is being displayed
        self.statesRobotinos = []
        self.transportTasks = set()

    def __del__(self):
        self.commandServer.stopServer()
        self.mesClient.stopClient()

    # connect all buttons from ui with callback functions
    def connectCallbackFunction(self):
        """
        start/stop servers
        """
        self.ui.buttonStartCommandServer.clicked.connect(
            self.startCommandServer)
        self.ui.buttonStopCommandServer.clicked.connect(
            self.stopCommandServer)
        self.ui.buttonStartMesClient.clicked.connect(self.startMesClient)
        self.ui.buttonStopMesClient.clicked.connect(self.stopMesClient)

        """
        manual operations
        """
        self.ui.buttonUndock.clicked.connect(self.manualUndock)
        self.ui.buttonDock.clicked.connect(self.manualDock)
        self.ui.buttonUnloadCarrier.clicked.connect(self.manualUnloadCarrier)
        self.ui.buttonLoadCarrier.clicked.connect(self.manualLoadCarrier)
        self.ui.buttonDriveTo.clicked.connect(self.manualDriveTo)
        self.ui.buttonSetAutomatic.clicked.connect(self.setAutoMode)
        self.ui.buttonSetManual.clicked.connect(self.setManualMode)
        self.ui.buttonSetDockingPos.clicked.connect(self.setDockingPos)
        self.ui.buttonEndTask.clicked.connect(self.endTask)

    # fills out the rows of the tableview of robotinomanager
    def fillTableViewRobotinoManager(self):
        self.ui.tableViewRobotinos.setRowCount(0)
        for robotino in self.statesRobotinos:
            # add empty row
            rowPosition = self.ui.tableViewRobotinos.rowCount()
            self.ui.tableViewRobotinos.insertRow(rowPosition)
            # fill row with items
            # id
            self.ui.tableViewRobotinos.setItem(
                rowPosition, 0,  QtWidgets.QTableWidgetItem(str(robotino.id)))
            # mode
            if robotino.autoMode:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 1, QtWidgets.QTableWidgetItem("Automated"))
            elif robotino.manualMode:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 1, QtWidgets.QTableWidgetItem("Manual"))
            # Battery
            # Battery has at full charge 12,7 V and two batterys are in series => Full accu has 25.4 V
            # Battery is empty at 11,5 V and two batterys are in series => Full accu has 23.0 V
            # => Voltage drops with 2.4V (1.2V with one battery) from full to empty with linear approximation
            # batterLevel = (25.4 V - current battery voltage )/2.4 (for notation in percentage it has to be multiplied with 100)
            batteryLevel = round((((25.4) - robotino.batteryVoltage)/2.4)*100)
            # set batteryLevel to 0% for invalid values e.g. when no battery voltage is given
            if batteryLevel > 100 or batteryLevel < 0:
                batteryLevel = 0
            self.ui.tableViewRobotinos.setItem(
                rowPosition, 2, QtWidgets.QTableWidgetItem(str(robotino.batteryVoltage) + " V"))
            # error
            if robotino.laserWarning:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 3, QtWidgets.QTableWidgetItem("Laserwarning"))
            elif robotino.laserSaftey:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 3, QtWidgets.QTableWidgetItem("Laser Saftey"))
            elif robotino.errorL2:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 3, QtWidgets.QTableWidgetItem("Operational Error"))
            else:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 3, QtWidgets.QTableWidgetItem("None"))
            # state
            if robotino.busy:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 4, QtWidgets.QTableWidgetItem("Busy"))
            elif not robotino.busy and robotino.errorL2:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 4, QtWidgets.QTableWidgetItem("Error"))
            elif not robotino.busy and not robotino.errorL2:
                self.ui.tableViewRobotinos.setItem(
                    rowPosition, 4, QtWidgets.QTableWidgetItem("Idle"))

    # fills out the rows of the tableview of mes
    def fillTableViewMES(self):
        self.ui.tableViewMes.setRowCount(0)
        for task in self.transportTasks:
            # add empty row
            rowPosition = self.ui.tableViewMes.rowCount()
            self.ui.tableViewMes.insertRow(rowPosition)
            # fill row with items
            # start
            self.ui.tableViewMes.setItem(
                rowPosition, 0, QtWidgets.QTableWidgetItem(str(task[0])))
            # target
            self.ui.tableViewMes.setItem(
                rowPosition, 1, QtWidgets.QTableWidgetItem(str(task[1])))
            # assigned robotino
            self.ui.tableViewMes.setItem(
                rowPosition, 2, QtWidgets.QTableWidgetItem(str(task[2])))
            # state
            self.ui.tableViewMes.setItem(
                rowPosition, 3, QtWidgets.QTableWidgetItem(task[3]))

    def showErrorDialog(self, errMsg, robotinoId, callbackFunc):
        """
        Setup Dialog
        """
        dialog = QtWidgets.QMessageBox()
        # set dialog title
        dialog.setWindowTitle("Error")
        # set error message and little description what the user can do
        dialog.setText(errMsg)
        dialog.setInformativeText(
            "Click \"Retry\" to retry the operation or click \"Abort\" to abort the operation (Warning: When error occurs on automated operation, the transporttask could get aborted)")
        # set dialog icon
        dialog.setIcon(QMessageBox.Critical)
        # set buttons of dialog
        dialog.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
        dialog.buttonClicked.connect(lambda: callbackFunc(
            errorMsg=errMsg, robotinoId=robotinoId))

        x = dialog.exec_()

    """
    Callback functions
    """

    # callback function to start commandServer
    def startCommandServer(self):
        print("[FLEETIAS] Starting CommandServer...")
        self.commandServer.runServer()

    # callback function to stop commandServer
    def stopCommandServer(self):
        print("[FLEETIAS] Stopping CommandServer...")
        self.commandServer.stopServer()

    # callback function to start mesClient
    def startMesClient(self):
        print("[FLEETIAS] Starting MESClient...")
        Thread(target=self.mesClient.run).start()
        Thread(target=self.robotinoManager.startAutomatedOperation).start()

    # callback function to stop mesClient
    def stopMesClient(self):
        print("[FLEETIAS] Stopping MESClient...")
        self.mesClient.stopClient()
        Thread(target=self.robotinoManager.stopAutomatedOperation).start()

    # callback function to manual trigger undocking
    def manualUndock(self):
        print("[FLEETIAS] Manual send command to robotino to undock")
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        if robotino != None:
            robotino.undock()
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command because robotino is not present")

    # callback function to manual trigger docking
    def manualDock(self):
        target = self.ui.inputResourceId.value()
        print(
            "[FLEETIAS] Manual send command to robotino to dock")
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        if robotino != None:
            robotino.dock(target)
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command becaus robotino is not present")

    # callback function to manual trigger unloading
    def manualUnloadCarrier(self):
        print("[FLEETIAS] Manual send command to robotino to unload carrier")
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        if robotino != None:
            robotino.unloadCarrier()
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command becaus robotino is not present")

    # callback function to manual trigger loading
    def manualLoadCarrier(self):
        print("[FLEETIAS] Manual send command to robotino to load carrier")
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        if robotino != None:
            robotino.loadCarrier()
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command becaus robotino is not present")

    # callback function to manual trigger driving to resource
    def manualDriveTo(self):
        target = self.ui.inputResourceId.value()
        print(
            "[FLEETIAS] Manual send command to robotino to drive to resource " + str(target))
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        if robotino != None:
            robotino.driveTo(target)
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command because robotino is not present")

    # callback function to manual setdocking Position of robotion
    def setDockingPos(self):
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        target = self.ui.inputResourceId.value()
        if robotino != None:
            robotino.setDockingPos(target)
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command because robotino is not present")

    # callback function to manual end task of robotiono
    def endTask(self):
        robotino = self.robotinoManager.getRobotino(
            self.ui.inputRobtinoId.value())
        if robotino != None:
            robotino.endTask()
        else:
            errLogger.error(
                "[FLEETIAS] Couldnt execute command because robotino is not present")

    # callback function to manual set robotino to automatic operation
    def setAutoMode(self):
        for robotino in self.statesRobotinos:
            if robotino.id == self.ui.inputRobtinoId.value():
                robotino.activateAutoMode()

    # callback function to manual set robotino to manual operation
    def setManualMode(self):
        for robotino in self.statesRobotinos:
            if robotino.id == self.ui.inputRobtinoId.value():
                robotino.activateManualMode()

    """
    Setter
    """

    def setStatesRobotino(self, statesRobotino):
        self.statesRobotinos = statesRobotino
        self.fillTableViewRobotinoManager()

    def addTransportTask(self, transportTask):
        self.transportTasks.add(transportTask)
        self.fillTableViewMES()

    def deleteTransportTask(self, transportTask):
        self.transportTasks.remove(transportTask)
        self.fillTableViewMES()
