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
import os
from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL
import time

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'duldul'
app.config['MYSQL_DATABASE_DB'] = 'fw_upgrade'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306


mysql.init_app(app)

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
    #parser.add_argument('-d', action="store", dest="device", 
                        #type=str, help="device name, eg. /dev/ttyUSB0")
    #parser.add_argument('-b', action="store", dest="baud_rate", 
                        #type=str, help="baud rate")
    parser.add_argument('-p', action="store", dest="hex_file", 
                        help="programs new hex file")
    parser.add_argument('-t', action="store", dest="timeout", 
                        help="port time out")

    args = parser.parse_args()


    
    #ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)
    #network_api = NetworkAPI(ser, "irda")

    binary_file = open(args.main_bin_file_1_path, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    length_of_file = len(hexfile_payload)
    print "Length of file before  = ", len(hexfile_payload)

    while(length_of_file%64):
        hexfile_payload.append(0x00)
        length_of_file = len(hexfile_payload)



    print "Length of file  = ", len(hexfile_payload),length_of_file
    print "No of sectors   = ", len(hexfile_payload)/4096
    print "No of Bytes in Last Sector = ", len(hexfile_payload)%4096

    no_of_sectors = length_of_file/4096
    no_of_bytes_in_last_sector = length_of_file%4096


    sectors = {}
    for i in range(0,no_of_sectors):
        sectors[i] = hexfile_payload[(i*4096) : ((i*4096)+4096)]
        print i

    print "No of Sectors:", no_of_sectors
    if(no_of_bytes_in_last_sector):
        
        temp = no_of_sectors - 1
        sectors[no_of_sectors] = hexfile_payload[(no_of_sectors*4096) : ]
        print len(sectors[no_of_sectors])
        no_of_sectors = no_of_sectors + 1
        print "No of Sectors:", no_of_sectors
        cnt = 0
        while(no_of_bytes_in_last_sector != 4096):
            no_of_bytes_in_last_sector += 1
            temp = no_of_sectors - 1
            #print "temp", temp
            sectors[temp].append(0xff)
            cnt = cnt + 1

    print "No of 64 byte chunk : ", length_of_file/64
    print "Count",cnt

    for i in range(0,no_of_sectors):
        crc = _get_crc(sectors[i])
        print "Sector ",i," CRC: ", crc
    #------------------------------------------------------
    conn = mysql.connect()
    cur = conn.cursor()
    crc0 = _get_crc(sectors[0])
    crc1 = _get_crc(sectors[1])
    version_no = deserialize_uint16(sectors[0][4:6])
    #print conn.status
    try:
        k=0
        query = "SELECT * FROM crcs WHERE TYPE = '%s' AND Address =  '%d'" % ('FW_3P', version_no)
        cur.execute(query)
        if(cur.rowcount != 0):
            query = "DELETE FROM crcs WHERE Address = '%d'" % (version_no)
            cur.execute(query)

        query = '''INSERT INTO crcs (TYPE,Address,sec_crc_00, sec_crc_01,sec_crc_02, sec_crc_03, sec_crc_04, sec_crc_05,\
        sec_crc_06, sec_crc_07, sec_crc_08, sec_crc_09, sec_crc_10, sec_crc_11, sec_crc_12, sec_crc_13, sec_crc_14,\
        sec_crc_15,sec_crc_16, sec_crc_17, sec_crc_18, sec_crc_19, sec_crc_20, sec_crc_21, sec_crc_22, sec_crc_23,\
        sec_crc_24, sec_crc_25, sec_crc_26, sec_crc_27, sec_crc_28, sec_crc_29, sec_crc_30, sec_crc_31) \
        VALUES('%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
        '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d')''' %\
        ('FW_3P',version_no,int(_get_crc(sectors[0])),\
            int(_get_crc(sectors[1])),\
            int(_get_crc(sectors[2])),\
            int(_get_crc(sectors[3])),\
            int(_get_crc(sectors[4])),\
            int(_get_crc(sectors[5])),\
            int(_get_crc(sectors[6])),\
            int(_get_crc(sectors[7])),\
            int(_get_crc(sectors[8])),\
            int(_get_crc(sectors[9])),\
            int(_get_crc(sectors[10])),\
            int(_get_crc(sectors[11])),\
            int(_get_crc(sectors[12])),\
            int(_get_crc(sectors[13])),\
            int(_get_crc(sectors[14])),\
            int(_get_crc(sectors[15])),\
            int(_get_crc(sectors[16])),\
            int(_get_crc(sectors[17])),\
            int(_get_crc(sectors[18])),\
            int(_get_crc(sectors[19])),\
            int(_get_crc(sectors[20])),\
            int(_get_crc(sectors[21])),\
            int(_get_crc(sectors[22])),\
            int(_get_crc(sectors[23])),\
            int(_get_crc(sectors[24])),\
            int(_get_crc(sectors[25])),\
            int(_get_crc(sectors[26])),\
            int(_get_crc(sectors[27])),\
            int(_get_crc(sectors[28])),\
            int(_get_crc(sectors[29])),\
            int(_get_crc(sectors[30])),\
            int(_get_crc(sectors[31])))

        cur.execute(query)
        print cur.rowcount
        conn.commit()
    except Exception as e:
        print e
    cur.execute("SELECT * FROM crcs")
    rv = cur.fetchall()
    
    print "-----------------"
    print str(rv)
    #conn.close()

    time.sleep(1)
    #------------------------------------------------
    '''
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')
    '''
    #-----------We made it till sector wise---------------
    no_of_chunks = length_of_file/64
    crc_chunks_64 = {}
    for i in range (0,no_of_chunks):
        crc_chunks_64[i] =_get_crc(hexfile_payload[i*64:(i*64)+64])
        #print "i      :",i,"   crc: ",crc_datachunks_64[i]

    temp_byte_array = bytearray()
    for i in range(0,64):
        temp_byte_array.append(0xff)

    for i in range(no_of_chunks,2048):
        crc_chunks_64[i] =_get_crc(temp_byte_array)
    #print "No of 64 byte chunk : ", length_of_file/64
    '''
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')
    '''
    #----------We got chunck wise CRC also----------------
    try:
        k=0
        print "version no", version_no
        query = "SELECT * FROM crc_chunk_64 WHERE TYPE = '%s' AND Address =  '%d'" % ('FW_3P', version_no)
        cur.execute(query)
        if(cur.rowcount != 0):
            query = "DELETE FROM crc_chunk_64 WHERE Address = '%d'" % (version_no)
            cur.execute(query)
        print no_of_sectors,"hdskjhgdkj"
        for i in range(0,no_of_sectors):
            query = "DELETE FROM crc_chunk_64 WHERE Address = '%d'AND sector_no =  '%d' " % (version_no,i)
            cur.execute(query)
            query = '''INSERT INTO crc_chunk_64 (TYPE,Address,sector_no,\
            chnk_crc_00,chnk_crc_01,chnk_crc_02,chnk_crc_03,chnk_crc_04,chnk_crc_05,chnk_crc_06,chnk_crc_07,\
            chnk_crc_08,chnk_crc_09,chnk_crc_10,chnk_crc_11,chnk_crc_12,chnk_crc_13,chnk_crc_14,chnk_crc_15,\
            chnk_crc_16,chnk_crc_17,chnk_crc_18,chnk_crc_19,chnk_crc_20,chnk_crc_21,chnk_crc_22,chnk_crc_23,\
            chnk_crc_24,chnk_crc_25,chnk_crc_26,chnk_crc_27,chnk_crc_28,chnk_crc_29,chnk_crc_30,chnk_crc_31,\
            chnk_crc_32,chnk_crc_33,chnk_crc_34,chnk_crc_35,chnk_crc_36,chnk_crc_37,chnk_crc_38,chnk_crc_39,\
            chnk_crc_40,chnk_crc_41,chnk_crc_42,chnk_crc_43,chnk_crc_44,chnk_crc_45,chnk_crc_46,chnk_crc_47,\
            chnk_crc_48,chnk_crc_49,chnk_crc_50,chnk_crc_51,chnk_crc_52,chnk_crc_53,chnk_crc_54,chnk_crc_55,\
            chnk_crc_56,chnk_crc_57,chnk_crc_58,chnk_crc_59,chnk_crc_60,chnk_crc_61,chnk_crc_62,chnk_crc_63)\
             VALUES('%s','%d','%d',\
             '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
             '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
             '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d',\
             '%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d')'''%('FW_3P',version_no,i,\
                int(crc_chunks_64[((i*64)+0)]),int(crc_chunks_64[((i*64)+1)]),int(crc_chunks_64[((i*64)+2)]),int(crc_chunks_64[((i*64)+3)]),\
                    int(crc_chunks_64[((i*64)+4)]),int(crc_chunks_64[((i*64)+5)]),int(crc_chunks_64[((i*64)+6)]),int(crc_chunks_64[((i*64)+7)]),\
                        int(crc_chunks_64[((i*64)+8)]),int(crc_chunks_64[((i*64)+9)]),int(crc_chunks_64[((i*64)+10)]),int(crc_chunks_64[((i*64)+11)]),\
                            int(crc_chunks_64[((i*64)+12)]),int(crc_chunks_64[((i*64)+13)]),int(crc_chunks_64[((i*64)+14)]),int(crc_chunks_64[((i*64)+15)]),\
                                int(crc_chunks_64[((i*64)+16)]),int(crc_chunks_64[((i*64)+17)]),int(crc_chunks_64[((i*64)+18)]),int(crc_chunks_64[((i*64)+19)]),\
                                int(crc_chunks_64[((i*64)+20)]),int(crc_chunks_64[((i*64)+21)]),int(crc_chunks_64[((i*64)+22)]),int(crc_chunks_64[((i*64)+23)]),\
                                    int(crc_chunks_64[((i*64)+24)]),int(crc_chunks_64[((i*64)+25)]),int(crc_chunks_64[((i*64)+26)]),int(crc_chunks_64[((i*64)+27)]),\
                                    int(crc_chunks_64[((i*64)+28)]),int(crc_chunks_64[((i*64)+29)]),int(crc_chunks_64[((i*64)+30)]),int(crc_chunks_64[((i*64)+31)]),\
                                    int(crc_chunks_64[((i*64)+32)]),int(crc_chunks_64[((i*64)+33)]),int(crc_chunks_64[((i*64)+34)]),int(crc_chunks_64[((i*64)+35)]),\
                                    int(crc_chunks_64[((i*64)+36)]),int(crc_chunks_64[((i*64)+37)]),int(crc_chunks_64[((i*64)+38)]),int(crc_chunks_64[((i*64)+39)]),\
                                    int(crc_chunks_64[((i*64)+40)]),int(crc_chunks_64[((i*64)+41)]),int(crc_chunks_64[((i*64)+42)]),int(crc_chunks_64[((i*64)+43)]),\
                                    int(crc_chunks_64[((i*64)+44)]),int(crc_chunks_64[((i*64)+45)]),int(crc_chunks_64[((i*64)+46)]),int(crc_chunks_64[((i*64)+47)]),\
                                    int(crc_chunks_64[((i*64)+48)]),int(crc_chunks_64[((i*64)+49)]),int(crc_chunks_64[((i*64)+50)]),int(crc_chunks_64[((i*64)+51)]),\
                                    int(crc_chunks_64[((i*64)+52)]),int(crc_chunks_64[((i*64)+53)]),int(crc_chunks_64[((i*64)+54)]),int(crc_chunks_64[((i*64)+55)]),\
                                    int(crc_chunks_64[((i*64)+56)]),int(crc_chunks_64[((i*64)+57)]),int(crc_chunks_64[((i*64)+58)]),int(crc_chunks_64[((i*64)+59)]),\
                                    int(crc_chunks_64[((i*64)+60)]),int(crc_chunks_64[((i*64)+61)]),int(crc_chunks_64[((i*64)+62)]),int(crc_chunks_64[((i*64)+63)]) )
            cur.execute(query)
            conn.commit()

        #print cur.rowcount
        #conn.commit()
    except Exception as e:
        print e
    cur.execute("SELECT * FROM crc_chunk_64")
    rv = cur.fetchall()
    
    print "-----------------"
    #print crc_chunks_64
    #print str(rv)
    conn.close()
    






    
    #print network_api.three_ph_get_ext_flash_crc(Address("0.0.0.255"),4096,0x1000)
    #create_sector_wise_file("filename.bin",file_by_sector)


    print "Done."


if __name__ == '__main__': 
    run()
