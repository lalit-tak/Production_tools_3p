
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
                    SCRIPT_LOG_STATUS_COMPLETED     ,\
                    SCRIPT_LOG_METER_ISSUE

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

from config import BROADCAST_FLASH_START_ADDRESS,\
                    SCRIPT_LOG_BROADCAST_ADDRESS,\
                    BROADCAST_DELAY_BETWEEN_PACKETS

from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

from gp_node.utils.address import Address


START_ADDRESS = BROADCAST_FLASH_START_ADDRESS

def program(filepath, flash_io, db, broadcast_address):


    db.display(BROADCAST_STEP_NO,'Broadcast Started .......', logging = True)

    binary_file = open(filepath, "rb")
    block = binary_file.read()
    hexfile_payload = bytearray()
    for ch in block:
        hexfile_payload.append(ch)
    then = time.time()
    flash_io.burn_nack(Address("0.0.0.255"),\
                        START_ADDRESS,\
                        hexfile_payload,\
                        db,\
                        broadcast_address,\
                        LOG_DEFAULT_METER_ADDRESS,\
                        BROADCAST_STEP_NO,\
                        SCRIPT_LOG_BROADCAST_ADDRESS,\
                        BROADCAST_DELAY_BETWEEN_PACKETS,\
                        to_print=True)
    now = time.time()
    diff = float(now - then)
    db.display(BROADCAST_STEP_NO,str("Time taken in seconds - " + str(diff)), logging = True)

def run(db, network_api, bin_file, broadcast_address):


    db.display(BROADCAST_STEP_NO, LOG_COMMENTS_RUN_EXECUTED,\
                upper_space = 2, lower_space = 2, logging = True)
    
    db.display(BROADCAST_STEP_NO, " ",status=SCRIPT_LOG_STATUS_IN_PROGRESS, script_logging = True)


    starttime = datetime.datetime.now()
    
    if bin_file is not None:

        db.display(BROADCAST_STEP_NO,"Broadcasting ...", logging = True)
        program(bin_file, network_api.my_flash_io_master, db, broadcast_address)



    EndTime = datetime.datetime.now()

    db.display(BROADCAST_STEP_NO,str('Broadcast Completed with start time '+ str(starttime) + ' and end time '+ str(EndTime)), logging = True)
    db.display(BROADCAST_STEP_NO, " " ,status=SCRIPT_LOG_STATUS_COMPLETED, script_logging = True)





if __name__ == "__main__":
    run()

