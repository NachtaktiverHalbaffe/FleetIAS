"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

import socket
from threading import Thread


class CommandServer(object):

    def __init__(self, robotinoManager):
        # setup addr
        self.PORT = 13000
        self.HOST = "129.69.102.129"
        self.ADDR = (self.HOST, self.PORT)
        # setup socket
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVER.bind(self.ADDR)
        self.FORMAT = 'utf-8'
        # messages
        self.response = ""
        self.encodedMsg = ""
        # robotinomanager for delegating messages
        self.robotinoManager = robotinoManager

    def runServer(self):
        self.SERVER.listen()
        print("[COMMANDSERVER] Commandserver started")
        # Start Tcp server on seperate Thread
        SERVER_THREADING = Thread(target=self.waitForConnection)
        try:
            SERVER_THREADING.start()
            SERVER_THREADING.join()
        except Exception as e:
            print(e)
        # Close server if all connections crashed
        self.SERVER.close()

    # Waits for a connection from a plc. When a plc connects,
    # it starts a new thread for the service specific communication
    def waitForConnection(self):
        while True:
            try:
                client, addr = self.SERVER.accept()
                print("[COMMANDSERVER]: " + str(addr) + "connected to socket")
                Thread(target=self.commandCommunication,
                       args=(client)).start()
            except Exception as e:
                print(e)
                break

    # Thread for the command communication.
    # @params:
    #   client: socket of the fleetias
    #   addr: ipv4 adress of fleetias
    def commandCommunication(self, client):
        while True:
            if self.encodedMsg != "":
                data = bytes.fromhex(self.encodedMsg)
                client.send(data)
                self.encodedMsg = ""
            try:
                response = client.recv(2048).decode(self.FORMAT)
                if response:
                    print(response)
                    # fetch state message
                    if "RobotInfo" in response:
                        strId = response.split("robotinoid:")
                        id = int(strId[1][1])
                        robotino = self.robotinoManager.getRobotino(id)
                        robotino.fetchStateMsg(response)
                    # create/update fleet
                    elif "AllRobotinoID" in response:
                        self.robotinoManager.createFleet(response)
                    # inform robotinomanager about commandinfo
                    elif "CommandInfo" in response:
                        self.robotinoManager.setCommandInfo(response)
            except Exception as e:
                print(e)

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
        self.respsone = "PushCommand GetAllRobotinoID"
        self.strToBin()

    # command to tell robotino that it has ended it transport task
    # @param:
    #   resourceId: resourceId of robotino which should execute the task
    def ack(self, resourceId=7):
        self.response = "PushCommand " + str(resourceId) + " Thank You"
        self.strToBin()


if __name__ == "__main__":
    sock = CommandServer()
    Thread(target=sock.runServer).start()
