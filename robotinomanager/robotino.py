"""
Filename: robotino.py
Version name: 1.1, 2022-12-02
Short description: Robotino class

(C) 2003-2022 IAS, Universitaet Stuttgart

"""
from threading import Thread
from conf import errLogger
import threading
import time


class Robotino(object):
    def __init__(self, mesClient, commandServer):
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
        # instances of mesclient and commandserver for executing operations
        self.mesClient = mesClient
        self.commandServer = commandServer
        self.task = (0, 0)
        self.commandInfo = ""
        # settings for robotino
        self.useOldControl = True
        # For task execution sychronization
        self.lock = threading.Lock()

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
            errLogger.error("[ROBOTINO] Could'nt fetch state from statemessage")
        # fetch battery voltage
        strBattery = msg.split("batteryvoltage:")
        strBattery = strBattery[1].split(" ")
        self.batteryVoltage = float(strBattery[0])
        # fetch laserwarning
        strLaserWarning = msg.split("laserwarning:")
        strLaserWarning = strLaserWarning[1].split(" ")
        if "0" in strLaserWarning[0]:
            self.laserWarning = False
        elif "1" in strLaserWarning[0]:
            self.laserWarning = True
            self.errorL2 = True
        else:
            errLogger.error("[ROBOTINO] Couldnt fetch laserwarning from statemessage")
        # fetch laserSaftey
        strLaserSafey = msg.split("lasersafety:")
        strLaserSafey = strLaserSafey[1].split(" ")
        if "0" in strLaserSafey[0]:
            self.laserSaftey = False
        elif "1" in strLaserSafey[0]:
            self.laserSaftey = True
            self.errorL2 = True
        else:
            errLogger.error("[ROBOTINO] Couldnt fetch lasersaftey from statemessage")
        # fetch boxPresent
        strBox = msg.split("boxpresent:")
        strBox = strBox[1].split(" ")
        if "0" in strBox[0]:
            self.boxPresent = False
        elif "1" in strBox[0]:
            self.boxPresent = True
        else:
            errLogger.error("[ROBOTINO] Couldnt fetch boxpresent from statemessage")
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
        print("ResourceId: " + str(self.id))
        print("AutoMode: " + str(self.autoMode))
        print("ManualMode: " + str(self.manualMode))
        print("Busy: " + str(self.busy))
        print("Reset: " + str(self.reset))
        print("ErrorL0: " + str(self.errorL0))
        print("ErrorL1: " + str(self.errorL1))
        print("ErrorL2: " + str(self.errorL2))
        print("MesMode: " + str(self.mesMode))
        print("Battery voltage: " + str(self.batteryVoltage))
        print("Laser Warning: " + str(self.laserWarning))
        print("Laser Saftey: " + str(self.laserSaftey))
        print("Box present: " + str(self.boxPresent))
        print("Position x: " + str(self.positionX))
        print("Position y: " + str(self.positionY))
        print("Position phi: " + str(self.positionPhi))

    def loadCarrier(self):
        """
        Push command to load carrier to Robotino and send corresponding servicerequest to IAS-MES
        """
        # Thread(target=self.mesClient.delBuf, args=[
        #     self.id]).start()
        Thread(target=self.commandServer.loadBox, args=[self.id]).start()
        if self._waitForOpStart("Started-LoadBox"):
            Thread(
                target=self.mesClient.moveBuf, args=[self.id, self.dockedAt, True]
            ).start()

    def unloadCarrier(self):
        """
        Push command to unload carrier to Robotino and send corresponding servicerequest to IAS-MES
        """
        Thread(target=self.commandServer.unloadBox, args=[self.id]).start()
        if self._waitForOpStart("Started-UnloadBox"):
            Thread(
                target=self.mesClient.moveBuf, args=[self.id, self.dockedAt, False]
            ).start()

    def dock(self, position):
        """
        Push command to dock to an resource to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            position (int): ResourceId of resource which it docks to
        """
        self.dockedAt = int(position)
        self.target = int(position)
        Thread(
            target=self.mesClient.setDockingPos, args=[self.dockedAt, self.id]
        ).start()
        if self.useOldControl:
            Thread(target=self.commandServer.dock, args=[self.id]).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for docking implemented. Using old control"
            )

    def undock(self):
        """
        Push command to undock from resource to Robotino and send corresponding servicerequest to IAS-MES
        """
        self.dockedAt = 0
        if self.useOldControl:
            Thread(target=self.commandServer.undock, args=[self.id]).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for undocking implemented. Using old controls"
            )

        Thread(
            target=self.mesClient.setDockingPos, args=[self.dockedAt, self.id]
        ).start()

    def driveTo(self, position):
        """
        Push command to drive to an resource to Robotino and send corresponding servicerequest to IAS-MES

        Args:
            position (int): ResourceId of resource which it drives to
        """
        self.target = int(position)
        # use commands to let robotino drive with its own steering
        if self.useOldControl:
            Thread(
                target=self.commandServer.goTo, args=[int(position), self.id]
            ).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for undocking implemented. Using old controls"
            )

    def driveToCor(self, position):
        """
        Push command to drive to a coordinate to Robotino and send corresponding servicerequest to IAS-MES

        Args:
             position ((int, int)): Coordinate where the Robotio should drive to. Is a (x,y)-tuple
        """
        self.target = int(position)
        # use commands to let robotino drive with its own steering
        if self.useOldControl:
            Thread(
                target=self.commandServer.goTo,
                args=[int(position), self.id, "coordinate"],
            ).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for undocking implemented. Using old controls"
            )

    def driveToROS(self, position):
        """
        Push command to drive to an resource using the ROS-Stack

        Args:
            position (int): ResourceId of resource which it drives to
        """
        Thread(
            target=self.commandServer.goToROS,
            args=[int(position), self.id],
        ).start()

    def driveToCorROS(self, position):
        """
        Push command to drive to a coordinate using the ROS-Stack

        Args:
            position ((int, int)): Coordinate where the Robotio should drive to. Is a (x,y)-tuple
        """
        x = int(position[0])
        y = int(position[1])
        Thread(
            target=self.commandServer.goToROS,
            args=[(x, y), self.id, "coordinate"],
        ).start()

    def setDockingPos(self, position):
        """
        Push command to set manually the docking position in the IAS-MES

        Args:
            position (int): ResourceId of resource which it is docked
        """
        self.target = int(position)
        Thread(
            target=self.mesClient.setDockingPos, args=[int(position), self.id]
        ).start()

    def endTask(self):
        """
        Push command end the task which also resets error
        """
        Thread(target=self.commandServer.endTask, args=[self.id]).start()
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
            state = state[1]

            return id, state
        else:
            return 0, ""

    def _waitForOpStart(self, strFinished):
        """
        Waits until automatic operation is started

        Args:
            robotinoId (int): id of robotino which waits
            strFinished (str): message which is received when operation is finished

        Returns:
            bool: If operation ended successfully (True) or not (False)
        """
        while True:
            id, state = self._parseCommandInfo()
            if id == self.id and state == strFinished:
                return True
            else:
                time.sleep(0.5)

    """
    Setter
    """

    def setCommandInfo(self, msg):
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

    def enableOldControl(self):
        self.useOldControl = True

    def disableOldControl(self):
        self.useOldControl = False
