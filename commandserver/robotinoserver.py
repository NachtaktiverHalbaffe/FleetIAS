"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


import socket
from threading import Thread, Event, Lock
from PySide6.QtCore import QThread, Signal

from conf import IP_FLEETIAS, TCP_BUFF_SIZE, appLogger


class RobotinoServer(QThread):
    """
    Class for sending commands to Robotino for executing them with proprietary software
    """

    stoppedSignal = Signal()
    errorSignal = Signal(str, int)

    def __init__(self):
        super(RobotinoServer, self).__init__()
        # setup addr
        self.ADDR = (IP_FLEETIAS, 13000)
        # setup socket
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.stopFlag = Event()
        self.lock = Lock()
        # messages
        self.encodedMsg = ""
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
            appLogger.warning(e)

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
                try:
                    client.send(data)
                    self.encodedMsg = ""
                    response = client.recv(TCP_BUFF_SIZE)

                    if response:
                        response = response.decode("utf-8")
                        # print(response)
                        # -------------------- Error handling ------------------------
                        # station doesnt respond when loading/unloading carrier
                        if "error" in response.lower():
                            _, id = self._parseCommandInfo(response)
                            # Give Robotino error msgs
                            if self.robotinoManager != None:
                                self.robotinoManager.setCommandInfo(response)
                            errMsg = ""
                            if (
                                "loadbox" in response.lower()
                                and "station" in response.lower()
                            ):
                                errMsg = (
                                    "Error while loading carrier: Station didn't respond"
                                )
                                appLogger.error(errMsg)
                            elif (
                                "unloadbox" in response.lower()
                                and "station" in response.lower()
                            ):
                                errMsg = (
                                    "Error while unloading Carrier: Station didn't respond"
                                )
                            # robotino tries to undock but isnt docked
                            elif "docked" in response.lower():
                                errMsg = "Error while undocking from resource: Robotino isn't docked"
                            # robotino tries to dock but didnt find markers to dock
                            elif "station" in response.lower():
                                errMsg = "Error while docking to resource: Robotino couldn't find markers to dock"
                            # robotino tries to drive to resource but path is blocked
                            elif "path" in response.lower():
                                errMsg = "Error while driving to resource: Path is blocked"
                            # robotino tries to load carrier, but a carrier is already present on robotino
                            elif "loadbox" in response.lower():
                                errMsg = "Error while loading carrier: A carrier is already present on carrier"
                            elif "unloadbox" in response.lower():
                                errMsg = "Error while unloading carrier: After finishing operation the box is still present"
                            # robotino tries to load carrier, but didnt get a carrier from station
                            elif "present" in response.lower():
                                errMsg = "Error while unloading carrier: Robotino hasn't a box present"
                            elif "loadbox" in response.lower() and "no_box" in response.lower():
                                errMsg = "Error while loading carrier: Carrier was not sucessfully loaded"
                            else:
                                print(f"Unclassified error occured: {response}")

                            self.errorSignal.emit(errMsg, id)
                            appLogger.error(errMsg)
                            self.endTask(id)

                        # -------- Handling responses from commands -----------
                        # response from commandexecution
                        if "commandinfo" in response.lower():
                            if self.robotinoManager != None:
                                self.robotinoManager.setCommandInfo(response)
                        # fetch state message
                        elif "robotinfo" in response.lower():
                            strId = response.split("robotinoid:")
                            id = int(strId[1][0])
                            if self.robotinoManager != None:
                                robotino = self.robotinoManager.getRobotino(id)
                                robotino.fetchStateMsg(response)
                        # create/update fleet
                        elif "allrobotinoid" in response.lower():
                            if self.robotinoManager != None:
                                self.robotinoManager.createFleet(response)
                        # print out response which isnt handled when received
                        else:
                            appLogger.error(
                                "Catched unhandled response from robotino: " + str(response)
                            )
                except Exception as e:
                    print(e)

    def strToBin(self, request):
        """
        Converts the string to binary which the server can send

        Args:
            request (str): The message to convert
        """
        self.encodedMsg = ""
        for i in range(len(request)):
            # convert character to hex value
            self.encodedMsg += str(format(ord(request[i]), "x"))
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
        request = "PushCommand " + str(resourceId) + " LoadBox 0"
        self.strToBin(request)

    def unloadBox(self, resourceId=7):
        """
        Native command to let the robotino unload the carrier

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        request = "PushCommand " + str(resourceId) + " UnloadBox 0"
        self.strToBin(request)

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

        request = f"PushCommand {resourceId} GoToPosition {position}"
        self.strToBin(request)

    def dock(self, resourceId=7):
        """
        Command to let the robotino dock to a resource

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        request = f"PushCommand {resourceId} DockTo 1"
        self.strToBin(request)

    def undock(self, resourceId=7):
        """
        Command to let the robotino undock from an resource

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Return:
            Nothing
        """
        request = f"PushCommand {resourceId} Undock"
        self.strToBin(request)

    def getRobotinoInfo(self, resourceId=7):
        """
        Command to get the state from an robotino

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        request = f"GetRobotInfo {resourceId}"
        self.strToBin(request)

    def getAllRobotinoID(self):
        """
        Command to get the resourceIds of all active robotinos
        """
        # self.response = "PushCommand GetAllRobotinoID"
        request = "GetAllRobotinoID"
        self.strToBin(request)

    def endTask(self, resourceId=7):
        """
        Command to get the resourceIds of all active robotinos

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        # self.response = "PushCommand GetAllRobotinoID"
        request = f"EndTask {resourceId}"
        self.strToBin(request)

    def ack(self, resourceId=7):
        """
        Command to tell robotino that it has ended it transport task

        Args:
            resourceId (int): ResourceId of robotino which should execute the task

        Returns:
            Nothing
        """
        request = f"PushCommand {resourceId} Thank You"
        self.strToBin(request)

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
            if len(state)>= 2:
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
