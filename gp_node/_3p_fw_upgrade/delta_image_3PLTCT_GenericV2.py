"""
Adds meta data to TI-TXT file
"""

import argparse
import collections
# import crc16
import re
import sys
import os.path
import gp_node.utils.serialize as serialize
from optparse import OptionParser
from binascii import unhexlify, hexlify
# from gp_node.utils.soft_crc import SoftCRC
from soft_crc import SoftCRC

MAGIC_NUMBER = 0xBABE
MAIN_FLASH_START_ADDR = 0x3000
MAIN_FLASH_END_ADDR = 0x80000;
ALLOCATION_TABLE_ROWS = 251
ALLOCATION_TABLE_SIZE = 12 * ALLOCATION_TABLE_ROWS
HEADER_SIZE = 10 + ALLOCATION_TABLE_SIZE # Includes magic number, protocol version, firmware version, delta version and CRC
HEADER_START_ADDR = 0x2800 #MAIN_FLASH_START_ADDR - HEADER_SIZE
FULL_IMAGE_FILE = 0xFFFF

class Row(collections.namedtuple('Row', ['storage_addr', 'flash_addr', 'length', 'crc'])):
    """
    Wrapped around namedtuple purely to have a better __str__ representation
    by use base 16 representation instead of base 10 representation. Each row contains

    - storage_addr
    - flash_addr
    - length
    - crc
    """
    def __str__(self):
        return "Row(storage_addr={storage_addr}, flash_addr={flash_addr},"\
               " length={length}, crc={crc}) \n".format(storage_addr=hex(self.storage_addr),
                                                     flash_addr=hex(self.flash_addr),
                                                     length=hex(self.length),
                                                     crc=hex(self.crc))

    def __repr__(self):
        return self.__str__()


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


def get_total_size(sections):
    """
    :param dict sections: A dictionary whose key is "address" and value is bytearray
    
    :returns: The summation of all bytearrays in the input sections. This essentially\
        is used to calculate the total size of the hex file which the sections argument represent
    """
    # Validate total size of sections which will be loaded
    return sum([len(sections[section]) for section in sections]);




def _get_crc(block):
    """
    This function is similar to crc16.crc16xmodem() except that it uses
    0xFFFF as the initial value (crc16.crc16xmodem() uses 0x0000 as the initial value).
    The C++ implementation of CRC in node_bsl should be changed to use 0x0000
    as the initial value; once that is done, simply replace _get_crc with crc16.crc16xmodem    

    :param bytearray block: The bytearray whose CRC is to be calculated

    :returns: CRC16-CCITT of the input block
    """
    soft_crc = SoftCRC()
    crc = soft_crc.crc16ccitt(str(block))
    # if args.printID == 1:
    #     print "Length of block & CRC:",len(block), hex(crc)
    return crc


def get_allocation_table(sections):
    """
    Create the allocation table for a list of sections, assigning a storage
    address to each section.

    :param bytearray sections: A dictionary whose indices are addresses, and values are bytearrays
    
    :returns: The allocation table which is a list of Rows (which are namedtuples)
    """

    address_list=[]
    for section in sections:
        address_list.append(section)

    address_list.sort() 

    if len(sections) > ALLOCATION_TABLE_ROWS:
        sys.exit("  ERROR: Program contains {num_sections} sections, but the allocation table "
                 "can only support {num_table_rows} rows. Exiting."\
                 .format(num_sections=len(sections), num_table_rows=ALLOCATION_TABLE_ROWS))

    allocation_table = []
    currentImageAddr = HEADER_SIZE
    for section in address_list:
        allocation_table.append(Row(currentImageAddr, section, len(sections[section]), _get_crc(str(sections[section]))))
        currentImageAddr += len(sections[section])
    # print "--------------------------------"
    # print allocation_table
    #allocation_table.sort(key = lambda x: x.flash_addr)
    return allocation_table


def serialize_uint16(num):
    """
    Serializes num into a 2 byte bytearray

    :param int num: The number which is to be serialzed. num should be in the range\
        0 to 2**16 - 1

    :returns: bytearray of length 2
    """
    if num < 0 or num >= 2**16:
        raise ValueError("{} cannot be serialized as a uint16!".format(num))

    return bytearray([(num & 0xFF), ((num >> 8) & 0xFF)])


def serialize_uint32(num):
    """
    Serializes num into a 4 byte bytearray

    :param int num: The number which is to be serialzed. num should be in the range\
        0 to 2**32 - 1

    :returns: bytearray of length 4
    """    
    if num < 0 or num >= 2**32:
        raise ValueError("{} cannot be serialized as a uint32!".format(num))

    return bytearray([(num & 0xFF), ((num >> 8) & 0xFF), ((num >> 16) & 0xFF),
                      ((num >> 24) & 0xFF)])



def deserialize_uint16(array):
    """
    Deserializes given bytearray into an interger

    :param bytearray array: A bytearray of length 2

    :returns: interger in range 0 to 2**16 - 1
    """
    if len(array) != 2:
        raise Exception

    return int(array[0]) + (int(array[1]) << 8)

def deserialize_uint32(array):
    """
    Deserializes given bytearray into an interger

    :param bytearray array: A bytearray of length 2

    :returns: interger in range 0 to 2**16 - 1
    """
    if len(array) != 4:
        raise Exception

    return (int(array[0]) + (int(array[1]) << 8)+ (int(array[2]) << 16)+ (int(array[3]) << 24))

def create_binary_image(bin_name, firmware_version, delta_version, protocol_version, sections, allocation_table):
    """
    Create the raw binary image file containing the given sections and GP header.
    
    :param str name: filename of the bin file (usually out.bin)

    :param int firmware_version: Firmware version in the TI .txt file

    :param dict sections: dictionary whose keys are addresses, and values are bytearray\
        representing TI .txt file

    :param allocation_table: Allocation table representing the TI .txt file
    """

    address_list=[]
    for section in sections:
        address_list.append(section)

    address_list.sort() 

    with open(bin_name, 'wb') as fp:
        header = _get_serialized_header(firmware_version, delta_version, protocol_version, allocation_table)
        # fp.write(_get_serialized_header(firmware_version, allocation_table))
        fp.write(header)
        for section in address_list:
            fp.write(sections[section])
        # print len(header) + len(sections[0x2000]) + len(sections[0x2400]) + len(sections[0x12380])

    """
    Create name.txt(TI.txt format) from out.bin.
    This reverse engineering only for debugging purpose
    """
    with open(bin_name, 'rb') as fp:
        binary_file = bytearray()
        binary_file = fp.read()
        """
        Extract length of each section from header.
        This is little bit tricky as .bin file is binary file
        TODO : An easier way to extract data form header????
        """
        header = binary_file[0:HEADER_SIZE]
        allocation_address = [0 for n in range(ALLOCATION_TABLE_ROWS)]

        header_str = header
        binary_img_sections = {}
        start_address = int(HEADER_SIZE)  #1208
        end_address = start_address
        address = 0
        index = int(10)  # flash addr offset
        for n in range(ALLOCATION_TABLE_ROWS):
            data0 = str(header_str[index]).encode('hex')
            index += 1
            data1 = str(header_str[index]).encode('hex')
            index += 1
            data2 = str(header_str[index]).encode('hex')
            index += 1
            data3 = str(header_str[index]).encode('hex')

            data0  = int(str(data0), 16)
            data1  = int(str(data1), 16)
            data2  = int(str(data2), 16)
            data3  = int(str(data3), 16)
            #print n, hex(data0),hex(data1),hex(data2),hex(data3)
            address = data0 + (data1<<8)+ (data2<<16)+ (data3<<24)
            allocation_address[n] = address

            index += 1
            data0 = str(header_str[index]).encode('hex')
            index += 1
            data1 = str(header_str[index]).encode('hex')
            data0  = int(str(data0), 16)
            data1  = int(str(data1), 16)

            length = data0 + (data1<<8)
            end_address += length

            # print hex(start_address), hex(end_address),hex(length), hex(address)
            #print start_address, end_address,length
            new_section = str(binary_file[start_address:end_address]).encode('hex')
            new_section = new_section.upper()
            binary_img_sections[address] = new_section
            # print address

            # print "length of this section", len (binary_img_sections[address]), address
            start_address = end_address
            index = index + 7

        flash_start_address = int(HEADER_START_ADDR)
        binary_img_sections[flash_start_address] = (str(binary_file[:HEADER_SIZE]).encode('hex')).upper()
        #print str(allocation_address[0])
        #print allocation_address
        #print "printing dictionary sections"
        # for section in binary_img_sections:
        #     print section, len(binary_img_sections[section])
        # with open(txt_name, 'w') as fp:
        #     for section in sorted(binary_img_sections):
        #         fp.write(create_bin_text_image(binary_img_sections[section],section))
        #     fp.write('q\n')

def create_bin_text_image(section,addr):
    """
    Convert  Hex section format from .bin file to ti.txt format
    """
    to_return = '@'
    to_return += hex(addr)
    to_return += '\n'

    lines = [section[n:n+32] for n in range(0, len(section), 32)]
    #print "test", lines
    for line in lines:
        #print line
        to_return += format_bin_text_secion(line)
        to_return += '\n'
    #print "Formated String\n", to_return
    return to_return


def format_bin_text_secion(section):
    """
    format into ti.txt 
    """
    chr_array = str(section)
    #print chr_array
    result_str = ""
    length = len(chr_array)
    for i in range(length):
        if i%2 == 0:
            result_str =  result_str + " " + chr_array[i]
        else:
            result_str = result_str + chr_array[i]
    result_str_new = result_str[1:]
    #print result_str_new
    return result_str_new



def create_ti_txt_image(name, firmware_version, delta_version, sections, allocation_table):
    """
    Create a TI .txt image file containing the given sections and header.

    :param int firmware_version: Firmware version number to be placed in the header of the output file

    :param str name: The name of the output file (typically out.txt)

    :param sections: Dictionary representing contents of the TI .txt file

    :param list(Row) allocation_table: The allocation table to be placed in the header of the output file
    """
    with open(name, 'w') as fp:
        header = _get_serialized_header(firmware_version, delta_version, protocol_version, allocation_table)
        fp.write(_get_ti_txt_section(MAIN_FLASH_START_ADDR, header))
        for section in sorted(sections):
            fp.write(_get_ti_txt_section(section, sections[section]))
        fp.write('q\n')


def _get_ti_txt_section(addr, data):
    """
    Helper function to create_ti_txt_image

    :param int addr:
    :param bytearray data:
    """
    to_return = ''
    lines = [data[n:n+16] for n in range(0, len(data), 16)]
    #print "test", lines
    to_return += '@{}\n'.format(format(addr, '04x'))
    #print to_return
    for line in lines:
        to_return += ' '.join([format(byte, '02X') for byte in line])
        to_return += '\n'
    return to_return

def _get_serialized_header(firmware_version, delta_version, protocol_version, allocation_table):
    """
    This function is used to create out.bin file. The out.bin file
    contains a "header" field, and this function is used to get the hex data
    which sits in the out.bin files

    :param int firmware_version: 
    :param list(Row) allocation_table:

    :returns: bytearray which represents the header of the out.bin file
    """
    header = bytearray([])
    header.extend(serialize_uint16(MAGIC_NUMBER))
    header.extend(serialize_uint16(protocol_version))
    header.extend(serialize_uint16(firmware_version))
    header.extend(serialize_uint16(delta_version))
    # print "Exiting header"
    for row in allocation_table:
        header.extend(serialize_uint32(row.storage_addr))
        header.extend(serialize_uint32(row.flash_addr))
        header.extend(serialize_uint16(row.length))
        header.extend(serialize_uint16(row.crc))
    # Fill any unused rows with zeroes
    for _ in range(ALLOCATION_TABLE_ROWS - len(allocation_table)):
        header.extend(chr(0) * 12)

    header.extend(serialize_uint16(_get_crc(str(header))))
    return header


def get_image_header(sections):
    """
    Extracts version number and magic number field from the sections argument,
    which is a representation of the TI .txt file being processed

    :param dict sections: A dictionary whose keys are addresses and value is bytearray

    :returns: A dictionary which contains two keys: "magic_num" and "version"    
    """
    found = False
    header = {}
    for section in sections:
        min_addr, max_addr = (section, section + len(sections[section]) - 1)
        if (HEADER_START_ADDR + 0x02) in range(min_addr, max_addr) and\
                (HEADER_START_ADDR + 0x06) in range(min_addr, max_addr):
            # magic_num_pos = HEADER_START_ADDR + 0x02
            header['magic_num']        = deserialize_uint16(sections[section][0:2])
            header['protocol_version'] = deserialize_uint16(sections[section][2:4])
            header['firmware_version'] = deserialize_uint16(sections[section][4:6])
            header['delta_version']    = deserialize_uint16(sections[section][6:8])
            break
    return header


def run():
    #parser = argparse.ArgumentParser(description="Creates image of new firmware for"
    #                                             "info flash")
    # parser.add_argument('main_txt_file_path', help="Path to TI .txt file containing new "
    #                                           "firmware")

    # args = parser.parse_args()

    parser = OptionParser()
    parser.add_option("-o", "--file1", dest="file1",
                      help="containing old firmware .txt file path")

    parser.add_option("-n", "--file2", dest="file2",
                      help="containing new firmware .txt file path")

    parser.add_option("-s", dest="printID", type=int, help="Enable to see Block sizes")

    (options, args) = parser.parse_args()

    if options.file1 is None:
        sys.exit("-- Couldn't txt file1.")


    input_lines = None
    with open(options.file1, 'r') as fp:
        input_lines = fp.readlines()

    #--------------------------------------------------------------
    print "1.Extracting sections from file1.txt ..."
    #--------------------------------------------------------------
    all_sections = extract_sections(input_lines)


    #--------------------------------------------------------------
    print "2.Extracting firmware version..."
    #--------------------------------------------------------------
    image_header = get_image_header(all_sections)
    if not image_header:
        sys.exit("  ERROR: Couldn't find the image header.")
    if image_header['magic_num'] != MAGIC_NUMBER:
        sys.exit("  ERROR: Image Magic Number mismatched.")
    if image_header['delta_version'] != FULL_IMAGE_FILE:
        sys.exit("  ERROR: Image type mismatched.")

    HDPT_VERSION_FILE1     = image_header['protocol_version']
    PROTOCOL_VERSION_FILE1 = HDPT_VERSION_FILE1 & 0x00FF
    FIRMWARE_VERSION_FILE1 = image_header['firmware_version']
    DELTA_VERSION_FILE1    = image_header['delta_version']

    # if PROTOCOL_VERSION > 255:
    #     print "  FIRMWARE_VERSION: {}, PROTOCOL_VERSION: {}".format(FIRMWARE_VERSION,PROTOCOL_VERSION)
    #     sys.exit("  ERROR: Invalid Protocol version founds from the Image. Enter Manually or see -h [help]")
    # else:
    #     PROTOCOL_VERSION = args.protocol_x

    if PROTOCOL_VERSION_FILE1 == 2:
        PROJECT_VERSION_FILE1 = 'WC MANIPUR UTILITY'
    elif PROTOCOL_VERSION_FILE1 == 3:
        PROJECT_VERSION_FILE1 = 'WC UP UTILITY'
    elif PROTOCOL_VERSION_FILE1 == 4:
        PROJECT_VERSION_FILE1 = 'WC WB UTILITY'
    elif PROTOCOL_VERSION_FILE1 == 6:
        PROJECT_VERSION_FILE1 = 'LTCT MANIPUR UTILITY'
    elif PROTOCOL_VERSION_FILE1 == 7:
        PROJECT_VERSION_FILE1 = 'LTCT UP UTILITY'
    elif PROTOCOL_VERSION_FILE1 == 8:
        PROJECT_VERSION_FILE1 = 'LTCT WB UTILITY'
    else:
        PROJECT_VERSION_FILE1 = str(PROTOCOL_VERSION_FILE1)

    del all_sections[HEADER_START_ADDR]  # remove magic number & version number from current image

    #--------------------------------------------------------------
    print "3.Extracting Image Block(s)..."
    #--------------------------------------------------------------
    new_section = {}
    for section in all_sections:
        len_section = len(all_sections[section])
        current_sector = section/2048
        next_sector = current_sector+1

        next_sector_len = next_sector*2048
        allowed_length = next_sector_len-section
        print("  Address: {}, Length: {}".format(str(hex(section)), str(len_section)))
        
        if(len_section > allowed_length):
            new_section[section] = all_sections[section][0:allowed_length]
            len_section = len_section - allowed_length

            while len_section>0:
                if (len_section > 2048):
                    new_section[section+allowed_length] = all_sections[section][allowed_length:(allowed_length+2048)]
                else:
                    new_section[section+allowed_length] = all_sections[section][allowed_length:(allowed_length+len_section)]

                allowed_length += 2048
                len_section -= 2048
        else:
            new_section[section] = all_sections[section]
    all_sections = new_section


    #--------------------------------------------------------------
    print "4.Breaking into blocks[2kB]"
    #--------------------------------------------------------------
    file1_address_list=[]
    for section in all_sections:
        file1_address_list.append(section)
    file1_address_list.sort()  

    print "  Created {} blocks.".format(len(all_sections))
    if options.printID == 1:
        for i in file1_address_list:
            print "  New_block_address: ",hex(i), ", New_block_length: ",len(new_section[i])
    

    #--------------------------------------------------------------
    print "5.Checking Blocks validity..."
    #--------------------------------------------------------------
    valid_sections = get_valid_sections(all_sections, MAIN_FLASH_START_ADDR, MAIN_FLASH_END_ADDR)

    if len(all_sections) == len(valid_sections):
        print "  All {} Blocks are valid.".format(len(all_sections))
    else:
        print "  WARNING: One or more sections fall outside the valid address range."
        print "  WARNING: These will not be included in the image:"
        print "  WARNING: {}".format([hex(section) for section in all_sections if section not in valid_sections])


    #--------------------------------------------------------------
    print "6.Checking Image size..."
    #--------------------------------------------------------------
    total_size = get_total_size(valid_sections)
    MAX_SIZE = MAIN_FLASH_END_ADDR - MAIN_FLASH_START_ADDR
    if total_size > MAX_SIZE:
        sys.exit(" ERROR: Program is {prog_size} bytes, but max size is {max_size}. Exiting...".\
                 format(prog_size=total_size, max_size=MAX_SIZE))
    else:
        print "  Total Image size [{} bytes].".format(total_size)

    file1_valid_section = valid_sections

    #--------------------------------------------------------------
    print "7.Allocating Blocks in the image..."
    #--------------------------------------------------------------
    allocation_table = get_allocation_table(valid_sections)
    if options.printID == 1:
        print allocation_table


    BinFile1 = options.file1.replace('.txt', '.bin')
    #--------------------------------------------------------------
    print "8.Writing image to {}...".format(BinFile1)
    #--------------------------------------------------------------
    create_binary_image(BinFile1, FIRMWARE_VERSION_FILE1, DELTA_VERSION_FILE1, HDPT_VERSION_FILE1, valid_sections, allocation_table)

    print "  FIRMWARE_VERSION: {}, PROTOCOL_VERSION: {}, PROJECT_NAME: {}".format(FIRMWARE_VERSION_FILE1,PROTOCOL_VERSION_FILE1,PROJECT_VERSION_FILE1)
    print "  SUCCESS: Image File Created !!!"


    # ---------------------------------------------------------------------------------------

    print "----------------------------------------------------------------------------\n"

    if options.file2 is None:
        sys.exit("-- Couldn't txt file2.")


    input_lines = None
    with open(options.file2, 'r') as fp:
        input_lines = fp.readlines()

    #--------------------------------------------------------------
    print "1.Extracting sections from file2.txt ..."
    #--------------------------------------------------------------
    all_sections = extract_sections(input_lines)


    #--------------------------------------------------------------
    print "2.Extracting firmware version..."
    #--------------------------------------------------------------
    image_header = get_image_header(all_sections)
    if not image_header:
        sys.exit("  ERROR: Couldn't find the image header.")
    if image_header['magic_num'] != MAGIC_NUMBER:
        sys.exit("  ERROR: Image Magic Number mismatched.")
    if image_header['delta_version'] != FULL_IMAGE_FILE:
        sys.exit("  ERROR: Image type mismatched.")

    HDPT_VERSION_FILE2     = image_header['protocol_version']
    PROTOCOL_VERSION_FILE2 = HDPT_VERSION_FILE2 & 0x00FF
    FIRMWARE_VERSION_FILE2 = image_header['firmware_version']
    DELTA_VERSION_FILE2    = image_header['delta_version']

    # if PROTOCOL_VERSION > 255:
    #     print "  FIRMWARE_VERSION: {}, PROTOCOL_VERSION: {}".format(FIRMWARE_VERSION,PROTOCOL_VERSION)
    #     sys.exit("  ERROR: Invalid Protocol version founds from the Image. Enter Manually or see -h [help]")
    # else:
    #     PROTOCOL_VERSION = args.protocol_x

    if PROTOCOL_VERSION_FILE2 == 2:
        PROJECT_VERSION_FIL2 = 'WC MANIPUR UTILITY'
    elif PROTOCOL_VERSION_FILE2 == 3:
        PROJECT_VERSION_FILE2 = 'WC UP UTILITY'
    elif PROTOCOL_VERSION_FILE2 == 4:
        PROJECT_VERSION_FILE2 = 'WC WB UTILITY'
    elif PROTOCOL_VERSION_FILE2 == 6:
        PROJECT_VERSION_FILE2 = 'LTCT MANIPUR UTILITY'
    elif PROTOCOL_VERSION_FILE2 == 7:
        PROJECT_VERSION_FILE2 = 'LTCT UP UTILITY'
    elif PROTOCOL_VERSION_FILE2 == 8:
        PROJECT_VERSION_FILE2 = 'LTCT WB UTILITY'
    else:
        PROJECT_VERSION_FILE2 = str(PROTOCOL_VERSION_FILE2)

    del all_sections[HEADER_START_ADDR]  # remove magic number & version number from current image

    #--------------------------------------------------------------
    print "3.Extracting Image Block(s)..."
    #--------------------------------------------------------------
    new_section = {}
    for section in all_sections:
        len_section = len(all_sections[section])
        current_sector = section/2048
        next_sector = current_sector+1

        next_sector_len = next_sector*2048
        allowed_length = next_sector_len-section
        print("  Address: {}, Length: {}".format(str(hex(section)), str(len_section)))
        
        if(len_section > allowed_length):
            new_section[section] = all_sections[section][0:allowed_length]
            len_section = len_section - allowed_length

            while len_section>0:
                if (len_section > 2048):
                    new_section[section+allowed_length] = all_sections[section][allowed_length:(allowed_length+2048)]
                else:
                    new_section[section+allowed_length] = all_sections[section][allowed_length:(allowed_length+len_section)]

                allowed_length += 2048
                len_section -= 2048
        else:
            new_section[section] = all_sections[section]
    all_sections = new_section


    #--------------------------------------------------------------
    print "4.Breaking into blocks[2kB]"
    #--------------------------------------------------------------
    file2_address_list=[]
    for section in all_sections:
        file2_address_list.append(section)
    file2_address_list.sort()  

    print "  Created {} blocks.".format(len(all_sections))
    if options.printID == 1:
        for i in file2_address_list:
            print "  New_block_address: ",hex(i), ", New_block_length: ",len(new_section[i])
    

    #--------------------------------------------------------------
    print "5.Checking Blocks validity..."
    #--------------------------------------------------------------
    valid_sections = get_valid_sections(all_sections, MAIN_FLASH_START_ADDR, MAIN_FLASH_END_ADDR)

    if len(all_sections) == len(valid_sections):
        print "  All {} Blocks are valid.".format(len(all_sections))
    else:
        print "  WARNING: One or more sections fall outside the valid address range."
        print "  WARNING: These will not be included in the image:"
        print "  WARNING: {}".format([hex(section) for section in all_sections if section not in valid_sections])

    
    #--------------------------------------------------------------
    print "6.Checking Image size..."
    #--------------------------------------------------------------
    total_size = get_total_size(valid_sections)
    MAX_SIZE = MAIN_FLASH_END_ADDR - MAIN_FLASH_START_ADDR
    if total_size > MAX_SIZE:
        sys.exit(" ERROR: Program is {prog_size} bytes, but max size is {max_size}. Exiting...".\
                 format(prog_size=total_size, max_size=MAX_SIZE))
    else:
        print "  Total Image size [{} bytes].".format(total_size)

    file2_valid_section = valid_sections

    #--------------------------------------------------------------
    print "7.Allocating Blocks in the image..."
    #--------------------------------------------------------------
    allocation_table = get_allocation_table(valid_sections)
    if options.printID == 1:
        print allocation_table

    BinFile2 = options.file2.replace('.txt', '.bin')
    #--------------------------------------------------------------
    print "8.Writing image to {}...".format(BinFile2)
    #--------------------------------------------------------------
    create_binary_image(BinFile2, FIRMWARE_VERSION_FILE2, DELTA_VERSION_FILE2, HDPT_VERSION_FILE2, valid_sections, allocation_table)

    print "  FIRMWARE_VERSION: {}, PROTOCOL_VERSION: {}, PROJECT_NAME: {}".format(FIRMWARE_VERSION_FILE2,PROTOCOL_VERSION_FILE2,PROJECT_VERSION_FILE2)
    print "  SUCCESS: Image File Created !!!"


    #--------------------------------------------------------------------------------------
    print "----------------------------------------------------------------------------\n"

    if HDPT_VERSION_FILE1 != HDPT_VERSION_FILE2:
        sys.exit("  ERROR: DELTA FILE CANNOT CREATED [protocol_version Mismatched]")

    #--------------------------------------------------------------
    print "1. Finding Delta Sections ..."
    #--------------------------------------------------------------

    delta_valid_section1 = {}
    delta_valid_section2 = {}

    # If file2 is lengthy
    if len(file2_address_list) > len(file1_address_list):
        dif = len(file2_address_list)-len(file1_address_list)
        for i in range(dif):
            file1_address_list.append(0)

    for section in file2_address_list:
        if file2_valid_section[section] == file1_valid_section[section]:
            if options.printID == 1:
                print "data matchedin file2 @", hex(section)
        else:
            delta_valid_section1[section] = file2_valid_section[section]
            print "data unmatched in file2 @", hex(section) 

    for section in file1_address_list:
        if file1_valid_section[section] == file2_valid_section[section]:
            if options.printID == 1:
                print "data matched in file1 @", hex(section)
        else:
            delta_valid_section2[section] = file1_valid_section[section]
            print "data unmatched in file1 @", hex(section)  

    #--------------------------------------------------------------
    print "2.Allocating Delta Blocks in the image..."
    #--------------------------------------------------------------
    allocation_table1 = get_allocation_table(delta_valid_section1)
    if options.printID == 1:
        print allocation_table1

    allocation_table2 = get_allocation_table(delta_valid_section2)
    if options.printID == 1:
        print allocation_table2


    fwVerFile1 = str(FIRMWARE_VERSION_FILE1)
    fwVerFile2 = str(FIRMWARE_VERSION_FILE2)

    deltaFwVersion1 = "delta_{}_{}".format(FIRMWARE_VERSION_FILE1, FIRMWARE_VERSION_FILE2)
    deltaFwVersion2 = "delta_{}_{}".format(FIRMWARE_VERSION_FILE2, FIRMWARE_VERSION_FILE1)
    BinFileDelta1 = BinFile1.replace(fwVerFile1, deltaFwVersion1)
    BinFileDelta2 = BinFile2.replace(fwVerFile2, deltaFwVersion2)
    #--------------------------------------------------------------
    print "3.Writing image to {}...".format(BinFileDelta1)
    #--------------------------------------------------------------
    create_binary_image(BinFileDelta1, FIRMWARE_VERSION_FILE2, FIRMWARE_VERSION_FILE1, HDPT_VERSION_FILE2, delta_valid_section1, allocation_table1)
    print "  FIRMWARE_VERSION: {}-{}, PROTOCOL_VERSION: {}-{}, PROJECT_NAME: {}-{}".format(FIRMWARE_VERSION_FILE1, FIRMWARE_VERSION_FILE2, PROTOCOL_VERSION_FILE1, PROTOCOL_VERSION_FILE2, PROJECT_VERSION_FILE1, PROJECT_VERSION_FILE2)

    #--------------------------------------------------------------
    print "4.Writing image to {}...".format(BinFileDelta2)
    #--------------------------------------------------------------
    create_binary_image(BinFileDelta2, FIRMWARE_VERSION_FILE1, FIRMWARE_VERSION_FILE2, HDPT_VERSION_FILE1, delta_valid_section2, allocation_table2)
    print "  FIRMWARE_VERSION: {}-{}, PROTOCOL_VERSION: {}-{}, PROJECT_NAME: {}-{}".format(FIRMWARE_VERSION_FILE2, FIRMWARE_VERSION_FILE1, PROTOCOL_VERSION_FILE2, PROTOCOL_VERSION_FILE1, PROJECT_VERSION_FILE2, PROJECT_VERSION_FILE1)
    print "  SUCCESS: Delta Image Files Created !!!"


if __name__ == '__main__': 
    run()
