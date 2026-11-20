import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime


START_ADDRESS = 0x0100
"""
This is purely for debugging purpose
Create ext_flash.bin binary file by reading external flash firmware image
"""
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
        args.device = "com16"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 0.6

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    data = bytearray()
    #data = network_api.my_flash_io_master.fetch(Address("0.0.0.255"), START_ADDRESS, 128)
    #print "Header :", data
    """
    TODO: get binary file length from header rather than manually updating...????
    """
    bin_file_length = 146240
    starttime = datetime.datetime.now()
    data = network_api.my_flash_io_master.fetch(Address("0.0.0.255"), START_ADDRESS, bin_file_length, to_print=True)
    print "Data Recieved"
    # print "Recieved Data is :", data
    with open("ext_flash.bin", 'wb') as fp:
        fp.write(data)
    print "File Created"
    EndTime = datetime.datetime.now()
    print "StartTime:",starttime
    print "EndTime:",EndTime

    print "Diff:",EndTime-starttime
if __name__ == "__main__":
    run()
