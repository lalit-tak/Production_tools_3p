import time
import sys
import os
import serial
import copy
from framework_files.config.config import config
from procedure import test_case_procedures

def run():

    cfg = config()
    # Reading configuration and logs
    cfg.verify_config_json()

    # Serial Port
    ser = None
    try:
        ser = serial.Serial(cfg.DEVICE, cfg.BAUDRATE, 
                        timeout=cfg.SERIAL_TIMEOUT)

    except (serial.serialutil.SerialException, OSError) as err:
            print(err)
            print "Cannot open serial port mentioned in config file"
            return


    case = test_case_procedures(cfg, ser)   

    # If serial port and json is available than 
    # take input of serial number        
        # case.mri_101()
        # case.mri_104()
        # case.mri_105()
        # case.mri_106()
    # case.test_case_101()
    case.test_case_102()
        # case.mri_102(serial_num)
        # case.mri_103(address)


if __name__ == "__main__":
    run()
