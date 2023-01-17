"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


import socket
import json
from threading import Thread, Event
import time
from PySide6.QtCore import QThread, Signal

from conf import IP_ROS, IP_FLEETIAS, TCP_BUFF_SIZE, appLogger, rosLogger
from robotinomanager.robotino import Robotino
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
        self.HOST = IP_FLEETIAS
        self.HOSTROS = IP_ROS
        self.ADDR = (self.HOST, self.PORT)
        self.ADDRROS = (self.HOSTROS, self.PORTROS)

        # setup socket
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.stopFlag = Event()

        # robotinomanager for delegating messages to be handled
        self.robotinoManager = None

    def run(self):
        """
        Starts the Commandserver in its own thread
        """
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
        Waits for a connection from a client (mainly evaluationmanager)
        """
        while not self.stopFlag.is_set():
            try:
                client, addr = self.SERVER.accept()
                appLogger.debug(f"{addr} connected to socket")
                Thread(target=self.commandCommunication, args=[client]).start()
            except Exception as e:
                appLogger.error(e)
                break

    def commandCommunication(self, client):
        """
        Receives commands from the client and delegates them either to a Robotino with the proprietary software
        or a prototype

        Args:
            client: Client which connected to the socket
        """
        while not self.stopFlag.is_set():
            try:
                request = client.recv(TCP_BUFF_SIZE)
                if request:
                    data = request.decode("utf-8")
                    data = json.loads(data)

                    response = ""
                    # ----------------------- Push Target -------------------------
                    if data["command"].lower() == "pushtarget":
                        #  Drive to a workstation
                        if data["type"].lower() == "resource":
                            # Prototype
                            if data["executioner"].lower() == "prototype":
                                response = self.goTo(
                                    position=data["workstationID"],
                                    resourceId=data["robotinoID"],
                                    type="resource",
                                )
                            # Proprietary software
                            elif data["executioner"].lower() == "proprietary":
                                if self.robotinoManager != None:
                                    self.robotinoManager.getRobotino(
                                        data["robotinoID"]
                                    ).driveTo(data["workstationID"])

                                if self._waitForCompletion(int(data["robotinoID"])):
                                    response = "Success"
                                else:
                                    response = "Error"
                            else:
                                appLogger.warning(
                                    f'Couldn\'t execute command PushTarget: Executioner "{data["executioner"]}" is invalid'
                                )
                        # Drive to coordinate
                        elif data["type"].lower() == "coordinate":
                            # Prototype
                            if data["executioner"].lower() == "prototype":
                                response = self.goTo(
                                    position=data["coordinate"],
                                    resourceId=data["robotinoID"],
                                    type="coordinate",
                                )
                            # Proprietary
                            elif data["executioner"].lower() == "proprietary":
                                self.robotinoManager.getRobotino(
                                    data["robotinoID"]
                                ).driveToCor(data["coordinate"])

                                if self._waitForCompletion(int(data["robotinoID"])):
                                    response = "Success"
                                else:
                                    response = "Error"
                            else:
                                appLogger.warning(
                                    f'Couldn\'t execute command PushTarget: Executioner "{data["executioner"]}" is invalid'
                                )
                        else:
                            rosLogger.warning(
                                f'Couldn\'t execute command PushTarget: Type "{data["type"]}" is invalid'
                            )
                    # -------------------- Activate Feature --------------------------
                    elif data["command"].lower() == "activatefeature":
                        response = self.activateFeature(
                            feature=data["feature"],
                            value=data["value"],
                            resourceId=data["robotinoID"],
                        )
                    # ------------------------- Add offset ----------------------------
                    elif data["command"].lower() == "addoffset":
                        response = self.addOffset(
                            name=data["feature"],
                            offset=data["offset"],
                            resourceId=data["robotinoID"],
                        )
                    #  ------------------- Set auto mode ----------------------------
                    elif data["command"].lower() == "setautomode":
                        if data["enabled"]:
                            self.robotinoManager.getRobotino(
                                data["robotinoID"]
                            ).activateAutoMode()
                        elif not data["enabled"]:
                            self.robotinoManager.getRobotino(
                                data["robotinoID"]
                            ).activateManualMode()
                        else:
                            appLogger.warning(
                                f'Couldn\'t set Automode of Robotino {data["robotinoID"]}: "Enabled" is not specified'
                            )
                    else:
                        errMsg = f'Couldn\'t process message "{data}": Command wrong formatted or not implemented'
                        appLogger.warning(errMsg)
                        response = errMsg
                    # Send response to client
                    client.sendall(bytes(response, encoding="utf-8"))
            except Exception as e:
                appLogger.warning(
                    f"Communication with socket {client} failed.\nError message: {e}"
                )

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
        ROS_RESP_REACHED_TARGET = "target reached"
        ROS_RESP_FEATURE = "feature set"
        ROS_RESP_OFFSET = "offset set"
        ROS_RESP_ERR = "error"

        # Connect to ROS
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.HOSTROS, self.PORTROS))
        # Send command to ROS
        clientSocket.sendall(bytes(json.dumps(request), encoding="utf-8"))
        while not self.stopFlag.is_set():
            # Wait for response
            data = clientSocket.recv(1024).decode("utf-8")
            #  Logging
            if ROS_RESP_REACHED_TARGET in data.lower():
                rosLogger.info(f"Command run successfully on ROS: PushTarget")
            elif ROS_RESP_FEATURE in data.lower():
                rosLogger.info(f"Command run successfully on ROS: ActivateFeature")
            elif ROS_RESP_OFFSET in data.lower():
                rosLogger.info(f"Command run successfully on ROS: AddOffset")
            elif ROS_RESP_ERR in data.lower():
                rosLogger.error(msg="[ROS] " + data.split(":")[1])
            else:
                rosLogger.error(f"[ROS] Unkown response: {data}")
            clientSocket.close()
            return data

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
        if type.lower() == "resource":
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
        elif type.lower() == "coordinate":
            if (position[0] >= 0 and position[0] <= 200) and (
                position[1] >= 0 and position[1] <= 200
            ):
                rosLogger.info(
                    f"Send Command to ROS: PushTarget with coordinate {position}"
                )
                request = {
                    "command": "PushTarget",
                    "robotinoID": resourceId,
                    "type": type,
                    "coordinate": position,
                }
            else:
                appLogger.error(
                    f"Argument position {position} has wrong format. Must be a tuple (x,y), where both x and y are int betwenn 0 and 200"
                )
                return
        else:
            appLogger.error(
                f'{type} is a invalid target type. Must be either "resource" or "coordinate"'
            )
            return
        return self.runClientROS(request)

    def activateFeature(self, feature, value=True, resourceId=7):
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

    def addOffset(self, name, offset, resourceId=7):
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
            self.runClientROS(request)
        else:
            appLogger.error(
                f"Argument offset: {offset} has wrong format. Must be an float"
            )

    def _waitForCompletion(self, robotinoId: int):
        """
        Waits until the state from a Robotino changes from busy to idle

        Args:
            robotinoId (int): ResourceID of the Robotino

        Returns:
            True if Robotino completed or False if Robotino is already idle
        """
        robotino = self.robotinoManager.getRobotino(robotinoId)

        if robotino.busy == True:
            return False

        while True:
            if robotino.busy == False:
                return True
            time.sleep(1)

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
