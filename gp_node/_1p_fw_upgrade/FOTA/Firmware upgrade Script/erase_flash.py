import time
import datetime
import json

import config

from config import  SQL_CONNECT_STRING              ,\
                    CONFIG_SESSION_NUMBER

from config import  LOG_TYPE_NORMAL                 ,\
                    LOG_TYPE_ERROR                  ,\
                    LOG_DEFAULT_METER_ADDRESS       ,\
                    LOG_COMMENTS_RUN_EXECUTED       ,\
                    SCRIPT_LOG_STATUS_NOT_STARTED   ,\
                    SCRIPT_LOG_STATUS_IN_PROGRESS   ,\
                    SCRIPT_LOG_STATUS_COMPLETED     ,\
                    SCRIPT_LOG_METER_ISSUE,\
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

from config import  ERASE_LOG_TABLE_NAME

from config import  FILL_STRING_SUCCESS,\
                    FILL_STRING_ERROR,\
                    FILL_STRING_NOT_STARTED,\
                    FILL_STRING_NO_BAD_CHUNK,\
                    FILL_STRING_BLACKLIST

from config import  ERASE_FLASH_RETRY

from config import  AddressList_1P
                    

from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

from gp_node.utils.address import Address



def erase_flash(flash_io, db, meter_address_index):



    erase_log_object = eraseLogData()

    db.display(ERASE_FLASH_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)

    i = meter_address_index

    while i < len(AddressList_1P):
        """
        These flags are used for database purpose
        """
        addr = str(AddressList_1P[i])
        meter_id = config.convert_address_to_int(addr)
        erase_status_flag = FILL_STRING_NOT_STARTED        # Giving default values to before starting erase
        erase_block0_flag = FILL_STRING_NOT_STARTED
        erase_block1_flag = FILL_STRING_NOT_STARTED
        erase_sector32_flag = FILL_STRING_NOT_STARTED
        erase_total_retry = 0
        block0_retry = 0
        block1_retry = 0
        sector32_retry = 0
        diff = 0.0

        db.display(ERASE_FLASH_STEP_NO, " ",meter_address = meter_id, status=SCRIPT_LOG_STATUS_IN_PROGRESS, script_logging = True)


        #--------------------------------- Check meter in blacklist ---------------------------------#
        if db.check_meter_in_blacklist(meter_id, ERASE_FLASH_STEP_NO) == True:

            erase_status_flag = FILL_STRING_BLACKLIST       # Parameters for blacklisted meter
            erase_block0_flag = FILL_STRING_BLACKLIST
            erase_block1_flag = FILL_STRING_BLACKLIST
            erase_sector32_flag = FILL_STRING_BLACKLIST
            erase_total_retry = 0
            block0_retry = 0
            block1_retry = 0
            sector32_retry = 0
            diff = 0.0
            erase_log_object.set_erase_log_params(\
                                                    meter_id,\
                                                    erase_status_flag,\
                                                    erase_total_retry,\
                                                    erase_block0_flag,\
                                                    block0_retry,\
                                                    erase_block1_flag,\
                                                    block1_retry,\
                                                    erase_sector32_flag,\
                                                    sector32_retry,\
                                                    datetime.datetime.now(),\
                                                    diff)
            db.populate_erase_log_data(erase_log_object)

            db.display(ERASE_FLASH_STEP_NO, str('Entry added - Meter Blacklisted' + ERASE_LOG_TABLE_NAME), meter_address = meter_id,status = LOG_TYPE_ERROR, logging = True)
            
            db.display(ERASE_FLASH_STEP_NO, SCRIPT_LOG_METER_ISSUE ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_DONE, script_logging = True)

        else:

        #------------------------------------------------------------------------------------------#
        
            start_time = datetime.datetime.now()
            then = time.time()


            current_retry_count = ERASE_FLASH_RETRY
            while(current_retry_count):                         # Loop to erase block 1  

                current_retry_count = current_retry_count - 1
                erase_total_retry = erase_total_retry + 1
                try:
                    flash_io.erase(Address(addr), 0)
                except Exception as e:
                    
                    db.display(ERASE_FLASH_STEP_NO, str("block-0 error, while erasing"+'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = current_retry_count, logging = True)

                    
                    erase_block0_flag = FILL_STRING_ERROR
                    block0_retry = ERASE_FLASH_RETRY - current_retry_count

                else:
                    db.display(ERASE_FLASH_STEP_NO, "Block 0 erased",meter_address = meter_id, logging = True)

                    erase_block0_flag = FILL_STRING_SUCCESS
                    block0_retry = ERASE_FLASH_RETRY - current_retry_count
                    current_retry_count = 0
                    
            current_retry_count = ERASE_FLASH_RETRY
            
            
            while(current_retry_count):                         # Loop to erase block 2
                current_retry_count = current_retry_count - 1
                erase_total_retry = erase_total_retry + 1
                try:
                    flash_io.erase(Address(addr), 1)
                except Exception as e:

                    db.display(ERASE_FLASH_STEP_NO, str("block-1 error, while erasing"+'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = current_retry_count, logging = True)

                    erase_block1_flag = FILL_STRING_ERROR
                    block1_retry = ERASE_FLASH_RETRY - current_retry_count

                else:
                    erase_block1_flag = FILL_STRING_SUCCESS
                    block1_retry = ERASE_FLASH_RETRY - current_retry_count
                    current_retry_count = 0

                    db.display(ERASE_FLASH_STEP_NO, "Block 1 erased",meter_address = meter_id, logging = True)

            current_retry_count = ERASE_FLASH_RETRY        
            
            
            while(current_retry_count):                         # Loop to sector 32
                current_retry_count = current_retry_count - 1
                erase_total_retry = erase_total_retry + 1
                try:
                    flash_io.erase(Address(addr), int(32),sector_erase = True)
                except Exception as e:

                    db.display(ERASE_FLASH_STEP_NO, str("Sector - 32 error, while erasing"+'\n'+ str(e)),\
                                status = LOG_TYPE_ERROR,meter_address = meter_id, retry = current_retry_count, logging = True)

                    erase_sector32_flag = FILL_STRING_ERROR
                    sector32_retry = ERASE_FLASH_RETRY - current_retry_count  

                  
                else:
                    erase_sector32_flag = FILL_STRING_SUCCESS
                    sector32_retry = ERASE_FLASH_RETRY - current_retry_count 
                    current_retry_count = 0
                    db.display(ERASE_FLASH_STEP_NO, 'Sector-32 erased',meter_address = meter_id, logging = True)
            
            end_time = datetime.datetime.now()
            now = time.time()
            diff = float(now - then)


            if erase_block0_flag == FILL_STRING_SUCCESS:
                if erase_block1_flag ==FILL_STRING_SUCCESS:
                    if erase_sector32_flag == FILL_STRING_SUCCESS:
                        erase_status_flag = FILL_STRING_SUCCESS
            



            erase_log_object.set_erase_log_params(\
                                                    meter_id,\
                                                    erase_status_flag,\
                                                    erase_total_retry,\
                                                    erase_block0_flag,\
                                                    block0_retry,\
                                                    erase_block1_flag,\
                                                    block1_retry,\
                                                    erase_sector32_flag,\
                                                    sector32_retry,\
                                                    datetime.datetime.now(),\
                                                    diff)
            db.populate_erase_log_data(erase_log_object)


            if erase_status_flag == FILL_STRING_SUCCESS:

                db.display(ERASE_FLASH_STEP_NO, str('Added Entry in table ' + ERASE_LOG_TABLE_NAME),meter_address = meter_id, logging = True)

                db.display(ERASE_FLASH_STEP_NO, str('Added Entry in table ' + ERASE_LOG_TABLE_NAME) ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_DONE, script_logging = True)

            else:

                db.add_meter_to_blacklist(meter_id, ERASE_FLASH_STEP_NO)

                db.display(ERASE_FLASH_STEP_NO, str('Entry added - Unable to erase flash for this meter' + ERASE_LOG_TABLE_NAME), status = LOG_TYPE_ERROR,meter_address = meter_id, logging = True)

                db.display(ERASE_FLASH_STEP_NO, SCRIPT_LOG_METER_ISSUE ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_DONE, script_logging = True)



        i = i + 1
    db.display(ERASE_FLASH_STEP_NO, " " ,meter_address = meter_id,status=SCRIPT_LOG_STATUS_COMPLETED, script_logging = True)




def run(db, network_api, meter_address_index):

    erase_flash(network_api.my_flash_io_master, db, meter_address_index)
