import json
import datetime
import os
import sys
from os.path import expanduser
import time
import getpass


user=getpass.getuser()

RUN_DIR_STR = "/home/"+user+"/grampower/gp_node/gp_node/_1p_fw_upgrade/FOTA/Firmware upgrade Script"
UI_CONFIG_DIR_STR = "/home/"+user+"/fw_upgrade/FOTA_sync/ui_config.json"
BIN_FILE_DIR_STR = "/home/"+user+"/fw_upgrade/FOTA_sync/"
SLEEP_TIME = 5



CHECK_JSON = False
RUN_FOTA = False                      
CURRENT_TIME = datetime.datetime.now()
DATA_COLLECTION=True

def run():

    global CHECK_JSON           
    global RUN_FOTA             
    global SCRIPT_START_TIME    
    global CURRENT_TIME           
    global BIN_FILE_NAME        
    
    if os.path.exists(UI_CONFIG_DIR_STR) == True:
        print "json for FOTA available"
        CHECK_JSON = True

    else:
        print "json for FOTA not available"    
        CHECK_JSON = False  

    
    CURRENT_TIME = datetime.datetime.now()

    if CHECK_JSON == True:
        with open(UI_CONFIG_DIR_STR, 'r+') as file:
            str_ui_dict = file.read()
            file.close()   
            try:        
                ui_config_dict = json.loads(str_ui_dict)
            except Exception as e:
                print "UI config file corrupted, ERROR: ", str(e)
            else:
                RUN_FOTA = ui_config_dict['RUN_FOTA']
                SCRIPT_START_TIME = ui_config_dict['SCRIPT_START_TIME']
                BIN_FILE_NAME = ui_config_dict['BIN_FILE_NAME']
                # print 'RUN_FOTA         ',RUN_FOTA
                # print 'SCRIPT_START_TIME',SCRIPT_START_TIME 
                # print 'BIN_FILE_NAME    ',BIN_FILE_NAME 
        if RUN_FOTA != True:
            time.sleep(SLEEP_TIME)
        else:
            # print 'Checking time to schedule FOTA'    

            temp_str1 = trim_string(str(SCRIPT_START_TIME),10) # Date comparision only.
            temp_str2 = trim_string(str(CURRENT_TIME),10)
            # print 'Script start time is - ', temp_str1
            # print 'Current time is      - ', temp_str2

            if temp_str1 == temp_str2:
                print "Starting script to run firmware upgrade"
                os.chdir(RUN_DIR_STR)
                try:
                    os.system('supervisorctl stop conc-engine')
                    DATA_COLLECTION=False
                    a = os.system("/home/"+user+"/Envs/fw_upgrade/bin/python run.py -p " + str(BIN_FILE_DIR_STR) + str(BIN_FILE_NAME))
                except Exception as e:
                    print "Error caught in Fota main script >>> "+str(e)
                    pass
            else:
                print 'Waiting for scheduled time, ', temp_str1
                time.sleep(SLEEP_TIME)
                

    else:
        time.sleep(SLEEP_TIME)





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

if __name__ == "__main__":
    run()
    if DATA_COLLECTION is False:
        try:
            os.system('supervisorctl start conc-engine')
        except Exception as e:
            print "Error in starting of conc-engine"
            time.sleep(1)
            os.system('supervisorctl start conc-engine')

