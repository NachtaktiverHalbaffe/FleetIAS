"""
Filename: commandserver.py
Version name: 1.0, 2021-07-02
Short description: tcp server to receive and send commands to robotino

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

import socket
from threading import Thread

class CommandServer(object):

    def __init__(self):
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

    def runServer(self):
        self.SERVER.listen()
        print("[CONNECTION] Commandserver started")
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
                Thread(target=self.serviceCommunication,
                       args=(client, addr)).start()
            except Exception as e:
                print(e)
                break


    # Thread for the service communication.
    # @params:
    # client: socket of the plc
    # addr: ipv4 adress of the plc
    def serviceCommunication(self, client, addr):
        while True:
            if self.encodedMsg != "":
                data = bytes.fromhex(self.encodedMsg)
                client.send(data)
                self.encodedMsg = ""
            try:
                while True:
                    response = client.recv(2048).decode(self.FORMAT)
                    if response:
                        print(response)
                        break
            except Exception as e:
                print(e)


    
    def strToBin(self):
        self.encodedMsg = ""
        for i in range(len(self.response)):
            # convert character to hex value
            self.encodedMsg += str(format(ord(self.response[i]), "x"))
        # line of end ascii
        self.encodedMsg += "0a"
    
    def loadBox(self, resourceId = 7):
        self.response = "PushCommand " +  str(resourceId) + " LoadBox 0"
        self.strToBin()


    def unloadBox(self, resourceId = 7):
        self.response = "PushCommand " +  str(resourceId) + " UnloadBox 0"
        self.strToBin()
   
    
    def goTo(self, position,  resourceId = 7):
        self.response = "PushCommand " +  str(resourceId) + " GoTo Position " + str(position)
        self.strToBin()
  
    
    def dock(self, position, resourceId = 7):
        self.response = "PushCommand " +  str(resourceId) + " DockTo " + str(position)
        self.strToBin()


    def undock(self, resourceId = 7):
        self.response = "PushCommand " +  str(resourceId) + " Undock"
        self.strToBin()
      
    
    def ack(self, resourceId = 7):
        self.response = "PushCommand " +  str(resourceId)+ " Thank You" 
        self.strToBin()



if __name__ =="__main__":
    sock = CommandServer()
    Thread(target=sock.runServer).start()

