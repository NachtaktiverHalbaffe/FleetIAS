"""
Filename: conf.py
Version name: 1.1, 2022-12-02
Short description: Configruation File of FleetIAS

(C) 2003-2022 IAS, Universitaet Stuttgart
"""
import logging

# Conf for TCP-Communication
IP_FLEETIAS = "129.69.102.129"
IP_MES = "129.69.102.129"
IP_ROS = "129.69.102.239"
TCP_BUFF_SIZE = 512

# Whether to use ROS system or not
USEROSSYSTEM = 1

# Poll times (in seconds)
POLL_TIME_STATUSUPDATES = 1
POLL_TIME_TASKS = 3

"""
Logger
"""
# ERROR LOGGING
log_formatter = logging.Formatter("[%(asctime)s ] %(message)s")
# handler for logging to file
file_handler = logging.FileHandler("errors.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
# handler for logging to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)
# setup logger itself
errLogger = logging.getLogger("errors")
errLogger.setLevel(logging.INFO)
# add logger handler to logger
errLogger.handlers = []
errLogger.addHandler(stream_handler)
errLogger.addHandler(file_handler)

# ERROR LOGGING
log_formatter = logging.Formatter("[%(asctime)s ] %(message)s")
# handler for logging to file
file_handler = logging.FileHandler("errors.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
# handler for logging to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)
# setup logger itself
errLogger = logging.getLogger("errors")
errLogger.setLevel(logging.INFO)
# add logger handler to logger
errLogger.handlers = []
errLogger.addHandler(stream_handler)
errLogger.addHandler(file_handler)

# ROS LOGGING
log_formatter_ros = logging.Formatter("[%(asctime)s ] [ROS] %(message)s")
# handler for logging to file
file_handler_ros = logging.FileHandler("ros_logs.log")
file_handler_ros.setFormatter(log_formatter)
file_handler_ros.setLevel(logging.INFO)
# handler for logging to console
stream_handler_ros = logging.StreamHandler()
stream_handler_ros.setFormatter(log_formatter)
stream_handler_ros.setLevel(logging.INFO)
# setup logger itself
rosLogger = logging.getLogger("ros")
rosLogger.setLevel(logging.INFO)
# add logger handler to logger
rosLogger.handlers = []
rosLogger.addHandler(stream_handler_ros)
rosLogger.addHandler(file_handler_ros)
