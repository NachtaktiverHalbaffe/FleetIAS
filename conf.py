"""
Filename: conf.py
Version name: 1.1, 2022-12-02
Short description: Configruation File of FleetIAS

(C) 2003-2022 IAS, Universitaet Stuttgart
"""
import logging
from enum import Enum

# Conf for TCP-Communication
IP_FLEETIAS = "129.69.102.129"
IP_MES = "129.69.102.129"
IP_ROS = "129.69.102.180"
TCP_BUFF_SIZE = 512

# Poll times (in seconds)
POLL_TIME_STATUSUPDATES = 1
POLL_TIME_TASKS = 3

"""
Logger
"""

# APP LOGGING
log_formatter_app = logging.Formatter("[%(asctime)s][%(module)s] %(levelname)s: %(message)s")
# handler for logging to file
file_handler_app = logging.FileHandler("logs/fleetias.log")
file_handler_app.setFormatter(log_formatter_app)
file_handler_app.setLevel(logging.INFO)
# handler for logging to console
stream_handler_app = logging.StreamHandler()
stream_handler_app.setFormatter(log_formatter_app)
stream_handler_app.setLevel(logging.INFO)
# setup logger itself
appLogger = logging.getLogger(__name__)
appLogger.setLevel(logging.DEBUG)
# add logger handler to logger
appLogger.handlers = []
appLogger.addHandler(stream_handler_app)
appLogger.addHandler(file_handler_app)

# ROS LOGGING
log_formatter_ros = logging.Formatter("[%(asctime)s ] [ROS] %(message)s")
# handler for logging to file
file_handler_ros = logging.FileHandler("logs/ros_logs.log")
file_handler_ros.setFormatter(log_formatter_ros)
file_handler_ros.setLevel(logging.INFO)
# handler for logging to console
stream_handler_ros = logging.StreamHandler()
stream_handler_ros.setFormatter(log_formatter_ros)
stream_handler_ros.setLevel(logging.INFO)
# setup logger itself
rosLogger = logging.getLogger("ros")
rosLogger.setLevel(logging.INFO)
# add logger handler to logger
rosLogger.handlers = []
rosLogger.addHandler(stream_handler_ros)
rosLogger.addHandler(file_handler_ros)


class Metrics(Enum):
    COLLISIONS = "collisions"
    PRODUCTION_STOPS = "prodStop"
    RISK = "risk"
    STARTED_TASKS = "startedTasks"
    SUCCESSFUL_TASKS = "successfulTasks"
    COLLISION_PROBABILITY = "collisionProbability"


class LoggingLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    EVAL = "EVAL"
