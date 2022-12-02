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
from threading import Thread
from .servicerequests import ServiceRequests
from conf import IP_FLEETIAS, TCP_BUFF_SIZE, IP_MES, errLogger


class MESClient(object):
    def __init__(self):
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

    def __del__(self):
        # Close server if all connections crashed
        self.CYCLIC_SOCKET.close()
        self.SERVICE_SOCKET.close()

    def run(self):
        """
        Runs/starts the MESClient
        """
        print("[MESCLIENT] MESClient started")
        self.CYCLIC_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CYCLIC_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVICE_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            cyclicCommunicationThread = Thread(target=self.cyclicCommunication)
            cyclicCommunicationThread.start()
        except Exception as e:
            errLogger.error("[MESCLIENT] " + str(e))

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
            while True:
                # get response and fetch transport tasks
                msg = self.SERVICE_SOCKET.recv(self.BUFFSIZE)
                if msg:
                    responseGenerator = ServiceRequests()
                    responseGenerator.decodeMessage(binascii.hexlify(msg).decode())
                    response = responseGenerator.readTransportTasks()
                    return response

        except Exception as e:
            self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            errLogger.error("[MESCLIENT] " + str(e))

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
        except Exception as e:
            self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            errLogger.error("[MESCLIENT] " + str(e))

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
        except Exception as e:
            self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            errLogger.error("[MESCLIENT] " + str(e))

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
        except Exception as e:
            self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            errLogger.error("[MESCLIENT] " + str(e))

    def cyclicCommunication(self):
        """
        Thread for cyclically sending state of Robotinos to IAS-MES
        """
        lastUpdate = time.time()
        while True:
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
        self.SERVICE_SOCKET.close()
        self.CYCLIC_SOCKET.close()
        print("[MESCLIENT] Stopped client")


if __name__ == "__main__":
    mesClient = MESClient()
    Thread(target=mesClient.run).start()
