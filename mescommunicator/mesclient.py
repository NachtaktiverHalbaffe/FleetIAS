"""
Filename: mesclient.py
Version name: 1.0, 2021-07-21
Short description: tcp server to receive and send messages to mes

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
import binascii
import numpy as np
import socket
import time
from threading import Thread
from .servicerequests import ServiceRequests


class MESClient(object):

    def __init__(self):
        # setup addr
        self.HOST = "129.69.102.129"
        self.IP_MES = "129.69.102.129"
        self.BUFFSIZE = 512
        # setup socket for cyclic communication
        self.CYCLIC_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CYCLIC_SOCKET.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # setup socket for service requests
        self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVICE_SOCKET.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # params regarding robotinos
        self.statesRobotinos = []

    def __del__(self):
        # Close server if all connections crashed
        self.CYCLIC_SOCKET.close()
        self.SERVICE_SOCKET.close()

    # run/start the mesClient
    def run(self):
        print("[MESCLIENT] MESClient started")
        self.CYCLIC_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CYCLIC_SOCKET.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVICE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVICE_SOCKET.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            self.SERVICE_SOCKET.connect((self.IP_MES, 2000))
            cyclicCommunicationThread = Thread(target=self.cyclicCommunication)
            cyclicCommunicationThread.start()
        except Exception as e:
            print(e)

    # get transport tasks from mes
    # @param:
    #   noOfActiveAGV: number of active robotinos which can execute tasks
    # @return:
    #   transportTasks: set of transport tasks, each item is a tupel with: (startId, targetId)
    def getTransportTasks(self, noOfActiveAGV):
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
                    responseGenerator.decodeMessage(
                        binascii.hexlify(msg).decode())
                    response = responseGenerator.readTransportTasks()
                    return response

        except Exception as e:
            self.SERVICE_SOCKET = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            print(e)

    # inform mes that robotino loads/unloads carrier
    # @param:
    #   robotinoId: resourceId of the robotino which loads/unloads
    #   resourceId: resourceId of resource where it loads/unloads the carrier
    #   isLoading: if robotino loads (True) or unLoads(False) the carrier
    def moveBuf(self, robotinoId, resourceId, isLoading):
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
            self.SERVICE_SOCKET = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            print(e)

    # delete buffer in mes
    # @params:
    #   isBuffOut: if it is the Buffer Out (True) or Buffer In (False)
    #   robotinoId: resourceId of robotino which buffer should be deleted
    def delBuf(self, isBuffOut, robotinoId):
        requestGenerator = ServiceRequests()
        requestGenerator.delBuf(isBuffOut, robotinoId)
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
            self.SERVICE_SOCKET = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            print(e)

    # set docking position in mes
    # @params:
    #   dockedAt: resourceId of resource where it is docked at (undocked: dockedAt=0)
    #   robotinoID: resourceId of robotino which has docked
    def setDockingPos(self, dockedAt, robotinoId):
        requestGenerator = ServiceRequests()
        requestGenerator.setDockingPos(dockedAt, robotinoId)
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
            self.SERVICE_SOCKET = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.CYCLIC_SOCKET.connect((self.IP_MES, 2001))
            print(e)

    # Thread for cyclically sending state of robotinos to mes
    def cyclicCommunication(self):
        lastUpdate = time.time()
        while True:
            if lastUpdate - time.time() >= 1:
                # send task
                for i in range(len(self.statesRobotinos)):
                    msg = ""
                    # resourceId of robotino
                    msg += format(self.statesRobotinos[i].id, "04x")
                    # sps type of robotino (set to 2 for readability)
                    msg += format(2, "04x")
                    # statusbits
                    statusbits = [
                        self.statesRobotinos[i].mesMode,
                        self.statesRobotinos[i].errorL2,
                        self.statesRobotinos[i].errorL1,
                        self.statesRobotinos[i].errorL0,
                        self.statesRobotinos[i].reset,
                        self.statesRobotinos[i].busy,
                        self.statesRobotinos[i].manualMode,
                        self.statesRobotinos[i].autoMode
                    ]
                    msg += format(statusbits.packbits, "02x")
                    self.CYCLIC_SOCKET.send(bytes.fromhex(msg))
                lastUpdate = time.time()

    """
    Setter
    """

    def setStatesRobotinos(self, states):
        self.setStatesRobotinos = states

    def stopClient(self):
        self.SERVICE_SOCKET.close()
        self.CYCLIC_SOCKET.close()
        print("[MESCLIENT] Stopped client")
