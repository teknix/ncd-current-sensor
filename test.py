import os
import logging
# import asyncio
import sys, time, re, datetime, json, socket, errno
from pymongo import MongoClient
import Industrial_Relay_Control.ncd_industrial_relay as ncd
from mqttwrapper.hbmqtt_backend import run_script
# import ncd_industrial_relay as ncd
from decimal import *
getcontext().prec = 2

# Setup logging
# create logger with 'spam_application'
logger = logging.getLogger('AmpMeter_Rewrite')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('ampmeter.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# Set NCD AMP Meter IP address
NCD_IP = '192.168.1.102'
# Set Listening Port on Remote Fusuion Controller
NCD_PORT = 2101
# Set Buffer Size



# MQTT Server IP or HOSTNAME
mqtt_server = '192.168.1.10'
# MQTT Port Number, usally 1883
mqtt_port = 1883
broker = "mqtt://" + str(mqtt_server) + ":" + str(mqtt_port)
topics =["amps", "control"]

# Mongo Server
MONGO_IP = '192.168.1.9'
MONGO_PORT = 27017

# Setup Dict for motor High and Low Amps
# Could be set for MongoDB later
# ampMaxMin = motors_config.ampMaxMin

# Setup NCD Fusion Board Socket
logger.info('Setting up Socket')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = sock
# set up your socket with the desired settings.

# instantiate the board object and pass it the network socket
board = ncd.Relay_Controller(sock)
logger.info('Passed socket to NCD')
# connect the socket using desired IP and Port
logger.info('Connecting to AmpMeter')
sock.connect((NCD_IP, NCD_PORT))
sock.settimeout(5)
# print board1.test_comms()
while True:
    # pass these methods a number between 1 and 512
    # to set the current status of the relay
    logger.info('Sending command to NCD')
    # print(board.lantronix_read_amps())
    logger.info('AmpMeter returned' + str(board.lantronix_read_amps()))
    time.sleep(3.5)

sock.close()
