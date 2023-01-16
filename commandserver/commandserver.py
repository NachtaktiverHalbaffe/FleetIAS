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


class CommandServer(QThread):
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
        super(CommandServer, self).__init__()
        # setup addr
        self.PORT = 13004
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
        appLogger.info("Commandserver started")
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
                rosLogger.error(msg="[ROS] " + data.split(":")[1])
            else:
                rosLogger.error(f"[ROS] Unkown response: {data}")
            clientSocket.close()
            break

    def goTo(self, position, resourceId=7, type="resource"):
        """
        Sends a command to ROS where the Robotino should drive to an resource

        Args:
            position (either int or (int, int)): Either resourceID of the target resource or coordinate. See argument type
            type (str, optional): Type of position. Can be either "resource" (position: resourceID) or "coordinate" (position (x,y)-tuple). Defaults to "resource"
            resourceID (int, optional): ResourceID of the robotino which should execute this command. Defaults to 7

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
                appLogger.error(
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
                appLogger.error(
                    "Argument position {position} has wrong format. Must be a tuple (x,y), where both x and y are int betwenn 0 and 200"
                )
                return
        else:
            appLogger.error(
                f'{type} is a invalid target type. Must be either "resource" or "coordinate"'
            )
            return
        Thread(target=self.runClientROS, args=[request]).start()

    def ActivateFeature(self, feature, value=True, resourceId=7):
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
                "command": "ActivateFeature",
                "robotinoID": resourceId,
                "feature": feature,
                "value": value,
            }
            Thread(target=self.runClientROS, args=[request]).start()
        else:
            appLogger.error("Wrong argument value: {value}. Must be an bool")

    def AddOffset(self, name, offset, resourceId=7):
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
            # TODO Make offset to a tuple
            request = {
                "command": "AddOffset",
                "robotinoID": resourceId,
                "feature": name,
                "offset": offset,
            }
            Thread(target=self.runClientROS, args=[request]).start()
        else:
            appLogger.error(
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
        try:
            self.SERVER.shutdown(socket.SHUT_RDWR)
        except:
            pass
        appLogger.info("Commandserver stopped")


if __name__ == "__main__":
    sock = CommandServer()
    sock.start()
    Thread(target=sock.runClientROS).start()
