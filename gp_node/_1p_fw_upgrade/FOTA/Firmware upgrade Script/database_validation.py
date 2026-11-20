

from database_handler import dataCollectionDbHandler


from config import LOG_TYPE_NORMAL,\
                    LOG_TYPE_ERROR,\
                    LOG_COMMENTS_RUN_EXECUTED

from config import  SQL_CONNECT_STRING,\
                    CONFIG_SESSION_NUMBER,\
                    ENTRY_AUTO_DELETION,\
                    RUN_STEP_NO

from config import RESULT_TABLE_NAME        ,\
                    STATUS_TABLE_NAME       ,\
                    ERASE_LOG_TABLE_NAME    ,\
                    HEALTH_LOG_TABLE_NAME   ,\
                    HEAL_LOG_TABLE_NAME     ,\
                    LOG_TABLE_NAME          ,\
                    SCRIPT_LOG_TABLE_NAME

from config import FILL_STRING_ERROR

from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

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
                    STEP_NAME


import datetime


def run(db):

    
    result_object       = resultData()  
    status_object       = statusData()
    erase_log_object    = eraseLogData()
    health_log_object   = healthLogData()
    heal_log_data       = healLogData()    
    log_object          = logData()
    
    try:
        db.createLogTable(LOG_TABLE_NAME)
    except Exception as e:
        db.display(DATABASE_VALIDATION_STEP_NO,"Database Validation - failed",status = LOG_TYPE_ERROR,logging = True)
        return False
    else:
               
        db.createResultTable(RESULT_TABLE_NAME)                    
        db.createStatusTable(STATUS_TABLE_NAME)        
        db.createEraseLogTable(ERASE_LOG_TABLE_NAME)        
        db.createHealthLogTable(HEALTH_LOG_TABLE_NAME)        
        db.createHealLogTable(HEAL_LOG_TABLE_NAME)               
        db.createScriptLogTable(SCRIPT_LOG_TABLE_NAME)        
        db.display(DATABASE_VALIDATION_STEP_NO,"Database Validation - Success",logging = True)
        return True


        


