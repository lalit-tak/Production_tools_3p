import json
import datetime
"""
This file generates ui_config.json if we manually wangt to generate it.
"""
###################### Directory to create ui_config ###################

UI_CONFIG_DIR_STR = 'C:\\Users\\paree\\Desktop\\ui_config.json'

#####################################################################


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


    a = datetime.datetime.now()
    ui_dict = {\
                'CONFIG_SESSION_NUMBER':3007,\
                'BROADCAST_FLASH_START_ADDRESS':0x100,\
                'HEAL_FLASH_START_ADDRESS':256,\
                'TOTAL_HEALING_LOOP_COUNT':4,\
                'RESTART_LOOP_COUNT':4,\
                'THRESHOLD_FOR_BURN_NACK':100.1,\
                'BAUDRATE':19200,\
                'CRC_VALUE_FOR_ERASED_CHUNK':0,\
                'ENTRY_AUTO_DELETION':True,\
                'EMPTY_CHUNK_VALUE':8867,\
                'UPDATE_RESULT_WAIT':50,\
                'SERIAL_TIMEOUT':3,\
                'BROADCAST_DELAY_BETWEEN_PACKETS':0.5,\
                'HEALING_DELAY_BETWEEN_PACKETS':0.5,\
                'HEALTH_DELAY_BETWEEN_PACKETS':0.5,\
                'HEALING_RETRY':12,\
                'HEALING_VALIDATION_RETRY':5,\
                'ERASE_FLASH_RETRY':5,\
                'SECTOR_READ_RETRY':5,\
                'BLOCK_READ_RETRY':8,\
                'RUN_FOTA': True,\
                'SCRIPT_START_TIME': str(a),\
                'BIN_FILE_NAME': 'out_3007.bin',\
                'NO_OF_METERS':1,\
                0:"9.9.9.2"\
            }

    str_ui_dict = json.dumps(ui_dict)
    with open(UI_CONFIG_DIR_STR, 'w') as file:
        file.write(str_ui_dict)
        file.close()    



if __name__ == "__main__":
    update_config()