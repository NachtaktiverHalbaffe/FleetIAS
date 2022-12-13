"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from types import resolve_bases
from robotinomanager.robotinomanager import RobotinoManager
import socket
from threading import Thread, Event
from conf import IP_ROS, IP_FLEETIAS, TCP_BUFF_SIZE, errLogger, rosLogger, USEROSSYSTEM
import json


class CommandServer(object):
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

    def __init__(self):
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

    def __del__(self):
        self.SERVER.close()
        self.stopFlag.set()

    def runServer(self):
        self.stopFlag.clear()
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print("[COMMANDSERVER] Commandserver started")
        # Start Tcp server on seperate Thread
        SERVER_THREADING = Thread(target=self.waitForConnection)
        try:
            SERVER_THREADING.start()
        except Exception as e:
            print(e)

    def waitForConnection(self):
        """
        Waits for a connection from a plc. When a plc connects, it starts a new thread for the service specific communication
        """
        while not self.stopFlag.is_set():
            try:
                client, addr = self.SERVER.accept()
                print("[COMMANDSERVER]: " + str(addr) + "connected to socket")
                Thread(target=self.commandCommunication, args=[client]).start()
            except Exception as e:
                print(e)
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
                            errLogger.error("[COMMANDSERVER] " + errMsg)
                        elif "UnloadBox" in response:
                            errMsg = (
                                "Error while unloading Carrier: Station didn't respond"
                            )
                            errLogger.error("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to undock but isnt docked
                    elif "ROBOT_NOT_DOCKED" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = (
                            "Error while undocking from resource: Robotino isn't docked"
                        )
                        errLogger.error("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to dock but didnt find markers to dock
                    elif "NO_DOCK_STATION" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while docking to resource: Robotino couldn't find markers to dock"
                        errLogger.error("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to drive to resource but path is blocked
                    elif "PATH_BLOCKED" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while driving to resource: Path is blocked"
                        errLogger.error("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to load carrier, but a carrier is already present on robotino
                    elif "BOX_PRESENT" in response and "LoadBox" in response:
                        state, id = self._parseCommandInfo(response)
                        if "LoadBox" in response:
                            errMsg = "Error while loading carrier: A carrier is already present on carrier"
                            errLogger.error("[COMMANDSERVER] " + errMsg)
                        elif "UnloadBox" in response:
                            errMsg = "Error while unloading carrier: After finishing operation the box is still present"
                            errLogger.error("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to load carrier, but didnt get a carrier from station
                    elif "NO_BOX" in response:
                        state, id = self._parseCommandInfo(response)
                        if "UnloadBox" in response:
                            errMsg = "Error while unloading carrier: Robotino hasn't a box present"
                            errLogger.error("[COMMANDSERVER] " + errMsg)
                        elif "LoadBox" in response:
                            errMsg = "Error while loading carrier: Carrier was not sucessfully loaded"
                            errLogger.error("[COMMANDSERVER] " + errMsg)
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
                            id = response.split("robotinoid:")
                            if id[0] != "":
                                id = int(id[1][0])
                            if self.robotinoManager != None:
                                robotino = self.robotinoManager.getRobotino(id)
                                Thread(
                                    target=robotino.setCommandInfo, args=[response]
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
                        errLogger.error(
                            "[COMMANDSERVER] Catched unhandled response from robotino: "
                            + str(response)
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

    def goTo(self, position, resourceId=7):
        """
        Native command to let the robotino drive to an resource

        Args:
            resourceId (int): ResourceId of Robotino which should execute the task
            position (int): ResourceId of resource where it should drive to

        Returns:
            Nothing
        """
        self.response = (
            "PushCommand " + str(resourceId) + " GoToPosition " + str(position)
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

    def runClientROS(self, request={}):
        """
        Starts a client which sends the command to ROS and waits for the response

        Args:
            request (dict): The command which should be send to ROS. Has following format:
                    request = {
                        "command": command,
                        "someSpecificValueForCommand": value,
                    }
        """
        ROS_RESP_REACHED_TARGET = "Target reached"
        ROS_RESP_FEATURE = "Feature set"
        ROS_RESP_OFFSET = "Offset set"
        ROS_RESP_ERR = "Error"

        # Connect to ROS
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.HOSTROS, self.PORTROS))
        # Send command to ROS
        clientSocket.sendall(bytes(json.dumps(request), encoding="utf-8"))
        while not self.stopFlag.is_set():
            # Wait for response
            data = clientSocket.recv(1024).decode("utf-8")
            if data == ROS_RESP_REACHED_TARGET:
                rosLogger.info(f"Command run successfully on ROS: PushTarget")
            elif data == ROS_RESP_FEATURE:
                rosLogger.info(f"Command run successfully on ROS: ActivateFeature")
            elif data == ROS_RESP_OFFSET:
                rosLogger.info(f"Command run successfully on ROS: AddOffset")
            elif data.contains(ROS_RESP_ERR):
                errLogger.info(msg="[ROS] " + data.split(":")[1])
            else:
                errLogger.error(f"[ROS] Unkown response: {data}")
            clientSocket.close()
            break

    def goToROS(self, position, resourceId=7, type="resource"):
        """
        Sends a command to ROS where the Robotino should drive to an resource

        Args:
            position (either int or (int, int)): Either resourceID of the target resource or coordinate. See argument type
            type (str): Type of position. Can be either "resource" (position: resourceID) or "coordinate" (position (x,y)-tuple)
            resourceID (int): ResourceID of the robotino which should execute this command. Defaults to 7

        Returns:
            Nothing
        """
        if type == "resource":
            # Type checking
            if position > 0 and position < 8:
                rosLogger.info(
                    f"Send Command to ROS: PushTarget with targetID {position}"
                )
                request = {
                    "command": "PushTarget",
                    "robotinoID": resourceId,
                    "type": type,
                    "workstationID": position,
                }
            else:
                errLogger.error(
                    f"Argument position {position} has wrong format. Must be a int betwenn 1 and 7"
                )
                return
        elif type == "coordinate":
            if (position[0] >= 0 and position[0] <= 200) and (
                position[1] >= 0 and position[1] <= 200
            ):
                rosLogger.info(
                    f"Send Command to ROS: PushTarget with coordinate {position.toString()}"
                )
                request = {
                    "command": "PushTarget",
                    "robotinoID": resourceId,
                    "type": type,
                    "coordinate": position,
                }
            else:
                errLogger.error(
                    "Argument position {position} has wrong format. Must be a tuple (x,y), where both x and y are int betwenn 0 and 200"
                )
                return
        else:
            errLogger.error(
                f'{type} is a invalid target type. Must be either "resource" or "coordinate"'
            )
            return
        Thread(target=self.runClientROS, args=[request]).start()

    def ROSActivateFeature(self, feature, value=True, resourceId=7):
        """
        Sends a command to ROS where a certain feature gets activated (value: True) or deactivated (value: False)

        Args:
            feature (str): Name of feature which should get deactivated
            value (bool): If feature should be activated (True) or deactivated (False)
            resourceID (int): ResourceID of the robotino which should execute this command. Defaults to 7

        Returns:
            Nothing
        """
        if type(value) == bool:
            rosLogger.info(
                msg=f"Send Command to ROS: ActivateFeature with value {value}"
            )
            request = {
                "command": "PushTarget",
                "robotinoID": resourceId,
                "feature": feature,
                "value": value,
            }
            Thread(target=self.runClientROS, args=[request]).start()
        else:
            errLogger.error("Wrong argument value: {value}. Must be an bool")

    def ROSAddOffset(self, name, offset, resourceId=7):
        """
        Sends a command to ROS to add an Offset to a certain topic

        Args:
            name (str): Name of topic to which the offset should be added
            offset (dynamic): Value of offset which should be added to the topic
            resourceID (int): ResourceID of the robotino which should execute this command. Defaults to 7

        Returns:
            Nothing
        """
        if type(offset) == float:
            rosLogger.info(
                msg=f"Send Command to ROS: AddOffset to topic {name} with value {offset}"
            )
            request = {
                "command": "PushTarget",
                "robotinoID": resourceId,
                "feature": name,
                "offset": offset,
            }
            Thread(target=self.runClientROS, args=[request]).start()
        else:
            errLogger.error(
                f"Argument offset: {offset} has wrong format. Must be an float"
            )

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
        self.SERVER.close()
        print("[COMMANDSERVER] Commandserver stopped")


if __name__ == "__main__":
    sock = CommandServer()
    Thread(target=sock.runServer).start()
    if USEROSSYSTEM == 1:
        print("Using ROS System")
        Thread(target=sock.runClientROS).start()
