"""
Filename: robotinomanager.py
Version name: 1.0, 2022-12-02
Short description: class to manage all robotinos (delegate tasks, delegate statemessages to specific robotino)

(C) 2003-2022 IAS, Universitaet Stuttgart

"""

import time
from threading import Event, Thread, Lock
from PySide6.QtCore import QThread, Signal

from .robotino import Robotino
from conf import POLL_TIME_STATUSUPDATES, POLL_TIME_TASKS, appLogger


class RobotinoManager(QThread):
    deleteTaskInfoSignal = Signal(int, int, int, str)
    newTaskInfoSignal = Signal(int, int, int, str)
    statesRobotinoSignal = Signal(list)

    def __init__(self, mesClient, robotinoServer):
        super(RobotinoManager, self).__init__()
        # fleet
        self.fleet = []
        # params for automated control
        self.transportTasks = []
        self.commandInfo = ""
        self.POLL_TIME_STATEUPDATES = POLL_TIME_STATUSUPDATES
        self.POLL_TIME_TASKS = POLL_TIME_TASKS
        # instances of mesclient and commandserver for executing operations
        self.mesClient = mesClient
        self.robotinoServer = robotinoServer
        # Internal threading
        self.isAutoMode = False
        self.runsStateUpdates = False
        self.stopFlagCyclicUpdates = Event()
        self.stopFlagAutoOperation = Event()
        self.stopFlag = Event()
        self.automatedOpThread = Thread(target=self.automatedOperation)
        self.cyclicStateUpdateThread = Thread(target=self.cyclicStateUpdate)
        self.robotinoServerLock = Lock()

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

                time.sleep(1)
        except Exception as e:
            appLogger.error(f"Robotinomanager crashed. Exception: {e}")

        self.fleet = []
        appLogger.info("Stopped RobotinoManager")

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
                    mesClient=self.mesClient, robotinoServer=self.robotinoServer
                )
                robotino.id = int(id)
                robotino.manualMode = True
                robotino.deleteTaskInfoSignal.connect(self.emitDeleteTaskInfo)
                robotino.newTaskInfoSignal.connect(self.emitNewTaskInfo)
                self.fleet.append(robotino)
        else:
            robotino = Robotino(
                mesClient=self.mesClient, robotinoServer=self.robotinoServer
            )
            robotino.id = 7
            robotino.manualMode = True
            self.fleet.append(robotino)
        self.statesRobotinoSignal.emit(self.fleet)
        self.startCyclicStateUpdate()

    def cyclicStateUpdate(self):
        """
        Cyclically update state of Robotinos. Is started from the class itself and runs as a thread
        """
        appLogger.info("Started cyclic state updates")
        while not self.stopFlagCyclicUpdates.is_set():
            for robotino in self.fleet:
                self.robotinoServer.lock.acquire()
                self.robotinoServer.getRobotinoInfo(robotino.id)
                self.robotinoServer.lock.release()
            self.mesClient.setStatesRobotinos(self.fleet)
            self.statesRobotinoSignal.emit(self.fleet)
            time.sleep(self.POLL_TIME_STATEUPDATES)
        # reset stopflag after the cyclicStateUpdate got killed
        appLogger.info("[ROBOTINOMANAGER] Stopped cyclic state updates")
        self.stopFlagCyclicUpdates.clear()

    def automatedOperation(self):
        """
        Operates the Robotino in automated operation where it gets the transport tasks from the IAS-MES and executes them
        """
        appLogger.info("Started automated operation")
        self.stopFlagAutoOperation.clear()

        while not self.stopFlagAutoOperation.is_set():
            # poll transport task from mes
            if self.mesClient.serviceSocketIsAlive:
                self.transportTasks = self.mesClient.getTransportTasks(len(self.fleet))
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
                        appLogger.debug(
                            f"Got transport task {task} from MES. Assigning to Robotino"
                        )
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
                                robotino.start()
                                break

            time.sleep(self.POLL_TIME_TASKS)

        appLogger.info("Stopped automated operation")

        # reset stopflag after the automatedOperation got killed
        self.stopFlagAutoOperation.clear()

    def retryOp(self, errorMsg, robotinoId):
        """
        Retries an failed operation

        Args:
            errorMsg (str): message of error which identifies the op
            robotinoId (int): id of robotino with the error
            buttonClicked (bool): button which was clicked in the errordialog (optional)
        """
        robotino = self.getRobotino(robotinoId)
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
        self.commandInfo = msg
        id = self._getIDfromCommandInfo()
        self.getRobotino(int(id)).setCommandInfo(msg)

    def getRobotino(self, id):
        for robotino in self.fleet:
            if robotino.id == id:
                return robotino
        appLogger.error(
            "[ROBOTINOMANAGER] Couldnt return robotino, because it doesnt exist"
        )
        return None

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
    
    def emitNewTaskInfo(self,start:int,target:int,robotinoId:int,state:str):
        self.newTaskInfoSignal.emit(start,target,robotinoId,state)

    
    def emitDeleteTaskInfo(self,start:int,target:int,robotinoId:int,state:str):
        self.deleteTaskInfoSignal.emit(start,target,robotinoId,state)

    def stop(self):
        self.isAutoMode = False
        self.runsStateUpdates = False
        self.stopFlagAutoOperation.set()
        self.stopFlagCyclicUpdates.set()
        self.stopFlag.set()
        for robotino in self.fleet:
            robotino.stopFlagAutoOperation.set()
        self.fleet = []
        self.statesRobotinoSignal.emit(self.fleet)


if __name__ == "__main__":
    from commandserver.robotinoserver import RobotinoServer
    from mescommunicator.mesclient import MESClient

    # setup components
    commandServer = RobotinoServer()
    mesClient = MESClient()
    robotinoManager = RobotinoManager(mesClient=mesClient, robotinoServer=commandServer)
    # link component to robotinomanager so commandserver could update tasks
    commandServer.setRobotinoManager(robotinoManager)
