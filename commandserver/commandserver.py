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
from conf import IP_FLEETIAS, TCP_BUFF_SIZE


class CommandServer(object):

    def __init__(self):
        # setup addr
        self.PORT = 13000
        self.HOST = IP_FLEETIAS
        self.ADDR = (self.HOST, self.PORT)
        # setup socket
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.FORMAT = 'utf-8'
        self.buffSize = TCP_BUFF_SIZE
        self.stopFlag = Event()
        # messages
        self.response = ""
        self.encodedMsg = ""
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

    # Waits for a connection from a plc. When a plc connects,
    # it starts a new thread for the service specific communication
    def waitForConnection(self):
        while not self.stopFlag.is_set():
            try:
                client, addr = self.SERVER.accept()
                print("[COMMANDSERVER]: " + str(addr) + "connected to socket")
                self.getAllRobotinoID()
                Thread(target=self.commandCommunication,
                       args=[client]).start()
            except Exception as e:
                print(e)
                break

    # Thread for the command communication.
    # @params:
    #   client: socket of the robotino
    def commandCommunication(self, client):
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
                            errMsg = "Error while loading carrier: Station didn't respond"
                            print("[COMMANDSERVER] " + errMsg)
                        elif "UnloadBox" in response:
                            errMsg = "Error while unloading Carrier: Station didn't respond"
                            print("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                                self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to undock but isnt docked
                    elif "ROBOT_NOT_DOCKED" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while undocking from resource: Robotino isn't docked"
                        print("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                                self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to dock but didnt find markers to dock
                    elif "NO_DOCK_STATION" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while docking to resource: Robotino couldn't find markers to dock"
                        print("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                                self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to drive to resource but path is blocked
                    elif "PATH_BLOCKED" in response:
                        state, id = self._parseCommandInfo(response)
                        errMsg = "Error while driving to resource: Path is blocked"
                        print("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                            self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to load carrier, but a carrier is already present on robotino
                    elif "BOX_PRESENT" in response and "LoadBox" in response:
                        state, id = self._parseCommandInfo(response)
                        if "LoadBox" in response:
                            errMsg = "Error while loading carrier: A carrier is already present on carrier"
                            print("[COMMANDSERVER] " + errMsg)
                        elif "UnloadBox" in response:
                            errMsg = "Error while unloading carrier: After finishing operation the box is still present"
                            print("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                                self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)
                    # robotino tries to load carrier, but didnt get a carrier from station
                    elif "NO_BOX" in response:
                        state, id = self._parseCommandInfo(response)
                        if "UnloadBox" in response:
                            errMsg = "Error while unloading carrier: Robotino hasn't a box present"
                            print("[COMMANDSERVER] " + errMsg)
                        elif "LoadBox" in response:
                            errMsg = "Error while loading carrier: Carrier was not sucessfully loaded"
                            print("[COMMANDSERVER] " + errMsg)
                        if self.robotinoManager != None:
                                self.robotinoManager.handleError(errMsg, id)
                        self.endTask(id)

                    # info messages and responses from commands
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
                            Thread(target=self.robotinoManager.createFleet,
                                   args=[response]).start()
                    # inform robotinomanager about commandinfo
                    elif "CommandInfo" in response:
                        if self.robotinoManager != None:
                            Thread(target=self.robotinoManager.setCommandInfo,
                                   args=[response]).start()
                    # print out response which isnt handled when received
                    else:
                        print(
                            "[COMMANDSERVER] Catched unhandled response from robotino: " + str(response))

    # converts the string to binary which the server can send
    def strToBin(self):
        self.encodedMsg = ""
        for i in range(len(self.response)):
            # convert character to hex value
            self.encodedMsg += str(format(ord(self.response[i]), "x"))
        # line of end ascii
        self.encodedMsg += "0a"

    # command to let the robotino load the carrier
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def loadBox(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " LoadBox 0"
        self.strToBin()

    # command to let the robotino unload the carrier
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def unloadBox(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " UnloadBox 0"
        self.strToBin()

    # command to let the robotino drive to an resource
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    #   position: resourceId of resource where it should drive to
    def goTo(self, position,  resourceId=7):
        self.response = "PushCommand " + \
            str(resourceId) + " GoToPosition " + str(position)
        self.strToBin()

    # command to let the robotino dock to a resource
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    #   position: resourceId of resource where it should dock to
    def dock(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " DockTo 1"
        self.strToBin()

    # command to let the robotino undock from an resource
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def undock(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " Undock"
        self.strToBin()

    # command to get the state from an robotino
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def getRobotinoInfo(self, resourceId=7):
        self.response = "GetRobotInfo " + str(resourceId)
        self.strToBin()

    # command to get the resourceIds of all active robotinos
    def getAllRobotinoID(self):
        # self.response = "PushCommand GetAllRobotinoID"
        self.response = "GetAllRobotinoID"
        self.strToBin()

    # command to get the resourceIds of all active robotinos
    #   resourceId: resourceId of robotino which should execute the task
    def endTask(self, resourceId=7):
        # self.response = "PushCommand GetAllRobotinoID"
        self.response = "EndTask " + str(resourceId)
        self.strToBin()

    # command to tell robotino that it has ended it transport task
    # @param:
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def ack(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " Thank You"
        self.strToBin()

    # splits the commandinfo into an id and state
    # @param:
    #   msg: message from which the state and id is extracted
    # @return:
    #   state: string with the state message of the command info
    #   id: resourceId of robotino from which the command info comes
    def _parseCommandInfo(self, msg):
        id = msg.split("robotinoid:")
        print(id)
        if id[0] != "":
            id = int(id[1][0])
            state = msg.split("\"")
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
        self.SERVER.close()
        print("[COMMANDSERVER] Commandserver stopped")


if __name__ == "__main__":
    sock = CommandServer()
    Thread(target=sock.runServer).start()
