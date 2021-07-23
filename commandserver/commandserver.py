"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from robotinomanager.robotinomanager import RobotinoManager
import socket
from threading import Thread, Event


class CommandServer(object):

    def __init__(self):
        # setup addr
        self.PORT = 13000
        # self.HOST = "129.69.102.129"
        self.HOST = "192.168.178.30"
        self.ADDR = (self.HOST, self.PORT)
        # setup socket
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.FORMAT = 'utf-8'
        self.stopFlag = Event()
        # messages
        self.response = ""
        self.encodedMsg = ""
        # robotinomanager for delegating messages
        self.robotinoManager = None

    def __del__(self):
        self.SERVER.close()

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
    #   client: socket of the fleetias
    #   addr: ipv4 adress of fleetias
    def commandCommunication(self, client):
        while not self.stopFlag.is_set():
            if self.encodedMsg != "":
                data = bytes.fromhex(self.encodedMsg)
                client.send(data)
                self.encodedMsg = ""

                response = client.recv(512)
                if response:
                    response = response.decode('utf-8')
                    # fetch state message
                    if "RobotInfo" in response:
                        strId = response.split("robotinoid:")
                        id = int(strId[1][1])
                        robotino = self.robotinoManager.getRobotino(id)
                        robotino.fetchStateMsg(response)
                    # create/update fleet
                    elif "AllRobotinoID" in response:
                        Thread(target=self.robotinoManager.createFleet,
                               args=[response]).start()
                    # inform robotinomanager about commandinfo
                    elif "CommandInfo" in response:
                        Thread(target=self.robotinoManager.setCommandInfo,
                               args=[response]).start()

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
            str(resourceId) + " GoTo Position " + str(position)
        self.strToBin()

    # command to let the robotino dock to a resource
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    #   position: resourceId of resource where it should dock to
    def dock(self, position, resourceId=7):
        self.response = "PushCommand " + \
            str(resourceId) + " DockTo " + str(position)
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
        self.response = "GetRobotinoInfo " + str(resourceId)
        self.strToBin()

    # command to get the resourceIds of all active robotinos
    def getAllRobotinoID(self):
        self.response = "PushCommand GetAllRobotinoID"
        self.strToBin()

    # command to tell robotino that it has ended it transport task
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def ack(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " Thank You"
        self.strToBin()

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
