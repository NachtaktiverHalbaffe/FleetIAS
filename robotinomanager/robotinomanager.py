"""
Filename: robotinomanager.py
Version name: 1.0, 2021-07-22
Short description: class to manage all robotinos (delegate tasks, delegtae statemessages to specific robotino)

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from .robotino import Robotino
from threading import Thread, Event
import time


class RobotinoManager(object):

    def __init__(self, mesClient, commandServer):
        # fleet
        self.fleet = []
        # params for automated control
        self.transportTasks = []
        self.commandInfo = ""
        self.stopFlagCyclicUpdates = Event()
        self.stopFlagAutoOperation = Event()
        self.POLL_TIME = 2
        self.POLL_TIME_TASKS = 3
        # instances of mesclient and commandserver for executing operations
        self.mesClient = mesClient
        self.commandServer = commandServer

    # creates the fleet with robotinos inside
    # @params:
    #   msg: message from the commandserver
    def createFleet(self, msg):
        self.stopCyclicStateUpdate()
        self.fleet = []
        strIds = msg.split("AllRobotinoID")
        strIds = strIds[1].split(",")
        for id in strIds:
            robotino = Robotino(mesClient=self.mesClient,
                                commandServer=self.commandServer)
            robotino.id = id
            self.fleet.append(robotino)
        Thread(target=self.startCyclicStateUpdate).start()

    # cyclically update state of robotinos, runs as thread
    def cyclicStateUpdate(self):
        lastUpdate = time.time()
        while not self.stopFlagCyclicUpdates.is_set():
            if lastUpdate - time.time > self.POLL_TIME:
                for robotino in self.fleet:
                    self.commandServer.getRobotinoInfo(robotino.id)
                lastUpdate = time.time()
                self.mesClient.setStatesRobotinos(self.fleet)
        # reset stopflag after the cyclicStateUpdate got killed
        self.stopFlagCyclicUpdates.clear()

    # operates the robotino in automated operation where it gets the transport tasks from the
    # mes and executes them
    def automatedOperation(self):
        lastUpdate = time.time()
        while not self.stopFlagAutoOperation:
            # poll transport task from mes
            if lastUpdate - time.time > self.POLL_TIME_TASKS:
                self.transportTasks = self.mesClient.getTransportTasks(
                    len(self.fleet))
                self.transportTasks = list(self.transportTasks)
                # assign Tasks
                for task in self.transportTasks:
                    # check if task is already assigned
                    isAlreadyAssigned = False
                    for robotino in self.fleet:
                        if robotino.task == task:
                            isAlreadyAssigned = True
                            break
                    # assign task if it isnt already assigned
                    if not isAlreadyAssigned:
                        for robotino in self.fleet:
                            if robotino.task == (0, 0):
                                robotino.task = task
                                Thread(target=self.executeTransportTask,
                                       args=[robotino]).start()
                                break
        # reset stopflag after the automatedOperation got killed
        self.stopFlagAutoOperation.clear()

    # execute an transport task which got assigend from the mes
    # @param:
    #   robotino: instance of robotino which executes the task
    def executeTransportTask(self, robotino):
        """
        Load carrier at start
        """
        # drive to start
        if robotino.dockedAt != robotino.task[0]:
            robotino.driveTo(robotino.task[0])
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-GotoPosition":
                break
        # dock to resource
        if robotino.dockedAt != robotino.task[0]:
            robotino.dock(robotino.task[0])
        id, state = self._parseCommandInfo()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-DockTo":
                break
        # load box
        robotino.loadCarrier()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-LoadBox":
                break
        # undock
        robotino.undock()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-Undock":
                break

        """
        Unload carrier at target
        """

        # drive to target
        robotino.driveTo(robotino.task[1])
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-GotoPosition":
                break
        # dock to resource
        robotino.dock(robotino.task[1])
        id, state = self._parseCommandInfo()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-DockTo":
                break
        # load box
        robotino.unloadCarrier()
        while True:
            id, state = self._parseCommandInfo()
            if id == robotino.id and state == "Finished-UnloadBox":
                break

        """
        Finishing task
        """
        # inform robotino
        self.commandServer.ack(robotino.id)
        # remove task from transporttasks
        tasks = set(self.transportTasks)
        tasks.remove(robotino.task)
        self.transportTasks = list(tasks)
        # remove task from robotino
        robotino.task = (0, 0)

    # splits the commandinfo into an id and state
    # @return:
    #   state: string with the state message of the command info
    #   id: resourceId of robotino from which the command info comes
    def _parseCommandInfo(self):
        id = self.commandInfo.split("robotinoid:")
        id = int(id[1][0])
        state = self.commandInfo.split("\"")
        state = state[1]

        return id, state

    """
    Setter and getter
    """

    def setCommandInfo(self, msg):
        self.commandInfo = msg

    def getRobotino(self, id):
        for robotino in self.fleet:
            if robotino.id == id:
                return robotino

    def startAutomatedOperation(self):
        Thread(target=self.automatedOperation).start()

    def stopAutomatedOperation(self):
        self.stopFlagAutoOperation.set()

    def startCyclicStateUpdate(self):
        Thread(target=self.cyclicStateUpdate).start()

    def stopCyclicStateUpdate(self):
        self.stopFlagCyclicUpdates.set()
