import time
import datetime
import json

import collections
import crc16
import re
import sys
import os
import gp_node.utils.serialize as serialize
from binascii import unhexlify, hexlify
from gp_node.utils.address import Address


import config

from config import  AddressList_1P



from config import  SQL_CONNECT_STRING              ,\
                    CONFIG_SESSION_NUMBER           ,\
                    HEAL_FLASH_START_ADDRESS

from config import  ERASE_FLASH_RETRY           ,\
                    HEALING_RETRY               ,\
                    HEALING_VALIDATION_RETRY    ,\
                    ERASE_FLASH_RETRY           ,\
                    SECTOR_READ_RETRY           ,\
                    BLOCK_READ_RETRY            


from config import  LOG_TYPE_NORMAL                 ,\
                    LOG_TYPE_ERROR                  ,\
                    LOG_DEFAULT_METER_ADDRESS       ,\
                    LOG_COMMENTS_RUN_EXECUTED       ,\
                    SCRIPT_LOG_STATUS_NOT_STARTED   ,\
                    SCRIPT_LOG_STATUS_IN_PROGRESS   ,\
                    SCRIPT_LOG_STATUS_COMPLETED     ,\
                    SCRIPT_LOG_METER_ISSUE          ,\
                    SCRIPT_LOG_STATUS_DONE

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
                    RESET_AND_UPDATE_RESULT_STEP_NO,\
                    SCRIPT_LOG_BROADCAST_ADDRESS


from config import  FILL_STRING_SUCCESS,\
                    FILL_STRING_ERROR,\
                    FILL_STRING_NOT_STARTED,\
                    FILL_STRING_NO_BAD_CHUNK,\
                    FILL_STRING_BLACKLIST

from config import BROADCAST_FLASH_START_ADDRESS

from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

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

def _parse_crc(meter_crc_string):
    __meter_crc_string = str(meter_crc_string)
    arg = __meter_crc_string.split("\n")
    ___crc = []
    try:
        for line_number in range(0,32):
            ___crc.append((arg[line_number].split(": ")[1]))
    except Exception as e:
        print e
    #values = int(___bundle_3p[17])
    #print "recieved Tamper Flag:", ___crc
    return ___crc


def chunkwise_crc_calculator(meter_id,addr, network_api,db, bad_sectors_array):




    chunk_read_status = FILL_STRING_NOT_STARTED
    total_chunks_retries_observed = 0
    time_diff = 0


    result_dict = {'Status':chunk_read_status,\
                    'Retry':total_chunks_retries_observed,\
                    'Time Taken':time_diff,\
                    'Chunks':''}

    meter_sectors_crc_dict = {}
        

    then = time.time()

    for q in range(0,len(bad_sectors_array)):

        i = int(bad_sectors_array[q])

        db.display(UPDATE_HEALTH_STEP_NO, str("Sector Number for chunk CRC calculator :  " + str(i)), meter_address = meter_id)

        #crc_chnk_mter = []
        temp_dict = {}

        for k in range(0,2):

            retry_counts_chunks = BLOCK_READ_RETRY

            while(retry_counts_chunks):
                retry_counts_chunks = retry_counts_chunks - 1
                total_chunks_retries_observed = total_chunks_retries_observed + 1
                try:
                    temp_crc_string =  network_api.three_ph_get_crc_bundle(Address(addr),(HEAL_FLASH_START_ADDRESS+(i*4096)+(k*2048)),64)
                except Exception as e:
                       
                    temp_str =  "Error in meter " + str(meter_id) + " in getting crc of chunks"

                    db.display(UPDATE_HEALTH_STEP_NO, str(temp_str+'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = retry_counts_chunks, logging = True)                      

                    del(temp_str)
                    chunk_read_status = FILL_STRING_ERROR
                    
                else:
                    chunk_read_status = FILL_STRING_SUCCESS
                    retry_counts_chunks = 0                    
                    #crc_chnk_mter += _parse_crc(temp_crc_string)
                    temp_dict = _parse_crc(temp_crc_string)

                    for z in range(0,len(temp_dict)):
                        meter_sectors_crc_dict[z + (i*64) + (k*32) ] = temp_dict[z]
                        #print int(z + (i*64) + (k*32) )                        
                    del(temp_dict)

    #print meter_sectors_crc_dict\

    temp_str_chunks_json = json.dumps(meter_sectors_crc_dict)
    now = time.time()
    time_diff = float(now - then)

    result_dict = {'Status':chunk_read_status,\
                    'Retry':total_chunks_retries_observed,\
                    'Time Taken':time_diff,\
                    'Chunks':temp_str_chunks_json}


    if chunk_read_status == FILL_STRING_SUCCESS:
        temp_str =  "Successfully got chunks CRCs for meter " + str(meter_id) + " in total tries of : " + str(total_chunks_retries_observed)
        
        db.display(UPDATE_HEALTH_STEP_NO, temp_str, meter_address = meter_id, logging = True)
        del(temp_str)


    return result_dict






def run(db, network_api, meter_address_index):



    health_log_object = healthLogData()

    db.display(UPDATE_HEALTH_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)

    db.display(UPDATE_HEALTH_STEP_NO, " ", status=SCRIPT_LOG_STATUS_IN_PROGRESS, script_logging = True)



    firmware_sectors_crc_dict = {}
    firmware_chunks_crc_dict = {}


    firmware_sectors_json = db.get_firmware_sectorwise_crc()
    firmware_chunks_json = db.get_firmware_blockwise_crc()        

    firmware_sectors_crc_dict = json.loads(firmware_sectors_json)
    firmware_chunks_crc_dict = json.loads(firmware_chunks_json)

    i = meter_address_index


    while i < len(AddressList_1P):

        addr = str(AddressList_1P[i])                      
        meter_id = config.convert_address_to_int(addr)

        #####################  Check meter in blacklist ##############################
        if db.check_meter_in_blacklist(meter_id, UPDATE_HEALTH_STEP_NO) == True:

            
            health_log_object.set_health_log_params(\
                                                    meter_id,\
                                                    FILL_STRING_BLACKLIST,\
                                                    0,\
                                                    0.0,\
                                                    FILL_STRING_BLACKLIST,\
                                                    0,\
                                                    0.0,\
                                                    FILL_STRING_BLACKLIST,\
                                                    FILL_STRING_BLACKLIST)

            db.populate_health_log_data(health_log_object)

            db.display(UPDATE_HEALTH_STEP_NO, str("Entry added - Meter found in blacklist"), meter_address = meter_id,status = LOG_TYPE_ERROR, logging = True)
            
            db.display(UPDATE_HEALTH_STEP_NO, SCRIPT_LOG_METER_ISSUE ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_DONE, script_logging = True)


        else:   
        ##############################################################################


            total_sector_retries_observed = 0
            sector_read_status = FILL_STRING_NOT_STARTED
            then = time.time()

            meter_crc_string = ""
            retry_counts_sectors = SECTOR_READ_RETRY
        

            while(retry_counts_sectors):
                retry_counts_sectors = retry_counts_sectors - 1
                total_sector_retries_observed = total_sector_retries_observed + 1

                try:
                    meter_crc_string =  network_api.three_ph_get_crc_bundle(Address(addr),HEAL_FLASH_START_ADDRESS,4096)
                except Exception as e:                   
                               
                    
                    db.display(UPDATE_HEALTH_STEP_NO, str("Error in meter, in getting crc of sectors"+'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = retry_counts_sectors, logging = True)               

                    
                    sector_read_status = FILL_STRING_ERROR
                else:
                    sector_read_status = FILL_STRING_SUCCESS
                    retry_counts_sectors = 0
                    now = time.time()
                    time_diff = float(now - then)

                    meter_sectors_crc_dict =  _parse_crc(meter_crc_string)

                    temp_count = 0
                    bad_sectors_array = bytearray()
                    meter_bad_sectors_dict = {}


                    for q in range(0,32):

                        db.display(UPDATE_HEALTH_STEP_NO,  str("Sector " + str(q) + " CRCs : " + str(firmware_sectors_crc_dict[str(q)]) + "  " +  str(meter_sectors_crc_dict[q]))\
                                ,meter_address = meter_id, retry = retry_counts_sectors) 

                        
                        
                       
                        
                        if int(firmware_sectors_crc_dict[str(q)]) != int(meter_sectors_crc_dict[q]):
                            bad_sectors_array.append(q)
                            meter_bad_sectors_dict[temp_count] = int(q)
                            temp_count = temp_count + 1
                    del(temp_count)

                    bad_sectors_json = json.dumps(meter_bad_sectors_dict)

                   

                    temp_str = "Sectorwise CRC received for meter : " + str(addr) + ", " + str(len(bad_sectors_array)) +" bad sectors observed"                
                    
                    db.display(UPDATE_HEALTH_STEP_NO, temp_str\
                                ,meter_address = meter_id, retry = retry_counts_sectors, logging = True) 

                    del(temp_str)

                    if len(bad_sectors_array) != 0:
                        result_dict = chunkwise_crc_calculator(meter_id, addr, network_api,db, bad_sectors_array)
                    

    ############################# Adding entry in database ########################################                 
                    heal_advisor_str = "Healing required"

                    if len(bad_sectors_array) != 0:
                        heal_advisor_str = "Healing required"

                        health_log_object.set_health_log_params(\
                                                                meter_id,\
                                                                sector_read_status,\
                                                                total_sector_retries_observed,\
                                                                time_diff,\
                                                                result_dict['Status'],\
                                                                result_dict['Retry'],\
                                                                result_dict['Time Taken'],\
                                                                bad_sectors_json,\
                                                                result_dict['Chunks'])

                        db.populate_health_log_data(health_log_object)
                        db.display(UPDATE_HEALTH_STEP_NO, str("health is updated in database for meter " + str(addr) + "and healing required")\
                                ,meter_address = meter_id, retry = retry_counts_sectors, logging = True) 

                        db.display(UPDATE_HEALTH_STEP_NO, heal_advisor_str ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_DONE, script_logging = True)
                        
                    else:
                        heal_advisor_str = "Healing not required"

                        health_log_object.set_health_log_params(\
                                                                meter_id,\
                                                                sector_read_status,\
                                                                total_sector_retries_observed,\
                                                                time_diff,\
                                                                FILL_STRING_SUCCESS,\
                                                                0,\
                                                                0.0,\
                                                                bad_sectors_json,\
                                                                FILL_STRING_NO_BAD_CHUNK)

                        db.populate_health_log_data(health_log_object)

                        db.display(UPDATE_HEALTH_STEP_NO, str("health is updated in database for meter " + str(addr) + "and no exception found")\
                                ,meter_address = meter_id, retry = retry_counts_sectors, logging = True) 

                        db.display(UPDATE_HEALTH_STEP_NO, heal_advisor_str ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_DONE, script_logging = True)
                        

                

################################################################################################


        i = i + 1

    db.display(UPDATE_HEALTH_STEP_NO, " " ,status=SCRIPT_LOG_STATUS_COMPLETED, script_logging = True)

