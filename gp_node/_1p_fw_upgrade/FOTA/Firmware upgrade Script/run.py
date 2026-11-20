#python run.py -d COM20 -p out_3006.bin

import config

#patch - because ui values were not updating because update_caonfig was
#called after import 
if config.update_config() == False:
    pass


from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData


from database_handler import dataCollectionDbHandler

import  database_validation         ,\
        update_firmware_health      ,\
        erase_flash                 ,\
        broadcast                   ,\
        config                      ,\
        update_health               ,\
        heal_by_chunk               ,\
        update_status               ,\
        reset_and_update_result         


import datetime
import time
import argparse
import serial

from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io import FlashIOMaster, FlashIOError
from gp_node.utils.address import Address
import gp_node.utils.serialize as serialize



from config import  LOG_TYPE_NORMAL                 ,\
                    LOG_TYPE_ERROR                  ,\
                    LOG_DEFAULT_METER_ADDRESS       ,\
                    LOG_COMMENTS_RUN_EXECUTED       ,\
                    SCRIPT_LOG_STATUS_NOT_STARTED   ,\
                    SCRIPT_LOG_STATUS_IN_PROGRESS   ,\
                    SCRIPT_LOG_STATUS_COMPLETED     ,\
                    SCRIPT_LOG_BROADCAST_ADDRESS    ,\
                    SCRIPT_LOG_STATUS_DONE


from config import  SQL_CONNECT_STRING              ,\
                    CONFIG_SESSION_NUMBER           ,\
                    ENTRY_AUTO_DELETION             ,\
                    SERIAL_TIMEOUT                  ,\
                    BAUDRATE                        ,\
                    UPDATE_RESULT_WAIT              ,\
                    DEVICE

                    
from config import BROADCAST_FLASH_START_ADDRESS

from config import TOTAL_HEALING_LOOP_COUNT

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
                    TOTAL_STEPS

from config import  RESULT_TABLE_NAME       ,\
                    STATUS_TABLE_NAME       ,\
                    ERASE_LOG_TABLE_NAME    ,\
                    HEALTH_LOG_TABLE_NAME   ,\
                    HEAL_LOG_TABLE_NAME     ,\
                    LOG_TABLE_NAME          ,\
                    SCRIPT_LOG_TABLE_NAME

from config import FILL_STRING_ERROR



RESUME_FLAG = False  # This flag decides to resume script or start from beginning 


def main():    
    """
    This function is entry point for firmware upgrade. It creates
    object of database handler and network api classes which is used by all
    other files.
    
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', action="store", dest="hex_file", 
                        help="programs new hex file")

    args = parser.parse_args()


    ser = serial.Serial(DEVICE, BAUDRATE , timeout=SERIAL_TIMEOUT)
    network_api = NetworkAPI(ser, "irda")


    db = dataCollectionDbHandler()         # All other files use this object to access dataCollectionDbHandler class 

    db.display(RUN_STEP_NO, 'Checking requirements.............', upper_space = 2, lower_space = 2)
    time.sleep(3)

    ############################# DATABASE VALIDATION ###########################

    database_validation_result = database_validation.run(db)

    if database_validation_result == False:
        db.display(RUN_STEP_NO, 'Error in validating database', status = LOG_TYPE_ERROR)
        return

    db.display(RUN_STEP_NO,LOG_COMMENTS_RUN_EXECUTED,logging = True)
    db.display(RUN_STEP_NO,"Database Validated",logging = True)
    time.sleep(3)
    ############################################################################




    ################## Checking meter address present in DCU ###################
    # Checking UI_config file 
    if config.update_config() == False:
        db.display(RUN_STEP_NO, 'Error in reading config file',\
            upper_space = 2, lower_space = 2, status = LOG_TYPE_ERROR, logging = True)        
        return



    if config.get_meter_address_from_dcu() != True:
        
        db.display(RUN_STEP_NO,"Error in fetching meter address from DCU",status = LOG_TYPE_ERROR,logging = True)
        time.sleep(1)
        return
    ############################################################################





    ######################## CHECKING DB TO SET RESUME FLAG #########################
        
    script_table_last_entry = db.check_script()

    if script_table_last_entry['Total successful entries for current session'] > 0:
        RESUME_FLAG = True

        db.display(RUN_STEP_NO,"Previous entries are available",logging = True,upper_space = 1)        
        
        db.display(RUN_STEP_NO,\
                            str("Last entry in " + SCRIPT_LOG_TABLE_NAME + ' -' +\
                            '\nStep Number - ' + str(script_table_last_entry['Step number']) +\
                            '\nMeter Address - ' + str(script_table_last_entry['Meter Address']) +\
                            '\nStatus - ' + str(script_table_last_entry['Status']) + \
                            '\nComments - ' + str(script_table_last_entry['Comments'])),\
            logging = True)
        
        time.sleep(3)

    else:
        RESUME_FLAG = False
    ###############################################################################




    ##################### Setting parameters for resuming #########################
    if RESUME_FLAG == False:

        db.display(RUN_STEP_NO, 'Starting Firmware Upgrade..........',\
                        upper_space = 2, lower_space = 2, logging = True)
        time.sleep(3)



        METER_ADDRESS_INDEX = 0
        CURRENT_STEP_NO = UPDATE_FIRMWARE_HEALTH_STEP_NO
        CURRENT_BROADCAST_ADDRESS = BROADCAST_FLASH_START_ADDRESS
        LOOP_NO = 0
        current_loop_no = 0
        update_health_flag = 0 # For resuming purpose
        db.erase_blacklist(RUN_STEP_NO)
        db.display(RUN_STEP_NO, 'Blacklist erased',logging = True)
        time.sleep(3)


    else:
        db.display(RUN_STEP_NO, 'Resuming Firmware Upgrade..........',\
                        upper_space = 2, lower_space = 2, logging = True)
        time.sleep(3)

        METER_ADDRESS_INDEX = 0
        CURRENT_STEP_NO = UPDATE_FIRMWARE_HEALTH_STEP_NO
        CURRENT_BROADCAST_ADDRESS = BROADCAST_FLASH_START_ADDRESS
        LOOP_NO = db.get_loop_no()
        current_loop_no = LOOP_NO

        update_health_flag = 0
        
        if script_table_last_entry['Status'] == SCRIPT_LOG_STATUS_COMPLETED:            
            CURRENT_STEP_NO = script_table_last_entry['Step number'] + 1

        else:

            CURRENT_STEP_NO = script_table_last_entry['Step number']

            METER_ADDRESS_INDEX = config.get_meter_address_index(int(script_table_last_entry['Meter Address']))
            if METER_ADDRESS_INDEX == 1000:         # Unexpected value
                METER_ADDRESS_INDEX = LOG_DEFAULT_METER_ADDRESS
            if script_table_last_entry['Status'] == SCRIPT_LOG_STATUS_DONE: 
                METER_ADDRESS_INDEX = METER_ADDRESS_INDEX + 1


            if CURRENT_STEP_NO == BROADCAST_STEP_NO:
                if script_table_last_entry['Status'] == SCRIPT_LOG_BROADCAST_ADDRESS:
                    CURRENT_BROADCAST_ADDRESS = int(script_table_last_entry['Comments'])
                    
                    db.display(RUN_STEP_NO,str("Resuming broadcast at address - " + str(CURRENT_BROADCAST_ADDRESS)),\
                                            upper_space = 2, lower_space = 2, logging = True)
    ####################################################################################







    ############################ Starting upgrade process #################################

    while CURRENT_STEP_NO <= TOTAL_STEPS:
        if CURRENT_STEP_NO == UPDATE_FIRMWARE_HEALTH_STEP_NO:
            update_firmware_health.run(db, args.hex_file)
            
        elif CURRENT_STEP_NO == ERASE_FLASH_STEP_NO:
            erase_flash.run(db, network_api, METER_ADDRESS_INDEX)   
            #pass
        
        elif CURRENT_STEP_NO == BROADCAST_STEP_NO:
            broadcast.run(db, network_api, args.hex_file, CURRENT_BROADCAST_ADDRESS)
            #pass

        elif CURRENT_STEP_NO == UPDATE_HEALTH_STEP_NO:            
            update_health.run(db, network_api, METER_ADDRESS_INDEX)
            update_health_flag = 1

        elif CURRENT_STEP_NO == HEAL_BY_CHUNK_STEP_NO:            
            
            if update_health_flag == 0:       # In case of power cycle, it will update health first before healing to resume healing from same point         
                update_status.run(db, network_api, current_loop_no) 
                #current_loop_no = current_loop_no + 1
                update_health.run(db, network_api, METER_ADDRESS_INDEX)
                current_loop_no = current_loop_no + 1

            while int(current_loop_no) < int(TOTAL_HEALING_LOOP_COUNT):                
                update_status.run(db, network_api, current_loop_no)
                heal_by_chunk.run(db, network_api, METER_ADDRESS_INDEX, args.hex_file, current_loop_no)
                update_health.run(db, network_api, METER_ADDRESS_INDEX)
                current_loop_no = current_loop_no + 1           
                       
                heal_status_all_meters = db.get_all_meter_heal_status()

                if heal_status_all_meters == 'Good':
                    update_status.run(db, network_api, current_loop_no)

                    db.display(RUN_STEP_NO,str("Healing is successful for all meters, loops taken : " + str(current_loop_no)),\
                                            logging = True, upper_space = 2, lower_space = 2)

                    db.display(HEAL_BY_CHUNK_STEP_NO," ",status = SCRIPT_LOG_STATUS_COMPLETED,script_logging = True)
                    break              

        elif CURRENT_STEP_NO == UPDATE_STATUS_STEP_NO:
            update_status.run(db, network_api, current_loop_no)
            

        elif CURRENT_STEP_NO == RESET_AND_UPDATE_RESULT_STEP_NO:
            reset_and_update_result.run(db, network_api, current_loop_no)
            time.sleep(UPDATE_RESULT_WAIT)
            reset_and_update_result.run(db, network_api, current_loop_no)



        CURRENT_STEP_NO = CURRENT_STEP_NO + 1
        METER_ADDRESS_INDEX = 0
    ######################################################################################
        


if __name__ == "__main__":
    main()



