"""
Adds meta data to TI-TXT file
"""

import argparse
import collections
import crc16
import re
import sys
import serial
from gp_node.network.network_api import NetworkAPI
import gp_node.utils.serialize as serialize
from binascii import unhexlify, hexlify
from gp_node.utils.address import Address

MAGIC_NUMBER = 0xBABE
VERSION_MAGIC_NUMBER = 0xADD1
# New in Protcol v3: firmware version number
# New in Protocol v4: CRCs (allocation table + sections)
# In Protocol v6: Changed flash addresses to be 32 bits
PROTOCOL_VERSION = 6
MAIN_FLASH_START_ADDR = 0x4000
MAIN_FLASH_END_ADDR = 0x23FFF
BSL_FLASH_START_ADDR = 0x1000
BSL_FLASH_END_ADDR = 0x17FF
ALLOCATION_TABLE_ROWS = 10
ALLOCATION_TABLE_FIELDS = 4
ALLOCATION_TABLE_SIZE = 12 * ALLOCATION_TABLE_ROWS
HEADER_SIZE = 8 + ALLOCATION_TABLE_SIZE # Includes magic number, protocol version, firmware version, and CRC

def deserialize_uint16(array):
    """
    Deserializes given bytearray into an interger

    :param bytearray array: A bytearray of length 2

    :returns: interger in range 0 to 2**16 - 1
    """
    if len(array) != 2:
        raise Exception

    return int(array[0]) + (int(array[1]) << 8)

def get_header_info(filename):
    binary_file = open(filename, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    
    sections = {}
    for i in range(0,10):
    	k = (i*12)+6
    	sections[i] = hexfile_payload[k:(k+10)]
    
    for sec in sections:
    	a = bytearray()
    	for byte in sections[sec]:
    		a.append(byte)

def _get_crc(block):
    """
    This function is similar to crc16.crc16xmodem() except that it uses
    0xFFFF as the initial value (crc16.crc16xmodem() uses 0x0000 as the initial value).
    The C++ implementation of CRC in node_bsl should be changed to use 0x0000
    as the initial value; once that is done, simply replace _get_crc with crc16.crc16xmodem    

    :param bytearray block: The bytearray whose CRC is to be calculated

    :returns: CRC16-CCITT of the input block
    """
    def _bit_reverse(x):
        first_half = x%16
        second_half = x/16
        table = {0:0, 1:8, 2:4, 3:12, 4:2, 5:10, 6:6, 7:14, 8:1, 9:9, 10:5, 11:13, 12:3, 13:11, 14:7, 15:15}
        return_value = 16*table[first_half] + table[second_half]
        return return_value

    formatted_block = bytearray([])
    for byte in block:
        formatted_block.append(_bit_reverse(byte))
        formatted_block.append(0)

    crc = crc16.crc16xmodem(str(formatted_block),0)
    #print "In CRC Length of block:",len(block), hex(crc)
    return crc

def get_no_of_sectors(filename):
    binary_file = open(filename, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)

    no_of_sectors = len(hexfile_payload)/4096
    file_by_sector = {}
    for i in range(0,no_of_sectors):
        k = (i*4096)
        file_by_sector[i] = hexfile_payload[k:(k+4096)]

    for byte in file_by_sector[0]:
        hexfile_payload.append(byte)

    for i in range(0,sector_chunk_bytes):
        k = (i*32)
        #file_chunk_bytes[i] = hexfile_payload[k:(k+32)]
        file_chunk_bytes[0] = hexfile_payload[0:(0+32)]
        create_sector_wise_file("ugra.bin",file_chunk_bytes)
        
        SECTOR_ADDRESS = 0x1000
        print network_api.three_ph_erase_flash_sector(Address('0.0.0.255'),1)
        print network_api.my_flash_io_master.write(Address("0.0.0.255"), 4096,file_chunk_bytes[0])
        #print "calculating 32 bytes CRC : "
        calculated_crc = _get_crc(file_chunk_bytes[0])
        #print calculated_crc
    #print "computed CRC of 32 bytes : "
    computed_crc = network_api.three_ph_get_ext_flash_crc(Address("0.0.0.255"),4096,0x20)
    #print computed_crc
    if computed_crc == calculated_crc:
        print "sector of chunk bytes crc is correct "
    else:
        print "CRC mismatch : "
    #print network_api.three_ph_get_ext_flash_crc(Address("0.0.0.255"),4096,0x1000)
    #create_sector_wise_file("filename.bin",file_by_sector)
    print "length of file = ", len(hexfile_payload)
    print "no of sectors = ", len(hexfile_payload)/4096
    print "no of Remaining Bytes = ", len(hexfile_payload)%4096

def create_sector_wise_file(filename,sections):
    with open(filename, 'wb') as fp:
        for section in sections:
            #fp.write('@')
            #fp.write(str(section))
            #fp.write(str('\n'))
            fp.write(sections[section])
            #fp.write(str('\n'))
def compare_files(filename1,filename2):
    binary_file_1 = open(filename1, "rb")
    block = binary_file_1.read()
    hexfile1_payload = bytearray()
    for ch in block:
        hexfile1_payload.append(ch)

    binary_file_2 = open(filename2, "rb")
    block = binary_file_2.read()
    hexfile2_payload = bytearray()
    for ch in block:
        hexfile2_payload.append(ch)

    #for i in range(0,10):
        


def run():
    parser = argparse.ArgumentParser(description="Creates image of new firmware for"
                                                 "info flash")
    parser.add_argument('main_bin_file_1_path', help="Path to TI .txt file containing the BSL. "
                                         "Including this path indicates that the BSL code "
                                          "should be included in the .txt output file.")
    parser.add_argument('-d', action="store", dest="device", 
                        type=str, help="device name, eg. /dev/ttyUSB0")
    parser.add_argument('-b', action="store", dest="baud_rate", 
                        type=str, help="baud rate")
    parser.add_argument('-p', action="store", dest="hex_file", 
                        help="programs new hex file")
    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")

    args = parser.parse_args()

    if args.device is None:
        args.device = "/dev/gp-gateway"
    if args.baud_rate is None:
        args.baud_rate = 9600
    if args.timeout is None:
        args.timeout = 4

    args = parser.parse_args()
    #get_header_info(args.main_bin_file_1_path)
    #get_header_info(args.main_bin_file_2_path)

    binary_file = open(args.main_bin_file_1_path, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)

    print "length of file = ", len(hexfile_payload)
    print "no of iteration = ", len(hexfile_payload)/64
    print "no of Remaining Bytes = ", len(hexfile_payload)%64
    
    
    ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)
    network_api = NetworkAPI(ser, "irda")


    no_of_iteration = len(hexfile_payload)/64
    no_of_bytes_remaining = len(hexfile_payload)%64
    SECTOR_ADDRESS = 0x100
    print network_api.three_ph_erase_flash_sector(Address('0.0.0.255'),31)
    print network_api.my_flash_io_master_3p.erase(Address("0.0.0.255"), 0)
    print network_api.my_flash_io_master_3p.erase(Address("0.0.0.255"), 1)
    sectors = {}
    with open("fw_status.txt", 'w') as fp:
        for i in range(0,no_of_iteration):
            print i
            #result = network_api.my_flash_io_master_3p.write_fw_upgrade(Address("0.0.0.255"),\
             #SECTOR_ADDRESS+(i*32),hexfile_payload[(i*32) : ((i*32)+32)])
            sectors[i] = hexfile_payload[(i*64) : ((i*64)+64)]
            fp.write(str(i))
            fp.write(result)
            fp.write('\n')

    for i in range(0,no_of_iteration):
        crc = _get_crc(sectors[0])
        print "Sector ",i," CRC: ", crc
    #print network_api.three_ph_get_ext_flash_crc(Address("0.0.0.255"),4096,0x1000)
    #create_sector_wise_file("filename.bin",file_by_sector)


    print "Done."


if __name__ == '__main__': 
    run()
