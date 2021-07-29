"""
Filename: conf.py
Version name: 1.0, 2021-07-26
Short description: Configruation File of FleetIAS

(C) 2003-2021 IAS, Universitaet Stuttgart
"""
import logging

# Conf for TCP-Communication
# IP_FLEETIAS = "129.69.102.129"
IP_FLEETIAS = "192.168.178.30"
IP_MES = "129.69.102.129"
TCP_BUFF_SIZE = 512

# Poll times (in seconds)
POLL_TIME_STATUSUPDATES = 1
POLL_TIME_TASKS = 3

# setup logging
log_formatter = logging.Formatter('[%(asctime)s ] %(name)s : %(message)s')
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
