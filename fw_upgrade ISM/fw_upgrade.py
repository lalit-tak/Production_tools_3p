import os
import argparse
from tap import TAPHandler, TAPPacket, TAPError
from flash_io import FlashIOMaster, FlashIOError
from address import Address
import serial
import serialize as serialize
import json
import datetime
import serial
import struct
import sys
from os.path import expanduser
import time
import getpass

START_ADDRESS = 0x100

def program(filepath, flash_io):
    flash_io.erase(Address("255.255.255.255"), 0)
    # flash_io.erase(Address("255.255.255.255"), 1)
    # flash_io.erase(Address("255.255.255.255"), 2)
    # flash_io.erase(Address("255.255.255.255"), 3)
    # Here we have to do erase sector command
    binary_file = open(filepath, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    flash_io.burn(Address("255.255.255.255"), START_ADDRESS, hexfile_payload, to_print=True)

def run():

    print("Starting firmware upgrade\n\n")

    # device = "/dev/gp-gateway"
    baudrate = 9600
    timeout = 0.6
    hex_file = "out.bin"

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
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 7
    print("args",args)

    log_path=os.path.expanduser("~/fw_upgrade_exe")
    mode="irda"
    ser = serial.Serial(args.device,args.baud_rate, timeout=7)
    
    

    my_address = Address("0.0.1.2")    
    my_tap_handler = TAPHandler(ser, 7, mode, log_path)
    my_flash_io_master = FlashIOMaster(my_address, my_tap_handler)


    starttime = datetime.datetime.now()
    if hex_file is not None:
        print("\n\nNow Programing\n")
        program(hex_file, my_flash_io_master)
        
    EndTime = datetime.datetime.now()
    print("StartTime:",starttime)
    print("EndTime:",EndTime)
    print("Diff : ", EndTime - starttime)
    ser.close()



    # dongle_dlms_to_tap = bytearray()
    # meter_dlms_to_tap = bytearray()

    # dongle_dlms_to_tap = [0xAA, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3, 0xB3]
    # meter_dlms_to_tap = [0x7E, 0xA0, 0x07, 0xBB, 0x41, 0x93, 0xDA, 0x28, 0x7E]
    
    # for byte in dongle_dlms_to_tap:
    #     ser.write(chr(byte))
    #     time.sleep(0.1)


    # print '\n\nDongle DLMS to tap'

    # for byte in meter_dlms_to_tap:
    #     ser.write(chr(byte))
    #     time.sleep(0.1)


    # print 'Meter DLMS to tap'

    starttime = datetime.datetime.now()
    if hex_file is not None:
        print("\n\nNow Programing\n")
        program(hex_file, my_flash_io_master)
        
    EndTime = datetime.datetime.now()
    print("\n\nStartTime:",starttime)
    print("EndTime:",EndTime)
    print("Diff : ", EndTime - starttime)
    ser.close()


if __name__ == "__main__":
    run()



