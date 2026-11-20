import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io_new import FlashIOMasterNew, FlashIOErrorNew
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import time


START_ADDRESS = 0x0100
METER_ADDRESS = "255.255.255.255"

def program(filepath, flash_io):
    flash_io.erase(Address(METER_ADDRESS), 0)
    # flash_io.erase(Address(METER_ADDRESS), 1)
    # flash_io.erase(Address(METER_ADDRESS), 2)
    # flash_io.erase(Address(METER_ADDRESS), 3)
    # Here we have to do erase sector command
    binary_file = open(filepath, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    flash_io.burn(Address(METER_ADDRESS), START_ADDRESS, hexfile_payload, to_print=True)

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
    parser.add_argument('-t', action="store", dest="timeout",type=int, 
                        help="port time out")
    parser.add_argument("--id", "--portID", dest="portID",
                      help="device id")

    args = parser.parse_args()
    if args.device is None:
        args.device = "/dev/gp-gateway"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 3
    if args.portID is None:
        args.portID = 4

    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)

    network_api = NetworkAPI(ser, args.portID, "irda")
    starttime = datetime.datetime.now()
    print network_api.get_live_version(Address(METER_ADDRESS))
    if args.hex_file is not None:
        print "Erasing..."
        program(args.hex_file, network_api.my_flash_io_master_new)
        print network_api.get_ext_version(Address(METER_ADDRESS))
        
    EndTime = datetime.datetime.now()
    print "\nStartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime
    print network_api.initiate_fw_upgrade(Address(METER_ADDRESS))
    time.sleep(40)
    print network_api.get_live_version(Address(METER_ADDRESS))

if __name__ == "__main__":
    run()
