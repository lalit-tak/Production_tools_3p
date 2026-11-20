import json
import datetime
import time
import getpass


user=getpass.getuser()


"""
This is the configuration file to configure the configurable parameters 
of firmware upgrade process.
"""
###################### Directory to read ui_config ###################

SYNC_LOCATION = "/home/" + user + "/fw_upgrade/FOTA_sync"
UI_CONFIG_DIR_STR = SYNC_LOCATION + '/' + 'ui_config.json'
RUN_FOTA = False

######################################################################


############################ MySql Configuration #####################
SQL_USER = 'root'
SQL_PASSWORD = 'grampower'
SQL_SERVER_IP = 'localhost'
SQL_SERVER_PORT = '3306'
DATABASE_NAME = 'fw_upgrade'
SQL_CONNECT_STRING = 'mysql://' + SQL_USER + ':' + SQL_PASSWORD + '@' + SQL_SERVER_IP + ':' + SQL_SERVER_PORT +'/' + DATABASE_NAME
SQL_CREATE_STRING = 'mysql://' + SQL_USER + ':' + SQL_PASSWORD + '@' + SQL_SERVER_IP + ':' + SQL_SERVER_PORT

######################################################################


############################ Meter Address List ######################
meter_address_dict = {}
AddressList_1P = {}
######################################################################


######################### Log Table Parameters #######################
LOG_TYPE_NORMAL                     = 'Normal'
LOG_TYPE_ERROR                      = 'Error'
LOG_DEFAULT_METER_ADDRESS           = 0
LOG_COMMENTS_RUN_EXECUTED           = 'Run Executed'
SCRIPT_LOG_STATUS_NOT_STARTED       = 'Not Started'
SCRIPT_LOG_STATUS_IN_PROGRESS       = 'In Progress'
SCRIPT_LOG_STATUS_COMPLETED         = 'Completed'
SCRIPT_LOG_METER_ISSUE              = 'Issue with meter'
SCRIPT_LOG_BROADCAST_ADDRESS        = 'Broadcast address'
SCRIPT_LOG_STATUS_DONE              = 'Done'
######################################################################


############################ Basic Configuration #####################
CONFIG_SESSION_NUMBER               = 97
BROADCAST_FLASH_START_ADDRESS       = 0x100
HEAL_FLASH_START_ADDRESS            = 256
TOTAL_HEALING_LOOP_COUNT            = 4
RESTART_LOOP_COUNT                  = 4
THRESHOLD_FOR_BURN_NACK             = 100.1
BAUDRATE                            = 19200
CRC_VALUE_FOR_ERASED_CHUNK          = 0
ENTRY_AUTO_DELETION                 = True
EMPTY_CHUNK_VALUE                   = 8867
DEVICE                              = "/dev/gp-gateway"
####################### Basic Configuration ##########################

####################### Time Configuration ###########################
UPDATE_RESULT_WAIT                  = 50
SERIAL_TIMEOUT                      = 5
BROADCAST_DELAY_BETWEEN_PACKETS     = 0.5
HEALING_DELAY_BETWEEN_PACKETS       = 0.5
HEALTH_DELAY_BETWEEN_PACKETS        = 0.5
######################################################################

############################ Retries #################################
HEALING_RETRY                       = 12
HEALING_VALIDATION_RETRY            = 3
ERASE_FLASH_RETRY                   = 10
SECTOR_READ_RETRY                   = 4
BLOCK_READ_RETRY                    = 8
############################ Retries #################################

############################ Table names #############################
RESULT_TABLE_NAME   = 'Result'
STATUS_TABLE_NAME =  'Status'
ERASE_LOG_TABLE_NAME = 'Erase'
HEALTH_LOG_TABLE_NAME = 'Health'
HEAL_LOG_TABLE_NAME = 'Heal'
LOG_TABLE_NAME = 'Log'
SCRIPT_LOG_TABLE_NAME = 'Process Vault'
######################################################################

############################ Step numbers ############################
TOTAL_STEPS                         = 12
CONFIG_STEP_NO                      = 0 
RUN_STEP_NO                         = 1
DATABASE_VALIDATION_STEP_NO         = 2
DATABASE_HANDLER_STEP_NO            = 3
ORM_MODEL_STEP_NO                   = 4
ORM_OBJECTS_STEP_NO                 = 5
UPDATE_FIRMWARE_HEALTH_STEP_NO      = 6
ERASE_FLASH_STEP_NO                 = 7
BROADCAST_STEP_NO                   = 8
UPDATE_HEALTH_STEP_NO               = 9
HEAL_BY_CHUNK_STEP_NO               = 10
UPDATE_STATUS_STEP_NO               = 11
RESET_AND_UPDATE_RESULT_STEP_NO     = 12

STEP_NAME = {}

STEP_NAME[CONFIG_STEP_NO]                   = 'CONFIG'                   
STEP_NAME[RUN_STEP_NO]                      = 'RUN'   
STEP_NAME[DATABASE_VALIDATION_STEP_NO]      = 'DATABASE_VALIDATION' 
STEP_NAME[DATABASE_HANDLER_STEP_NO]         = 'DATABASE_HANDLER' 
STEP_NAME[ORM_MODEL_STEP_NO]                = 'ORM_MODEL' 
STEP_NAME[ORM_OBJECTS_STEP_NO]              = 'ORM_OBJECTS' 
STEP_NAME[UPDATE_FIRMWARE_HEALTH_STEP_NO]   = 'UPDATE_FIRMWARE_HEALTH' 
STEP_NAME[ERASE_FLASH_STEP_NO]              = 'ERASE_FLASH' 
STEP_NAME[BROADCAST_STEP_NO]                = 'BROADCAST' 
STEP_NAME[UPDATE_HEALTH_STEP_NO]            = 'UPDATE_HEALTH' 
STEP_NAME[HEAL_BY_CHUNK_STEP_NO]            = 'HEAL_BY_CHUNK' 
STEP_NAME[UPDATE_STATUS_STEP_NO]            = 'UPDATE_STATUS' 
STEP_NAME[RESET_AND_UPDATE_RESULT_STEP_NO]  = 'RESET_AND_UPDATE_RESULT' 
######################################################################

########################## Fill Strings ##############################
FILL_STRING_NOT_STARTED = "Not Started"
FILL_STRING_ERROR = "Error Occured"
FILL_STRING_SUCCESS = "Success"
FILL_STRING_NO_BAD_CHUNK = "No bad chunk left"
FILL_STRING_BLACKLIST = "Blacklisted"
######################################################################

################## Display Configuration Parameters ##################
STEP_DISPLAY_SIZE       = 16
STRING_DISPLAY_SIZE     = 80
ADDRESS_DISPLAY_SIZE    = 6
STATUS_DISPLAY_SIZE     = 6
RETRY_DISPLAY_SIZE      = 2
STRING_DIVIDER          = ' : '
######################################################################





def get_meter_address_from_dcu():
    """
    This method reads .txt file present in DCU and collects meter
    address present in DCU. 

    @param 1: No params.
    @return : True/False 
                True : At least one meter address found.
                False : If no address available.

    """

    """
    Check at least one meter should be there (Handeled only here)   
    """ 
    # meter_address_dict[0] = "0.0.0.2"     # Change into reading from DCU
    # meter_address_dict[1] = "0.0.0.3"
    # meter_address_dict[2] = "0.0.0.4"
    # meter_address_dict[3] = "0.0.0.5"


    if len(meter_address_dict) > 0:

        for i in range(0,len(meter_address_dict)):
            AddressList_1P[i] = meter_address_dict[i]
        return True
    else:
        return False


def get_meter_address_index(meter_address):
    """
    This method returns index of dictionary whose value matches 
    with input address.

    @param 1: meter address of integer type.
    @return : index of dictionary whose value matches with input address.
    """

    for i in range(0, len(AddressList_1P)):
        
        addr = str(AddressList_1P[i])  
        d = addr.split('.') 
        meter_id = (int(d[0])<<24)+(int(d[1])<<16)+(int(d[2])<<8)+(int(d[3])<<0)

        if meter_id == meter_address:
            return i
    return int(1000)


def convert_address_to_int(address):
    """
    This method converts string type meter address to integer

    @param 1: address of string type.
    @return : address of int type.
    """


    d = address.split('.')                
    meter_id = (int(d[0])<<24)+(int(d[1])<<16)+(int(d[2])<<8)+(int(d[3])<<0)   
    return meter_id


def trim_string(string, size):
    """
    This method trims string from right if smaller size provided than its 
     actual length and it fill spaces on right if larger size provided  

    @param 1: string of any size.
    @param 2: Size for output string.

    @return : string.
    """

    if int(len(string)) > int(size):
        return_str = string[:int(size)]
        return return_str
    else:
        return_str = string.ljust(size)
        return return_str


def update_config():

    global CONFIG_SESSION_NUMBER          
    global BROADCAST_FLASH_START_ADDRESS  
    global HEAL_FLASH_START_ADDRESS       
    global TOTAL_HEALING_LOOP_COUNT       
    global RESTART_LOOP_COUNT             
    global THRESHOLD_FOR_BURN_NACK        
    global BAUDRATE                       
    global CRC_VALUE_FOR_ERASED_CHUNK     
    global ENTRY_AUTO_DELETION            
    global EMPTY_CHUNK_VALUE              
    global UPDATE_RESULT_WAIT             
    global SERIAL_TIMEOUT                 
    global BROADCAST_DELAY_BETWEEN_PACKETS
    global HEALING_DELAY_BETWEEN_PACKETS  
    global HEALTH_DELAY_BETWEEN_PACKETS   
    global HEALING_RETRY                  
    global HEALING_VALIDATION_RETRY       
    global ERASE_FLASH_RETRY              
    global SECTOR_READ_RETRY              
    global BLOCK_READ_RETRY               
    global RUN_FOTA                       
    global SCRIPT_START_TIME 
    global BIN_FILE_NAME
    global NO_OF_METERS
    global meter_address_dict




    with open(UI_CONFIG_DIR_STR, 'r+') as file:
        str_ui_dict = file.read()
        file.close()   
        try:        
            ui_config_dict = json.loads(str_ui_dict)

            CONFIG_SESSION_NUMBER              = ui_config_dict['CONFIG_SESSION_NUMBER']                
            BROADCAST_FLASH_START_ADDRESS      = ui_config_dict['BROADCAST_FLASH_START_ADDRESS']            
            HEAL_FLASH_START_ADDRESS           = ui_config_dict['HEAL_FLASH_START_ADDRESS']         
            TOTAL_HEALING_LOOP_COUNT           = ui_config_dict['TOTAL_HEALING_LOOP_COUNT']                 
            RESTART_LOOP_COUNT                 = ui_config_dict['RESTART_LOOP_COUNT']                        
            THRESHOLD_FOR_BURN_NACK            = ui_config_dict['THRESHOLD_FOR_BURN_NACK']                  
            BAUDRATE                           = ui_config_dict['BAUDRATE']                          
            CRC_VALUE_FOR_ERASED_CHUNK         = ui_config_dict['CRC_VALUE_FOR_ERASED_CHUNK']           
            ENTRY_AUTO_DELETION                = ui_config_dict['ENTRY_AUTO_DELETION']                    
            EMPTY_CHUNK_VALUE                  = ui_config_dict['EMPTY_CHUNK_VALUE']                       
            UPDATE_RESULT_WAIT                 = ui_config_dict['UPDATE_RESULT_WAIT']                        
            SERIAL_TIMEOUT                     = ui_config_dict['SERIAL_TIMEOUT']                            
            BROADCAST_DELAY_BETWEEN_PACKETS    = ui_config_dict['BROADCAST_DELAY_BETWEEN_PACKETS']              
            HEALING_DELAY_BETWEEN_PACKETS      = ui_config_dict['HEALING_DELAY_BETWEEN_PACKETS']                    
            HEALTH_DELAY_BETWEEN_PACKETS       = ui_config_dict['HEALTH_DELAY_BETWEEN_PACKETS']                 
            HEALING_RETRY                      = ui_config_dict['HEALING_RETRY']                               
            HEALING_VALIDATION_RETRY           = ui_config_dict['HEALING_VALIDATION_RETRY']             
            ERASE_FLASH_RETRY                  = ui_config_dict['ERASE_FLASH_RETRY']                     
            SECTOR_READ_RETRY                  = ui_config_dict['SECTOR_READ_RETRY']                          
            BLOCK_READ_RETRY                   = ui_config_dict['BLOCK_READ_RETRY']                           
            RUN_FOTA                           = ui_config_dict['RUN_FOTA']                              
            SCRIPT_START_TIME                  = ui_config_dict['SCRIPT_START_TIME'] 
            BIN_FILE_NAME                      = ui_config_dict['BIN_FILE_NAME'] 
            NO_OF_METERS                       = ui_config_dict['NO_OF_METERS']

        except Exception as e:
            print "UI config file corrupted, ERROR: ",e
            # db.display(CONFIG_STEP_NO, str("UI config file corrupted, ERROR: " + str(e)),\
            #     upper_space = 2, lower_space = 2, status = LOG_TYPE_ERROR, logging = True)    
            return False
        else:
            if int(NO_OF_METERS) < 1:
                print "No meter address available in UI config file"
                # db.display(CONFIG_STEP_NO, "No meter address available in UI config file",\
                # upper_space = 2, lower_space = 2, status = LOG_TYPE_ERROR, logging = True) 
                return False
            else:
                #db.display(CONFIG_STEP_NO, str(str_ui_dict), logging = True, printing = False) # Logging complete UI file in log table
                
                #db.display(CONFIG_STEP_NO, str('UI config file data...................................'))
                
                for p in range(0,int(NO_OF_METERS)):
                    meter_address_dict[p] = ui_config_dict[str(p)]
                    #db.display(CONFIG_STEP_NO, str('Meter Address : ' + str(meter_address_dict[p])))


                print 'CONFIG_SESSION_NUMBER          ',CONFIG_SESSION_NUMBER
                print 'BROADCAST_FLASH_START_ADDRESS  ',BROADCAST_FLASH_START_ADDRESS
                print 'HEAL_FLASH_START_ADDRESS       ',HEAL_FLASH_START_ADDRESS
                print 'TOTAL_HEALING_LOOP_COUNT       ',TOTAL_HEALING_LOOP_COUNT 
                print 'RESTART_LOOP_COUNT             ',RESTART_LOOP_COUNT
                print 'THRESHOLD_FOR_BURN_NACK        ',THRESHOLD_FOR_BURN_NACK 
                print 'BAUDRATE                       ',BAUDRATE
                print 'CRC_VALUE_FOR_ERASED_CHUNK     ',CRC_VALUE_FOR_ERASED_CHUNK 
                print 'ENTRY_AUTO_DELETION            ',ENTRY_AUTO_DELETION
                print 'EMPTY_CHUNK_VALUE              ',EMPTY_CHUNK_VALUE 
                print 'UPDATE_RESULT_WAIT             ',UPDATE_RESULT_WAIT 
                print 'SERIAL_TIMEOUT                 ',SERIAL_TIMEOUT 
                print 'BROADCAST_DELAY_BETWEEN_PACKETS',BROADCAST_DELAY_BETWEEN_PACKETS 
                print 'HEALING_DELAY_BETWEEN_PACKETS  ',HEALING_DELAY_BETWEEN_PACKETS 
                print 'HEALTH_DELAY_BETWEEN_PACKETS   ',HEALTH_DELAY_BETWEEN_PACKETS 
                print 'HEALING_RETRY                  ',HEALING_RETRY 
                print 'HEALING_VALIDATION_RETRY       ',HEALING_VALIDATION_RETRY 
                print 'ERASE_FLASH_RETRY              ',ERASE_FLASH_RETRY 
                print 'SECTOR_READ_RETRY              ',SECTOR_READ_RETRY 
                print 'BLOCK_READ_RETRY               ',BLOCK_READ_RETRY 
                print 'RUN_FOTA                       ',RUN_FOTA 
                print 'SCRIPT_START_TIME              ',SCRIPT_START_TIME   
                print 'BIN_FILE_NAME                  ',BIN_FILE_NAME                 

                # db.display(CONFIG_STEP_NO, str('CONFIG_SESSION_NUMBER          ' + str(CONFIG_SESSION_NUMBER))) 
                # db.display(CONFIG_STEP_NO, str('BROADCAST_FLASH_START_ADDRESS  ' + str(BROADCAST_FLASH_START_ADDRESS)))
                # db.display(CONFIG_STEP_NO, str('HEAL_FLASH_START_ADDRESS       ' + str(HEAL_FLASH_START_ADDRESS))) 
                # db.display(CONFIG_STEP_NO, str('TOTAL_HEALING_LOOP_COUNT       ' + str(TOTAL_HEALING_LOOP_COUNT))) 
                # db.display(CONFIG_STEP_NO, str('RESTART_LOOP_COUNT             ' + str(RESTART_LOOP_COUNT))) 
                # db.display(CONFIG_STEP_NO, str('THRESHOLD_FOR_BURN_NACK        ' + str(THRESHOLD_FOR_BURN_NACK))) 
                # db.display(CONFIG_STEP_NO, str('BAUDRATE                       ' + str(BAUDRATE))) 
                # db.display(CONFIG_STEP_NO, str('CRC_VALUE_FOR_ERASED_CHUNK     ' + str(CRC_VALUE_FOR_ERASED_CHUNK))) 
                # db.display(CONFIG_STEP_NO, str('ENTRY_AUTO_DELETION            ' + str(ENTRY_AUTO_DELETION))) 
                # db.display(CONFIG_STEP_NO, str('EMPTY_CHUNK_VALUE              ' + str(EMPTY_CHUNK_VALUE))) 
                # db.display(CONFIG_STEP_NO, str('UPDATE_RESULT_WAIT             ' + str(UPDATE_RESULT_WAIT))) 
                # db.display(CONFIG_STEP_NO, str('SERIAL_TIMEOUT                 ' + str(SERIAL_TIMEOUT)))
                # db.display(CONFIG_STEP_NO, str('BROADCAST_DELAY_BETWEEN_PACKETS' + str(BROADCAST_DELAY_BETWEEN_PACKETS)))
                # db.display(CONFIG_STEP_NO, str('HEALING_DELAY_BETWEEN_PACKETS  ' + str(HEALING_DELAY_BETWEEN_PACKETS)))
                # db.display(CONFIG_STEP_NO, str('HEALTH_DELAY_BETWEEN_PACKETS   ' + str(HEALTH_DELAY_BETWEEN_PACKETS)))
                # db.display(CONFIG_STEP_NO, str('HEALING_RETRY                  ' + str(HEALING_RETRY)))
                # db.display(CONFIG_STEP_NO, str('HEALING_VALIDATION_RETRY       ' + str(HEALING_VALIDATION_RETRY)))
                # db.display(CONFIG_STEP_NO, str('ERASE_FLASH_RETRY              ' + str(ERASE_FLASH_RETRY)))
                # db.display(CONFIG_STEP_NO, str('SECTOR_READ_RETRY              ' + str(SECTOR_READ_RETRY)))
                # db.display(CONFIG_STEP_NO, str('BLOCK_READ_RETRY               ' + str(BLOCK_READ_RETRY)))
                # db.display(CONFIG_STEP_NO, str('RUN_FOTA                       ' + str(RUN_FOTA)))
                # db.display(CONFIG_STEP_NO, str('SCRIPT_START_TIME              ' + str(SCRIPT_START_TIME)))  
                # db.display(CONFIG_STEP_NO, str('BIN_FILE_NAME                  ' + str(BIN_FILE_NAME)))


                return True        
                 

if __name__ == "__main__":
    update_config()
