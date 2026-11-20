"""
Adds meta data to TI-TXT file
"""
import time
import datetime
import serial

import argparse
import collections
import crc16
import re
import sys
import os


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
                    SCRIPT_LOG_BROADCAST_ADDRESS

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
                    


from config import  FILL_STRING_SUCCESS,\
                    FILL_STRING_ERROR,\
                    FILL_STRING_NOT_STARTED,\
                    FILL_STRING_NO_BAD_CHUNK

from config import  RESULT_TABLE_NAME,\
                    STATUS_TABLE_NAME,\
                    ERASE_LOG_TABLE_NAME,\
                    HEALTH_LOG_TABLE_NAME,\
                    HEAL_LOG_TABLE_NAME,\
                    LOG_TABLE_NAME,\
                    SCRIPT_LOG_TABLE_NAME

from config import BROADCAST_FLASH_START_ADDRESS

from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

from gp_node.utils.address import Address



def run(db, network_api, loop_no):
    

    status_object = statusData()

    db.display(UPDATE_STATUS_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)



    for i in AddressList_1P:
       
        addr = str(AddressList_1P[i])
        meter_id = config.convert_address_to_int(addr)

        #--------------------------------- Check meter in blacklist ---------------------------------#
        if db.check_meter_in_blacklist(meter_id, UPDATE_STATUS_STEP_NO) == True:

            db.display(UPDATE_STATUS_STEP_NO, 'Status cannot update - Meter Found in blacklist',\
            status = LOG_TYPE_ERROR,upper_space = 2, lower_space = 2, logging = True) 

        else:

        #------------------------------------------------------------------------------------------#
            session_number = CONFIG_SESSION_NUMBER      
            meter_address = meter_id                        
            erase_status = FILL_STRING_NOT_STARTED      
            erase_time_taken = 0.0 
            erase_total_retry = 0  
            sector_read_status = FILL_STRING_NOT_STARTED
            bad_sectors = FILL_STRING_NOT_STARTED        
            total_sector_retry = 0
            sectors_reading_time = 0.0
            chunk_read_status = FILL_STRING_NOT_STARTED   
            bad_chunk_percent = 0.0  
            bad_chunk_count = 0     
            bad_chunks = FILL_STRING_NOT_STARTED         
            total_chunk_retry = 0  
            chunk_reading_time = 0.0 
            healing_status = FILL_STRING_NOT_STARTED    
            total_healing_time = 0.0
            total_healing_retry = 0

            erase_log_table_object = db.return_latest_entry(ERASE_LOG_TABLE_NAME, meter_id)
            health_log_table_object = db.return_latest_entry(HEALTH_LOG_TABLE_NAME, meter_id)

            erase_status            = erase_log_table_object.ERASE_STATUS
            erase_time_taken        = erase_log_table_object.EXECUTION_TIME
            erase_total_retry       = erase_log_table_object.TOTAL_RETRY
            sector_read_status      = health_log_table_object.SECTOR_READ_STATUS
            bad_sectors             = health_log_table_object.BAD_SECTORS_JSON 
            total_sector_retry      = health_log_table_object.TOTAL_SECTOR_READ_RETRY
            sectors_reading_time    = health_log_table_object.SECTORS_READING_TIME 
            chunk_read_status       = health_log_table_object.CHUNK_READ_STATUS            
            total_chunk_retry       = health_log_table_object.TOTAL_CHUNK_RETRY
            chunk_reading_time      = health_log_table_object.CHUNK_READING_TIME

            try:

                heal_log_table_object = db.return_latest_entry(HEAL_LOG_TABLE_NAME, meter_id)
                

                bad_chunk_percent       = heal_log_table_object.BAD_CHUNK_PERCENT
                bad_chunk_count         = heal_log_table_object.BAD_CHUNK_COUNT
                bad_chunks              = heal_log_table_object.BAD_CHUNKS
                healing_status          = heal_log_table_object.HEALING_STATUS
                total_healing_time      = heal_log_table_object.TOTAL_HEALING_TIME
                total_healing_retry     = heal_log_table_object.TOTAL_HEALING_RETRY


            except Exception as e:
                db.display(UPDATE_STATUS_STEP_NO, str("Healing not done, filling default values for some entries - "+'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, logging = True)

            else:
                db.display(UPDATE_STATUS_STEP_NO, "All values successfully received",\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, logging = True)
            status_object.set_status_params(\
                                            CONFIG_SESSION_NUMBER,\
                                            1,\
                                            meter_id,\
                                            loop_no,\
                                            erase_status         ,\
                                            erase_time_taken     ,\
                                            erase_total_retry    ,\
                                            sector_read_status   ,\
                                            bad_sectors          ,\
                                            total_sector_retry   ,\
                                            sectors_reading_time ,\
                                            chunk_read_status    ,\
                                            bad_chunk_percent    ,\
                                            bad_chunk_count      ,\
                                            bad_chunks           ,\
                                            total_chunk_retry    ,\
                                            chunk_reading_time   ,\
                                            healing_status       ,\
                                            total_healing_time   ,\
                                            total_healing_retry  ) 

            db.populate_status_data(status_object)
            db.display(UPDATE_STATUS_STEP_NO, 'Status updated',\
            upper_space = 2, lower_space = 2, logging = True)    


