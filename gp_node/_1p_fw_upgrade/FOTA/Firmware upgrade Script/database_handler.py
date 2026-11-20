
import time
import datetime
import serial

import os
import argparse
import json
import csv


from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import asc,desc

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

import config
             
     
from config import STEP_DISPLAY_SIZE    ,\
                   STRING_DISPLAY_SIZE  ,\
                   ADDRESS_DISPLAY_SIZE ,\
                   STATUS_DISPLAY_SIZE  ,\
                   RETRY_DISPLAY_SIZE   ,\
                   STRING_DIVIDER       


from orm_model import  Base,\
                        resultTableCreator,\
                        statusTableCreator,\
                        eraseLogTableCreator,\
                        healthLogTableCreator,\
                        healLogTableCreator,\
                        logTableCreator,\
                        scriptLogTableCreator

from config import  AddressList_1P

from config import  SQL_CONNECT_STRING,\
                    CONFIG_SESSION_NUMBER,\
                    ENTRY_AUTO_DELETION,\
                    SYNC_LOCATION,\
                    SQL_CREATE_STRING,\
                    DATABASE_NAME

from config import  RESULT_TABLE_NAME,\
                    STATUS_TABLE_NAME,\
                    ERASE_LOG_TABLE_NAME,\
                    HEALTH_LOG_TABLE_NAME,\
                    HEAL_LOG_TABLE_NAME,\
                    LOG_TABLE_NAME,\
                    SCRIPT_LOG_TABLE_NAME

from config import  LOG_TYPE_NORMAL                 ,\
                    LOG_TYPE_ERROR                  ,\
                    LOG_DEFAULT_METER_ADDRESS       ,\
                    LOG_COMMENTS_RUN_EXECUTED       ,\
                    SCRIPT_LOG_STATUS_NOT_STARTED   ,\
                    SCRIPT_LOG_STATUS_IN_PROGRESS   ,\
                    SCRIPT_LOG_STATUS_COMPLETED     ,\
                    SCRIPT_LOG_BROADCAST_ADDRESS

from config import  FILL_STRING_NOT_STARTED         ,\
                    FILL_STRING_ERROR               ,\
                    FILL_STRING_SUCCESS             ,\
                    FILL_STRING_NO_BAD_CHUNK

from orm_objects import resultData      ,\
                        statusData      ,\
                        eraseLogData    ,\
                        healthLogData   ,\
                        healLogData     ,\
                        logData         ,\
                        scriptLogData

log_object = logData()
script_log_object = scriptLogData()


class dataCollectionDbHandler():
    """
    This is a singleton class that handles all communication to the
    DB and all modules should go through this to use the DB. This
    uses the orm_models.py to obtain the DB schema. Application should
    take care to ensure multiple instances of this module is not
    created.
    """
    

    def __init__(self):
        
        try:
            self.engine = create_engine(SQL_CONNECT_STRING)        
            self.connection = self.engine.connect() 
        except Exception as e:
            print 'Database not available - ', e             
            print 'Creating new database......'
            self.engine = create_engine(SQL_CREATE_STRING) # connect to server
            self.engine.execute(str("CREATE DATABASE "+ DATABASE_NAME)) #create db
            print 'New Database created - ', DATABASE_NAME             
            
            #self.engine.execute(str("USE "+ DATABASE_NAME)) # select new db
            self.engine = create_engine(SQL_CONNECT_STRING) 
            self.connection = self.engine.connect() 
            self.Sessionmaker_instance = sessionmaker(bind=self.engine)
            self.session = self.Sessionmaker_instance()
            self.table_dict = {}
        else:
            self.Sessionmaker_instance = sessionmaker(bind=self.engine)
            self.session = self.Sessionmaker_instance()
            self.table_dict = {}

    def createResultTable(self, table_name):

        """
        Creates a new table to store result of firmware upgrade for 
        current session. This is usually called when we need to add a new meter.
        If a table is already present in the DB, the API just generates the 
        mapping class and adds that to the table_dict
        @param 1: table name

        """
        # It will not through any error as, log table is already created   
        self.display(DATABASE_HANDLER_STEP_NO, str('Creating table ' + \
                            str(table_name)), upper_space = 2, logging = True) 

        table = resultTableCreator(table_name)
        Base.metadata.create_all(self.engine)
        self.table_dict[table_name] = table

        return table
    
    def createStatusTable(self, table_name):
        
        self.display(DATABASE_HANDLER_STEP_NO, str('Creating table ' + \
                                            str(table_name)), logging = True)
        table = statusTableCreator(table_name)
        Base.metadata.create_all(self.engine)
        self.table_dict[table_name] = table
        return table

    
    def createEraseLogTable(self, table_name):

        self.display(DATABASE_HANDLER_STEP_NO, str('Creating table ' + \
                                        str(table_name)), logging = True)
        table = eraseLogTableCreator(table_name)
        Base.metadata.create_all(self.engine)
        self.table_dict[table_name] = table
        return table


    
    def createHealthLogTable(self, table_name):

        self.display(DATABASE_HANDLER_STEP_NO, str('Creating table ' + \
                                            str(table_name)), logging = True)
        table = healthLogTableCreator(table_name)
        Base.metadata.create_all(self.engine)
        self.table_dict[table_name] = table
        return table


    
    def createHealLogTable(self, table_name):

        self.display(DATABASE_HANDLER_STEP_NO, str('Creating table ' + 
                            str(table_name)), logging = True)
        table = healLogTableCreator(table_name)
        Base.metadata.create_all(self.engine)
        self.table_dict[table_name] = table
        return table


    
    def createLogTable(self, table_name):

        
        table = logTableCreator(table_name)
        Base.metadata.create_all(self.engine)
        self.table_dict[table_name] = table
        return table


    def createScriptLogTable(self, table_name):

        self.display(DATABASE_HANDLER_STEP_NO, str('Creating table ' + \
            str(table_name)), logging = True)
        table = scriptLogTableCreator(table_name)
        Base.metadata.create_all(self.engine)
 
        self.table_dict[table_name] = table
        return table



    def populate_result_data(self, data):

        """
            This populates data to the result table. Before populating, 
            it also validates entry for dupicate primary key. Instance
            of resultData() in orm_objects corresponds to a row in the Table.

            @param : Object of type resultData() from orm_objects 
            @return : None
        """

        table_name = RESULT_TABLE_NAME


        self.display(DATABASE_HANDLER_STEP_NO, str('Checking to Populate ' + \
                                                            str(table_name)))
        table_list = Base.metadata.tables.keys()

        if table_name in self.table_dict:
            table = self.table_dict[table_name]
        else:
            self.display(DATABASE_HANDLER_STEP_NO, str(str(table_name) + \
                                                        " Table not available"))
            table = self.createResultTable(table_name)

        if self.validate_entry(data, table, RESULT_TABLE_NAME) == False:
            self.display(DATABASE_HANDLER_STEP_NO, str("EXCEPTION - Entry "\
                "validation failed in table "+ str(table_name)), logging = True)
        else:
            try:
                self.populate_table(data, table, table_name)
            except Exception as e:
                self.display(DATABASE_HANDLER_STEP_NO, str("Validation "\
                    "successful but error in inserting in table "+\
                    str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR,\
                     logging = True)





    def populate_status_data(self, data):

        """
            This populates data to the status table. Before populating, 
            it also validates entry for dupicate primary key. Instance
            of statusData() in orm_objects corresponds to a row in the Table.

            @param : Object of type statusData() from orm_objects 
            @return : None

        """

        table_name = STATUS_TABLE_NAME
        self.display(DATABASE_HANDLER_STEP_NO, str('Checking to Populate ' + str(table_name)))

        table_list = Base.metadata.tables.keys()
        
        if table_name in self.table_dict:
            
            table = self.table_dict[table_name]
        else:
            self.display(DATABASE_HANDLER_STEP_NO, str(str(table_name) + " Table not available"))
            table = self.createStatusTable(table_name)
        
        if self.validate_entry(data, table, STATUS_TABLE_NAME) == False:
            self.display(DATABASE_HANDLER_STEP_NO, str("EXCEPTION - Entry validation failed in table "+ str(table_name)), logging = True)
        else:    
            try:
                self.populate_table(data, table, table_name)
            except Exception as e:                
                self.display(DATABASE_HANDLER_STEP_NO, str("Validation successful but error in inserting in table "+\
                                                    str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR, logging = True)


    def populate_erase_log_data(self, data):
      
        table_name = ERASE_LOG_TABLE_NAME
        self.display(DATABASE_HANDLER_STEP_NO, str('Checking to Populate ' + str(table_name)))

        table_list = Base.metadata.tables.keys()
        
        if table_name in self.table_dict:            
            table = self.table_dict[table_name]
        else:
            self.display(DATABASE_HANDLER_STEP_NO, str(str(table_name) + " Table not available"))
            table = self.createEraseLogTable(table_name)

        if self.validate_entry(data, table, ERASE_LOG_TABLE_NAME) == False:
            self.display(DATABASE_HANDLER_STEP_NO, str("EXCEPTION - Entry validation failed in table "+ str(table_name)), logging = True)
        else:    
            try:
                self.populate_table(data, table, table_name)
            except Exception as e:                
                self.display(DATABASE_HANDLER_STEP_NO, str("Validation successful but error in inserting in table "+\
                                                    str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR, logging = True)



    def populate_health_log_data(self, data):

        table_name = HEALTH_LOG_TABLE_NAME

        self.display(DATABASE_HANDLER_STEP_NO, str('Checking to Populate ' + str(table_name)))

        table_list = Base.metadata.tables.keys()
        
        if table_name in self.table_dict:
            
            table = self.table_dict[table_name]
        else:
            self.display(DATABASE_HANDLER_STEP_NO, str(str(table_name) + " Table not available"))
            table = self.createHealthLogTable(table_name)
        
        if self.validate_entry(data, table, HEALTH_LOG_TABLE_NAME) == False:
            self.display(DATABASE_HANDLER_STEP_NO, str("EXCEPTION - Entry validation failed in table "+ str(table_name)), logging = True)
        else:    
            try:
                self.populate_table(data, table, table_name)
            except Exception as e:                
                self.display(DATABASE_HANDLER_STEP_NO, str("Validation successful but error in inserting in table "+\
                                                    str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR, logging = True)



    def populate_heal_data(self, data):

        table_name = HEAL_LOG_TABLE_NAME
        self.display(DATABASE_HANDLER_STEP_NO, str('Checking to Populate ' + str(table_name)))

        table_list = Base.metadata.tables.keys()
        
        if table_name in self.table_dict:
            
            table = self.table_dict[table_name]
        else:
            self.display(DATABASE_HANDLER_STEP_NO, str(str(table_name) + " Table not available"))
            table = self.createHealLogTable(table_name)

        if self.validate_entry(data, table, HEAL_LOG_TABLE_NAME) == False:
            self.display(DATABASE_HANDLER_STEP_NO, str("EXCEPTION - Entry validation failed in table "+ str(table_name)), logging = True)
        else:    
            try:
                self.populate_table(data, table, table_name)
            except Exception as e:                
                self.display(DATABASE_HANDLER_STEP_NO, str("Validation successful but error in inserting in table "+\
                                                    str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR, logging = True)

    def populate_log_data(self, data):

        table_name = LOG_TABLE_NAME

        table_list = Base.metadata.tables.keys()
        
        if table_name in self.table_dict:
            
            table = self.table_dict[table_name]
        else:
            
            table = self.createLogTable(table_name)

   
        try:

            self.populate_table(data, table, table_name)

        except Exception as e:                
            self.display(DATABASE_HANDLER_STEP_NO, str("Validation successful but error in inserting in table "+\
                                                str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR)



    def populate_script_log_data(self, data):

        table_name = SCRIPT_LOG_TABLE_NAME

        table_list = Base.metadata.tables.keys()
        
        if table_name in self.table_dict:            
            table = self.table_dict[table_name]
        else:
            
            table = self.scriptLogTableCreator(table_name)

        try:
            self.populate_table(data, table, table_name)
        except Exception as e:                
            self.display(DATABASE_HANDLER_STEP_NO, str("Validation successful but error in inserting in table "+\
                                                str(table_name) +'\n'+str(e)),status = LOG_TYPE_ERROR, logging = True)



    def populate_table(self, data, table, name):

        """

        Handles population to table and ORM related tasks
        @param 1: Data to be populated(object of class from orm_objects)
        @param 2: Class from dictionary table_dict 
        @param 3: Table name (From config file)

        @return : None
        
        """

        parser = data
        
        if name == RESULT_TABLE_NAME:
            self.display(DATABASE_HANDLER_STEP_NO, str("In table "+ str(name) + " Now Populating...."))
            data_to_db = table(\
                                SESSION_NUMBER                      = parser.SESSION_NUMBER                   ,\
                                METER_ADDRESS                       = parser.METER_ADDRESS                    ,\
                                CURRENT_FIRMWARE_VERSION_IN_METER   = parser.CURRENT_FIRMWARE_VERSION_IN_METER,\
                                UPGRADE_STATUS                      = parser.UPGRADE_STATUS                   ,\
                                TOTAL_LOOPS                         = parser.TOTAL_LOOPS                      ,\
                                START_TIME_OF_UPGRADE               = parser.START_TIME_OF_UPGRADE            ,\
                                END_TIME_OF_UPGRADE                 = parser.END_TIME_OF_UPGRADE              )

        elif name == STATUS_TABLE_NAME:
            self.display(DATABASE_HANDLER_STEP_NO, str("In table "+ str(name) + "Now Populating...."), logging = True)
            data_to_db = table(\
                                SESSION_NUMBER       = parser.SESSION_NUMBER      ,\
                                RESTART_LOOP_NO      = parser.RESTART_LOOP_NO     ,\
                                METER_ADDRESS        = parser.METER_ADDRESS       ,\
                                LOOP_NO              = parser.LOOP_NO             ,\
                                ERASE_STATUS         = parser.ERASE_STATUS        ,\
                                ERASE_TIME_TAKEN     = parser.ERASE_TIME_TAKEN    ,\
                                ERASE_TOTAL_RETRY    = parser.ERASE_TOTAL_RETRY   ,\
                                SECTOR_READ_STATUS   = parser.SECTOR_READ_STATUS  ,\
                                BAD_SECTORS          = parser.BAD_SECTORS         ,\
                                TOTAL_SECTOR_RETRY   = parser.TOTAL_SECTOR_RETRY  ,\
                                SECTORS_READING_TIME = parser.SECTORS_READING_TIME,\
                                CHUNK_READ_STATUS    = parser.CHUNK_READ_STATUS   ,\
                                BAD_CHUNK_PERCENT    = parser.BAD_CHUNK_PERCENT   ,\
                                BAD_CHUNK_COUNT      = parser.BAD_CHUNK_COUNT     ,\
                                BAD_CHUNKS           = parser.BAD_CHUNKS          ,\
                                TOTAL_CHUNK_RETRY    = parser.TOTAL_CHUNK_RETRY   ,\
                                CHUNK_READING_TIME   = parser.CHUNK_READING_TIME  ,\
                                HEALING_STATUS       = parser.HEALING_STATUS      ,\
                                TOTAL_HEALING_TIME   = parser.TOTAL_HEALING_TIME  ,\
                                TOTAL_HEALING_RETRY  = parser.TOTAL_HEALING_RETRY )
        
        elif name == ERASE_LOG_TABLE_NAME:
            self.display(DATABASE_HANDLER_STEP_NO, str("In table "+ str(name) + "Now Populating...."), logging = True)
            data_to_db = table(\
                                METER_ADDRESS       = parser.METER_ADDRESS    ,\
                                ERASE_STATUS        = parser.ERASE_STATUS     ,\
                                TOTAL_RETRY         = parser.TOTAL_RETRY      ,\
                                CHUNK_1_STATUS      = parser.CHUNK_1_STATUS   ,\
                                CHUNK_1_RETRY       = parser.CHUNK_1_RETRY    ,\
                                CHUNK_2_STATUS      = parser.CHUNK_2_STATUS   ,\
                                CHUNK_2_RETRY       = parser.CHUNK_2_RETRY    ,\
                                SECTOR_32_STATUS    = parser.SECTOR_32_STATUS ,\
                                SECTOR_32_RETRY     = parser.SECTOR_32_RETRY  ,\
                                START_TIME          = parser.START_TIME       ,\
                                EXECUTION_TIME      = parser.EXECUTION_TIME   )

        elif name == HEALTH_LOG_TABLE_NAME:
            self.display(DATABASE_HANDLER_STEP_NO, str("In table "+ str(name) + "Now Populating...."), logging = True)
            data_to_db = table(\
                                METER_ADDRESS           = parser.METER_ADDRESS          ,\
                                SECTOR_READ_STATUS      = parser.SECTOR_READ_STATUS     ,\
                                TOTAL_SECTOR_READ_RETRY = parser.TOTAL_SECTOR_READ_RETRY,\
                                SECTORS_READING_TIME    = parser.SECTORS_READING_TIME   ,\
                                CHUNK_READ_STATUS       = parser.CHUNK_READ_STATUS      ,\
                                TOTAL_CHUNK_RETRY       = parser.TOTAL_CHUNK_RETRY      ,\
                                CHUNK_READING_TIME      = parser.CHUNK_READING_TIME     ,\
                                BAD_SECTORS_JSON        = parser.BAD_SECTORS_JSON       ,\
                                CHUNKS_CRC_JSON         = parser.CHUNKS_CRC_JSON        )

        elif name == HEAL_LOG_TABLE_NAME:
            self.display(DATABASE_HANDLER_STEP_NO, str("In table "+ str(name) + "Now Populating...."), logging = True)
            data_to_db = table(\
                                METER_ADDRESS           = parser.METER_ADDRESS         ,\
                                LOOP_NO                 = parser.LOOP_NO               ,\
                                HEALING_STATUS          = parser.HEALING_STATUS        ,\
                                HEAL_START_TIME         = parser.HEAL_START_TIME       ,\
                                TOTAL_HEALING_TIME      = parser.TOTAL_HEALING_TIME    ,\
                                TOTAL_HEALING_RETRY     = parser.TOTAL_HEALING_RETRY   ,\
                                TOTAL_VALIDATION_RETRY  = parser.TOTAL_VALIDATION_RETRY,\
                                BAD_CHUNK_PERCENT       = parser.BAD_CHUNK_PERCENT     ,\
                                BAD_CHUNK_COUNT         = parser.BAD_CHUNK_COUNT       ,\
                                BAD_CHUNKS              = parser.BAD_CHUNKS            )

        elif name == LOG_TABLE_NAME:
            
            data_to_db = table(\

                                SESSION_NUMBER          = parser.SESSION_NUMBER       ,\
                                METER_ADDRESS           = parser.METER_ADDRESS        ,\
                                DATE_TIME               = parser.DATE_TIME            ,\
                                TYPE                    = parser.TYPE                 ,\
                                STEP_NUMBER             = parser.STEP_NUMBER          ,\
                                COMMENTS                = parser.COMMENTS             )
        
        elif name == SCRIPT_LOG_TABLE_NAME:
            
            data_to_db = table(\
                                SESSION_NUMBER          = parser.SESSION_NUMBER       ,\
                                STEP_NUMBER             = parser.STEP_NUMBER          ,\
                                METER_ADDRESS           = parser.METER_ADDRESS        ,\
                                STATUS                  = parser.STATUS               ,\
                                COMMENTS                = parser.COMMENTS             )                
        try:
            self.session.add_all([data_to_db])
            self.session.dirty
            self.session.commit()
        except Exception as e:
            print e
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - "+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return "Logging failed"
        else:
            pass


    def validate_entry(self, data, table, name):

        """
        
        Validates data to be populated by comparing primary key of data in db.
        It also provides option for entry auto deletion or to skip duplicate entry. 
        @param 1: Data need to validate(object of class from orm_objects)
        @param 2: Class from dictionary table_dict 
        @param 3: Table name (From config file)

        @return : True/False
                    True : In case of successfull validation/ duplicate entry 
                    deletion/ skipping

                    False: If fails in reading database
        
        """

        parser = data        
                
        if name == RESULT_TABLE_NAME:

            self.display(DATABASE_HANDLER_STEP_NO, str("Validating Entry in table " + str(name)))


            try:
                validate_result = self.session.query(table).filter_by(SESSION_NUMBER = parser.SESSION_NUMBER, METER_ADDRESS = parser.METER_ADDRESS).all()
            except Exception as e:

                self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to validate table "+ str(name)),status = LOG_TYPE_ERROR, logging = True)

                return False
            else:    
                if len(validate_result) > 0:
                    self.display(DATABASE_HANDLER_STEP_NO, str(str(len(validate_result)) + " similar entry found"))

                    if ENTRY_AUTO_DELETION == True:                        
                        self.session.query(table).filter_by(SESSION_NUMBER = parser.SESSION_NUMBER, METER_ADDRESS = parser.METER_ADDRESS, TOTAL_LOOPS = parser.TOTAL_LOOPS).delete()
                        self.display(DATABASE_HANDLER_STEP_NO, str("Older entry deleted in table" +  str(name)), logging = True)

                        return True
                    else:
                        self.display(DATABASE_HANDLER_STEP_NO, str("Entry already exists in table " +  str(name)), logging = True)

                        return False
                else:
                    self.display(DATABASE_HANDLER_STEP_NO, str("No older entry exist in table " +  str(name)), logging = True)                
                    return True



        elif name == STATUS_TABLE_NAME:

            self.display(DATABASE_HANDLER_STEP_NO, str("Validating Entry in table " + str(name)))

            try:
                validate_status = self.session.query(table).filter_by(SESSION_NUMBER = parser.SESSION_NUMBER, METER_ADDRESS = parser.METER_ADDRESS, LOOP_NO = parser.LOOP_NO, RESTART_LOOP_NO = parser.RESTART_LOOP_NO).all()
            except Exception as e:
                self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to validate table "+ str(name)),status = LOG_TYPE_ERROR, logging = True)
                return False    
            else:    
                if len(validate_status) > 0:
                    self.display(DATABASE_HANDLER_STEP_NO, str(str(len(validate_status)) + " similar entry found"))                    
                    if ENTRY_AUTO_DELETION == True:
                        self.session.query(table).filter_by(SESSION_NUMBER = parser.SESSION_NUMBER, METER_ADDRESS = parser.METER_ADDRESS, LOOP_NO = parser.LOOP_NO).delete()
                        self.display(DATABASE_HANDLER_STEP_NO, str("Older entry deleted in table" +  str(name)), logging = True)

                        return True
                    else:
                        self.display(DATABASE_HANDLER_STEP_NO, str("Entry already exists in table " +  str(name)), logging = True)

                        return False
                else:
                    self.display(DATABASE_HANDLER_STEP_NO, str("No older entry exist in table " +  str(name)), logging = True)                    
                    return True



        elif name == ERASE_LOG_TABLE_NAME:

            self.display(DATABASE_HANDLER_STEP_NO, str("Validating Entry in table " + str(name)))
            try:
                validate_erase_log = self.session.query(table).filter_by(METER_ADDRESS = parser.METER_ADDRESS).all()
            except Exception as e:
                self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to validate table "+ str(name)),status = LOG_TYPE_ERROR, logging = True)
                return False    
            else:    
                if len(validate_erase_log) > 0:

                    self.display(DATABASE_HANDLER_STEP_NO, str(str(len(validate_erase_log)) + " similar entry found"))
                    
                    if ENTRY_AUTO_DELETION == True:                        
                        self.session.query(table).filter_by(METER_ADDRESS = parser.METER_ADDRESS).delete()
                        self.display(DATABASE_HANDLER_STEP_NO, str("Older entry deleted in table" +  str(name)), logging = True)

                        return True
                    else:
                        self.display(DATABASE_HANDLER_STEP_NO, str("Entry already exists in table " +  str(name)), logging = True)

                        return False
                else:
                    self.display(DATABASE_HANDLER_STEP_NO, str("No older entry exist in table " +  str(name)), logging = True)                   
                    return True


        elif name == HEALTH_LOG_TABLE_NAME:

            self.display(DATABASE_HANDLER_STEP_NO, str("Validating Entry in table " + str(name)))

            try:
                validate_health_log = self.session.query(table).filter_by(METER_ADDRESS = parser.METER_ADDRESS).all()
            except Exception as e:
                self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to validate table "+ str(name)),status = LOG_TYPE_ERROR, logging = True)
                return False    
            else:    
                if len(validate_health_log) > 0:

                    self.display(DATABASE_HANDLER_STEP_NO, str(str(len(validate_health_log)) + " similar entry found"))
                    
                    if ENTRY_AUTO_DELETION == True:                        
                        self.session.query(table).filter_by(METER_ADDRESS = parser.METER_ADDRESS).delete()
                        self.display(DATABASE_HANDLER_STEP_NO, str("Older entry deleted in table" +  str(name)), logging = True)

                        return True
                    else:
                        self.display(DATABASE_HANDLER_STEP_NO, str("Entry already exists in table " +  str(name)), logging = True)
                        return False
                else:
                    self.display(DATABASE_HANDLER_STEP_NO, str("No older entry exist in table " +  str(name)), logging = True)                   
                    return True


        elif name == HEAL_LOG_TABLE_NAME:
            self.display(DATABASE_HANDLER_STEP_NO, str("Validating Entry in table " + str(name)))
            try:
                validate_heal_log = self.session.query(table).filter_by(METER_ADDRESS = parser.METER_ADDRESS).all()
            except Exception as e:
                self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to validate table "+ str(name)),status = LOG_TYPE_ERROR, logging = True)
                return False    
            else:    
                if len(validate_heal_log) > 0:
                    self.display(DATABASE_HANDLER_STEP_NO, str(str(len(validate_heal_log)) + " similar entry found"))
                     
                    if ENTRY_AUTO_DELETION == True:                        
                        self.session.query(table).filter_by(METER_ADDRESS = parser.METER_ADDRESS).delete()
                        self.display(DATABASE_HANDLER_STEP_NO, str("Older entry deleted in table" +  str(name)), logging = True)

                        return True
                    else:
                        self.display(DATABASE_HANDLER_STEP_NO, str("Entry already exists in table " +  str(name)), logging = True)
                     
                    
                        return False
                else:
                    self.display(DATABASE_HANDLER_STEP_NO, str("No older entry exist in table " +  str(name)), logging = True)
                                      
                    return True




    def check_script(self):

        """
        
        It checks script_log table and returns its last entry.

        @param : None
        @return : Dictionary having last entry values if entries are > 0
                and if no entry available, dictionary will have default values
        
        """

        print('Checking last session')  

        dict_last_entry = {}   
        dict_last_entry = {'Total successful entries for current session': 0,\
                            'Step number':  0,\
                            'Meter Address': 0,\
                            'Status': "Null",\
                            'Comments': "Null"\
                            }

        table = self.table_dict[SCRIPT_LOG_TABLE_NAME]           

        try:
            check_script_log = self.session.query(table).filter_by(SESSION_NUMBER = CONFIG_SESSION_NUMBER,STATUS = SCRIPT_LOG_STATUS_COMPLETED).all()
        except Exception as e:
            print e
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get last session data"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return dict_last_entry                     
        else:
            script_log_last_entry = self.session.query(table).filter_by(SESSION_NUMBER = CONFIG_SESSION_NUMBER).all()
            index = len(script_log_last_entry) - 1

            if len(script_log_last_entry) > 0:
                dict_last_entry = {'Total successful entries for current session': len(check_script_log),\
                                    'Step number':  int(script_log_last_entry[index].STEP_NUMBER),\
                                    'Meter Address': int(script_log_last_entry[index].METER_ADDRESS),\
                                    'Status': script_log_last_entry[index].STATUS,\
                                    'Comments': script_log_last_entry[index].COMMENTS\
                                }
                return dict_last_entry
            else:
                return dict_last_entry



    def return_latest_entry(self, table_name, meter_id):



        table = self.table_dict[table_name]
        try:
            table_object = self.session.query(table).filter_by(METER_ADDRESS = meter_id).first()

        except Exception as e:
            print e
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to return latest entry"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return table_object                   
        else:                                       
            return table_object



    def delete_script_brodcast_entry(self):
        """
        This function deletes all entries of current session from script log table having 
        status is SCRIPT_LOG_BROADCAST_ADDRESS, 

        @params - None.
        @returns - string in json format for firmware sectorwise CRCs.
        """


        table = self.table_dict[SCRIPT_LOG_TABLE_NAME]           

        try:
            check_script_log = self.session.query(table).filter_by(SESSION_NUMBER = CONFIG_SESSION_NUMBER,STATUS = SCRIPT_LOG_BROADCAST_ADDRESS).all()
        except Exception as e:
            print e
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to delete script broadcast entry"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return False                   
        else:
            self.session.query(table).filter_by(SESSION_NUMBER = CONFIG_SESSION_NUMBER,STATUS = SCRIPT_LOG_BROADCAST_ADDRESS).delete()
            return True


    def get_firmware_sectorwise_crc(self):
        """
        It reads sectorwise CRC of firmware from health table and returns
        its string in json format.

        @params - None.
        @returns - string in json format for firmware sectorwise CRCs.
        """

        table = self.table_dict[HEALTH_LOG_TABLE_NAME]  
        firmware_health_sector_json = ""         

        try:
            firmware_sector_crc = self.session.query(table).filter_by(METER_ADDRESS = LOG_DEFAULT_METER_ADDRESS,SECTOR_READ_STATUS = FILL_STRING_SUCCESS).first()
        except Exception as e:
            print e
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get firmware sectorwise CRC"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return firmware_health_sector_json                   
        else:
            firmware_health_sector_json = firmware_sector_crc.BAD_SECTORS_JSON
            return firmware_health_sector_json



    def get_firmware_blockwise_crc(self):

        """
        This function returns string in json format having CRCs of
        all 64 B chunks of 128 KB of firmware.

        @params : None.
        @returns : Chunkwise CRC (string in form of json)

        """

        table = self.table_dict[HEALTH_LOG_TABLE_NAME]  
        firmware_health_chunk_json = ""         

        try:
            firmware_chunk_crc = self.session.query(table).filter_by(METER_ADDRESS = LOG_DEFAULT_METER_ADDRESS,CHUNK_READ_STATUS = FILL_STRING_SUCCESS).first()
        except Exception as e:
            
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get firmware blockwise CRC"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return firmware_health_chunk_json                   
        else:
            firmware_health_chunk_json = firmware_chunk_crc.CHUNKS_CRC_JSON
            return firmware_health_chunk_json



    def get_meter_bad_sectors(self, meter_id):

        table = self.table_dict[HEALTH_LOG_TABLE_NAME]  
        meter_bad_sectors_json = ""         

        try:
            meter_sector_crc = self.session.query(table).filter_by(METER_ADDRESS = meter_id,SECTOR_READ_STATUS = FILL_STRING_SUCCESS).first()
        except Exception as e:
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get meter bad sectors"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return meter_bad_sectors_json                   
        else:
            meter_bad_sectors_json = meter_sector_crc.BAD_SECTORS_JSON
            return meter_bad_sectors_json



    def get_meter_chunkwise_health(self,  meter_id):

        """
        This function returns string in json format having CRCs of
        all 64 B chunks of 32 sectors. It reads health

        @params : Meter address.
        @returns : Chunkwise CRC (string in form of json)
        """

        table = self.table_dict[HEALTH_LOG_TABLE_NAME]  
        meter_chunkwise_health_json = " "

        try:
            meter_chunk_crc = self.session.query(table).filter_by(METER_ADDRESS = meter_id, CHUNK_READ_STATUS = FILL_STRING_SUCCESS).first()
        except Exception as e:            
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get meter chunkwise health"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            return meter_chunkwise_health_json                   
        else:
            meter_chunkwise_health_json = meter_chunk_crc.CHUNKS_CRC_JSON
            return meter_chunkwise_health_json


    def get_meter_health(self,  meter_id):

        """
        This function checks meter health in health table
        and returns its status.

        @params : Meter address to check in health table.
        @returns : 'Good' - If meter doesn't need healing.
                   'Bad' - if meter requires healing
        """


        table = self.table_dict[HEALTH_LOG_TABLE_NAME]  
        meter_health_status = 'Bad'

        try:
            meter_health = self.session.query(table).filter_by(METER_ADDRESS = meter_id, CHUNKS_CRC_JSON = FILL_STRING_NO_BAD_CHUNK).all()
            if len(meter_health) > 0:
                meter_health_status = 'Good'
        except Exception as e:
            print e
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get meter health"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)   
            return meter_health_status                   
        else:           
            return meter_health_status


    def get_all_meter_heal_status(self):
        """
        It checks health of all meters in current session and returns 
        'Good' if all meters of current session (except blacklisted meters)
        are successfully repaired. Return 'Bad', if any meter requires
        healing.

        @params : None.
        @returns : 'Good' - If all meters of current session doesn't need healing.
                   'Bad' - If any meter of current session requires healing.

        """


        table = self.table_dict[HEALTH_LOG_TABLE_NAME]  
        all_meter_health_status = 'Bad'

        try:
            all_meter_health = self.session.query(table).filter_by(CHUNKS_CRC_JSON = FILL_STRING_NO_BAD_CHUNK).all()
        except Exception as e:
           
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to get all meter heal status"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)   
           
            return all_meter_health_status
        else:
            if len(all_meter_health) == (len(AddressList_1P) - int(self.length_of_blacklist())):
                all_meter_health_status = 'Good'            
            return all_meter_health_status


    def get_loop_no(self):
        """
        returns last healing loop number logged in database. It 
        checks for loop number in table heal.

        @params : None.
        @ returns : loop number, returns zero in case of exception.

        """

        table = self.table_dict[HEAL_LOG_TABLE_NAME]  
        current_loop_no = 0

        try:
            loop_no = self.session.query(table).filter_by(HEALING_STATUS = FILL_STRING_SUCCESS).all()
            if len(loop_no) > 0:
                current_loop_no = loop_no[int(len(loop_no)-1)].LOOP_NO        
        except Exception as e:
            self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to read loop number"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)            
            return current_loop_no                   
        else:                                       
            return current_loop_no


    def add_meter_to_blacklist(self,meter_address, step_no):
        """
        Meters which are not responding, their addresses are added 
        to a text file named blacklisted_meters. Before communicating 
        to any meter, this blacklist is checked and while communicating to 
        any meter, if no response received, that address added to blacklist.

        @param 1 : Meter address to add in blacklist 
        @param 2 : Step no from where this function is called (For logging).
         
        @ returns : None
        
        """
        file = open('blacklisted_meters.txt', 'a+')
        file.write(str(meter_address) + '\n')
        file.close()
        self.display(DATABASE_HANDLER_STEP_NO, str("Meter added to blacklist " + str(meter_address)), logging = True)
        time.sleep(2)


    def check_meter_in_blacklist(self, meter_address, step_no):
        """
        It checks input meter address present in blacklist or not.

        @param 1: meter address to search.
        @param 2: Step no from where this function is called (For logging).

        @return : True - Meter found in blacklist.
                  False - Address not present in blacklist.

        """
        file = open('blacklisted_meters.txt', 'a+')
        file.close()
        file = open('blacklisted_meters.txt', 'r+')
        content = file.readlines()
        temp_str = str(meter_address) + '\n'
        for i in range(0, len(content)):
            if temp_str == content[i]:                
                file.close()
                self.display(DATABASE_HANDLER_STEP_NO,str("Meter found in blacklist " + str(meter_address)), logging = True)
                return True
        return False


    def erase_blacklist(self,step_no):
        """
        It erases .txt file named blacklisted_meters.txt

        @param 1: Step No from where this method is getting called (For logging).
        @return : None.

        """
        line = '' 
        file = open('blacklisted_meters.txt', 'w+')
        file.write(line)
        file.close()
        self.display(DATABASE_HANDLER_STEP_NO,"Blacklist Erased", logging = True)


    def length_of_blacklist(self):
        
        """
        This provides number of meters present in blacklist 

        @param 1: None.
        @return : No of meters.

        """
        
        length = 0 
        file = open('blacklisted_meters.txt', 'a+')
        file.close()
        file = open('blacklisted_meters.txt', 'r+')        
        content = file.readlines()
        length = len(content)
        file.close()
        return length



    def display(self, step_no,\
                      string_to_display,\
                      meter_address = LOG_DEFAULT_METER_ADDRESS,\
                      status = LOG_TYPE_NORMAL,\
                      retry = int(-1),\
                      upper_space = 0,\
                      lower_space = 0,\
                      printing = True,\
                      logging = False,\
                      script_logging = False):
        """
        This method helps in managing display at terminal, logging in log and script log
        table. It provides configurable positions to display and also maintains
        symmetry. Reason for developing this function is to merge logging and printing
        at one place with symmetry in display and every statement gets associated with 
        its step number, meter address, status etc.

        @return : None

        """


        for i in range(0, int(upper_space)):
            print '\n'
        str_step        = config.trim_string(str(STEP_NAME[step_no]),  STEP_DISPLAY_SIZE)
        #str_display     = config.trim_string(str(string_to_display), STRING_DISPLAY_SIZE)      Trimming not require
        str_display     = str(string_to_display)
        str_meter_addr  = config.trim_string(str(meter_address), ADDRESS_DISPLAY_SIZE)
        str_status      = config.trim_string(str(status), STATUS_DISPLAY_SIZE)   
        str_retry       = config.trim_string(str(retry), RETRY_DISPLAY_SIZE)     

        if retry >= 0:
            make_string = 'In '+str_step+STRING_DIVIDER+'Meter = '+str_meter_addr+STRING_DIVIDER+\
                            str_status+STRING_DIVIDER+'Retry - '+str_retry+STRING_DIVIDER+str_display
        else:
            make_string = 'In '+str_step+STRING_DIVIDER+'Meter = '+str_meter_addr+STRING_DIVIDER+\
                            str_status+STRING_DIVIDER+str_display
        

        if printing == True:
            print make_string

        if logging == True:
            if retry >= 0:
                log_string =  'In '+str_step+STRING_DIVIDER+' Retry - '+str_retry+STRING_DIVIDER+str_display

            else:
                log_string =  'In '+str_step+STRING_DIVIDER+STRING_DIVIDER+str_display

            log_object.set_log_params(meter_address, status, step_no, log_string)                
            self.populate_log_data(log_object)
            try:
                self.create_csv(LOG_TABLE_NAME, SYNC_LOCATION)
                self.create_csv(RESULT_TABLE_NAME, SYNC_LOCATION)
                self.create_csv(STATUS_TABLE_NAME, SYNC_LOCATION)
                self.create_csv(SCRIPT_LOG_TABLE_NAME, SYNC_LOCATION)
            except Exception as e:
                print 'Error in updating CSV', str(e), '\n'
            else:
                pass
            
        if script_logging == True:

            script_log_object.set_script_log_params(step_no, meter_address, status, string_to_display)
            self.populate_script_log_data(script_log_object)            
            try:
                self.create_csv(LOG_TABLE_NAME, SYNC_LOCATION)
                self.create_csv(RESULT_TABLE_NAME, SYNC_LOCATION)
                self.create_csv(STATUS_TABLE_NAME, SYNC_LOCATION)
                self.create_csv(SCRIPT_LOG_TABLE_NAME, SYNC_LOCATION)
            except Exception as e:
                print 'Error in updating CSV', str(e), '\n'
            else:
                pass

         
        for i in range(0, int(lower_space)):
            print '\n'


    def create_csv(self, table_name, location):

        """
        This function creates csv file of table from database. 

        @param 1: table name.
        @param 1: location to save CSV files.
        
        @return : True/False.
                    True - CSV file created 
                    False - Failed in creating CSV file
        """    

        table = self.table_dict[table_name]

        try:
            table_all_entries = self.session.query(table).all()
        except Exception as e:            
            #self.display(DATABASE_HANDLER_STEP_NO, str("ERROR - unable to fetch table for CSV"+'\n'+ str(e)),status = LOG_TYPE_ERROR, logging = True)
            print 'Error in updating CSV file\n' + str(e)
            return False                   
        else:
            file_name_str = str(str(table_name) + '.csv') 
            file_name_with_loc = location + '/' + file_name_str
            #self.display(DATABASE_HANDLER_STEP_NO,str("Creating CSV file named " + str(file_name_str) + ' with location ' + str(file_name_with_loc) ), logging = True)
            
            with open(file_name_with_loc, 'wb') as f:
                out = csv.writer(f)                
                if table_name == LOG_TABLE_NAME:
                    out.writerow([\
                                    'SR_NO',\
                                    'SESSION_NUMBER',\
                                    'METER_ADDRESS',\
                                    'DATE_TIME',\
                                    'TYPE',\
                                    'STEP_NUMBER',\
                                    'COMMENTS'\
                                    ])
                    for item in self.session.query(table).all():
                        out.writerow([item.SR_NO,\
                                      item.SESSION_NUMBER,\
                                      item.METER_ADDRESS,\
                                      item.DATE_TIME,\
                                      item.TYPE,\
                                      item.STEP_NUMBER,\
                                      item.COMMENTS\
                                      ])

                if table_name == SCRIPT_LOG_TABLE_NAME:
                    out.writerow([\
                                    'SR_NO',\
                                    'SESSION_NUMBER',\
                                    'STEP_NUMBER',\
                                    'METER_ADDRESS',\
                                    'STATUS',\
                                    'COMMENTS'\
                                    ])
                    for item in self.session.query(table).all():
                        out.writerow([\
                                      item.SR_NO,\
                                      item.SESSION_NUMBER,\
                                      item.STEP_NUMBER,\
                                      item.METER_ADDRESS,\
                                      item.STATUS,\
                                      item.COMMENTS\
                                      ])
                
                if table_name == RESULT_TABLE_NAME:
                    out.writerow([\
                                    'SESSION_NUMBER',\
                                    'METER_ADDRESS',\
                                    'CURRENT_FIRMWARE_VERSION_IN_METER',\
                                    'UPGRADE_STATUS',\
                                    'TOTAL_LOOPS',\
                                    'START_TIME_OF_UPGRADE',\
                                    'END_TIME_OF_UPGRADE',\
                                    ])
                    for item in self.session.query(table).all():
                        out.writerow([\
                                        item.SESSION_NUMBER,\
                                        item.METER_ADDRESS,\
                                        item.CURRENT_FIRMWARE_VERSION_IN_METER,\
                                        item.UPGRADE_STATUS,\
                                        item.TOTAL_LOOPS,\
                                        item.START_TIME_OF_UPGRADE,\
                                        item.END_TIME_OF_UPGRADE\
                                      ])
                
                if table_name == STATUS_TABLE_NAME:

                    out.writerow([\
                                    'SESSION_NUMBER',\
                                    'RESTART_LOOP_NO',\
                                    'METER_ADDRESS',\
                                    'LOOP_NO',\
                                    'ERASE_STATUS',\
                                    'ERASE_TIME_TAKEN',\
                                    'ERASE_TOTAL_RETRY',\
                                    'SECTOR_READ_STATUS',\
                                    'BAD_SECTORS',\
                                    'TOTAL_SECTOR_RETRY',\
                                    'SECTORS_READING_TIME',\
                                    'CHUNK_READ_STATUS',\
                                    'BAD_CHUNK_PERCENT',\
                                    'BAD_CHUNK_COUNT',\
                                    'BAD_CHUNKS',\
                                    'TOTAL_CHUNK_RETRY',\
                                    'CHUNK_READING_TIME',\
                                    'HEALING_STATUS',\
                                    'TOTAL_HEALING_TIME',\
                                    'TOTAL_HEALING_RETRY'\
                                    ])
                    for item in self.session.query(table).all():


                        out.writerow([\
                                        item.SESSION_NUMBER,\
                                        item.RESTART_LOOP_NO,\
                                        item.METER_ADDRESS,\
                                        item.LOOP_NO,\
                                        item.ERASE_STATUS,\
                                        item.ERASE_TIME_TAKEN,\
                                        item.ERASE_TOTAL_RETRY,\
                                        item.SECTOR_READ_STATUS,\
                                        item.BAD_SECTORS,\
                                        item.TOTAL_SECTOR_RETRY,\
                                        item.SECTORS_READING_TIME,\
                                        item.CHUNK_READ_STATUS,\
                                        item.BAD_CHUNK_PERCENT,\
                                        item.BAD_CHUNK_COUNT,\
                                        item.BAD_CHUNKS,\
                                        item.TOTAL_CHUNK_RETRY,\
                                        item.CHUNK_READING_TIME,\
                                        item.HEALING_STATUS,\
                                        item.TOTAL_HEALING_TIME,\
                                        item.TOTAL_HEALING_RETRY\
                                      ])
            f.close()

            return True

