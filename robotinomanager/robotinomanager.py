"""
Filename: robotinomanager.py
Version name: 1.0, 2021-07-22
Short description: class to manage all robotinos (delegate tasks, delegate statemessages to specific robotino)

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from .robotino import Robotino
from threading import Thread, Event
from PyQt5.QtCore import QThread
import time
from conf import POLL_TIME_STATUSUPDATES, POLL_TIME_TASKS


class RobotinoManager(object):

    def __init__(self, mesClient, commandServer, guiManager=None):
        # fleet
        self.fleet = []
        # params for automated control
        self.transportTasks = []
        self.commandInfo = ""
        self.stopFlagCyclicUpdates = Event()
        self.stopFlagAutoOperation = Event()
        self.POLL_TIME_STATEUPDATES = POLL_TIME_STATUSUPDATES
        self.POLL_TIME_TASKS = POLL_TIME_TASKS
        # instances of mesclient and commandserver for executing operations
        self.mesClient = mesClient
        self.commandServer = commandServer
        self.guiManager = guiManager
        self.cyclicThread = QThread()
        self.cyclicThread.started.connect(self.startCyclicStateUpdate)

    # creates the fleet with robotinos inside
    # @params:
    #   msg: message from the commandserver
    def createFleet(self, msg):
        self.stopCyclicStateUpdate()
        self.fleet = []
        strIds = msg.split("AllRobotinoID")
        strIds = strIds[1].split(",")
        if len(strIds) != 0:
            for id in strIds:
                robotino = Robotino(mesClient=self.mesClient,
                                    commandServer=self.commandServer)
                robotino.id = int(id)
                robotino.manualMode = True
                self.fleet.append(robotino)
        else:
            robotino = Robotino(mesClient=self.mesClient,
                                commandServer=self.commandServer)
            robotino.id = 7
            robotino.manualMode = True
            self.fleet.append(robotino)
        self.cyclicThread.start()
        # Thread(target=self.startCyclicStateUpdate).start()

    # cyclically update state of robotinos, runs as thread
    def cyclicStateUpdate(self):
        lastUpdate = time.time()
        print("[ROBOTINOMANAGER] Started cyclic state updates")
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
        print("[ROBOTINOMANAGER] Stopped cyclic state updates")
        self.stopFlagCyclicUpdates.clear()

    # operates the robotino in automated operation where it gets the transport tasks from the
    # mes and executes them
    def automatedOperation(self):
        print("[ROBOTINOMANAGER] Started automated operation")
        lastUpdate = time.time()
        while not self.stopFlagAutoOperation.is_set():
            # poll transport task from mes
            if time.time() - lastUpdate > self.POLL_TIME_TASKS:
                self.transportTasks = self.mesClient.getTransportTasks(
                    len(self.fleet))
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
                                if robotino.task == (0, 0) and robotino.autoMode:
                                    print(
                                        "[ROBOTINOMANAGER] Assigned task to robotino " + str(robotino.id))
                                    robotino.task = task
                                    Thread(target=self.executeTransportTask,
                                           args=[robotino]).start()
                                    break

        # reset stopflag after the automatedOperation got killed
        self.stopFlagAutoOperation.clear()

    # execute an transport task which got assigend from the mes
    # @param:
    #   robotino: instance of robotino which executes the task
    # @return:
    #   If transport taks gots successfully executed (True) or not/abroted (False)
    def executeTransportTask(self, robotino):
        """
        Load carrier at start
        """
        # only do updates in gui if module runs/is configured with gui
        if self.guiManager != None:
            taskInfo = (robotino.task[0],
                        robotino.task[1], robotino.id, "loading")
            self.guiManager.addTransportTask(taskInfo)
        # drive to start
        if robotino.dockedAt != robotino.task[0]:
            robotino.driveTo(robotino.task[0])
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-GotoPosition":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)
        # dock to resource
        if robotino.dockedAt != robotino.task[0]:
            robotino.dock(int(robotino.task[0]))
        id, state = self._parseCommandInfo()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-DockTo":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)
        # load box
        robotino.loadCarrier()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-LoadBox":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)
        # undock
        robotino.undock()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-Undock":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)

        """
        Unload carrier at target
        """
        # only do updates in gui if module runs/is configured with gui
        if self.guiManager != None:
            self.guiManager.deleteTransportTask(taskInfo)
            taskInfo = (robotino.task[0], robotino.task[1],
                        robotino.id, "transporting")
            self.guiManager.addTransportTask(taskInfo)
        # drive to target
        robotino.driveTo(robotino.task[1])
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-GotoPosition":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)
        self.guiManager.deleteTransportTask(taskInfo)
        taskInfo = (robotino.task[0], robotino.task[1],
                    robotino.id, "unloading")
        self.guiManager.addTransportTask(taskInfo)
        # dock to resource
        robotino.dock(int(robotino.task[1]))
        id, state = self._parseCommandInfo()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-DockTo":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)
        # load box
        robotino.unloadCarrier()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-UnloadBox":
                break
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(0.5)

        """
        Finishing task
        """
        if self.guiManager != None:
            self.guiManager.deleteTransportTask(taskInfo)
            taskInfo = (robotino.task[0], robotino.task[1],
                        robotino.id, "finished")
            self.guiManager.addTransportTask(taskInfo)
        # inform robotino
        self.commandServer.ack(robotino.id)
        # remove task from transporttasks
        tasks = set(self.transportTasks)
        tasks.remove(robotino.task)
        self.transportTasks = list(tasks)
        # remove task from robotino
        robotino.task = (0, 0)
        # only do updates in gui if module runs/is configured with gui
        if self.guiManager != None:
            self.guiManager.deleteTransportTask(taskInfo)

        return True

    # handles error when robotino returns an error during operation
    # @params:
    #   errMsg: error message
    #   robotinoId: id of robotino which has the error
    #   isAutoRetring: if operation is automatically retried (only necessary if package is running without gui)
    def handleError(self, errMsg, robotinoId, isAutoRetrying=True):
        if self.guiManager != None:
            self.guiManager.showErrorDialog(errMsg, robotinoId, self._retryOp)
        elif isAutoRetrying:
            self._retryOp(errorMsg=errMsg, robotinoId=robotinoId)

    # retrys the operation
    # params:
    #   errorMsg: message of error which identifies the op
    #   robotinoId: id of robotino with the error
    #   buttonClicked: button which was clicked in the errordialog (optional)
    def _retryOp(self, errorMsg, robotinoId, buttonClicked=None):
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

    # splits the commandinfo into an id and state
    # @return:
    #   state: string with the state message of the command info
    #   id: resourceId of robotino from which the command info comes
    def _parseCommandInfo(self):
        id = self.commandInfo.split("robotinoid:")
        print(id)
        if id[0] != "":
            id = int(id[1][0])
            state = self.commandInfo.split("\"")
            state = state[1]

            return id, state
        else:
            return 0, ""

    """
    Setter and getter
    """

    def setCommandInfo(self, msg):
        self.commandInfo = msg

    def getRobotino(self, id):
        for robotino in self.fleet:
            if robotino.id == id:
                return robotino
        print("[ROBOTINOMANAGER] Couldnt return robotino, because it doesnt exist")
        return

    def startAutomatedOperation(self):
        self.stopFlagAutoOperation.clear()
        Thread(target=self.automatedOperation).start()

    def stopAutomatedOperation(self):
        self.stopFlagAutoOperation.set()

    def startCyclicStateUpdate(self):
        self.stopFlagCyclicUpdates.clear()
        Thread(target=self.cyclicStateUpdate).start()

    def stopCyclicStateUpdate(self):
        self.stopFlagCyclicUpdates.set()


if __name__ == "__main__":
    from commandserver.commandserver import CommandServer
    from mescommunicator.mesclient import MESClient

    # setup components
    commandServer = CommandServer()
    mesClient = MESClient()
    robotinoManager = RobotinoManager(
        mesClient=mesClient, commandServer=commandServer)
    # link component to robotinomanager so commandserver could update tasks
    commandServer.setRobotinoManager(robotinoManager)
