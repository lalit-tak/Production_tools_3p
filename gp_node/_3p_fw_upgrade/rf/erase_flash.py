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
from device_address import AddressList_3P





def erase_flash(filepath, flash_io):
    for i in AddressList_3P:
        addr = str(AddressList_3P[i])
        retry_cnt = 3
        while(retry_cnt):
            retry_cnt = retry_cnt - 1
            try:
                flash_io.erase(Address(addr), 0)
            except Exception as e:
                print e
                print addr, "block-0 error, while erasing, count: ", retry_cnt
            else:
                retry_cnt = 0
                print addr, "block-0 erased"
        retry_cnt = 3
        while(retry_cnt):
            retry_cnt = retry_cnt - 1
            try:
                flash_io.erase(Address(addr), 1)
            except Exception as e:
                print e
                print addr, "block-1 error, while erasing, count: ", retry_cnt
            else:
                retry_cnt = 0
                print addr, "block-1 erased"
        retry_cnt = 3        
        while(retry_cnt):
            retry_cnt = retry_cnt - 1
            try:
                flash_io.erase(Address(addr), int(32),sector_erase = True)
            except Exception as e:
                print e
                print addr, "sector-0 error, while erasing, count: ", retry_cnt
            else:
                retry_cnt = 0
                print addr, "sector-32 erased"


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")
    parser.add_argument('-p', action="store", dest="hex_file", 
                        help="programs new hex file")
    parser.add_argument('-V', action="store", dest="version", 
                        help="options are 'live' and 'ext'")
    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")
    args = parser.parse_args()
    if args.device is None:
        args.device = "/dev/gp-gateway"
    if args.baud_rate is None:
        args.baud_rate = 19200
    if args.timeout is None:
        args.timeout = 2

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, "irda")
    starttime = datetime.datetime.now()
  

    erase_flash(args.hex_file, network_api.my_flash_io_master_3p)
    EndTime = datetime.datetime.now()
    print "StartTime:",starttime
    print "EndTime:",EndTime


if __name__ == "__main__":
    run()
