"""
Run this file only when tables are not available in database

"""
import datetime
from sqlalchemy import *
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

from config import SQL_CONNECT_STRING, CONFIG_SESSION_NUMBER

Base = declarative_base()

def resultTableCreator(tablename):

    class Result(Base):

        __tablename__ = tablename

        SESSION_NUMBER = Column(Integer, primary_key=True, default=0)
        METER_ADDRESS = Column(Integer, primary_key=True, default=0)
        CURRENT_FIRMWARE_VERSION_IN_METER = Column(Integer, default=0)
        UPGRADE_STATUS = Column(String(300), default = 'Not Started')
        TOTAL_LOOPS = Column(Integer, default=0)    
        START_TIME_OF_UPGRADE =  Column(DateTime)
        END_TIME_OF_UPGRADE =  Column(DateTime)

        def __repr__(self):
            return ("SESSION_NUMBER: {}\n"
            "METER_ADDRESS: {}\n"
            "CURRENT_FIRMWARE_VERSION_IN_METER: {} \n"
            "UPGRADE_STATUS: {} \n"
            "TOTAL_LOOPS: {} \n" 
            "START_TIME_OF_UPGRADE: {}\n"
            "END_TIME_OF_UPGRADE: {}").format(self.SESSION_NUMBER,
                                self.METER_ADDRESS,
                                self.CURRENT_FIRMWARE_VERSION_IN_METER,
                                self.UPGRADE_STATUS,
                                self.TOTAL_LOOPS,
                                self.START_TIME_OF_UPGRADE,
                                self.END_TIME_OF_UPGRADE)
    #print 'Result table created'
    return Result




def statusTableCreator(tablename):

    class Status(Base):

        __tablename__ = tablename

        SESSION_NUMBER = Column(Integer, primary_key=True, default=0)
        RESTART_LOOP_NO = Column(Integer, primary_key=True, default=0)
        METER_ADDRESS = Column(Integer, primary_key=True, default=0)        
        LOOP_NO = Column(Integer, primary_key=True, default=0)
        ERASE_STATUS = Column(String(300))
        ERASE_TIME_TAKEN = Column(Float, default=0)
        ERASE_TOTAL_RETRY = Column(Integer, default=0)    
        SECTOR_READ_STATUS = Column(String(300))
        BAD_SECTORS = Column(Text(30000))
        TOTAL_SECTOR_RETRY = Column(Integer, default=0)
        SECTORS_READING_TIME = Column(Float, default=0)
        CHUNK_READ_STATUS = Column(String(3000))
        BAD_CHUNK_PERCENT = Column(Float, default=0)
        BAD_CHUNK_COUNT = Column(Integer, default=0)
        BAD_CHUNKS = Column(Text(30000))
        TOTAL_CHUNK_RETRY = Column(Integer, default=0)
        CHUNK_READING_TIME = Column(Float, default=0)
        HEALING_STATUS = Column(String(300))    #In further improvement, healing in next loop will be based on previous loop instead of complete healing 
        TOTAL_HEALING_TIME = Column(Float, default=0)
        TOTAL_HEALING_RETRY = Column(Integer, default=0)

        def __repr__(self):
            return ("SESSION_NUMBER: {}\n"
            "RESTART_LOOP_NO: {}\n"
            "METER_ADDRESS: {}\n"
            "LOOP_NO: {} \n"
            "ERASE_STATUS: {} \n"
            "ERASE_TIME_TAKEN: {} \n"            
            "ERASE_TOTAL_RETRY: {}\n"
            "SECTOR_READ_STATUS: {}\n"
            "BAD_SECTORS: {}\n"
            "TOTAL_SECTOR_RETRY: {}\n"
            "SECTORS_READING_TIME: {}\n"
            "CHUNK_READ_STATUS: {}\n"
            "BAD_CHUNK_PERCENT: {}\n"
            "BAD_CHUNK_COUNT: {}\n"
            "BAD_CHUNKS: {}\n"
            "TOTAL_CHUNK_RETRY: {}\n"
            "CHUNK_READING_TIME: {}\n"
            "HEALING_STATUS: {}\n"
            "TOTAL_HEALING_TIME: {}\n"
            "TOTAL_HEALING_RETRY: {}").format(self.SESSION_NUMBER,
                                self.RESTART_LOOP_NO,
                                self.METER_ADDRESS,
                                self.LOOP_NO,
                                self.ERASE_STATUS,
                                self.ERASE_TIME_TAKEN,
                                self.ERASE_TOTAL_RETRY,
                                self.SECTOR_READ_STATUS,
                                self.BAD_SECTORS,
                                self.TOTAL_SECTOR_RETRY,
                                self.SECTORS_READING_TIME,
                                self.CHUNK_READ_STATUS,
                                self.BAD_CHUNK_PERCENT,
                                self.BAD_CHUNK_COUNT,
                                self.BAD_CHUNKS,
                                self.TOTAL_CHUNK_RETRY,
                                self.CHUNK_READING_TIME,
                                self.HEALING_STATUS,
                                self.TOTAL_HEALING_TIME,
                                self.TOTAL_HEALING_RETRY)
    #print 'Status table created'
    return Status



def eraseLogTableCreator(tablename):

    class Erase_Log(Base):

        __tablename__ = tablename

        METER_ADDRESS = Column(Integer, primary_key=True, default=0)    
        ERASE_STATUS = Column(String(300))
        TOTAL_RETRY = Column(Integer, default=0)
        CHUNK_1_STATUS = Column(String(300))
        CHUNK_1_RETRY = Column(Integer, default=0)
        CHUNK_2_STATUS = Column(String(300))
        CHUNK_2_RETRY = Column(Integer, default=0)
        SECTOR_32_STATUS = Column(String(300))
        SECTOR_32_RETRY = Column(Integer, default=0)
        START_TIME = Column(DateTime)
        EXECUTION_TIME = Column(Float, default=0)

        def __repr__(self):
            return ("METER_ADDRESS: {}\n"
            "ERASE_STATUS: {}\n"
            "TOTAL_RETRY: {} \n"
            "CHUNK_1_STATUS: {} \n"
            "CHUNK_1_RETRY: {} \n"            
            "CHUNK_2_STATUS: {}\n"
            "CHUNK_2_RETRY: {}\n"
            "SECTOR_32_STATUS: {}\n"
            "SECTOR_32_RETRY: {}\n"
            "START_TIME: {}\n"           
            "EXECUTION_TIME: {}").format(self.METER_ADDRESS,
                                self.ERASE_STATUS,
                                self.TOTAL_RETRY,
                                self.CHUNK_1_STATUS,
                                self.CHUNK_1_RETRY,
                                self.CHUNK_2_STATUS,
                                self.CHUNK_2_RETRY,
                                self.SECTOR_32_STATUS,
                                self.SECTOR_32_RETRY,
                                self.START_TIME,
                                self.EXECUTION_TIME)
    #print 'Erase log table created'
    return Erase_Log


def healthLogTableCreator(tablename):    
    
    class Health_Log(Base):

        __tablename__ = tablename


        METER_ADDRESS = Column(Integer, primary_key=True, default=0)        
        SECTOR_READ_STATUS = Column(String(300))
        TOTAL_SECTOR_READ_RETRY = Column(Integer, default=0)
        SECTORS_READING_TIME = Column(Float, default=0)
        CHUNK_READ_STATUS = Column(String(300))
        TOTAL_CHUNK_RETRY = Column(Integer, default=0)
        CHUNK_READING_TIME = Column(Float, default=0) 
        BAD_SECTORS_JSON = Column(Text(20000))
        CHUNKS_CRC_JSON = Column(Text(30000))

        def __repr__(self):
            return ("METER_ADDRESS: {}\n"
            "SECTOR_READ_STATUS: {}\n"
            "TOTAL_SECTOR_READ_RETRY: {} \n"
            "SECTORS_READING_TIME: {} \n"
            "CHUNK_READ_STATUS: {} \n"            
            "TOTAL_CHUNK_RETRY: {}\n"
            "CHUNK_READING_TIME: {}\n"
            "BAD_SECTORS_JSON: {}\n"           
            "CHUNKS_CRC_JSON: {}").format(self.METER_ADDRESS,
                                self.SECTOR_READ_STATUS,
                                self.TOTAL_SECTOR_READ_RETRY,
                                self.SECTORS_READING_TIME,
                                self.CHUNK_READ_STATUS,
                                self.TOTAL_CHUNK_RETRY,
                                self.CHUNK_READING_TIME,
                                self.BAD_SECTORS_JSON,
                                self.CHUNKS_CRC_JSON)
    #print 'Health log table created'
    return Health_Log

def healLogTableCreator(tablename):

    class Heal_Log(Base):

        __tablename__ = tablename

        METER_ADDRESS = Column(Integer, primary_key=True, default=0)
        LOOP_NO = Column(Integer, primary_key=True, default=0)
        HEALING_STATUS = Column(String(300))    #In further improvement, healing in next loop will be based on previous loop instead of complete healing 
        HEAL_START_TIME = Column(DateTime)
        TOTAL_HEALING_TIME = Column(Float, default=0)
        TOTAL_HEALING_RETRY = Column(Integer, default=0)
        TOTAL_VALIDATION_RETRY = Column(Integer, default=0)
        BAD_CHUNK_PERCENT = Column(Float, default=0)
        BAD_CHUNK_COUNT = Column(Integer, default=0)
        BAD_CHUNKS = Column(Text(30000))
        
        def __repr__(self):
            return ("METER_ADDRESS: {}\n"
            "LOOP_NO: {}\n"
            "HEALING_STATUS: {} \n"
            "HEAL_START_TIME: {} \n"
            "TOTAL_HEALING_TIME: {} \n"            
            "TOTAL_HEALING_RETRY: {}\n"
            "TOTAL_VALIDATION_RETRY: {}\n"
            "BAD_CHUNK_PERCENT: {}\n"
            "BAD_CHUNK_COUNT: {}\n"           
            "BAD_CHUNKS: {}").format(self.METER_ADDRESS,
                                self.LOOP_NO,
                                self.HEALING_STATUS,
                                self.HEAL_START_TIME,
                                self.TOTAL_HEALING_TIME,
                                self.TOTAL_HEALING_RETRY,
                                self.TOTAL_VALIDATION_RETRY,
                                self.BAD_CHUNK_PERCENT,
                                self.BAD_CHUNK_COUNT,
                                self.BAD_CHUNKS)
    #print 'HeaL log table created'
    return Heal_Log

def logTableCreator(tablename):
    
    class Log(Base):

        __tablename__ = tablename
        SR_NO = Column(Integer, autoincrement=True,primary_key=True) # Take unsigned long or any large datatype
        SESSION_NUMBER = Column(Integer, default=0)
        METER_ADDRESS = Column(Integer, default=0)
        DATE_TIME = Column(DateTime)
        TYPE = Column(String(3000)) #Result/ query/ error
        STEP_NUMBER = Column(Integer, default=0)
        COMMENTS = Column(Text(30000))
        
        def __repr__(self):
            return ("SR_NO: {}\n"
            "SESSION_NUMBER: {}\n"
            "METER_ADDRESS: {} \n"
            "DATE_TIME: {} \n"
            "TYPE: {} \n"            
            "STEP_NUMBER: {}\n"            
            "COMMENTS: {}").format(self.SR_NO,
                                self.SESSION_NUMBER,
                                self.METER_ADDRESS,
                                self.DATE_TIME,
                                self.TYPE,
                                self.STEP_NUMBER,                                
                                self.COMMENTS)
    #print 'Log table created'
    return Log


def scriptLogTableCreator(tablename):

    class Script_Log(Base):

        __tablename__ = tablename

        SR_NO = Column(Integer, autoincrement=True,primary_key=True) # Take unsigned long or any large datatype
        SESSION_NUMBER = Column(Integer, default=0)
        STEP_NUMBER = Column(Integer, default=0)
        METER_ADDRESS = Column(Integer, default=0)
        STATUS = Column(String(3000)) #Completed/In progress/Not started
        COMMENTS = Column(String(3000))
        
        def __repr__(self):
            return ("SR_NO: {}\n"
            "SESSION_NUMBER: {}\n"
            "STEP_NUMBER: {} \n"
            "METER_ADDRESS: {} \n"
            "STATUS: {} \n"
            "COMMENTS: {}").format(self.SR_NO,
                                self.SESSION_NUMBER,
                                self.STEP_NUMBER,
                                self.METER_ADDRESS,
                                self.STATUS,
                                self.COMMENTS)
    #print 'Script Log table created'
    return Script_Log


