"""
This table will do following tasks
1. reset meter
2. get meter live version 
3. update final table

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
                    UPDATE_RESULT_WAIT

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



def run(db, network_api, LOOP_NUMBER):


    result_object = resultData()
    db.display(RESET_AND_UPDATE_RESULT_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)

    db.display(RESET_AND_UPDATE_RESULT_STEP_NO, " ",status=SCRIPT_LOG_STATUS_IN_PROGRESS, script_logging = True)

    try:
        network_api.reset(Address("0.0.0.255"))
    except Exception as e:
        print e
        pass
    else:
        print "Done"


    time.sleep(UPDATE_RESULT_WAIT)

    for i in AddressList_1P:
       
        addr = str(AddressList_1P[i])
        meter_id = config.convert_address_to_int(addr)
        

        erase_status = FILL_STRING_ERROR
        entry_start_time_of_upgrade = datetime.datetime.now()
        entry_upgrade_status = FILL_STRING_ERROR



        try:
            erase_log_table_object = db.return_latest_entry(ERASE_LOG_TABLE_NAME, meter_id)
            health_log_table_object = db.return_latest_entry(HEALTH_LOG_TABLE_NAME, meter_id)
            heal_log_table_object = db.return_latest_entry(HEAL_LOG_TABLE_NAME, meter_id)
            
            erase_status            = erase_log_table_object.ERASE_STATUS
            entry_start_time_of_upgrade = erase_log_table_object.START_TIME
            healing_status          = heal_log_table_object.HEALING_STATUS



        except Exception as e:

            db.display(RESET_AND_UPDATE_RESULT_STEP_NO, str('Error in getting data from tables' + '\n'+ str(e)), meter_address = meter_id,status = LOG_TYPE_ERROR, logging = True)

        else:
            pass


        version = 0
        try:
            version = network_api.get_live_version(Address(addr))
        except Exception as e:
             db.display(RESET_AND_UPDATE_RESULT_STEP_NO, str('Error in getting live version' + '\n'+ str(e)), meter_address = meter_id,status = LOG_TYPE_ERROR, logging = True)
        else:
            db.display(RESET_AND_UPDATE_RESULT_STEP_NO, str("live version in meter " +str(addr)+ ' is '+ str(version)), meter_address = meter_id, logging = True)


        

        if erase_status == FILL_STRING_SUCCESS:
            if healing_status == FILL_STRING_SUCCESS:
                if int(version) == int(CONFIG_SESSION_NUMBER):
                	entry_upgrade_status = FILL_STRING_SUCCESS


        result_object.set_result_params(\
                                          CONFIG_SESSION_NUMBER,\
                                          meter_id,\
                                          version,\
                                          entry_upgrade_status,\
                                          LOOP_NUMBER,\
                                          entry_start_time_of_upgrade,\
                                          datetime.datetime.now())
        db.populate_result_data(result_object)

        db.display(RESET_AND_UPDATE_RESULT_STEP_NO, str('Added Entry in table ' + RESULT_TABLE_NAME),meter_address = meter_id, logging = True)

    db.display(RESET_AND_UPDATE_RESULT_STEP_NO," " ,status=SCRIPT_LOG_STATUS_COMPLETED, script_logging = True)