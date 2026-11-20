import datetime
from config import FILL_STRING_NOT_STARTED,\
                    CONFIG_SESSION_NUMBER


class resultData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """

    def __init__(self):

        self.SESSION_NUMBER = 0
        self.METER_ADDRESS = 0
        self.CURRENT_FIRMWARE_VERSION_IN_METER = 0
        self.UPGRADE_STATUS = FILL_STRING_NOT_STARTED
        self.TOTAL_LOOPS = 0
        self.START_TIME_OF_UPGRADE = datetime.datetime.now()
        self.END_TIME_OF_UPGRADE = datetime.datetime.now()

    def __str__(self):
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


    def set_result_params(self                                   ,\
                                session_number                   ,\
                                meter_address                    ,\
                                current_firmware_version_in_meter,\
                                upgrade_status                   ,\
                                total_loops                      ,\
                                start_time_of_upgrade            ,\
                                end_time_of_upgrade              ):
        self.SESSION_NUMBER                     = session_number                        
        self.METER_ADDRESS                      = meter_address                         
        self.CURRENT_FIRMWARE_VERSION_IN_METER  = current_firmware_version_in_meter         
        self.UPGRADE_STATUS                     = upgrade_status                        
        self.TOTAL_LOOPS                        = total_loops                       
        self.START_TIME_OF_UPGRADE              = start_time_of_upgrade             
        self.END_TIME_OF_UPGRADE                = end_time_of_upgrade               
     
class statusData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """
    def __init__(self):

        self.SESSION_NUMBER = 0
        self.RESTART_LOOP_NO = 0
        self.METER_ADDRESS = 0
        self.LOOP_NO = 0
        self.ERASE_STATUS = FILL_STRING_NOT_STARTED
        self.ERASE_TIME_TAKEN = 0.0
        self.ERASE_TOTAL_RETRY = 0
        self.SECTOR_READ_STATUS = FILL_STRING_NOT_STARTED
        self.BAD_SECTORS = FILL_STRING_NOT_STARTED
        self.TOTAL_SECTOR_RETRY = 0
        self.SECTORS_READING_TIME = 0.0
        self.CHUNK_READ_STATUS = FILL_STRING_NOT_STARTED
        self.BAD_CHUNK_PERCENT = 0.0
        self.BAD_CHUNK_COUNT = 0
        self.BAD_CHUNKS = FILL_STRING_NOT_STARTED
        self.TOTAL_CHUNK_RETRY = 0
        self.CHUNK_READING_TIME = 0.0
        self.HEALING_STATUS = FILL_STRING_NOT_STARTED    #In further improvement, healing in next loop will be based on previous loop instead of complete healing 
        self.TOTAL_HEALING_TIME = 0.0
        self.TOTAL_HEALING_RETRY = 0

    def __str__(self):
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

    def set_status_params(self,\
                                session_number      ,\
                                restart_loop_no     ,\
                                meter_address       ,\
                                loop_no             ,\
                                erase_status        ,\
                                erase_time_taken    ,\
                                erase_total_retry   ,\
                                sector_read_status  ,\
                                bad_sectors         ,\
                                total_sector_retry  ,\
                                sectors_reading_time,\
                                chunk_read_status   ,\
                                bad_chunk_percent   ,\
                                bad_chunk_count     ,\
                                bad_chunks          ,\
                                total_chunk_retry   ,\
                                chunk_reading_time  ,\
                                healing_status      ,\
                                total_healing_time  ,\
                                total_healing_retry  ):




        self.SESSION_NUMBER         = session_number
        self.RESTART_LOOP_NO        = restart_loop_no       
        self.METER_ADDRESS          = meter_address                     
        self.LOOP_NO                = loop_no                           
        self.ERASE_STATUS           = erase_status              
        self.ERASE_TIME_TAKEN       = erase_time_taken          
        self.ERASE_TOTAL_RETRY      = erase_total_retry         
        self.SECTOR_READ_STATUS     = sector_read_status
        self.BAD_SECTORS            = bad_sectors           
        self.TOTAL_SECTOR_RETRY     = total_sector_retry            
        self.SECTORS_READING_TIME   = sectors_reading_time      
        self.CHUNK_READ_STATUS      = chunk_read_status         
        self.BAD_CHUNK_PERCENT      = bad_chunk_percent         
        self.BAD_CHUNK_COUNT        = bad_chunk_count           
        self.BAD_CHUNKS             = bad_chunks            
        self.TOTAL_CHUNK_RETRY      = total_chunk_retry             
        self.CHUNK_READING_TIME     = chunk_reading_time        
        self.HEALING_STATUS         = healing_status            
        self.TOTAL_HEALING_TIME     = total_healing_time          
        self.TOTAL_HEALING_RETRY    = total_healing_retry       


class eraseLogData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """

    def __init__(self):


        self.METER_ADDRESS = 0 
        self.ERASE_STATUS = FILL_STRING_NOT_STARTED
        self.TOTAL_RETRY = 0
        self.CHUNK_1_STATUS = FILL_STRING_NOT_STARTED
        self.CHUNK_1_RETRY = 0
        self.CHUNK_2_STATUS = FILL_STRING_NOT_STARTED
        self.CHUNK_2_RETRY = 0
        self.SECTOR_32_STATUS = FILL_STRING_NOT_STARTED
        self.SECTOR_32_RETRY = 0
        self.START_TIME = datetime.datetime.now()
        self.EXECUTION_TIME = 0.0

    def __str__(self):
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


    def set_erase_log_params(self, \
                                meter_address   ,\
                                erase_status    ,\
                                total_retry     ,\
                                chunk_1_status  ,\
                                chunk_1_retry   ,\
                                chunk_2_status  ,\
                                chunk_2_retry   ,\
                                sector_32_status,\
                                sector_32_retry ,\
                                start_time      ,\
                                execution_time  ):

        self.METER_ADDRESS          = meter_address     
        self.ERASE_STATUS           = erase_status      
        self.TOTAL_RETRY            = total_retry       
        self.CHUNK_1_STATUS         = chunk_1_status    
        self.CHUNK_1_RETRY          = chunk_1_retry     
        self.CHUNK_2_STATUS         = chunk_2_status    
        self.CHUNK_2_RETRY          = chunk_2_retry     
        self.SECTOR_32_STATUS       = sector_32_status  
        self.SECTOR_32_RETRY        = sector_32_retry   
        self.START_TIME             = start_time        
        self.EXECUTION_TIME         = execution_time    

class healthLogData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """

    def __init__(self):


        self.METER_ADDRESS = 0      
        self.SECTOR_READ_STATUS = FILL_STRING_NOT_STARTED
        self.TOTAL_SECTOR_READ_RETRY = 0
        self.SECTORS_READING_TIME = 0.0
        self.CHUNK_READ_STATUS = FILL_STRING_NOT_STARTED
        self.TOTAL_CHUNK_RETRY = 0
        self.CHUNK_READING_TIME = 0.0 
        self.BAD_SECTORS_JSON = FILL_STRING_NOT_STARTED
        self.CHUNKS_CRC_JSON = FILL_STRING_NOT_STARTED

    def __str__(self):
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


    def set_health_log_params(self, \
                                meter_address          ,\
                                sector_read_status     ,\
                                total_sector_read_retry,\
                                sectors_reading_time   ,\
                                chunk_read_status      ,\
                                total_chunk_retry      ,\
                                chunk_reading_time     ,\
                                bad_sectors_json       ,\
                                chunks_crc_json        ):

        self.METER_ADDRESS              = meter_address                 
        self.SECTOR_READ_STATUS         = sector_read_status            
        self.TOTAL_SECTOR_READ_RETRY    = total_sector_read_retry           
        self.SECTORS_READING_TIME       = sectors_reading_time          
        self.CHUNK_READ_STATUS          = chunk_read_status             
        self.TOTAL_CHUNK_RETRY          = total_chunk_retry             
        self.CHUNK_READING_TIME         = chunk_reading_time            
        self.BAD_SECTORS_JSON           = bad_sectors_json          
        self.CHUNKS_CRC_JSON            = chunks_crc_json           



class healLogData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """

    def __init__(self):


        self.METER_ADDRESS = 0
        self.LOOP_NO = 0
        self.HEALING_STATUS = FILL_STRING_NOT_STARTED
        self.HEAL_START_TIME = datetime.datetime.now()
        self.TOTAL_HEALING_TIME = 0.0
        self.TOTAL_HEALING_RETRY = 0
        self.TOTAL_VALIDATION_RETRY = 0
        self.BAD_CHUNK_PERCENT = 0.0
        self.BAD_CHUNK_COUNT = 0
        self.BAD_CHUNKS = FILL_STRING_NOT_STARTED

    def __str__(self):
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

    def set_heal_log_params(self, \
                                meter_address         ,\
                                loop_no               ,\
                                healing_status        ,\
                                heal_start_time       ,\
                                total_healing_time    ,\
                                total_healing_retry   ,\
                                total_validation_retry,\
                                bad_chunk_percent     ,\
                                bad_chunk_count       ,\
                                bad_chunks            ):

        self.METER_ADDRESS              = meter_address                   
        self.LOOP_NO                    = loop_no                       
        self.HEALING_STATUS             = healing_status                
        self.HEAL_START_TIME            = heal_start_time           
        self.TOTAL_HEALING_TIME         = total_healing_time            
        self.TOTAL_HEALING_RETRY        = total_healing_retry           
        self.TOTAL_VALIDATION_RETRY     = total_validation_retry        
        self.BAD_CHUNK_PERCENT          = bad_chunk_percent         
        self.BAD_CHUNK_COUNT            = bad_chunk_count           
        self.BAD_CHUNKS                 = bad_chunks                     



class logData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """

    def __init__(self):

        
        self.SESSION_NUMBER = CONFIG_SESSION_NUMBER
        self.METER_ADDRESS = 0
        self.DATE_TIME = datetime.datetime.now()
        self.TYPE = FILL_STRING_NOT_STARTED
        self.STEP_NUMBER = 0        
        self.COMMENTS = FILL_STRING_NOT_STARTED


    def __str__(self):
        return ("SESSION_NUMBER: {}\n"
        "METER_ADDRESS: {} \n"
        "DATE_TIME: {} \n"
        "TYPE: {} \n"
        "STEP_NUMBER: {}\n"        
        "COMMENTS: {}").format(self.SESSION_NUMBER,
                            self.METER_ADDRESS,
                            self.DATE_TIME,
                            self.TYPE,
                            self.STEP_NUMBER,                            
                            self.COMMENTS)

    def set_log_params(self,\
                                meter_address ,\
                                _type         ,\
                                step_number   ,\
                                comments      ):
                     
        self.SESSION_NUMBER             = CONFIG_SESSION_NUMBER        
        self.METER_ADDRESS              = meter_address         
        self.DATE_TIME                  = datetime.datetime.now()        
        self.TYPE                       = _type             
        self.STEP_NUMBER                = step_number                   
        self.COMMENTS                   = comments


class scriptLogData(object):
    """
    This class is used to parse and store data recieved from GP Single 
    phase WiFi meters.
    """

    def __init__(self):

        
        self.SESSION_NUMBER = CONFIG_SESSION_NUMBER
        self.STEP_NUMBER = 0
        self.METER_ADDRESS = 0
        self.STATUS = FILL_STRING_NOT_STARTED
        self.COMMENTS = FILL_STRING_NOT_STARTED

    def __str__(self):
        return ("SESSION_NUMBER: {}\n"
        "STEP_NUMBER: {} \n"
        "METER_ADDRESS: {} \n"
        "STATUS: {} \n"
        "COMMENTS: {}").format(self.SESSION_NUMBER,
                            self.STEP_NUMBER,
                            self.METER_ADDRESS,
                            self.STATUS,
                            self.COMMENTS)

    def set_script_log_params(self,\
                                step_number             ,\
                                meter_address           ,\
                                status                  ,\
                                comments                ):

        self.SESSION_NUMBER = CONFIG_SESSION_NUMBER
        self.STEP_NUMBER = step_number
        self.METER_ADDRESS = meter_address
        self.STATUS = status
        self.COMMENTS = comments
        