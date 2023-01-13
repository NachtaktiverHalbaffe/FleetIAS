"""
Filename: robotinomanager.py
Version name: 1.0, 2022-12-02
Short description: class to manage all robotinos (delegate tasks, delegate statemessages to specific robotino)

(C) 2003-2022 IAS, Universitaet Stuttgart

"""

import time
from threading import Event, Thread
from PySide6.QtCore import QThread, Signal

from .robotino import Robotino
from conf import POLL_TIME_STATUSUPDATES, POLL_TIME_TASKS, appLogger


class RobotinoManager(QThread):
    errorSignal = Signal(str, int)

    def __init__(self, mesClient, commandServer):
        super(RobotinoManager, self).__init__()
        # fleet
        self.fleet = []
        # params for automated control
        self.transportTasks = []
        self.commandInfo = ""
        self.stopFlagCyclicUpdates = Event()
        self.stopFlagAutoOperation = Event()
        self.stopFlag = Event()
        self.POLL_TIME_STATEUPDATES = POLL_TIME_STATUSUPDATES
        self.POLL_TIME_TASKS = POLL_TIME_TASKS
        # instances of mesclient and commandserver for executing operations
        self.mesClient = mesClient
        self.commandServer = commandServer
        # Internal threading
        self.isAutoMode = False
        self.runsStateUpdates = False
        self.automatedOpThread = Thread(target=self.automatedOperation)
        self.cyclicStateUpdateThread = Thread(target=self.cyclicStateUpdate)

    def __del__(self):
        self.stopAutomatedOperation()
        self.stopCyclicStateUpdate()
        self.stop()

    def run(self):
        appLogger.info("Started RobotinoManager")
        try:
            while not self.stopFlag.is_set():
                # --------------------- Automated operation --------------------
                if self.isAutoMode and not self.automatedOpThread.is_alive():
                    self.stopFlagAutoOperation.clear()
                    self.automatedOpThread.start()
                elif not self.isAutoMode and self.automatedOpThread.is_alive():
                    self.stopFlagAutoOperation.clear()
                # --------------------- State updates ------------------------------
                elif (
                    self.runsStateUpdates
                    and not self.cyclicStateUpdateThread.is_alive()
                ):
                    self.stopFlagCyclicUpdates.clear()
                    self.cyclicStateUpdateThread.start()
                elif (
                    not self.runsStateUpdates
                    and not self.cyclicStateUpdateThread.is_alive()
                ):
                    self.stopFlagCyclicUpdates.set()
        except:
            pass
        appLogger.info("Stopped RobotinoManager")
        self.fleet = []

    def createFleet(self, msg):
        """
        Creates the fleet with robotinos inside

        Args:
            msg (str): message passed from the commandserver
        """
        self.stopCyclicStateUpdate()
        self.fleet = []
        strIds = msg.split("AllRobotinoID")
        strIds = strIds[1].split(",")
        if len(strIds) != 0:
            for id in strIds:
                robotino = Robotino(
                    mesClient=self.mesClient, commandServer=self.commandServer
                )
                robotino.id = int(id)
                robotino.manualMode = True
                self.fleet.append(robotino)
        else:
            robotino = Robotino(
                mesClient=self.mesClient, commandServer=self.commandServer
            )
            robotino.id = 7
            robotino.manualMode = True
            self.fleet.append(robotino)
        self.startCyclicStateUpdate()

    def cyclicStateUpdate(self):
        """
        Cyclically update state of Robotinos. Is started from the class itself and runs as a thread
        """
        lastUpdate = time.time()
        appLogger.info("Started cyclic state updates")
        while not self.stopFlagCyclicUpdates.is_set():
            if time.time() - lastUpdate > self.POLL_TIME_STATEUPDATES:
                for robotino in self.fleet:
                    time.sleep(0.002)
                    self.commandServer.getRobotinoInfo(robotino.id)
                lastUpdate = time.time()
                self.mesClient.setStatesRobotinos(self.fleet)
                # only do updates in gui if module runs/is configured with gui
                if self.guiManager != None:
                    self.guiManager.setStatesRobotino(self.fleet)
        # reset stopflag after the cyclicStateUpdate got killed
        appLogger.info("[ROBOTINOMANAGER] Stopped cyclic state updates")
        self.stopFlagCyclicUpdates.clear()

    def automatedOperation(self):
        """
        Operates the Robotino in automated operation where it gets the transport tasks from the IAS-MES and executes them
        """
        appLogger.info("Started automated operation")
        self.stopFlagAutoOperation.clear()
        lastUpdate = time.time()
        while not self.stopFlagAutoOperation.is_set():
            # poll transport task from mes
            if time.time() - lastUpdate > self.POLL_TIME_TASKS:
                if self.mesClient.serviceSocketIsAlive:
                    self.transportTasks = self.mesClient.getTransportTasks(
                        len(self.fleet)
                    )
                if self.transportTasks != None:
                    self.transportTasks = list(self.transportTasks)
                    # assign Tasks
                    for task in self.transportTasks:
                        # check if task is already assigned
                        isAlreadyAssigned = False
                        for robotino in self.fleet:
                            if robotino.task == task:
                                isAlreadyAssigned = True
                                break
                        # assign task if it isnt already assigned
                        if not isAlreadyAssigned:
                            for robotino in self.fleet:
                                if (
                                    robotino.task == (0, 0)
                                    and robotino.autoMode
                                    and task != (0, 0)
                                ):
                                    appLogger.info(
                                        "Assigned task to robotino " + str(robotino.id)
                                    )
                                    robotino.task = task
                                    Thread(
                                        target=robotino.executeTransportTask,
                                        args=[robotino],
                                    ).start()
                                    break
                    lastUpdate = time.time()

        appLogger.info("Stopped automated operation")

        # reset stopflag after the automatedOperation got killed
        self.stopFlagAutoOperation.clear()

    def handleError(self, errMsg, robotinoId, isAutoRetrying=True):
        """
        Handles error when robotino returns an error during operation

        Params:
            errMsg (str): error message
            robotinoId (int): id of robotino which has the error
            isAutoRetring (bool): if operation is automatically retried (only necessary if package is running without gui)
        """
        self.errorSignal.emit(errMsg, robotinoId)
        if isAutoRetrying:
            self.retryOp(errorMsg=errMsg, robotinoId=robotinoId)

    def retryOp(self, errorMsg, robotinoId, buttonClicked=None):
        """
        Retries an failed operation

        Args:
            errorMsg (str): message of error which identifies the op
            robotinoId (int): id of robotino with the error
            buttonClicked (bool): button which was clicked in the errordialog (optional)
        """
        if buttonClicked.text() == "Retry" or buttonClicked == None:
            robotino = self.robotinoManager.getRobotino(robotinoId)
            if "loading" in errorMsg:
                if robotino != None:
                    robotino.loadCarrier()
            elif "unloading" in errorMsg:
                if robotino != None:
                    robotino.unloadCarrier()
            elif "driving" in errorMsg:
                if robotino != None:
                    robotino.driveTo(robotino.target)
            elif "docking" in errorMsg:
                if robotino != None:
                    robotino.dock(robotino.target)
            elif "undocking" in errorMsg:
                if robotino != None:
                    robotino.undock()

    def _getIDfromCommandInfo(self):
        """
        Splits the commandinfo into an id and state

        Returns:
            int: resourceId of robotino from which the command info comes
        """
        id = self.commandInfo.split("robotinoid:")
        if id[0] != "":
            id = int(id[1][0])
            return id
        else:
            return 0

    """
    Setter and getter
    """

    def setCommandInfo(self, msg):
        id = self._getIDfromCommandInfo(msg)
        self.commandInfo = msg
        for robotino in self.fleet:
            if robotino.id == id:
                robotino.setCommandInfo(msg)
                return

    def getRobotino(self, id):
        for robotino in self.fleet:
            if robotino.id == id:
                return robotino
        appLogger.error(
            "[ROBOTINOMANAGER] Couldnt return robotino, because it doesnt exist"
        )
        return

    def startAutomatedOperation(self):
        self.isAutoMode = True

    def stopAutomatedOperation(self):
        self.isAutoMode = False
        self.stopFlagAutoOperation.set()

    def startCyclicStateUpdate(self):
        self.runsStateUpdates = True

    def stopCyclicStateUpdate(self):
        self.runsStateUpdates = False
        self.stopFlagCyclicUpdates.set()

    def setUseOldControlForWholeFleet(self, value):
        for robotino in self.fleet:
            robotino.useOldControl = value

    def stop(self):
        self.isAutoMode = False
        self.runsStateUpdates = False
        self.stopFlagAutoOperation.set()
        self.stopFlagCyclicUpdates.set()
        self.stopFlag.set()


if __name__ == "__main__":
    from commandserver.commandserver import CommandServer
    from mescommunicator.mesclient import MESClient

    # setup components
    commandServer = CommandServer()
    mesClient = MESClient()
    robotinoManager = RobotinoManager(mesClient=mesClient, commandServer=commandServer)
    # link component to robotinomanager so commandserver could update tasks
    commandServer.setRobotinoManager(robotinoManager)
