"""
Filename: mesclient.py
Version name: 1.1, 2022-12-02
Short description: tcp server to receive and send messages to mes

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
import binascii
import numpy as np
import socket
import time
from PySide6.QtCore import QThread, Signal
from threading import Event

from .servicerequests import ServiceRequests
from conf import IP_FLEETIAS, TCP_BUFF_SIZE, IP_MES, appLogger


class MESClient(QThread):
    stoppedSignal = Signal()

    def __init__(self):
        super(MESClient, self).__init__()
        # setup addr
        self.HOST = IP_FLEETIAS
        self.IP_MES = IP_MES
        self.BUFFSIZE = TCP_BUFF_SIZE
        # setup socket for cyclic communication
        self.CYCLIC_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CYCLIC_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # setup socket for service requests
        self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVICE_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # params regarding robotinos
        self.statesRobotinos = []
        self.stopFlag = Event()
        self.serviceSocketIsAlive = False

    def run(self):
        """
        Runs/starts the MESClient
        """
        appLogger.info("MESClient started")
        self.CYCLIC_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CYCLIC_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVICE_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            # Set timeout for connection
            self.CYCLIC_SOCKET.settimeout(5.0)
            self.SERVICE_SOCKET.settimeout(5.0)
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            self.serviceSocketIsAlive = True
            # Reset tinmeout so socket is in blocking mode
            self.CYCLIC_SOCKET.settimeout(None)
            self.SERVICE_SOCKET.settimeout(None)
            # Start cyclic communication
            self.stopFlag.clear()
            self.cyclicCommunication()
        except Exception as e:
            appLogger.error("[MESCLIENT] " + str(e))
        self.stoppedSignal.emit()

    def getTransportTasks(self, noOfActiveAGV):
        """
        Get transport tasks from IAS-MES

        Args:
            noOfActiveAGV(int): number of active robotinos which can execute tasks

        Returns:
            transportTasks (int, int): set of transport tasks, each item is a tupel with: (startId, targetId)
        """
        # generate request
        requestGenerator = ServiceRequests()
        requestGenerator.getTransportTasks(noOfActiveAGV)
        request = requestGenerator.encodeMessage()
        try:
            # send request
            self.SERVICE_SOCKET.send(bytes.fromhex(request))
            msg = self.SERVICE_SOCKET.recv(self.BUFFSIZE)
            if msg:
                responseGenerator = ServiceRequests()
                responseGenerator.decodeMessage(binascii.hexlify(msg).decode())
                response = responseGenerator.readTransportTasks()
                return response
        except BrokenPipeError:
            self.serviceSocketIsAlive = False
        except Exception as e:
            appLogger.error("[MESCLIENT] " + str(e))

    def moveBuf(self, robotinoId, resourceId, isLoading):
        """
        Inform mes that robotino loads/unloads carrier

        Args:
            robotinoId (int): resourceId of the robotino which loads/unloads
            resourceId (int): resourceId of resource where it loads/unloads the carrier
            isLoading (bool): if robotino loads (True) or unLoads(False) the carrier
        """
        requestGenerator = ServiceRequests()
        requestGenerator.moveBuf(robotinoId, resourceId, isLoading)
        request = requestGenerator.encodeMessage()
        try:
            # send request
            self.SERVICE_SOCKET.send(bytes.fromhex(request))
            while True:
                # get response and fetch transport tasks
                msg = self.SERVICE_SOCKET.recv(self.BUFFSIZE)
                if msg:
                    return True
        except BrokenPipeError:
            self.serviceSocketIsAlive = False
        except Exception as e:
            appLogger.error("[MESCLIENT] " + str(e))

    def delBuf(self, robotinoId):
        """
        Delete buffer in mes

        Args:
            robotinoId (int): resourceId of robotino which buffer should be deleted
        """
        requestGenerator = ServiceRequests()
        requestGenerator.delBuf(robotinoId)
        request = requestGenerator.encodeMessage()
        try:
            # send request
            self.SERVICE_SOCKET.send(bytes.fromhex(request))
            while True:
                # get response and fetch transport tasks
                msg = self.SERVICE_SOCKET.recv(self.BUFFSIZE)
                if msg:
                    return True
        except BrokenPipeError:
            self.serviceSocketIsAlive = False
        except Exception as e:
            appLogger.error("[MESCLIENT] " + str(e))

    def setDockingPos(self, dockedAt, robotinoId):
        """
        Set docking position in mes

        Args:
            dockedAt (int): resourceId of resource where it is docked at (undocked: dockedAt=0)
            robotinoID (int): resourceId of robotino which has docked
        """
        requestGenerator = ServiceRequests()
        requestGenerator.setDockingPos(int(dockedAt), int(robotinoId))
        request = requestGenerator.encodeMessage()
        try:
            # send request
            self.SERVICE_SOCKET.send(bytes.fromhex(request))
            while True:
                # get response and fetch transport tasks
                msg = self.SERVICE_SOCKET.recv(self.BUFFSIZE)
                if msg:
                    return True
        except BrokenPipeError:
            self.serviceSocketIsAlive = False
            appLogger.error(f"Can't send message to IAS-MES: Connection is broken")
        except Exception as e:
            appLogger.error(str(e))

    def cyclicCommunication(self):
        """
        Thread for cyclically sending state of Robotinos to IAS-MES
        """
        lastUpdate = time.time()
        while not self.stopFlag.is_set():
            if time.time() - lastUpdate >= 1:
                # send task
                for i in range(len(self.statesRobotinos)):
                    msg = ""
                    # resourceId of robotino
                    msg += format(self.statesRobotinos[i].id, "04x")
                    # sps type of robotino (set to 2 for readability)
                    msg += format(2, "02x")
                    # statusbits
                    statusbits = np.array(
                        [
                            int(self.statesRobotinos[i].mesMode),
                            int(self.statesRobotinos[i].errorL2),
                            int(self.statesRobotinos[i].errorL1),
                            int(self.statesRobotinos[i].errorL0),
                            int(self.statesRobotinos[i].reset),
                            int(self.statesRobotinos[i].busy),
                            int(self.statesRobotinos[i].manualMode),
                            int(self.statesRobotinos[i].autoMode),
                        ]
                    )
                    msg += format(np.packbits(statusbits)[0], "02x")
                    request = bytes.fromhex(msg)
                    self.CYCLIC_SOCKET.send(request)
                lastUpdate = time.time()

    """
    Setter
    """

    def setStatesRobotinos(self, states):
        self.statesRobotinos = states

    def stopClient(self):
        self.stopFlag.set()
        try:
            self.SERVICE_SOCKET.shutdown(socket.SHUT_RDWR)
            self.CYCLIC_SOCKET.shutdown(socket.SHUT_RDWR)
        except:
            pass
        appLogger.info("Stopped MESClient")


if __name__ == "__main__":
    mesClient = MESClient()
    mesClient.start()
