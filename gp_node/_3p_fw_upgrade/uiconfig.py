import argparse
import collections
import crc16
import re
import sys
from binascii import unhexlify, hexlify
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import serial
import gp_node.utils.serialize as serialize
import json


def extract_sections(input_lines):
    """
    Extract all sections from a TI .txt file and return as a list.

    :param list(str) input_lines: The contents of the TI .txt file in form of a list of strings
    
    :returns: A dictionary which contains one key for each address line & each dictionary entry\
        is a bytearray corresponding to the data content in that address range
    """
    sections = {}
    currentSection = None
    currentAddr = None
    #print "test 1"
    for line in input_lines:
        #i=0;
        #for char in line:
        #    if char == "\r":
        #        end_index = i
        #        print "index ",end_index
        #    i = i + 1
        #print "test 2", len(line),"-",line
        #j=0
        #for char in line:
        #    print j,"---",str(hex(ord(char)))
        #    j = j + 1
        address_match = None
        data_match = None
        address_match = re.match(r'^@([a-fA-F0-9]{4,5}) ?', line)

        #Match strings of type "A1 ", "AA ", "3A ", "A1", "AA" and "3A"
        data_match = re.match(r'^(([0-9A-F]{2} ?){1,16})', line)
        if address_match:
            #print "address found"
            address = int(address_match.groups()[0], 16)
            currentSection = address
            currentAddr = address
            sections[address] = bytearray([])
        elif data_match:
            #print "test 3"
            #print data_match.group().split(' ')
            str_elements = [element for element in data_match.group().split(' ') if element]
            binary_data = bytearray([int(byte, 16) for byte in str_elements])
            sections[currentSection].extend(binary_data)

    return sections


def get_valid_sections(sections, min_addr, max_addr):
    """
    Filter a list of sections, returning only those which fall within a certain
    valid address range

    :param dict sections: A dictionary whose key is "address" and value is a bytearray\
        representing data at that address
    
    :param int min_addr: The lower bound for a valid address. All keys in sections\
        which are smaller than min_addr would be dropped
    
    :param int max_addr: The uppoer bound for a valid address. All keys in sections\
        which are larger than max_addr would be dropped

    :returns: A dictionary which is a subset of the input sections.
    """
    valid_sections = {}
    # TODO: This only checks whether a section begins in a valid address range;
    # it won't catch the case when a section is too large and spills over into
    # a non-valid flash range. Fix this.
    for section in sections:
        if min_addr <= section <= max_addr:
            valid_sections[section] = sections[section];

    return valid_sections






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



def run():
    parser = argparse.ArgumentParser(description="Creates image of new firmware for"
                                                 "info flash")
    parser.add_argument('main_txt_file_path', help="Path to TI .txt file containing new "
                                              "firmware")
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
 
    input_lines = None
    with open(args.main_txt_file_path, 'r') as fp:
        input_lines = fp.readlines()
    
    print "Extracting sections from primary .txt file..."
    all_sections = extract_sections(input_lines)
    no_of_sctions = len(all_sections)
    if (no_of_sctions != 1):
        return "Not a valid config File"


    for byte in all_sections:
        print byte
        print "Address", hex(byte)
        print "length",len(all_sections[byte])
        #print all_sections[byte]

    with open("uiconfig.bin", 'wb') as fp:
        fp.write(all_sections[byte])
    fp.close();
    
    binary_file = open("uiconfig.bin", "rb")
    """
    Here we have to send Erase sector Command
    """
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)

    # net work API flash erase

    ser = serial.Serial(args.device, int(args.baud_rate), timeout=int(args.timeout))    
  
    network_api = NetworkAPI(ser, "irda")
    
    SECTOR_ADDRESS = 0x1000
    print network_api.three_ph_erase_flash_sector(Address('0.0.0.255'),1)
    print network_api.my_flash_io_master.burn(Address("0.0.0.255"), SECTOR_ADDRESS, hexfile_payload, to_print=True)
   # print Done

if __name__ == '__main__': 
    run()
