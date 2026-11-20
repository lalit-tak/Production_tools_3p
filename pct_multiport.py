import os
import argparse
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._1p.flash_io_new import FlashIOMasterNew, FlashIOErrorNew
from gp_node.utils.address import Address
import serial
import serial.tools.list_ports
import gp_node.utils.serialize as serialize
import json
import datetime
import time
import threading
from threading import Thread 
import time
import socket
import paho.mqtt.client as mqtt
import signal
import sys
from config import Config
from Test_cases_verificationClass import TestCasePCTMCT
import easygui
from queue import Queue
from colorama import Fore, Style, init
import win32com.client
import pythoncom
import logging
from logging.handlers import TimedRotatingFileHandler
import openpyxl
import tkinter as tk
import pandas as pd
import db_connect

ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"
bucket_name = "PUT_YOUR_BUCKET_NAME_HERE"
folder_name = "PUT_YOUR_FOLDER_NAME_HERE"

global abort_threads
global portID

def get_system_mac_address(toolname):
    mac = "None"
    try:
        if sys.platform == 'win32': 
            for line in os.popen("ipconfig /all"): 
                if line.lstrip().startswith('Physical Address'): 
                    mac = line.split(':')[1].strip().replace('-',':') 
                    break 
        else: 
            for line in os.popen("/sbin/ifconfig"): 
                if line.find('Ether') > -1: 
                    mac = line.split()[4] 
                    break
    except Exception as e:
        msg = "MAC ADDRESS NOT FOUND"
        easygui.msgbox(msg, title = (str(toolname)+str("|| GRAMPOWER")))#title="METER CUSTOMISATION TOOL || GRAMPOWER")
        sys.exit("Restart Tool")
    return mac        

def verify_log_xlsc(bookName,fileName):
    loc = bookName
    try:
        wb = openpyxl.load_workbook(loc)
        sheet = wb.active
        cell_value = sheet.cell(row=1, column=1).value
    except Exception as e:
        print("LOG XL file not found, creating one for you", str(e))
        wb = openpyxl.Workbook()
        wb.create_sheet(index = 0 , title = fileName) # MRI_DATA_LOG
        sheet = wb.active 
        print("sheet name = ",sheet.title)
        del(wb['Sheet'])
        wb.save(loc)
        print("New xlsc file created")
        return False
    else:
        return True 

def close_excel_file(filepath):
    pythoncom.CoInitialize()
    filepath = os.path.abspath(filepath)

    try:
        excel = win32com.client.GetObject(Class="Excel.Application")
    except Exception:
        # Excel is not running
        return False

    try:
        for wb in excel.Workbooks:
            if wb.FullName.lower() == filepath.lower():
                print("Closing Excel file:", filepath)
                wb.Close(SaveChanges=False)

                if excel.Workbooks.Count == 0:
                    excel.Quit()

                time.sleep(1)
                return True

    except Exception as e:
        print("Error while closing workbook:", e)

    return False

def add_log_xlsc(log, row_state):
    print("add_log_xlsc log = ",log)
    print("add_log_xlsc row_state = ",row_state)
    mac_address=log[0]
    MeterInfo=log[1]
    testResult=log[2]
    bookName=log[3]
    fileName=log[4]

    loc = bookName
    wb = openpyxl.load_workbook(loc)
    sheet = wb.active

    if(row_state == True):
        numRows = sheet.max_row
    else:
        numRows = sheet.max_row + 1

    wb = openpyxl.load_workbook(loc)
    sheet1 = wb[fileName]
    colx = 1
    cellToWrite = sheet1.cell(numRows,colx)
    cellToWrite.value = mac_address
    colx += 1
    if numRows > 1:
        cellToWrite = sheet1.cell(row=numRows, column=colx)
        cellToWrite.value = numRows - 1
        colx += 1

    for loopCount in range(len(MeterInfo)):
        cellToWrite = sheet1.cell(row=numRows, column=colx)
        data = MeterInfo[loopCount]
        cellToWrite.value = data
        colx += 1

    for loopCount in range(len(testResult)):
        cellToWrite = sheet1.cell(row=numRows, column=colx)
        data = testResult[loopCount]
        cellToWrite.value = data
        colx += 1

    wb.save(loc)
    
def addDefaultPCTLog(bookName, fileName, METER_TYPE):
    xyz=[]
    if False == verify_log_xlsc(bookName, fileName):
        print("xlsx file for log not found. creating one to store test report")
        result = []
        mac = "MAC_ADDR"
        # if "ltct" in METER_TYPE:
        #     MeterInfo = ['Index', 'Date_time', "CurrentR", "CurrentY", "CurrentB", "CurrentN", "live_tamper", "VoltageR", "VoltageY", "VoltageB","Set_Time_Value",'Meter_PCB_Serial_No','Nic_PCB_No', 'Meter_SERIAL_NUM','Manufacturing_Year','Live_Version','Internal_Version','Overall_Result']
        #     result = ['Factory_Reset', 'Verify_Current_in_all_CT', 'Verify_Voltage', 'Set_Time', 'Set_Meter_PCB_No','Set_Nic_PCB_No', 'Calibration_Unlock', 'Meter_Serial_Num', 'Set_Manufacturing_Year', 'live_version','Get_Internal_Version', 'Verify_DIDO_Status', 'Verify_Bootloader_Version', 'Set_Sim_Toggle', 'Set_GPRS_Protocol','Get_GPRS_Protocol']

        # elif "wc" in METER_TYPE:
        #     MeterInfo = ['Index', 'Date_time', "CurrentR", "CurrentY", "CurrentB", "CurrentN", "live_tamper", "VoltageR", "VoltageY", "VoltageB","Set_Time_Value",'Meter_PCB_Serial_No','Nic_PCB_No', 'Meter_SERIAL_NUM','Manufacturing_Year','Live_Version','Internal_Version','Overall_Result']
        #     result = ['Factory_Reset', 'Verify_Current_in_all_CT', 'Verify_Voltage', "Relay Off", 'Set_Time', 'Set_Meter_PCB_No','Set_Nic_PCB_No', 'Calibration_Unlock', 'Meter_Serial_Num', 'Set_Manufacturing_Year', 'live_version','Get_Internal_Version', 'Verify_Bootloader_Version', "After Relay Off Verify Current", 'Relay On', 'Set_Sim_Toggle', 'Set_GPRS_Protocol','Get_GPRS_Protocol']
        
        # else:
        #     MeterInfo = ['Index', 'Date_time', "CurrentR", "CurrentY", "CurrentB", "CurrentN", "live_tamper", "VoltageR", "VoltageY", "VoltageB","Set_Time_Value",'Meter_PCB_Serial_No','Nic_PCB_No', 'Meter_SERIAL_NUM','Manufacturing_Year','Live_Version','Internal_Version','Overall_Result']
        #     result = ['Factory_Reset', 'Verify_Current_in_all_CT', 'Verify_Voltage', "Relay Off", 'Set_Time', 'Set_Meter_PCB_No','Set_Nic_PCB_No', 'Calibration_Unlock', 'Meter_Serial_Num', 'Set_Manufacturing_Year', 'live_version','Get_Internal_Version', 'Verify_Bootloader_Version', "After Relay Off Verify Current", 'Relay On', 'Set_Sim_Toggle', 'Set_GPRS_Protocol','Get_GPRS_Protocol']

        if "ltct" in METER_TYPE:
            MeterInfo = ['Index', 'Date_time', "CurrentR", "CurrentY", "CurrentB", "CurrentN", "live_tamper", "VoltageR", "VoltageY", "VoltageB","Set_Time_Value",'Meter_PCB_Serial_No','Nic_PCB_No', 'Meter_SERIAL_NUM','Manufacturing_Year','Live_Version','Internal_Version','DIDO_Value', 'Bootloader_Version', 'GPRS_Protocol','Overall_Result']
            result = ['Factory_Reset', 'Verify_Current_in_all_CT', 'Verify_Voltage', 'Set_Time', 'Set_Meter_PCB_No','Set_Nic_PCB_No', 'Calibration_Unlock', 'Meter_Serial_Num', 'Set_Manufacturing_Year', 'live_version','Get_Internal_Version', 'Verify_DIDO_Status', 'Verify_Bootloader_Version', 'Set_Sim_Toggle', 'Set_GPRS_Protocol','Get_GPRS_Protocol']

        elif "wc" in METER_TYPE:
            MeterInfo = ['Index', 'Date_time', "CurrentR", "CurrentY", "CurrentB", "CurrentN", "live_tamper", "VoltageR", "VoltageY", "VoltageB","Set_Time_Value",'Meter_PCB_Serial_No','Nic_PCB_No', 'Meter_SERIAL_NUM','Manufacturing_Year','Live_Version','Internal_Version', 'Bootloader_Version', "CurrentR_After_Relay_Off", "CurrentY_After_Relay_Off", "CurrentB_After_Relay_Off", "CurrentN_After_Relay_Off", "Live_Temper_After_Relay_Off",'GPRS_Protocol','Overall_Result']
            result = ['Factory_Reset', 'Verify_Current_in_all_CT', 'Verify_Voltage', "Relay Off", 'Set_Time', 'Set_Meter_PCB_No','Set_Nic_PCB_No', 'Calibration_Unlock', 'Meter_Serial_Num', 'Set_Manufacturing_Year', 'live_version','Get_Internal_Version', 'Verify_Bootloader_Version', "After Relay Off Verify Current", 'Relay On', 'Set_Sim_Toggle', 'Set_GPRS_Protocol','Get_GPRS_Protocol']

        else:
            MeterInfo = ['Index', 'Date_time', "CurrentR", "CurrentY", "CurrentB", "CurrentN", "live_tamper", "VoltageR", "VoltageY", "VoltageB","Set_Time_Value",'Meter_PCB_Serial_No','Nic_PCB_No', 'Meter_SERIAL_NUM','Manufacturing_Year','Live_Version','Internal_Version', 'Bootloader_Version', "CurrentR_After_Relay_Off", "CurrentY_After_Relay_Off", "CurrentB_After_Relay_Off", "CurrentN_After_Relay_Off", "Live_Temper_After_Relay_Off",'GPRS_Protocol','Overall_Result']
            result = ['Factory_Reset', 'Verify_Current_in_all_CT', 'Verify_Voltage', "Relay Off", 'Set_Time', 'Set_Meter_PCB_No','Set_Nic_PCB_No', 'Calibration_Unlock', 'Meter_Serial_Num', 'Set_Manufacturing_Year', 'live_version','Get_Internal_Version', 'Verify_Bootloader_Version', "After Relay Off Verify Current", 'Relay On', 'Set_Sim_Toggle', 'Set_GPRS_Protocol','Get_GPRS_Protocol']

        xyz.append(result_log_dump(mac,MeterInfo,result,bookName,fileName,[]))
        row_status = True
        close_excel_file(bookName)
        add_log_xlsc(xyz[0],row_status)

def result_log_dump(mac,MeterInfo,result_list,bookName,fileName,result_to_save):
    result_to_save.append(mac)
    result_to_save.append(MeterInfo)
    result_to_save.append(result_list)
    result_to_save.append(bookName)
    result_to_save.append(fileName)
    return result_to_save

class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def parse_event_to_dict(raw_text):
    result = {}

    for line in raw_text.splitlines():
        if ':' not in line:
            continue

        key, value = line.split(':', 1)

        key = key.strip()
        value = value.strip()

        if key:  # ignore empty keys
            result[key] = value

    return result

def main_function(data_dict, com_port,meter_serial_num, pcb_serial_num, Nic_pcb_num,result_queue,abort_flag,result_log):
    setup_logger()
    logging.info(f"user input:")
    logging.info(f"Meter serial number: {meter_serial_num}")
    logging.info(f"PCB serial number: {pcb_serial_num}")
    logging.info(f"NIC PCB serial number: {Nic_pcb_num}")
    try:
        ser = serial.Serial(com_port, baudrate=9600, timeout=10)
        if not ser:
            return 0
        portID=4
        cases = TestCasePCTMCT(ser, portID, data_dict.get("RETRIES", 3))
        toolname = data_dict.get("TOOL_TYPE", "img_pct").lower()
        mac = get_system_mac_address(toolname)
        result_list = []
        MeterInfo = []
        result_save=[]
        fail_indexes = []
        ResultFinal=''
        pcb_start_address = 3079
        nic_start_address = 3111
        meter_type = data_dict.get("METER_TYPE", "3PWC")
        bookName = meter_type.upper() +"_"+ toolname.upper() +"_LOG.xlsx"
        fileName = toolname.upper() + "_DATA_LOG"
        starttime = datetime.datetime.now()
        print ("\nStartTime:",starttime, com_port)

        START_ADDRESS = 0x0100
        METER_ADDRESS = "255.255.255.255"


        
        Date_time=datetime.datetime.now()
        MeterInfo.append(Date_time)
        # close_excel_file(bookName)
        addDefaultPCTLog(bookName, fileName, meter_type.lower())
        if "ltct" in meter_type.lower():
            PCT_Fail_list = ['Fail in Factory Reset', 'Fail in Verify Current or CT connections are Reverse', 'Fail in Verify Voltage', 'Fail in Set Time', 'Fail in set Meter PCB No', 'Fail in Set NIC PCB No', 'Fail in Calib Unlock', 'Fail in set Meter Serial No', 'Fail in Set Manufacturing Year', 'Fail in Get live version','Fail in Get Internal Version', 'Fail in Verify DIDO Status', 'Fail in Verify Bootloader Version', 'Fail in Set Sim Toggle','Fail in Set GPRS Protocol','Fail in Get GPRS Protocol']
        elif "wc" in meter_type.lower():
            PCT_Fail_list = ['Fail in Factory Reset', 'Fail in Verify Current or CT connections are Reverse', 'Fail in Verify Voltage', 'Fail in  Relay Off', 'Fail in Set Time', 'Fail in set Meter PCB No', 'Fail in Set NIC PCB No', 'Fail in Calib Unlock', 'Fail in set Meter Serial No', 'Fail in Set Manufacturing Year', 'Fail in Get live version','Fail in Get Internal Version', 'Fail in Verify Bootloader Version', 'Fail in After Relay Off Verify Current', 'Fail in  Relay On', 'Fail in Set Sim Toggle','Fail in Set GPRS Protocol','Fail in Get GPRS Protocol']
        else:
            PCT_Fail_list = ['Fail in Factory Reset', 'Fail in Verify Current or CT connections are Reverse', 'Fail in Verify Voltage', 'Fail in  Relay Off', 'Fail in Set Time', 'Fail in set Meter PCB No', 'Fail in Set NIC PCB No', 'Fail in Calib Unlock', 'Fail in set Meter Serial No', 'Fail in Set Manufacturing Year', 'Fail in Get live version','Fail in Get Internal Version', 'Fail in Verify Bootloader Version', 'Fail in After Relay Off Verify Current', 'Fail in  Relay On', 'Fail in Set Sim Toggle','Fail in Set GPRS Protocol',' Fail in Get GPRS Protocol']
            
        
        # Live version with check port
        retryCnt = 3
        logging.info("Checking COM port connectivity and fetching live version...")
        while retryCnt:
            try:
                check_port = cases.get_live_version_val_check_port()
                logging.info(f"COM port check result: {check_port}")
                if 'Fail' == check_port:
                    msg = ["com port is unreachable:{}".format(com_port)]
                    result_queue.append(msg)
                    abort_flag.set()
                    return
                retryCnt = 0
            except Exception as e:
                logging.error(e)
                retryCnt -= 1

        # Factory Reset
        logging.info(f"Starting Factory Reset test case for COM: {com_port}")
        if data_dict.get("FACTORY_RESET", str(True)) == str(False):
            logging.info("Factory Reset test case is skipped as per configuration.")
            logging.info("Skipping to do Factory Reset")
            result_list.append('pass')
        else:
            retryCnt = 3
            logging.info(f"Performing Factory Reset for COM: {com_port}, Attempt: {4-retryCnt}")
            while (retryCnt):
                try:
                    factory_reset_val1=cases.Factory_reset_val()
                    logging.info(f"Factory Reset result: {factory_reset_val1}")
                    if factory_reset_val1.get("Result")=='Fail':
                        result_list.append('fail')
                    else:
                        result_list.append('pass')
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while performing Factory Reset: {str(e)}")
                    retryCnt = retryCnt-1

            time.sleep(data_dict.get("FACTORY_RESET_SLEEP_TIME", data_dict.get("Fact_Reset_sleepTime", 5)))

        # Verify Current
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Verify Current test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                check_current_on = cases.Verify_Current(float(data_dict.get("I_PHASE_MIN", 0.0)),float(data_dict.get("I_PHASE_MAX", 4.0)), IsOff = False)
                logging.info(f"Verify Current result: {check_current_on}")
                MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentR", 0.0)))
                MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentY", 0.0)))
                MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentB", 0.0)))
                MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentN", 0.0)))
                MeterInfo.append(str(check_current_on.get('value', {}).get("live_tamper", [])))
                if check_current_on.get("Result")=='Fail':
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error("Error occurred while verifying current")
                retryCnt = retryCnt-1
                if retryCnt == 0:
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('[]')
                    result_list.append('fail')

        # Verify Voltage
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Verify Voltage test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                verify_voltage =cases.Verify_Voltage(float(data_dict.get("Voltage_Min", 0.0)),float(data_dict.get("Voltage_Max", 0.0)))
                logging.info(f"Verify Voltage result: {verify_voltage}")
                # verify_voltage =cases.Verify_Voltage(float(0.0),float(200.0))
                if verify_voltage.get("Result")=='Fail':   
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                logging.info("Verify Voltage test case completed.")
                MeterInfo.append(str(verify_voltage.get('value', {}).get("VoltageR", 0.0)))
                MeterInfo.append(str(verify_voltage.get('value', {}).get("VoltageY", 0.0)))
                MeterInfo.append(str(verify_voltage.get('value', {}).get("VoltageB", 0.0)))
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while verifying voltage: {e}")
                retryCnt = retryCnt-1
                if retryCnt == 0:
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    result_list.append('fail')
        
        # Relay Off
        if 'wc' in meter_type.lower():
            retryCnt = 3
            while (retryCnt):
                logging.info(f"Starting Relay Off test case for COM: {com_port}, Attempt: {4-retryCnt}")
                try:
                    relay_off =cases.Meter_Relay_OFF()
                    logging.info(f"Relay Off result: {relay_off}")
                    if relay_off.get("Result")=='Fail':
                        result_list.append('fail')
                    else:
                        result_list.append('pass')
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while turning relay off: {str(e)}")
                    retryCnt = retryCnt-1
        
        # Set time
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Set Time test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                set_time=cases.Set_time_val()
                MeterInfo.append("now")
                logging.info(f"Set Time result: {set_time}")
                if set_time.get("Result")=='Fail':   
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while setting time: {e}")
                retryCnt = retryCnt-1

        # PCB Serial Number
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting PCB Serial Number test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                MeterInfo.append(pcb_serial_num)
                pcb_num = cases.Set_Meter_PCB_serial_number(pcb_serial_num, pcb_start_address)
                logging.info(f"Set Meter PCB Serial Number result: {pcb_num}")
                if pcb_num.get("Result")=='Fail':
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while setting PCB serial number: {e}")
                retryCnt = retryCnt-1
        # NIC PCB Number
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting NIC PCB Serial Number test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                MeterInfo.append(Nic_pcb_num)
                nic_pcb = cases.Set_nic_pcb_no(Nic_pcb_num, nic_start_address)
                logging.info(f"Set NIC PCB Serial Number result: {nic_pcb}")
                if nic_pcb.get("Result")=='Fail':
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while setting NIC PCB serial number: {e}")
                retryCnt = retryCnt-1

        # Calibration unlock
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Calibration Unlock test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                calibUnlock = cases.Calibration_unLock()
                logging.info(f"Calibration Unlock result: {calibUnlock}")
                if calibUnlock.get("Result")=='Fail':
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while unlocking calibration: {e}")
                retryCnt = retryCnt-1

        # Meter Serial Number
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Meter Serial Number test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                MeterInfo.append(meter_serial_num)
                MeterSerialNumSet=meter_serial_num[-8:]
                print (MeterSerialNumSet)
                sr_num = cases.Set_Meter_serial_number(int(MeterSerialNumSet))
                logging.info(f"Set Meter Serial Number result: {sr_num}")
                if sr_num.get("Result")=='Fail':
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while setting meter serial number: {e}")
                retryCnt = retryCnt-1

        # Manufacturing year
        if data_dict.get("MANUFACTURING_YEAR_SET", str(False)) == str(False):
            print("\nSkipping to set manufacturing year")
            logging.info("Skipping to set manufacturing year")
            result_list.append('skip')
            MeterInfo.append('0')
        else:
            retryCnt = 3
            while (retryCnt):
                try:
                    logging.info(f"Starting Manufacturing Year test case for COM: {com_port}, Attempt: {4-retryCnt}")
                    set_manufacturing_year=cases.Set_manufacturing_year(data_dict.get("MANUFACTURING_YEAR", ""))
                    logging.info(f"Set Manufacturing Year result: {set_manufacturing_year}")
                    if set_manufacturing_year.get("Result")=='Fail':   
                        result_list.append('fail')
                    else:
                        result_list.append('pass')
                    MeterInfo.append(data_dict.get("MANUFACTURING_YEAR", "0"))
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while setting manufacturing year: {e}")
                    retryCnt = retryCnt-1
                    MeterInfo.append('0')

        # Get Live Version
        retryCnt = 3
        logging.info(f"Starting Get Live Version test case for COM: {com_port}, Attempt: {4-retryCnt}")
        while (retryCnt):
            try:
                version_live=cases.get_live_version_val()
                MeterInfo.append(str(version_live)) 
                logging.info(f"Get Live Version result: {version_live}")
                if str(version_live)==str(data_dict.get("LIVE_VERSION", "")):
                    result_list.append('pass')
                else:
                    result_list.append('fail')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while fetching live version: {e}")
                retryCnt = retryCnt-1
                #     exit()

        # Get Internal Version
        if data_dict.get("INTERNAL_VERSION", "0") == "0":
            print("\nSkipping to Get INTERNAL VERSION")
            logging.info("Skipping to Get INTERNAL VERSION")
            result_list.append('skip')
            MeterInfo.append('0')
        else:
            retryCnt = 3
            while (retryCnt):
                logging.info(f"Starting Get Internal Version test case for COM: {com_port}, Attempt: {4-retryCnt}")
                try:
                    int_version=cases.get_internal_version_val()
                    logging.info(f"Get Internal Version result: {int_version}")
                    if str(int_version)==str(data_dict.get("INTERNAL_VERSION", "")):
                        result_list.append('pass')
                        MeterInfo.append(str(int_version))
                    else:
                        result_list.append('fail')
                        MeterInfo.append(str(int_version))
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while fetching internal version: {e}")
                    print(f"Error occurred while fetching internal version: {e}")
                    retryCnt = retryCnt-1

        # Verify DIDO for ltct
        if "ltct" in meter_type.lower():
            if str(data_dict.get("VERIFY_DIDO_STATUS", False)) == "False":
                print("\nSkipping to verify DIDO Status")
                logging.info("Skipping to verify DIDO Status")
                result_list.append('skip')
                MeterInfo.append('None')
            else:
                retryCnt = 3
                while (retryCnt):
                    logging.info(f"Starting Verify DIDO Status test case COM: {com_port}, Attempt: {4-retryCnt}")
                    try:
                        get_dido_state=cases.get_dido_status()
                        logging.info(f"Get DIDO Status result: {get_dido_state}")
                        if get_dido_state.get("Result")=='Fail':   
                            result_list.append('fail')
                        else:
                            result_list.append('pass')
                        MeterInfo.append(str(get_dido_state.get('value', None)))
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error occurred while fetching DIDO status: {e}")
                        retryCnt = retryCnt-1

        # Get Bootloader version
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Get Bootloader Version test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                boot_version=cases.get_bootloader_version_val(data_dict.get("BOOTLOADER_VERSION", ""))
                logging.info(f"Get Bootloader Version result: {boot_version}")
                if boot_version.get("Result")=='Fail':   
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                MeterInfo.append(float(boot_version.get('value', 0)))
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while fetching bootloader version: {e}")
                retryCnt = retryCnt-1
                MeterInfo.append("0.0")

        # Relay On and verify current
        if 'wc' in meter_type.lower():
            # Verify current After Relay Off
            retryCnt = 3
            while (retryCnt):
                logging.info(f"Starting After Relay Off Verify Current test case for COM: {com_port}, Attempt: {4-retryCnt}")
                try:
                    check_current_on = cases.Verify_Current(float(data_dict.get("I_PHASE_MIN", 0)),float(data_dict.get("I_PHASE_MAX", 0)), IsOff = True)
                    logging.info(f"After Relay Off Verify Current result: {check_current_on}")
                    if check_current_on.get("Result")=='Fail':
                        result_list.append('fail')
                    else:
                        result_list.append('pass')
                    MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentR", 0.0)))
                    MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentY", 0.0)))
                    MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentB", 0.0)))
                    MeterInfo.append(str(check_current_on.get('value', {}).get("CurrentN", 0.0)))
                    MeterInfo.append(str(check_current_on.get('value', {}).get("live_tamper", [])))
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while fetching current after relay off: {e}")
                    retryCnt = retryCnt-1
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('0.0')
                    MeterInfo.append('[]')
                    result_list.append('fail')

            # Relay On
            retryCnt = 3
            while (retryCnt):
                logging.info(f"Starting Relay On test case for COM: {com_port}, Attempt: {4-retryCnt}")
                try:
                    relay_on =cases.Meter_Relay_On()
                    logging.info(f"Relay On result: {relay_on}")
                    if relay_on.get("Result")=='Fail':   
                        result_list.append('fail')
                    else:
                        result_list.append('pass')
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while fetching relay on result: {e}")
                    retryCnt = retryCnt-1

        # Sim Set
        if str(data_dict.get("SET_SIM_TOGGLE", False)) == "False":
            print("\nSkipping to set sim Toggle")
            logging.info("Skipping to set sim Toggle")
            result_list.append('pass')
        else:
            retryCnt = 3
            while (retryCnt):
                logging.info(f"Starting Set Sim Toggle test case for COM: {com_port}, Attempt: {4-retryCnt}")
                try:
                    sim_toggle = cases.set_sim_toggle()
                    logging.info(f"Set Sim Toggle result: {sim_toggle}")
                    if sim_toggle.get("Result")=='Fail':   
                        result_list.append('fail')
                    else:
                        result_list.append('pass')
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while fetching sim toggle result: {e}")
                    retryCnt = retryCnt-1

        # Set Gprs Protocol
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Set GPRS Protocol test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                set_gprs_protocol =cases.set_gprs_protocol_val(1)
                logging.info(f"Set GPRS Protocol result: {set_gprs_protocol}")
                if set_gprs_protocol.get("Result")=='Fail':   
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while fetching GPRS protocol result: {e}")
                retryCnt = retryCnt-1

        # Get Gprs Protocol
        retryCnt = 3
        while (retryCnt):
            logging.info(f"Starting Get GPRS Protocol test case for COM: {com_port}, Attempt: {4-retryCnt}")
            try:
                get_gprs_protocol =cases.get_gprs_protocol_val()
                logging.info(f"Get GPRS Protocol result: {get_gprs_protocol}")
                if get_gprs_protocol.get("Result")=='Fail':   
                    result_list.append('fail')
                else:
                    result_list.append('pass')
                MeterInfo.append(str(get_gprs_protocol.get('value', None)))
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while fetching GPRS protocol result: {e}")
                retryCnt = retryCnt-1
                if retryCnt == 0:
                    MeterInfo.append(str(None))


        print (result_list)
        if 'fail' in result_list:
            MeterInfo.append('fail')
        else:
            MeterInfo.append('pass')

        ser.close()

        
        result_log.append((com_port, result_log_dump(mac,MeterInfo,result_list,bookName,fileName,result_save)))

        time.sleep(0.1)
        for idx, result in enumerate(result_list):
            if result == 'fail':
                fail_indexes.append(idx)


                
        EndTime = datetime.datetime.now()
        print ("\nStartTime:",starttime)
        print ("EndTime:",EndTime)
        print ("Diff : ", EndTime - starttime)



        if fail_indexes:
            fail_messages = ["COM Port: {}, {}".format(com_port, PCT_Fail_list[idx]) for idx in fail_indexes]
            result_queue.append(fail_messages)
        # print(fail_messages)
        # print(result_queue)
    

    except Exception as e:
        print("Error:", e)
        msg = ["com port is unreachable:{}".format(com_port)]
        result_queue.append(msg)
        if(ser):
            ser.close()
        return

def make_pop_result(list_port, unique_results=None):

    if unique_results is None:
        unique_results = []

    unreachable = []
    failures = []
    passes = []
    info = []

    for line in unique_results:

        line = str(line)

        if "unreachable" in line.lower():
            unreachable.append(line)

        elif "fail" in line.lower():
            failures.append(line)

        elif "pass" in line.lower():
            passes.append(line)

        else:
            info.append(line)


    total_ports = len(list_port)
    total_unreachable = len(unreachable)
    total_pass = len(passes)
    total_failures = total_ports - total_pass - total_unreachable


    # ----------------------------
    # Console Output (Colored)
    # ----------------------------

    print(Fore.CYAN + "========== PCT TEST SUMMARY ==========")
    print(Fore.CYAN + "Total Ports   :", total_ports)
    print(Fore.GREEN + "Passed        :", total_pass)
    print(Fore.YELLOW + "Failures      :", total_failures)
    print(Fore.RED + "Unreachable   :", total_unreachable)
    print(Fore.CYAN + "======================================\n")


    if unreachable:
        print(Fore.RED + "❌ UNREACHABLE PORTS")
        print(Fore.RED + "---------------------")
        for u in unreachable:
            print(Fore.RED + u)
        print()

    if failures:
        print(Fore.YELLOW + "⚠ TEST FAILURES")
        print(Fore.YELLOW + "----------------")
        for f in failures:
            print(Fore.YELLOW + f)
        print()

    if passes:
        print(Fore.GREEN + "✔ PASSED PORTS")
        print(Fore.GREEN + "----------------")
        for p in passes:
            print(Fore.GREEN + p)
        print()

    if info:
        print(Fore.CYAN + "Passed Ports")
        print(Fore.CYAN + "----")
        for i in info:
            print(Fore.CYAN + i)
        print()


    # ----------------------------
    # Popup Text Formatting
    # ----------------------------

    popup_text = []
    popup_text.append("========== PCT TEST SUMMARY ==========\n")

    popup_text.append(f"Total Ports   : {total_ports}")
    popup_text.append(f"Passed        : {total_pass}")
    popup_text.append(f"Failures      : {total_failures}")
    popup_text.append(f"Unreachable   : {total_unreachable}")
    popup_text.append("")


    if unreachable:
        popup_text.append("❌ UNREACHABLE PORTS")
        popup_text.append("---------------------")
        popup_text.extend(unreachable)
        popup_text.append("")

    if failures:
        popup_text.append("⚠ TEST FAILURES")
        popup_text.append("----------------")
        popup_text.extend(failures)
        popup_text.append("")

    if passes:
        popup_text.append("✔ PASSED PORTS")
        popup_text.append("----------------")
        popup_text.extend(passes)
        popup_text.append("")

    if info:
        popup_text.append("INFO")
        popup_text.append("----")
        popup_text.extend(info)

    msg_text = "\n".join(popup_text)
    print(Style.RESET_ALL)
    return msg_text

def run(data_json, list_port, upload_bench):
    
    port_inputs = []
    toolname = data_json.get("TOOL_TYPE", "").lower()
    meter_type = data_json.get("METER_TYPE", "").lower()
    if "ltct" in meter_type:
        pass
    elif 'wc' in meter_type:
        pass
    else:
        print("Wrong Meter Type Selected in config file, Please select correct Meter type")
        return
    bookName = meter_type.upper() + "_"+ toolname.upper() + "_LOG.xlsx"
    fileName = toolname.upper() + "_DATA_LOG"

    print(bookName, fileName)
    # list_port = data_json.get("Port_list", [])

    addDefaultPCTLog(bookName,fileName, meter_type.lower())

    # to take input 
    for i, port in enumerate(list_port):
        com_port = "COM{}".format(port)
        print(Fore.YELLOW + f"\nScanning Meter at Position {i+1} with COM Port: {com_port}" + Style.RESET_ALL)
        while True: 
            Meter_pcb_serial_no = input("Eneter Meter PCB serial No (Ex.(FOR PCB P24101301000000100210000001...... etc): ")
            if str(Meter_pcb_serial_no[9:16]) == str(data_json.get("Main_PCB_SFG_Prefix", "")):
                break
            else: 
                print("Invalid Format of Meter PCB Serial Num,Enter in this Format(Ex.(FOR PCB P24101301000000100210000001-- P24101301000000100210000001...... etc)")
        while True:
            if ((len(Meter_pcb_serial_no) > 12) and (str(Meter_pcb_serial_no[-8:]).isdigit())):
                Meter_serial_num = Meter_pcb_serial_no[-8:]
                break
            else:
                print("Meter PCB Serial Num length should be greater than 12 and last Eight Digits should be decimal only")
                easygui.msgbox("Restart the tool as Meter PCB Serial Num length should be greater than 12 and last Eight Digits should be decimal only", "Failures Detected")
                return
        while True:
            Nic_PCB_serial_no=input("Eneter NIC PCB serial No (Ex. P24101301000000400310000001 etc): ")
            if((str(Nic_PCB_serial_no[0:4]).lower() == 'r144') or (str(Nic_PCB_serial_no[9:16]) == str(data_json.get("NIC_PCB_SFG_PREFIX", "")))):
                break
            else:
                print("Invalid Format of NIC PCB Serial Num,Enter in this Format(Ex.P24101301000000400310000001 etc)")

        port_inputs.append((com_port.lower(), Meter_serial_num, Meter_pcb_serial_no, Nic_PCB_serial_no))
    

    input("Press Enter to start the script........")
    logging.info(f"User Inputs - {port_inputs}\n")


    starttimepct=datetime.datetime.now()

    # threads = []
    # results = []
    # result_dict = []
    # abort_flag=threading.Event()

    # for port_data in port_inputs:
    #     thread = StoppableThread(target=main_function, args=(data_json, port_data[0], port_data[1], port_data[2], port_data[3], results, abort_flag,result_dict))
    #     threads.append(thread)

    threads = []
    abort_flag = threading.Event()

    port_result_dicts = [[] for _ in port_inputs]
    port_results = [[] for _ in port_inputs]   # one results queue per port

    for i, port_data in enumerate(port_inputs):
        thread = StoppableThread(
            target=main_function,
            args=(data_json, port_data[0], port_data[1], port_data[2], port_data[3], port_results[i], abort_flag, port_result_dicts[i])
        )
        threads.append(thread)

    # threads = []
    # results = []
    # abort_flag = threading.Event()

    # port_result_dicts = [[] for _ in port_inputs]  # one result_dict per port

    # for i, port_data in enumerate(port_inputs):
    #     thread = StoppableThread(
    #         target=main_function,
    #         args=(data_json, port_data[0], port_data[1], port_data[2], port_data[3], results, abort_flag, port_result_dicts[i])
    #     )
    #     threads.append(thread)


    # Start all threads
    # for thread in threads:
    for thread in threads:
        thread.start()
        time.sleep(data_json.get("Thread_start_delay", 0.5))  # Add delay between starting threads if needed

    for thread in threads:
        thread.join(timeout=data_json.get("Thread_timeout", 40))  # Timeout for each thread to prevent hanging


    # Validate and update results dynamically for all COM ports

    # all_result_dicts = [result_dict]   # add more if needed
    # all_results = [results]
    # all_result_dicts = port_result_dicts   # one per port
    # all_results = [[] for _ in port_inputs] 
    all_result_dicts = port_result_dicts
    all_results = port_results   # already contains thread fail messages per port

    # print("All Result Dicts:", all_result_dicts)
    # print("All Results:", all_results)

    for idx, current_result_dict in enumerate(all_result_dicts):

        if len(current_result_dict) != 0:

            while True:

                Meter_pcb_serial_no = input(
                    f"\nRe-Enter Meter PCB serial No for COM{list_port[idx]}: "
                )
                logging.info(f"Re-entered Meter PCB Serial No for COM{list_port[idx]}: {Meter_pcb_serial_no}")

                # Validate prefix
                if str(Meter_pcb_serial_no[9:16]) == str(data_json.get("Main_PCB_SFG_Prefix", "")):

                    for l1 in current_result_dict:
                        # print("Current Result Dict Entry:", l1)

                        com_port = l1[0]

                        # Inside meter PCB serial number
                        target_value = l1[1][1][10]

                        print("Target PCB:", target_value)

                        # Match PCB serial number
                        if str(Meter_pcb_serial_no) == str(target_value):
                            print("Meter PCB Serial Number matches the target value.", l1)

                            # Final status
                            if l1[1][1][-1].lower() == 'pass':

                                pass_message = [
                                    f"PASS: {com_port.upper()}"
                                ]

                                all_results[idx].append(pass_message)

                        else:

                            # Update fail status
                            if "ltct" in meter_type.lower():
                                l1[1][2][4] = 'fail'
                            else:
                                l1[1][2][5] = 'fail'

                            l1[1][1][-1] = 'fail'

                            fail_message = [
                                f"COM Port: {com_port}, "
                                f"Fail in PCB Serial No Mismatch between "
                                f"Printed Meter PCB Serial No and Inside Meter PCB Serial No"
                            ]

                            all_results[idx].append(fail_message)

                    break

                else:
                    print(
                        "\nInvalid Format of Meter PCB Serial Num\n"
                        "Example: P24101301000000100210000001"
                    )


    for current_result_dict in all_result_dicts:
        print(current_result_dict)

    for current_results in all_results:
        print(current_results)


    # =========================
    # SAVE EXCEL LOGS
    # =========================

    for current_result_dict in all_result_dicts:

        if len(current_result_dict) != 0:

            for row in current_result_dict:

                try:
                    row_status = False

                    close_excel_file(bookName)

                    dump = row[1]
                    excel_row = [
                        dump[0],   # mac
                        dump[1],   # MeterInfo
                        dump[2],   # result_list
                        dump[3],   # bookName
                        dump[4]    # fileName
                    ]

                    add_log_xlsc(excel_row, row_status)

                except Exception as e:
                    print("Unknown error while adding logs in Excel:", e)
                    continue

    
            
    if data_json.get("IS_DATA_CONN", 1) == 1:
        df_frame = pd.read_excel(bookName)
        print(df_frame,'------------')


        try:
            status = False
            error = ""
            if 'ltct' in meter_type.lower():
                status, error = db_connect.upload_dataframe(df_frame, 'ltct')
            else:
                status, error = db_connect.upload_dataframe(df_frame, 'wc')
            if not status:
                print(f"DB upload failed . Saved locally for retry. Error: {error}")
            else:
                # if(len(result_dict) != 0):       # if the result file is empty then don't upload to server
                if any(len(rd) != 0 for rd in port_result_dicts):

                    import boto3
                    from botocore.exceptions import NoCredentialsError


                    def upload_to_aws(local_folder, bucket, s3_file,sub_folder, file_time,folder_name1):
                        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                        aws_secret_access_key=SECRET_KEY)

                        try:
                            s3.upload_file(s3_file, bucket, folder_name +  "/{0}/{1}/{2}/{3}".format(folder_name1,sub_folder,local_folder, str(upload_bench + "_" + file_time + "_" + s3_file)))
                            print("Upload Successful")
                            os.remove(s3_file)
                            return True
                        except NoCredentialsError:
                            print("Credentials not available")
                            return False
                        except Exception as e:
                            print(e)
                            print("The file was not found")
                            return False
                    
                    al = os.listdir("./")
                    txt = list(filter(lambda x: x[-5:] == '.xlsx',al))
                    print (txt)
                    if len(txt) == 0:
                        print("file doesn't exist")
                        return

                    for j in range(len(txt)):
                        xyz_time = datetime.datetime.now()
                        print ("time = ",xyz_time)
                        date_only = datetime.datetime.strftime(xyz_time, '%Y-%m-%d')
                        time_only = datetime.datetime.strftime(xyz_time, '%H_%M_%S')
                        print("time is",time_only)
                        print("date is",date_only)

                        sub_folder = "UNKNOWN"
                        xyx =  str(txt[j])
                        if('pct' in xyx.lower()):
                            sub_folder = "PCT"
                        elif('4g_mct' in xyx.lower()):
                            sub_folder = "4G_MCT"
                        elif('img_mct' in xyx.lower()):
                            sub_folder = "IMG_MCT"
                        elif('rtt' in xyx.lower()):
                            sub_folder = "RTT"    
                        else:
                            print("improper file name given for tool type")
                            continue
                        print ("sub_folder = ",sub_folder)

                        # print (xyx.find("AP"))
                        folder_name1 = "UNKNOWN"
                        if('sm_1p' in xyx.lower()):
                            folder_name1 = "ISM_1P"
                        elif('sm_3p' in xyx.lower()):
                            folder_name1 = "ISM_3P"
                        elif('ap_1p' in xyx.lower()):
                            folder_name1 = "CAP_3P"
                        elif('cu_' in xyx.lower()):
                            folder_name1 = "DCU_"  
                        elif('rud_' in xyx.lower()):
                            folder_name1 = "Garud"
                        elif('ltct' in xyx.lower()):
                            folder_name1 = "3PLTCT" 
                        elif('wc' in xyx.lower()):
                            folder_name1 = "3PWC" 
                        else:
                            print("improper file name given for Meter type")
                            continue
                        print ("folder_name1 = ",folder_name1)

                        uploaded = upload_to_aws(str(date_only), bucket_name, txt[j],sub_folder, time_only,folder_name1 )
                else:
                    print("Skipping to Upload the log file to server")


                # print (result_dict)
                # print (results)

                # if results:
                #     # Flatten the nested list
                #     flat_results = [item for sublist in results for item in sublist]
                #     # Remove duplicates
                #     unique_results = list(set(flat_results))
                #     # Join and show message
                #     msg_text = "\n".join(unique_results)
                #     easygui.msgbox(msg_text, "MCT Failures Detected")

        except:
            print("Error writing DB log")

    elif data_json.get("IS_DATA_CONN", 1) == 0:
        # if(len(result_dict) != 0):       # if the result file is empty then don't upload to server
        if any(len(rd) != 0 for rd in port_result_dicts):


            import boto3
            from botocore.exceptions import NoCredentialsError



            def upload_to_aws(local_folder, bucket, s3_file,sub_folder, file_time,folder_name1):
                s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                aws_secret_access_key=SECRET_KEY)

                try:
                    s3.upload_file(s3_file, bucket, folder_name +  "/{0}/{1}/{2}/{3}".format(folder_name1,sub_folder,local_folder, str(upload_bench + "_" + file_time + "_" + s3_file)))
                    print("Upload Successful")
                    os.remove(s3_file)
                    return True
                except NoCredentialsError:
                    print("Credentials not available")
                    return False
                except Exception as e:
                    print(e)
                    print("The file was not found")
                    return False
            
            al = os.listdir("./")
            txt = list(filter(lambda x: x[-5:] == '.xlsx',al))
            print (txt)
            if len(txt) == 0:
                print("file doesn't exist")
                return

            for j in range(len(txt)):
                xyz_time = datetime.datetime.now()
                print ("time = ",xyz_time)
                date_only = datetime.datetime.strftime(xyz_time, '%Y-%m-%d')
                time_only = datetime.datetime.strftime(xyz_time, '%H_%M_%S')
                print("time is",time_only)
                print("date is",date_only)

                sub_folder = "UNKNOWN"
                xyx =  str(txt[j])
                if('pct' in xyx.lower()):
                    sub_folder = "PCT"
                elif('4g_mct' in xyx.lower()):
                    sub_folder = "4G_MCT"
                elif('img_mct' in xyx.lower()):
                    sub_folder = "IMG_MCT"
                elif('rtt' in xyx.lower()):
                    sub_folder = "RTT"    
                else:
                    print("improper file name given for tool type")
                    continue
                print ("sub_folder = ",sub_folder)

                folder_name1 = "UNKNOWN"
                if('sm_1p' in xyx.lower()):
                    folder_name1 = "ISM_1P"
                elif('sm_3p' in xyx.lower()):
                    folder_name1 = "ISM_3P"
                elif('ap_1p' in xyx.lower()):
                    folder_name1 = "CAP_3P"
                elif('cu_' in xyx.lower()):
                    folder_name1 = "DCU_"  
                elif('rud_' in xyx.lower()):
                    folder_name1 = "Garud"
                elif('ltct' in xyx.lower()):
                    folder_name1 = "3PLTCT" 
                elif('wc' in xyx.lower()):
                    folder_name1 = "3PWC" 
                else:
                    print("improper file name given for Meter type")
                    continue
                print ("folder_name1 = ",folder_name1)

                uploaded = upload_to_aws(str(date_only), bucket_name, txt[j],sub_folder, time_only,folder_name1 )
        else:
            print("Skipping to Upload the log file to server")


        # print (result_dict)
        # print (results)

    # =========================
    # FINAL RESULT PROCESSING
    # =========================

    # =========================
    # FINAL RESULT PROCESSING
    # =========================

    final_results = []

    # Collect thread fail/unreachable/pass messages from port_results
    for port_result in port_results:
        for item in port_result:
            if isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, list):
                        final_results.extend(sub_item)
                    else:
                        final_results.append(str(sub_item))
            else:
                final_results.append(str(item))

    # Collect PCB mismatch and pass messages from all_results
    # (all_results == port_results so skip duplicate, only add PCB mismatch messages)
    for current_results in all_results:
        for item in current_results:
            if isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, list):
                        final_results.extend(sub_item)
                    else:
                        final_results.append(str(sub_item))
            else:
                final_results.append(str(item))

    endtimepct = datetime.datetime.now()
    diff = endtimepct - starttimepct

    final_results.append(f"Diff Time is: {diff}")

    # Remove duplicates while preserving order
    unique_results = list(dict.fromkeys(final_results))

    # Create JSON Summary
    msg_text = make_pop_result(list_port, unique_results)
    easygui.codebox(msg="PCT Test Results", title="Result Summary", text=msg_text)

def setup_logger():
    log_folder = "Logs"
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(log_folder, "PCT.log")

    logger = logging.getLogger()

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(processName)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

if __name__ == "__main__":
    setup_logger()
    cfg = Config()
    port_json = {}
    port_status = False
    serial_config = {}
    serial_config_status = False
    SADDLE_BROWN   = "\033[38;2;139;69;19m"
    RESET    = "\033[0m"
    print(Fore.GREEN + "Loading Configurations...")
    port_json, port_status = cfg.load_config_json('config.json')
    if not port_status:
        print(Fore.RED + "Com Port is not available in config...")
    else:
        print(Fore.GREEN + "Com port is loaded...")
        print(Fore.GREEN + "Used Com Port: " + SADDLE_BROWN + f"{port_json}")
        serial_config, serial_config_status = cfg.check_encrypted_json('config_file.enc')
        print(serial_config)
        if serial_config_status:
            while True:
                print (RESET +"<<<<<<<<<<<<<<<<<<<<<<<<<<<<............... 3P LTCT / WC PCT Tool V 3.12 .....................>>>>>>>>>>>>>>>>>>>")
                logging.info("\nStart new batch")
                run(serial_config, port_json.get("com_port", []), port_json.get("upload_bench", "1"))
        else:
            print(Fore.RED + "Fixed Serial config is currepted")
            time.sleep(2)
    print("Closing PCT Tool..")
    time.sleep(3)
    