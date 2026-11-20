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
                    HEAL_FLASH_START_ADDRESS        ,\
                    EMPTY_CHUNK_VALUE               ,\
                    SCRIPT_LOG_BROADCAST_ADDRESS    ,\
                    HEALING_DELAY_BETWEEN_PACKETS   ,\
                    BROADCAST_FLASH_START_ADDRESS


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
                    RESET_AND_UPDATE_RESULT_STEP_NO




from config import  FILL_STRING_SUCCESS             ,\
                    FILL_STRING_ERROR               ,\
                    FILL_STRING_NOT_STARTED         ,\
                    FILL_STRING_BLACKLIST


from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

from gp_node.utils.address import Address

from config import THRESHOLD_FOR_BURN_NACK          ,\
                   HEAL_FLASH_START_ADDRESS
                   



def start_address_cal(current_sector_fw, block_no):
    start_address = 4096*current_sector_fw + 64*block_no
    return start_address


def _parse_crc(crc_string):
    __crc_string = str(crc_string)
    arg = __crc_string.split("\n")
    ___crc = []
    try:
        for line_number in range(0,32):
            ___crc.append((arg[line_number].split(": ")[1]))
    except Exception as e:
        print e
    #values = int(___bundle_3p[17])
    #print "recieved Tamper Flag:", ___crc
    return ___crc



def run(db, network_api, meter_address_index, bin_file, loop_no):


    health_log_object = healthLogData()
    heal_log_object = healLogData()

    db.display(HEAL_BY_CHUNK_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)

    
    ########################## reading hex file ####################################################   
    binary_file = open(bin_file, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    length_of_file = len(hexfile_payload)


    while(length_of_file%64):
        hexfile_payload.append(0x00)
        length_of_file = len(hexfile_payload)


    db.display(HEAL_BY_CHUNK_STEP_NO, str("Bin file reading success, Length of file  = " + str(length_of_file)), logging = True)

    ###################################################################################################  

    # For all meter addresses present in address list 
    i = meter_address_index

    while i < len(AddressList_1P):       

        
        addr = str(AddressList_1P[i])
        meter_id = config.convert_address_to_int(addr)


        db.display(HEAL_BY_CHUNK_STEP_NO, " ",meter_address = meter_id, status=SCRIPT_LOG_STATUS_IN_PROGRESS, script_logging = True)

        #####################  Check meter in blacklist ##############################
        if db.check_meter_in_blacklist(meter_id, HEAL_BY_CHUNK_STEP_NO) == True:
            
            heal_log_object.set_heal_log_params(\
                                                    meter_id,\
                                                    loop_no,\
                                                    FILL_STRING_BLACKLIST,\
                                                    datetime.datetime.now(),\
                                                    0.0,\
                                                    0,\
                                                    1,\
                                                    0.0,\
                                                    0,\
                                                    FILL_STRING_BLACKLIST)
            db.populate_heal_data(heal_log_object)

            db.display(HEAL_BY_CHUNK_STEP_NO, SCRIPT_LOG_METER_ISSUE,meter_address = meter_id, status=SCRIPT_LOG_STATUS_DONE, script_logging = True)

        else:
        ###############################################################################

            ############ for database ################
            date_and_time = datetime.datetime.now()
            then = time.time()
            heal_status = FILL_STRING_NOT_STARTED 
            total_healing_retries_observed = 0
            temp_string = ""
            bad_block_total_count = 0        
            ############ for database ################


            meter_health_status = db.get_meter_health(meter_id) # Checking if meter requires healing or not            
            if meter_health_status == 'Good':

                db.display(HEAL_BY_CHUNK_STEP_NO,"meter is already repaired, no healing required" ,meter_address = meter_id, logging = True)
                
                db.display(HEAL_BY_CHUNK_STEP_NO, "Meter already repaired, healing skipped",meter_address = meter_id, status=SCRIPT_LOG_STATUS_DONE, script_logging = True)

            else:

                ############################### Getting chunkwise health from database #################### 

                meter_chunkwise_health_json = db.get_meter_chunkwise_health(meter_id)
                firmware_chunkwise_health_json = db.get_firmware_blockwise_crc()

                meter_chunkwise_health_dict = json.loads(meter_chunkwise_health_json)
                firmware_chunkwise_health_dict = json.loads(firmware_chunkwise_health_json)

                address_of_corrupt_chunks_dict = {}

                chunks_transfered_correctly = 0
                chunks_partially_written = 0 
                bad_chunks = 0
                temp_count = 0

                db.display(HEAL_BY_CHUNK_STEP_NO,"Now healing.... " ,meter_address = meter_id, logging = True)

                for key in meter_chunkwise_health_dict.keys():
                    
                    if int(meter_chunkwise_health_dict[key]) == int(firmware_chunkwise_health_dict[key]):                
                        chunks_transfered_correctly = chunks_transfered_correctly + 1        

                    elif int(meter_chunkwise_health_dict[key]) != EMPTY_CHUNK_VALUE:
                        chunks_partially_written = chunks_partially_written + 1

                    elif int(meter_chunkwise_health_dict[key]) == EMPTY_CHUNK_VALUE:
                        bad_chunks = bad_chunks + 1
                        address_of_corrupt_chunks_dict[temp_count] = int(key)
                        temp_count = temp_count + 1
                del(temp_count)

                db.display(HEAL_BY_CHUNK_STEP_NO,str("chunks_transfered_correctly " + str(chunks_transfered_correctly)),meter_address = meter_id, logging = True)
                db.display(HEAL_BY_CHUNK_STEP_NO,str("chunks_partially_written " + str(chunks_partially_written)),meter_address = meter_id, logging = True)
                db.display(HEAL_BY_CHUNK_STEP_NO,str("bad_chunks " + str(bad_chunks)),meter_address = meter_id, logging = True)



                percentage = 0.0
                percentage = 100.0*((bad_chunks*64.0)/(len(hexfile_payload)))

                db.display(HEAL_BY_CHUNK_STEP_NO,str("Error percentage is : " + str(percentage)),meter_address = meter_id, logging = True)
                
                time.sleep(5)           

                ##########################################################################################



                ################################ Now healing current meter ##############################################
                for q in range(0,len(address_of_corrupt_chunks_dict)):

                    current_heal_payload = bytearray()
                    address_to_read_in_hexfile = int(address_of_corrupt_chunks_dict[q])*64             
                    address_to_write_in_flash = HEAL_FLASH_START_ADDRESS + int(address_of_corrupt_chunks_dict[q])*64
                    
                    for z in range(0, 64):
                        current_heal_payload.append(hexfile_payload[address_to_read_in_hexfile+z])  
                    
                    retry_counts_heal = HEALING_RETRY
                    while(retry_counts_heal): 
                        retry_counts_heal = retry_counts_heal - 1
                        total_healing_retries_observed = total_healing_retries_observed + 1  

                        db.display(HEAL_BY_CHUNK_STEP_NO,str("Repairing chunk starting at flash address : " + str(address_to_write_in_flash)),retry = retry_counts_heal, meter_address = meter_id)     
                        
                        try:
                            if percentage <= THRESHOLD_FOR_BURN_NACK:
                                print network_api.my_flash_io_master.write(Address(addr), address_to_write_in_flash , current_heal_payload)
                                time.sleep(HEALING_DELAY_BETWEEN_PACKETS)
                            else:
                                network_api.my_flash_io_master.burn_nack(Address(addr), address_to_write_in_flash, current_heal_payload, to_print=True)
                        except Exception as e:

                            db.display(HEAL_BY_CHUNK_STEP_NO, str("Error in writing" +'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = retry_counts_heal, logging = True)
                            
                            heal_status = FILL_STRING_ERROR 

                        else:
                            retry_counts_heal = 0
                            heal_status = FILL_STRING_SUCCESS
                    if heal_status == FILL_STRING_ERROR:

                        db.display(HEAL_BY_CHUNK_STEP_NO, str(FILL_STRING_ERROR + "\n\n\nError occured while healing at address : " + str(address_to_write_in_flash) + " for meter : " + str(addr)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = retry_counts_heal, logging = True)                        
                    
                        break
                #########################################################################################################

                now = time.time()
                time_diff = float(now - then)
                bad_chunks_json = json.dumps(address_of_corrupt_chunks_dict)

                ################################## Adding entry in database #############################################
                heal_log_object.set_heal_log_params(\
                                                        meter_id,\
                                                        loop_no,\
                                                        heal_status,\
                                                        date_and_time,\
                                                        time_diff,\
                                                        total_healing_retries_observed,\
                                                        1,\
                                                        percentage,\
                                                        bad_chunks,\
                                                        bad_chunks_json)
                db.populate_heal_data(heal_log_object)
                
                db.display(HEAL_BY_CHUNK_STEP_NO, "Meter repaired, healing done",meter_address = meter_id, status=SCRIPT_LOG_STATUS_DONE, script_logging = True)

                #########################################################################################################            
                

        i = i + 1
    db.display(HEAL_BY_CHUNK_STEP_NO, " ", status=SCRIPT_LOG_STATUS_COMPLETED, script_logging = True)
