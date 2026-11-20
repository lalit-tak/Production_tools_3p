#!/usr/bin/python
"""
The concentrator engine is the primary binary in gp_concentrator.core.
It has two primary tasks:
    * Collect data from nodes of the grid & store them in the store
    * Monitor office, and execute any new transactions
"""


from gp_node.utils import Address
from gp_node.network.network_api import NetworkAPI
import serial
import sys
import datetime
import argparse
import yaml
import logging
import time
import os.path
import datetime
import getpass

try:
	ser = serial.Serial('/dev/gp-gateway',19200,timeout=3)

except (serial.serialutil.SerialException, OSError):
        logging.error('Could not open gateway device, exiting')
        sys.exit()

network_api = NetworkAPI(ser, mode='irda')

try:
	data=network_api.handle_function_request("255.255.255.255","106_get_dcu_bundle")
	print ("1result-->",data)
except Exception as e:
	print str(e)
	pass
