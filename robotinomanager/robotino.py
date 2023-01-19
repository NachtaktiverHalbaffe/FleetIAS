"""
Filename: robotino.py
Version name: 1.1, 2022-12-02
Short description: Robotino class

(C) 2003-2022 IAS, Universitaet Stuttgart

"""
import time
from PySide6.QtCore import Signal, QThread
from threading import Event, Lock

from conf import appLogger


class Robotino(QThread):
    deleteTaskInfoSignal = Signal(int, int, int, str)
    newTaskInfoSignal = Signal(int, int, int, str)

    def __init__(self, mesClient, robotinoServer):
        super(Robotino, self).__init__()
        # params for state
        self.id = 0
        self.autoMode = False
        self.manualMode = False
        self.busy = False
        self.reset = False
        self.errorL0 = False
        self.errorL1 = False
        self.errorL2 = False
        self.mesMode = False
        self.batteryVoltage = 0.0
        self.laserWarning = False
        self.laserSaftey = False
        self.boxPresent = False
        self.positionX = 0.0
        self.positionY = 0.0
        self.positionPhi = 0.0
        self.dockedAt = 0
        self.target = 0
        # instances of mesclient and robotinoserver for executing operations
        self.mesClient = mesClient
        self.robotinoServer = robotinoServer
        self.task = (0, 0)
        self.commandInfo = ""
        # For task execution sychronization
        self.lock = Lock()
        self.stopFlagAutoOperation = Event()

    def run(self):
        self.executeTransportTask()

    def fetchStateMsg(self, msg):
        """
        Fetches state message and parses them into the state attributes

        Args:
            msg (str): State message from which the information gets fetched
        """
        self.errorL2 = False
        # fetch resourceId
        strId = msg.split("robotinoid:")
        self.id = int(strId[1][0])
        # fetch state
        strState = msg.split("state:")
        if "IDLE" in strState[1]:
            self.busy = False
        elif "BUSY" in strState[1]:
            self.busy = True
        elif "ERROR" in strState[1]:
            self.busy = False
            self.errorL2 = True
        else:
            appLogger.error("[ROBOTINO] Could'nt fetch state from statemessage")
        # fetch battery voltage
        strBattery = msg.split("batteryvoltage:")
        strBattery = strBattery[1].split(" ")
        self.batteryVoltage = float(strBattery[0])
        # fetch laserwarning
        strLaserWarning = msg.split("laserwarning:")
        if len(strLaserWarning)>= 2:
            strLaserWarning = strLaserWarning[1].split(" ")
        if "0" in strLaserWarning[0]:
            self.laserWarning = False
        elif "1" in strLaserWarning[0]:
            self.laserWarning = True
            self.errorL2 = True
        else:
            appLogger.error("[ROBOTINO] Couldnt fetch laserwarning from statemessage")
        # fetch laserSaftey
        strLaserSafey = msg.split("lasersafety:")
        strLaserSafey = strLaserSafey[1].split(" ")
        if "0" in strLaserSafey[0]:
            self.laserSaftey = False
        elif "1" in strLaserSafey[0]:
            self.laserSaftey = True
            self.errorL2 = True
        else:
            appLogger.error("[ROBOTINO] Couldnt fetch lasersaftey from statemessage")
        # fetch boxPresent
        strBox = msg.split("boxpresent:")
        strBox = strBox[1].split(" ")
        if "0" in strBox[0]:
            self.boxPresent = False
        elif "1" in strBox[0]:
            self.boxPresent = True
        else:
            appLogger.error("[ROBOTINO] Couldnt fetch boxpresent from statemessage")
        # fetch position x
        strPosX = msg.split("x:")
        strPosX = strPosX[1].split(" ")
        self.positionX = float(strPosX[0])
        # fetch position y
        strPosY = msg.split("y:")
        strPosY = strPosY[1].split(" ")
        self.positionY = float(strPosY[0])
        # fetch position phi
        strPosPhi = msg.split("phi:")
        strPosPhi = strPosPhi[1].split(" ")
        self.positionPhi = float(strPosPhi[0])

    def printState(self):
        """
        Print out all state attributes of Robotino. Just for debugging
        """
        appLogger.debug("ResourceId: " + str(self.id))
        appLogger.debug("AutoMode: " + str(self.autoMode))
        appLogger.debug("ManualMode: " + str(self.manualMode))
        appLogger.debug("Busy: " + str(self.busy))
        appLogger.debug("Reset: " + str(self.reset))
        appLogger.debug("ErrorL0: " + str(self.errorL0))
        appLogger.debug("ErrorL1: " + str(self.errorL1))
        appLogger.debug("ErrorL2: " + str(self.errorL2))
        appLogger.debug("MesMode: " + str(self.mesMode))
        appLogger.debug("Battery voltage: " + str(self.batteryVoltage))
        appLogger.debug("Laser Warning: " + str(self.laserWarning))
        appLogger.debug("Laser Saftey: " + str(self.laserSaftey))
        appLogger.debug("Box present: " + str(self.boxPresent))
        appLogger.debug("Position x: " + str(self.positionX))
        appLogger.debug("Position y: " + str(self.positionY))
        appLogger.debug("Position phi: " + str(self.positionPhi))

    def executeTransportTask(self):
        """
        Execute an transport task which got assigend from the IAS-MES
        """
        SLEEP_TIME = 1
        self.busy = True
        self.stopFlagAutoOperation.clear()

        ### --------------------  Load carrier at start ------------------------
        # only do updates in gui if module runs/is configured with gui
        self._updateTaskFrontend("Driving to start")
        time.sleep(SLEEP_TIME)
        # drive to start
        if self.dockedAt != int(self.task[0]):
            self.driveTo(self.task[0], retryOp=False)
        # dock to resource
        self._updateTaskFrontend("Docking at start")
        time.sleep(SLEEP_TIME)
        if self.dockedAt != int(self.task[0]):
            self.dock(self.task[0], retryOp=False)
        # load box
        self._updateTaskFrontend("Loading")
        time.sleep(SLEEP_TIME)
        self.loadCarrier(retryOp=False)
        # undock
        time.sleep(SLEEP_TIME)
        self.undock(retryOp=False)

        # -------------------- Unload carrier at target ------------------------
        # drive to target
        self._updateTaskFrontend("Transporting")
        time.sleep(SLEEP_TIME)
        self.driveTo(self.task[1], retryOp=False)
        # dock to resource
        self._updateTaskFrontend("Docking at target")
        time.sleep(SLEEP_TIME)
        self.dock(self.task[1], retryOp=False)
        # Unload box
        self._updateTaskFrontend("Unloading")
        time.sleep(SLEEP_TIME)
        self.unloadCarrier(retryOp=False)

        # ---------------------------- Finishing task --------------------------
        # update state of transport task in gui
        self._updateTaskFrontend("finished")
        # inform robotino
        # self.robotinoServer.lock.acquire()
        # self.robotinoServer.ack(self.id)
        # self.robotinoServer.lock.release()
        # remove task from robotino
        appLogger.debug(f"Robotino {self.id} finished transport task {self.task}")

        self.deleteTaskInfoSignal.emit(self.task[0], self.task[1], self.id, "finished")
        self.task = (0, 0)
        self.busy = False
        self.stopFlagAutoOperation.set()

    def loadCarrier(self, retryOp=False):
        """
        Push command to load carrier to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            retryOp (bool, optional): If Robotino should retry operation when it fails. Defaults to False
        """
        ERROR_MSGS = ["NoStationResponse", "PartAlreadyPresent", "NoPartLoaded"]
        self.lock.acquire()

        self.robotinoServer.lock.acquire()
        self.robotinoServer.loadBox(self.id)
        self.robotinoServer.lock.release()

        # Update state in IAS-MES
        if (
            self._waitForOpResponse("Started-LoadBox")
            and self.mesClient.serviceSocketIsAlive
        ):
            self.mesClient.moveBuf(self.id, self.dockedAt, True)

        if self._waitForOpResponse("Finished-LoadBox", errMsgs=ERROR_MSGS):
            self.lock.release()
            appLogger.debug(
                f"Robotino {self.id} finished loading carrier at resource {self.dockedAt}"
            )
        elif retryOp:
            self.lock.release()
            self.loadCarrier(not retryOp)
        else:
            self.lock.release()
            self.endTask()
            appLogger.error(
                f"Error occured while Robotino {self.id} ftried to load carrier at resource {self.dockedAt}"
            )

    def unloadCarrier(self, retryOp=False):
        """
        Push command to unload carrier to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            retryOp (bool, optional): If Robotino should retry operation when it fails. Defaults to False
        """
        ERR_MSGS = ["NoStationResponse", "PartNotPresent", "PartNotUnloaded"]
        self.lock.acquire()

        self.robotinoServer.lock.acquire()
        self.robotinoServer.unloadBox(self.id)
        self.robotinoServer.lock.release()

        # Update state in IAS-MES
        if (
            self._waitForOpResponse("Started-UnloadBox")
            and self.mesClient.serviceSocketIsAlive
        ):
            self.mesClient.moveBuf(self.id, self.dockedAt, False)
        if self._waitForOpResponse("Finished-UnloadBox", errMsgs=ERR_MSGS):
            self.lock.release()
            appLogger.debug(
                f"Robotino {self.id} finished unloading carrier at resource {self.dockedAt}"
            )
        elif retryOp:
            self.lock.release()
            self.unloadCarrier(not retryOp)
        else:
            self.lock.release()
            self.endTask()
            appLogger.error(
                f"Error occured while Robotino {self.id} tried to unload carrier at resource {self.dockedAt}"
            )

    def dock(self, position, retryOp=False):
        """
        Push command to dock to an resource to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            position (int): ResourceId of resource which it docks to
            retryOp (bool, optional): If Robotino should retry operation when it fails. Defaults to False
        """
        ERR_MSGS = ["NoMarkerDetected"]
        self.dockedAt = int(position)
        self.target = int(position)

        self.lock.acquire()

        self.robotinoServer.lock.acquire()
        self.robotinoServer.dock(self.id)
        self.robotinoServer.lock.release()

        # Update state in IAS-MES
        if self._waitForOpResponse("Finished-DockTo", errMsgs=ERR_MSGS):
            if self.mesClient.serviceSocketIsAlive:
                self.mesClient.setDockingPos(self.dockedAt, self.id)
                self.lock.release()
                appLogger.debug(
                    f"Robotino {self.id} finished docking at resource {position}"
                )
        elif retryOp:
            self.lock.release()
            self.dock(position, not retryOp)
        else:
            self.lock.release()
            self.endTask()
            appLogger.error(
                f"Error occured while Robotino {self.id} tried to dock at resource {position}"
            )

    def undock(self, retryOp=False):
        """
        Push command to undock from resource to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            retryOp (bool, optional): If Robotino should retry operation when it fails. Defaults to False
        """
        ERR_MSGS = ["NotDocked"]
        self.lock.acquire()

        self.robotinoServer.lock.acquire()
        self.robotinoServer.undock(self.id)
        self.robotinoServer.lock.release()

        # Update state in IAS-MES
        if self._waitForOpResponse("Finished-Undock", errMsgs=ERR_MSGS):
            if self.mesClient.serviceSocketIsAlive:
                self.mesClient.setDockingPos(self.dockedAt, self.id)

            self.lock.release()
            appLogger.debug(
                f"Robotino {self.id} finished undocking from resource {self.dockedAt}"
            )
            self.dockedAt = 0
        elif retryOp:
            self.lock.release()
            self.undock(not retryOp)
        else:
            self.lock.release()
            self.endTask()
            appLogger.error(
                f"Error occured while Robotino {self.id} undocking from resource {self.dockedAt}"
            )

    def driveTo(self, position, retryOp=False):
        """
        Push command to drive to an resource to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            position (int): ResourceId of resource which it drives to
            retryOp (bool, optional): If Robotino should retry operation when it fails. Defaults to False
        """
        ERR_MSGS = ["PathBlocked"]
        self.target = int(position)
        self.setDockingPos(0)
        self.lock.acquire()

        self.robotinoServer.lock.acquire()
        self.robotinoServer.goTo(self.target, self.id)
        self.robotinoServer.lock.release()

        if self._waitForOpResponse("Finished-GotoPosition", errMsgs=ERR_MSGS):
            self.lock.release()
            appLogger.debug(
                f"Robotino {self.id} finished driving to resource {position}"
            )
        elif retryOp:
            self.lock.release()
            self.driveTo(position, not retryOp)
        else:
            self.lock.release()
            self.endTask()
            appLogger.error(
                f"Error occurred while Robotino {self.id} drove to resource {position}"
            )

    def driveToCor(self, position, retryOp=False):
        """
        Push command to drive to a coordinate to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            position ((int, int)): Coordinate where the Robotio should drive to. Is a (x,y)-tuple
            retryOp (bool, optional): If Robotino should retry operation when it fails. Defaults to False
        """
        self.target = (int(position[0]), int(position[1]))
        self.lock.acquire()

        self.robotinoServer.lock.acquire()
        self.robotinoServer.goTo(self.target, self.id, "coordinate")
        self.robotinoServer.lock.release()

        if self._waitForOpResponse("Finished-DriveToManual"):
            self.lock.release()
            appLogger.debug(
                f"Robotino {self.id} finished driving to coordinate {position}"
            )
        elif retryOp:
            self.lock.release()
            self.driveToCor(position, not retryOp)
        else:
            self.lock.release()
            self.endTask()
            appLogger.error(
                f"Error occured while Robotino {self.id} drove to coordinate {position}"
            )

    def setDockingPos(self, position):
        """
        Push command to set manually the docking position in the IAS-MES

        Args:
            position (int): ResourceId of resource which it is docked
        """
        self.target = int(position)
        self.dockedAt = int(position)
        if self.mesClient.serviceSocketIsAlive:
            self.mesClient.setDockingPos(int(position), self.id)

    def endTask(self):
        """
        Push command end the task which also resets error
        """
        self.robotinoServer.lock.acquire()
        self.robotinoServer.endTask(self.id)
        self.robotinoServer.lock.release()
        self.target = 0
        self.task = (0, 0)

    def _parseCommandInfo(self):
        """
        Splits the commandinfo into an id and state

        Returns:
            state (str): string with the state message of the command info
            id (int): resourceId of Robotino from which the command info comes
        """
        id = self.commandInfo.split("robotinoid:")
        if id[0] != "":
            id = int(id[1][0])
            state = self.commandInfo.split('"')
            if len(state)>=2:
                state = state[1]
            else:
                state =""
            return id, state
        else:
            return 0, ""

    def _updateTaskFrontend(self, strState):
        """
        Updates the state of an transporttaks in the frontend

        Args:
            strState (str): String of state which should be dislayed as state in frontend
        """
        self.deleteTaskInfoSignal.emit(self.task[0], self.task[1], self.id, strState)
        self.newTaskInfoSignal.emit(self.task[0], self.task[1], self.id, strState)

    def _waitForOpResponse(self, strFinished, errMsgs=[]):
        """
        Waits until automatic operation is started

        Args:
            robotinoId (int): id of robotino which waits
            strFinished (str): message which is received when operation is finished

        Returns:
            bool: If operation ended successfully (True) or not (False)
        """
        while not self.stopFlagAutoOperation.is_set():
            id, state = self._parseCommandInfo()
            # print(f"Robotino id: {id}\nRobotino state message:  {state}")
            if state=="":
                continue
            # Check for errorMsgs which show failure for operation
            for errMsg in errMsgs:
                if state.lower() in errMsg.lower():
                    return False

            # Check for response which show successful operation
            if (int(id) == int(self.id)) and (state.lower() in strFinished.lower()):
                return True
            # Check if autooperation stopped and no waiting for response is needed
            elif self.stopFlagAutoOperation.is_set():
                return False
            else:
                time.sleep(1)

    """
    Setter
    """

    def setCommandInfo(self, msg):
        appLogger.debug(f"Set commandinfo for Robotino {self.id}: {msg}")
        self.commandInfo = msg

    def activateAutoMode(self):
        self.manualMode = False
        self.autoMode = True

    def activateManualMode(self):
        self.autoMode = False
        self.manualMode = True

    def setMode(self, mode):
        if str(mode) == "Automated":
            self.activateAutoMode
        elif str(mode) == "Manual":
            self.activateManualMode
