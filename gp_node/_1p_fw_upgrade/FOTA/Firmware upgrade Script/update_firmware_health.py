#!/home/pi/Envs/bin/python
"""
Adds meta data to TI-TXT file
"""
import time
import datetime
import json

from config import  SQL_CONNECT_STRING              ,\
                    CONFIG_SESSION_NUMBER


from config import  LOG_TYPE_NORMAL                 ,\
                    LOG_TYPE_ERROR                  ,\
                    LOG_DEFAULT_METER_ADDRESS       ,\
                    LOG_COMMENTS_RUN_EXECUTED       ,\
                    SCRIPT_LOG_STATUS_NOT_STARTED   ,\
                    SCRIPT_LOG_STATUS_IN_PROGRESS   ,\
                    SCRIPT_LOG_STATUS_COMPLETED

from config import  RUN_STEP_NO                    ,\
                    DATABASE_VALIDATION_STEP_NO    ,\
                    DATABASE_HANDLER_STEP_NO       ,\
                    ORM_MODEL_STEP_NO              ,\
                    ORM_OBJECTS_STEP_NO            ,\
                    UPDATE_FIRMWARE_HEALTH_STEP_NO ,\
                    ERASE_FLASH_STEP_NO            ,\
                    BROADCAST_STEP_NO              ,\
                    UPDATE_HEALTH_STEP_NO          ,\
                    HEAL_BY_CHUNK_STEP_NO          ,\
                    UPDATE_STATUS_STEP_NO          ,\
                    RESET_AND_UPDATE_RESULT_STEP_NO

from config import  FILL_STRING_SUCCESS,\
                    FILL_STRING_ERROR,\
                    FILL_STRING_NOT_STARTED



from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData



import collections
import crc16
import re
import sys
import os
import gp_node.utils.serialize as serialize
from binascii import unhexlify, hexlify
from gp_node.utils.address import Address



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


       


def run(db, bin_file):



    health_log_object = healthLogData()

    db.display(UPDATE_FIRMWARE_HEALTH_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)
    db.display(UPDATE_FIRMWARE_HEALTH_STEP_NO, " ", status=SCRIPT_LOG_STATUS_IN_PROGRESS, script_logging = True)


    binary_file = open(bin_file, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    length_of_file = len(hexfile_payload)


    while(length_of_file%64):
        hexfile_payload.append(0x00)
        length_of_file = len(hexfile_payload)


    db.display(UPDATE_FIRMWARE_HEALTH_STEP_NO, str("Bin file reading success, Length of file  = " + str(length_of_file)), logging = True)

    no_of_sectors = length_of_file/4096
    no_of_bytes_in_last_sector = length_of_file%4096
 
    temp_string = 'Binary file data, Sectors -' + str(no_of_sectors) + ' , Length - ' + str(len(hexfile_payload))

    db.display(UPDATE_FIRMWARE_HEALTH_STEP_NO, temp_string, logging = True)

    del temp_string
    sectors = {}

    for i in range(0,no_of_sectors):
        sectors[i] = hexfile_payload[(i*4096) : ((i*4096)+4096)]

    #print "No of Sectors:", no_of_sectors
    if(no_of_bytes_in_last_sector):
        
        temp = no_of_sectors - 1
        sectors[no_of_sectors] = hexfile_payload[(no_of_sectors*4096) : ]
        #print len(sectors[no_of_sectors])
        no_of_sectors = no_of_sectors + 1
        #print "No of Sectors:", no_of_sectors
        cnt = 0
        while(no_of_bytes_in_last_sector != 4096):
            no_of_bytes_in_last_sector += 1
            temp = no_of_sectors - 1
            #print "temp", temp
            sectors[temp].append(0xff)
            cnt = cnt + 1

    # print "No of 64 byte chunk : ", length_of_file/64
    # print "Count",cnt

    for i in range(0,no_of_sectors):
        crc = _get_crc(sectors[i])
        #print "Sector ",i," CRC: ", crc


    version_no = deserialize_uint16(sectors[0][4:6])
    

    temp_dict = {}
    for x in range(0,32):
        temp_dict[x] = int(_get_crc(sectors[x]))      
    temp_str_sectors = json.dumps(temp_dict)



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

    temp_str_chunks = json.dumps(crc_chunks_64)



############################# Adding entry in database ########################################    
    
    health_log_object.set_health_log_params(\
                                            LOG_DEFAULT_METER_ADDRESS,\
                                            FILL_STRING_SUCCESS,\
                                            1,\
                                            1.0,\
                                            FILL_STRING_SUCCESS,\
                                            1,\
                                            1.0,\
                                            temp_str_sectors,\
                                            temp_str_chunks)

    db.populate_health_log_data(health_log_object)

    db.display(UPDATE_FIRMWARE_HEALTH_STEP_NO, "Firmware health is added in database", logging = True)
    db.display(UPDATE_FIRMWARE_HEALTH_STEP_NO, " ", status=SCRIPT_LOG_STATUS_COMPLETED, script_logging = True)

################################################################################################

