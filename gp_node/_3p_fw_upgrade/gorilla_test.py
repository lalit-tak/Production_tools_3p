import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import time
import logging

START_ADDRESS = 0x100

file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler('kunjappu.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(self.formatter)
# add the handlers to the logger
file_logger.addHandler(self.handler)

def my_print(data):
    print data
    self.file_logger.info(data) 

def erase_flash(flash_io):
    packet_retry_cnt = 0
    for i in range(0,32):
        retry = True
        while retry:
            try:
                flash_io.erase(Address("0.0.0.255"), i)
            except FlashIOError_3P as err:
                #print err
                packet_retry_cnt = packet_retry_cnt+1
                retry = True
            else:
                print i*64*1024 ,"Bytes Erased"
                retry = False
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')
    print i*64, "KB Erased" 
    

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")

    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")
    args = parser.parse_args()
    if args.device is None:
        args.device = "/dev/gp-gateway"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 1

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    starttime = datetime.datetime.now()

    print "DLMS to TAP"
    print network_api.three_ph_meter_dlms_to_tap(Address("0.0.0.255"))
    for i in range(0,200):
        print i, network_api.three_ph_set_survey_interval(Address("0.0.0.255"),30)
        time.sleep(.3)
        print i, network_api.three_ph_get_num_event_record(Address("0.0.0.255"))

    EndTime = datetime.datetime.now()
    print "StartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime


if __name__ == "__main__":
    run()

"""
Objective

1.Erase complete flash
2.Factory init
3.
"""