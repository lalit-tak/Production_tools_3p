import threading
from threading import Thread 
import time
import socket
import paho.mqtt.client as mqtt
import datetime
import signal
import sys

# from Test_Cases_function import CasesThread
import os
import argparse

from Test_Cases_function import CasesThread
from config import config
import serial
import gp_node.utils.serialize as serialize
import json
import datetime
import easygui
# from config import config

def handler(signal, frame):
    print ("sys.exit from the script...Ctrl+C^")
    sys.exit()

def run():
    

    cfg = config()
    cfg.verify_config_json()

    # Serial Port
    ser = None
    portID = 19
    try:
        ser = serial.Serial(cfg.DEVICE, cfg.BAUDRATE, 
                        timeout=cfg.SERIAL_TIMEOUT)

    except (serial.serialutil.SerialException, OSError) as err:
            print(err)
            print "Cannot open serial port mentioned in config file"
            show_msg = "Cannot open serial port mentioned in config file"
            toolName = "Serial Port"
            easygui.msgbox(show_msg,toolName)
            os._exit(0)
            return

    # serial_num = int(input("Enter Serial Num: ")) 
    # while(1):       
        
    if ((cfg.TOOL_TYPE == 'RTT' or cfg.TOOL_TYPE == 'RTI') and cfg.IS_RF_WORKING == False):
        from Mqtt_connect import ClientThread
        clecthread = ClientThread()
        clecthread.start()
        NConfirm_Flag = True
        while(NConfirm_Flag):
            Confirmation = clecthread.Comfirmation_Of_Connection()
            if (Confirmation == True):
                NConfirm_Flag = False
                

    casecls = CasesThread(ser, portID)
    time.sleep(0.5)
    casecls.start()
    # wait until thread 1 is completely executed
    signal.signal(signal.SIGINT, handler)
    casecls.join()
    Msg_Value = casecls.GetResultMsg()
    # print "Returned"
    if ((cfg.TOOL_TYPE == 'RTT' or cfg.TOOL_TYPE == 'RTI') and cfg.IS_RF_WORKING == False):
        
        # print "In if"
        clecthread.TerminateExit()
        clecthread.join()
        # wait until thread 2 is completely executed
    ser.close()
    try:
        # print ("Deleting")
        del casecls
        # print ("Deleted casecls")
        del clecthread
        # print ("Deleted clecthread")
        del cfg
        # print ("Deleted cfg")
    except Exception as err:
        print ("Error in del instance")        
    print "Complete"
    show_msg = Msg_Value[0]
    toolName = Msg_Value[1]
    # print "Show msg",show_msg, toolName
    easygui.msgbox(show_msg,toolName)



    

if __name__ == "__main__":
    while (1):
        print "Starting..............."
        run()
