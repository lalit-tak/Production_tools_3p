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
from soft_crc import SoftCRC


START_ADDRESS = 0x44000
SECTOR_SIZE   = 0x1000
START_SECTOR  = START_ADDRESS/4096
LEN_OF_HEADER = 24

def program(filepath, flash_io):
    flash_io.erase(Address("255.255.255.255"), START_SECTOR, True)
    binary_file = open(filepath, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)

    # create header information
    soft_crc = SoftCRC()
    protocol_version = (hexfile_payload[14]<<8)+hexfile_payload[15]
    print "UI Protocol Version : " + str(protocol_version)
    property_name = bytearray()
    for b in range(16):
        property_name.append(hexfile_payload[16+b])
    print "UI Property Name : " + property_name
    length = len(hexfile_payload)+LEN_OF_HEADER
    crc_image = soft_crc.crc16ccitt(str(hexfile_payload[0:]))
    # print "CRC Image : " + hex(crc_image)

    header_info = bytearray()
    header_info.extend(serialize.serialize_uint16(protocol_version, "reverse"))
    header_info.extend(property_name)
    header_info.extend(serialize.serialize_uint16(length, "reverse"))
    header_info.extend(serialize.serialize_uint16(crc_image, "reverse"))
    crc = soft_crc.crc16ccitt(str(header_info[0:]))
    header_info.extend(serialize.serialize_uint16(crc, "reverse"))
    # print "CRC header : " + hex(crc)
    for ch in block:
        header_info.append(ch)
    print [int(b) for b in header_info]    
    flash_io.burn(Address("255.255.255.255"), START_ADDRESS, header_info, to_print=True)

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
    if args.hex_file is not None:
        print "Erasing..."
        program(args.hex_file, network_api.my_flash_io_master_new)
    if args.version == "live":
        print network_api.get_live_version(Address('255.255.255.255'))
    if args.version == "ext":
        print network_api.get_ext_version(Address('255.255.255.255'))
        
    EndTime = datetime.datetime.now()
    print "\nStartTime:",starttime
    print "EndTime:",EndTime
    print "Diff : ", EndTime - starttime


if __name__ == "__main__":
    run()
