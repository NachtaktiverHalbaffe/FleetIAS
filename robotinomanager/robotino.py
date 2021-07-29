"""
Filename: robotino.py
Version name: 1.0, 2021-07-22
Short description: Robotino class

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
from threading import Thread
from conf import errLogger


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
        # settings for robotino
        self.useOldControl = True

    # fetches state message and parses them into the state attributes
    # @params:
    #   msg: state message from which the information gets fetched
    def fetchStateMsg(self, msg):
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
            errLogger.errorv(
                "[ROBOTINO] Couldnt fetch state from statemessage")
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
            errLogger.error(
                "[ROBOTINO] Couldnt fetch laserwarning from statemessage")
        # fetch laserSaftey
        strLaserSafey = msg.split("lasersafety:")
        strLaserSafey = strLaserSafey[1].split(" ")
        if "0" in strLaserSafey[0]:
            self.laserSaftey = False
        elif "1" in strLaserSafey[0]:
            self.laserSaftey = True
            self.errorL2 = True
        else:
            errLogger.error(
                "[ROBOTINO] Couldnt fetch lasersaftey from statemessage")
        # fetch boxPresent
        strBox = msg.split("boxpresent:")
        strBox = strBox[1].split(" ")
        if "0" in strBox[0]:
            self.boxPresent = False
        elif "1" in strBox[0]:
            self.boxPresent = True
        else:
            errLogger.error(
                "[ROBOTINO] Couldnt fetch boxpresent from statemessage")
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

    # print out all state attributes of robotino
    def printState(self):
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

    # push command to load carrier to robotino and send corresponding servicerequest to mes
    def loadCarrier(self):
        Thread(target=self.mesClient.moveBuf, args=[
            self.id, self.dockedAt, True]).start()
        Thread(target=self.commandServer.loadBox, args=[self.id]).start()

    # push command to unload carrier to robotino and send corresponding servicerequest to mes
    def unloadCarrier(self):
        Thread(target=self.mesClient.moveBuf, args=[
            self.id, self.dockedAt, False]).start()
        Thread(target=self.commandServer.unloadBox, args=[self.id]).start()

    # push command to dock to an resource to robotino and send corresponding servicerequest to mes
    # @params:
    #   position: resourceId of resource which it docks to
    def dock(self, position):
        self.dockedAt = int(position)
        self.target = int(position)
        Thread(target=self.mesClient.setDockingPos,
               args=[self.dockedAt, self.id]).start()
        if self.useOldControl:
            Thread(target=self.commandServer.dock, args=[self.id]).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for docking implemented")

    # push command to undock from resource to robotino and send corresponding servicerequest to mes
    def undock(self):
        self.dockedAt = 0
        Thread(target=self.mesClient.setDockingPos,
               args=[self.dockedAt, self.id]).start()

        if self.useOldControl:
            Thread(target=self.commandServer.undock, args=[self.id]).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for undocking implemented")

    # push command to drive to an resource to robotino and send corresponding servicerequest to mes
    # @params:
    #   position: resourceId of resource which it drives to
    def driveTo(self, position):
        self.target = int(position)
        # use commands to let robotino drive with its own steering
        if self.useOldControl:
            Thread(target=self.commandServer.goTo,
                   args=[int(position), self.id]).start()
        else:
            # implement own way of controlling
            errLogger.error(
                "[ROBOTINO] Old Controls are disabled, but theres no new control for driving to resource implemented")

    # push command to set manually the docking position in the mes
    # @params:
    #   position: resourceId of resource which it is docked
    def setDockingPos(self, position):
        self.target = int(position)
        Thread(target=self.mesClient.setDockingPos,
               args=[int(position), self.id]).start()

    # push command end the task which also resets error
    def endTask(self):
        Thread(target=self.commandServer.endTask,
               args=[self.id]).start()
        self.target = 0
        self.task = (0, 0)
    """
    Setter
    """

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
