"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


import socket
import json
from threading import Thread, Event
from PySide6.QtCore import QThread, Signal

from conf import IP_ROS, IP_FLEETIAS, TCP_BUFF_SIZE, appLogger, rosLogger
from robotinomanager.robotinomanager import RobotinoManager


class RobotinoServer(QThread):
    """
    Class for sending commands to robotino or ROS

    Attributes
    ----------
    PORT : int
        TCP Port for the robotino server
    PORTROS: int
        TCP port of the ROS TCP server
    HOST : str
        IP address of FleetIAS
    HOSTROS  : str
        IP adress of ROS master
    ADDR: (str, int)
        Complete ip address of robotino server
    ADDRROS: (str, int)
        Complete ip address of ROS TCP server
    """

    stoppedSignal = Signal()

    def __init__(self):
        super(RobotinoServer, self).__init__()
        # setup addr
        self.PORT = 13000
        self.PORTROS = 13002
        # self.HOST = IP_FLEETIAS
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.HOSTROS = IP_ROS
        self.ADDR = (self.HOST, self.PORT)
        self.ADDRROS = (self.HOSTROS, self.PORTROS)

        # setup socket
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.FORMAT = "utf-8"
        self.buffSize = TCP_BUFF_SIZE
        self.stopFlag = Event()
        # messages
        self.response = ""
        self.encodedMsg = ""

        # messages requested to the ROS pc
        self.request = {}

        # robotinomanager for delegating messages to be handled
        self.robotinoManager = None

    def run(self):
        self.stopFlag.clear()
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        appLogger.info("Robotinoserver started")
        # Start Tcp server
        try:
            self.SERVER.bind(self.ADDR)
            self.SERVER.listen()
            self.waitForConnection()
        except Exception as e:
            appLogger.error(e)

        self.stoppedSignal.emit()

    def waitForConnection(self):
        """
        Waits for a connection from a plc. When a plc connects, it starts a new thread for the service specific communication
        """
        while not self.stopFlag.is_set():
            try:
                client, addr = self.SERVER.accept()
                appLogger.info(f"{addr} connected to socket")
                Thread(target=self.commandCommunication, args=[client]).start()
            except Exception as e:
                appLogger.error(e)
                break

    def commandCommunication(self, client):
        """
        Thread for the command communication

        Args:
            client (Client): Socket of the Robotino
        """
        while not self.stopFlag.is_set():
            if len(self.robotinoManager.fleet) == 0 and self.encodedMsg == "":
                self.getAllRobotinoID()
            elif self.encodedMsg != "":
                data = bytes.fromhex(self.encodedMsg)
                client.send(data)
                self.encodedMsg = ""

                response = client.recv(self.buffSize)
                if response:
                    response = response.decode(self.FORMAT)
                    # Error handling
                    # station doesnt respond when loading/unloading carrier
                    if "NO_RESPONSE_FROM_STATION" in response:
                        state, id = self._parseCommandInfo(response)
                        if "LoadBox" in response:
                            errMsg = (
                                "Error while loading carrier: Station didn't respond"
                            )
                            appLogger.error(errMsg)
                        elif "UnloadBox" in response:
                            errMsg = (
                                "Error while unloading Carrier: Station didn't respond"
                            )
                            appLogger.error(errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to undock but isnt docked
                    elif "ROBOT_NOT_DOCKED" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = (
                            "Error while undocking from resource: Robotino isn't docked"
                        )
                        appLogger.error(errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to dock but didnt find markers to dock
                    elif "NO_DOCK_STATION" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while docking to resource: Robotino couldn't find markers to dock"
                        appLogger.error(errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to drive to resource but path is blocked
                    elif "PATH_BLOCKED" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while driving to resource: Path is blocked"
                        appLogger.error(errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to load carrier, but a carrier is already present on robotino
                    elif "BOX_PRESENT" in response and "LoadBox" in response:
                        state, id = self._parseCommandInfo(response)
                        if "LoadBox" in response:
                            errMsg = "Error while loading carrier: A carrier is already present on carrier"
                            appLogger.error(errMsg)
                        elif "UnloadBox" in response:
                            errMsg = "Error while unloading carrier: After finishing operation the box is still present"
                            appLogger.error(errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to load carrier, but didnt get a carrier from station
                    elif "NO_BOX" in response:
                        state, id = self._parseCommandInfo(response)
                        if "UnloadBox" in response:
                            errMsg = "Error while unloading carrier: Robotino hasn't a box present"
                            appLogger.error(errMsg)
                        elif "LoadBox" in response:
                            errMsg = "Error while loading carrier: Carrier was not sucessfully loaded"
                            appLogger.error(errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)

                    # info messages and responses from commands
                    # inform robotinomanager about commandinfo
                    if "CommandInfo" in response:
                        if self.robotinoManager != None:
                            Thread(
                                target=self.robotinoManager.setCommandInfo,
                                args=[response],
                            ).start()
                    # fetch state message
                    elif "RobotInfo" in response:
                        strId = response.split("robotinoid:")
                        id = int(strId[1][0])
                        if self.robotinoManager != None:
                            robotino = self.robotinoManager.getRobotino(id)
                            robotino.fetchStateMsg(response)
                    # create/update fleet
                    elif "AllRobotinoID" in response:
                        if self.robotinoManager != None:
                            Thread(
                                target=self.robotinoManager.createFleet, args=[response]
                            ).start()
                    # print out response which isnt handled when received
                    else:
                        appLogger.error(
                            "Catched unhandled response from robotino: " + str(response)
                        )

    def strToBin(self):
        """
        Converts the string to binary which the server can send

        Args:
            self.response:
        """
        self.encodedMsg = ""
        for i in range(len(self.response)):
            # convert character to hex value
            self.encodedMsg += str(format(ord(self.response[i]), "x"))
        # line of end ascii
        self.encodedMsg += "0a"

    def loadBox(self, resourceId=7):
        """
        Native command to let the robotino load the carrier

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        self.response = "PushCommand " + str(resourceId) + " LoadBox 0"
        self.strToBin()

    def unloadBox(self, resourceId=7):
        """
        Native command to let the robotino unload the carrier

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        self.response = "PushCommand " + str(resourceId) + " UnloadBox 0"
        self.strToBin()

    def goTo(self, position, resourceId=7, type="resource"):
        """
        Native command to let the robotino drive to an resource

        Args:
            resourceId (int): ResourceId of Robotino which should execute the task
            position (either int or (int, int)): Either resourceID of the target resource or coordinate. See argument type
            type (str, optional): Type of position. Can be either "resource" (position: resourceID) or "coordinate" (position (x,y)-tuple). Defaults to "resource"

        Returns:
            Nothing
        """
        if type == "resource":
            self.response = f"PushCommand {resourceId} GoToPosition {position}"
        elif type == "coordinate":
            # TODO sniff actual command
            self.response = f"PushCommand {resourceId} GoToManual {position}"
        else:
            appLogger.error(
                f'{type} is a invalid target type. Must be either "resource" or "coordinate"'
            )
        self.strToBin()

    def dock(self, resourceId=7):
        """
        Command to let the robotino dock to a resource

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        self.response = "PushCommand " + str(resourceId) + " DockTo 1"
        self.strToBin()

    def undock(self, resourceId=7):
        """
        Command to let the robotino undock from an resource

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Return:
            Nothing
        """
        self.response = "PushCommand " + str(resourceId) + " Undock"
        self.strToBin()

    def getRobotinoInfo(self, resourceId=7):
        """
        Command to get the state from an robotino

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        self.response = "GetRobotInfo " + str(resourceId)
        self.strToBin()

    def getAllRobotinoID(self):
        """
        Command to get the resourceIds of all active robotinos
        """
        # self.response = "PushCommand GetAllRobotinoID"
        self.response = "GetAllRobotinoID"
        self.strToBin()

    def endTask(self, resourceId=7):
        """
        Command to get the resourceIds of all active robotinos

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        # self.response = "PushCommand GetAllRobotinoID"
        self.response = "EndTask " + str(resourceId)
        self.strToBin()

    def ack(self, resourceId=7):
        """
        Command to tell robotino that it has ended it transport task

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        self.response = "PushCommand " + str(resourceId) + " Thank You"
        self.strToBin()

    def _parseCommandInfo(self, msg):
        """
        Splits the commandinfo into an id and state

        Args:
            msg (str): Message from which the state and id is extracted

        Returns:
            state (string): State message of the command info
            id (int): ResourceId of Robotino from which the command info comes
        """
        id = msg.split("robotinoid:")
        if id[0] != "":
            id = int(id[1][0])
            state = msg.split('"')
            state = state[1]

            return id, state
        else:
            return 0, ""

    """
    Setter
    """

    def setRobotinoManager(self, robotinoManager):
        self.robotinoManager = robotinoManager

    def stopServer(self):
        self.stopFlag.set()
        if self.robotinoManager != None:
            self.robotinoManager.stopCyclicStateUpdate()
            self.robotinoManager.stopAutomatedOperation()
        try:
            self.SERVER.shutdown(socket.SHUT_RDWR)
        except:
            pass
        appLogger.info("Robotinoserver stopped")


if __name__ == "__main__":
    sock = RobotinoServer()
    sock.start()