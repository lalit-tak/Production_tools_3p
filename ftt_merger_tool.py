import os
import queue
import serial
import datetime
import time
import threading
from threading import Thread 
import time
import sys
import easygui
import tkinter as Tk
import re
from colorama import Fore, Style, init
from Test_cases_verificationClass import TestCasePCTMCT
from provisioning_tool.communication import Communication
from provisioning_tool.provision_img_parameters import run_provisioning
import provisioning_tool.wirepas_provisioning as wirepas_provisioning
import win32com.client
import pythoncom
import openpyxl
import logging
import pandas as pd
import db_connect
global abort_threads


ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"
bucket_name = "PUT_YOUR_BUCKET_NAME_HERE"
folder_name = "PUT_YOUR_FOLDER_NAME_HERE"

DEFAULT_BAUDRATE = 9600

def run_provisioning_worker(result_queue, provisioning_param):
    nic_parameters_data, prov_success, summary = {}, False, ""
    try:
        nic_parameters_data, prov_success, summary = run_provisioning(provisioning_param)
        result_queue.put((nic_parameters_data, prov_success, summary))
    except Exception as e:
        summary = str(e)
        result_queue.put((nic_parameters_data, prov_success, summary))

def run_provisioning_with_timeout(provisioning_param, timeout_seconds=70):
    result_queue = queue.Queue()
    t = threading.Thread(target=run_provisioning_worker, args=(result_queue, provisioning_param), daemon=True)
    t.start()
    t.join(timeout_seconds)
    if t.is_alive():
        # Can't force-kill a thread. It keeps running in the background using `ser`;
        # we just stop waiting on it and report timeout to the caller.
        return {}, False, "TIMEOUT"
    if not result_queue.empty():
        return result_queue.get()
    else:
        return {}, False, "NO_RESPONSE"

def img_provisioning(data, img_id, gateway_id, com_port, com_ser ,baudrate = DEFAULT_BAUDRATE ):
    serial_port = com_port
    project = data.get('BROKER', '')
    reboot_time = str(data.get('REBOOT_TIME_SEC', "300"))
    # reboot_time = '0'
    network_channel = str(data.get("NETWORK_CHANNEL", "1"))
    # network_channel = "2"

    logging.info(f"Port {serial_port}, IMG Provisioning Started")

    provisioning_param = {}
    nic_parameters_data = {}
    prov_sucess = False
    summary = ""
    reason = ""
    print("\nStarting IMG Provisioning....")
    print(f"\nProject: {project}")
    try:
        user = ""
        password = ""
        hostname = ""
        ntp_addr = ""
        if project.upper() == "GOMATI":
            user = "Gomati-Broker"
            password = "G0m@ti-Br0k3r!2024$"
            # sync_apn = "polarisgomati"
            hostname = "broker.gomatimvvnl.in"
            ntp_addr = "wnms.gomatimvvnl.in"
        elif project.upper() == "SARYU":
            user = "Saryu-Broker"
            password = "S@ryu-Br0k3r!#V&2420$"
            # sync_apn = "polarissaryu"
            hostname = "broker.saryumvvnl.in"
            ntp_addr = "wnms.saryumvvnl.in"
        elif project.upper() == "MANIPUR":
            user = "sangaibroker"
            password = "V3aSLGXkUy4o1CIBs"
            # sync_apn = "polarissangai"
            hostname = "broker.sangaimspdcl.in"
            ntp_addr = "wnms.sangai.polarisgrids.com"
        elif project.upper() == "WB":
            user = "wbsedcl"
            password = "nU4Eq5rE2e"
            # sync_apn = "polarissangai"
            hostname = "broker.hooghlywbsedcl.in"
            ntp_addr = "wnms.hooghlywbsedcl.in"
        elif project.upper() == "TN":
            user = "TNPDCL-Broker"
            password = "oJBUnxKCqPjXoWgCz3Jwojce"
            # sync_apn = "polarissangai"
            hostname = "broker.private.tnpdcl.in"
            ntp_addr = "wnms.private.tnpdcl.in"
        elif project.upper() == "TATA_DELHI":
            user = "TNPDCL-Broker"
            password = "oJBUnxKCqPjXoWgCz3Jwojce"
            # sync_apn = "polarissangai"
            hostname = "broker.private.tnpdcl.in"
            ntp_addr = "wnms.private.tnpdcl.in"
        
        else:
            return {}, False, "No broker match"
        
        print("Starting provisioning script")
        provisioning_param = {
            "com_ser": com_ser,
            "serial_port": serial_port,
            "baudrate": data.get("baudrate", ''),
            "reboot_time": reboot_time,
            "encryption_key": "e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1",
            "authentication_key": "e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1",
            "network_address": "12238529",
            "network_channel": network_channel,
            "node_address": "1",
            "sink_address": img_id,
            "node_role": None,
            "gateway_id": gateway_id,
            "gw_key_enc_key": None,
            "mtr_auth_key": None,
            "mtr_enc_key": None,
            "mtr_mr_secret": None,
            "mtr_us_secret": None,
            "mtr_fu_secret": None,
            "mtr_baud_rate": None,
            "mtr_dlms_mode": None,
            "sim1_apn": None,
            "sim1_username": None,
            "sim1_password": None,
            "sim1_pdp_type": None,
            "sim1_pin": None,
            "sim1_puk": None,
            "sim1_band_lock": None,
            "sim2_apn": None,
            "sim2_username": None,
            "sim2_password": None,
            "sim2_pdp_type": None,
            "sim2_pin": None,
            "sim2_puk": None,
            "sim2_band_lock": None,
            "mqtt_hostname": hostname,
            "mqtt_port": "1883",
            "mqtt_username": user,
            "mqtt_password": password,
            "mqtt_unsecure": "true",
            "reset_hour": "21",
            "reset_minute": "30",
            "ntp_addr": ntp_addr,
            "tz_offset_min": "330",
            "keepalive_interval": "300",
            "sim_selection": "dual_prefer_sim1"
            }
        
        logging.info(f"Port {provisioning_param}, input")
        
        nic_parameters_data, prov_sucess, summary= run_provisioning_with_timeout(provisioning_param)   

        if prov_sucess:
            
            logging.info(f"Port {serial_port}, IMG Provisioning Successfully Completed")
        else:
            reason = summary
            print(f"Command failed with return code: {prov_sucess}")
            logging.info(f"Port {serial_port}, IMG Provisioning Failed")

        logging.info(f"Port {serial_port}, IMG Provisioning: {nic_parameters_data}")
        return nic_parameters_data, prov_sucess, reason
    except Exception as e:
        print(str(e))
        # show_results_popup("Fail", serial_port)
        logging.error(f"Port {serial_port}, Error during IMG Provisioning, Error: {e}")
    return nic_parameters_data, prov_sucess, "Error in Provisioning"

def check_provisioning_status(provision_data, serial_config_json):
    overall_result = "pass"
    reason = ""
    status_dict = {}
    sim2_id = ""
    sim1_id = ""

    if provision_data.get('GW_CORE_VER', '') == serial_config_json['GW_CORE_VER']:
        status_dict['GW_CORE_VER_STATUS'] = "pass"
    else:
        status_dict['GW_CORE_VER_STATUS'] = "fail"
        overall_result = "fail"
        reason = "GW_CORE_VER not match"
    
    if provision_data.get('GW_MAIN_VER', '') == serial_config_json['GW_MAIN_VER']:
        status_dict['GW_MAIN_VER_STATUS'] = "pass"
        # overall_result = True
    else:
        status_dict['GW_MAIN_VER_STATUS'] = "fail"
        overall_result = "fail"
        reason = "GW_MAIN_VER not match"
    
    if provision_data.get('GW_SINK_APP_VER', '') == serial_config_json['GW_SINK_APP_VER']:
        status_dict['GW_SINK_APP_VER_STATUS'] = "pass"
        # overall_result = True
    else:
        status_dict['GW_SINK_APP_VER_STATUS'] = "fail"
        overall_result = "fail"
        reason = "GW_SINK_APP_VER not match"
    
    if provision_data.get('GW_MODEM_FIRMWARE_VER', '') == serial_config_json['GW_MODEM_FIRMWARE_VER']:
        status_dict['GW_MODEM_FIRMWARE_VER_STATUS'] = "pass"
        # overall_result = True
    else:
        status_dict['GW_MODEM_FIRMWARE_VER_STATUS'] = "fail"
        overall_result = "fail"
        reason = "GW_MODEM_FIRMWARE_VER not match"
    
    if provision_data.get('GW_METER_LIB_VER') == serial_config_json['GW_METER_LIB_VER']:
        status_dict['GW_METER_LIB_VER_STATUS'] = "pass"
        # overall_result = True
    else:
        status_dict['GW_METER_LIB_VER_STATUS'] = "fail"
        overall_result = "fail"
        reason = "GW_METER_LIB_VER not match"
    

    if serial_config_json.get('BROKER', '').lower() == 'manipur':
        if 'sangai' not in  provision_data.get('WIREPAS_MQTT_USERNAME', '').lower():
            overall_result = "FAIL"
            reason = "Broker not found in provisioning"
    elif serial_config_json.get('BROKER', '').lower() == 'wb':
        if 'wbsedcl' not in  provision_data.get('WIREPAS_MQTT_USERNAME', '').lower():
            overall_result = "FAIL"
            reason = "Broker not found in provisioning"
    else:
        if (serial_config_json.get('BROKER', '').lower() not in  provision_data.get('WIREPAS_MQTT_USERNAME', '').lower()):
            overall_result = "FAIL"
            reason = "Broker not found in provisioning"

    if 'GW_SIM2_ICCID' in provision_data.keys():
        sim2_id = provision_data.get("GW_SIM2_ICCID", '')
    if 'GW_SIM1_ICCID' in provision_data.keys():
        sim1_id = provision_data.get("GW_SIM1_ICCID", '')
    
    

    if (sim1_id != '') and (sim2_id != ''):
        # overall_result = "pass"
        status_dict['PROVISIONING_STATUS'] = "pass"
        if len(provision_data['GW_SIM1_ICCID']) > 19:
            provision_data['GW_SIM1_ICCID'] = provision_data['GW_SIM1_ICCID'][:19]
        
        summary = wirepas_provisioning.print_provisioning_summary(provision_data)
        print("Provisioning Status: \n",summary)
        print(Fore.GREEN + "✅ IMG Provisioning Successfully Completed!")
        print(Style.RESET_ALL)
    else:
        overall_result = "FAIL"
        status_dict['PROVISIONING_STATUS'] = "FAIL"
        reason = "sim not found in img provisioning"
        summary = wirepas_provisioning.print_provisioning_summary(provision_data)
        print("Provisioning Status: \n",summary)
        print(Fore.RED + "❌ IMG Provisioning Failed! SIM not found")
        print(Style.RESET_ALL)
        # return result_dict, overall_result

    return status_dict, overall_result, reason, provision_data

def get_system_mac_address(toolName):
    mac = "None"
    try:
        if sys.platform == 'win32':
            current_header = ""
            for raw_line in os.popen("ipconfig /all"):
                line = raw_line.rstrip('\n')
                if not line.strip():
                    continue
                if line == line.lstrip():          # unindented line = new adapter section header
                    current_header = line.strip()
                    continue
                stripped = line.lstrip()
                if stripped.startswith('Physical Address') and ':' in stripped:
                    if current_header.lower().startswith('ethernet adapter'):
                        value = stripped.split(':', 1)[1].strip()
                        if value:
                            mac = value.replace('-', ':')
                            break
        else:
            for line in os.popen("/sbin/ifconfig"):
                if line.find('Ether') > -1:
                    mac = line.split()[4]
                    break
    except Exception as e:
        logging.error(f"Error in get mac address: {e}")
    logging.info(f"In Calibration, MAC Address of system: {mac}")
    return mac           

def verify_log_xlsc(bookName,fileName):
    loc = bookName#self.LOG_FILE_NAME 
    
    try:
        wb = openpyxl.load_workbook(loc)
        sheet = wb.active
        cell_value = sheet.cell(row=1, column=1).value
    except Exception as e:
        logging.error(f"Error loading workbook: {e}")
        print("LOG XL file not found, creating one for you")
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
        return  # Excel not open

    for wb in excel.Workbooks:
        if wb.FullName.lower() == filepath.lower():
            print("Closing Excel file:", filepath)
            wb.Close(SaveChanges=False)
            excel.Quit()
            time.sleep(1)
            return True
    return False

END_BYTES = bytes([0xAA, 0xBB, 0xCC, 0xDD])  # sent to the NIC to leave tunnel mode

# Excel / DB column names used as dict keys everywhere in this module
MAC_COLUMN = "FTT_MAC_ADDR"
INDEX_COLUMN = "FTT_Index"
SERIAL_COLUMN = "FTT_Original_Serial_Number"
OVERALL_COLUMN = "FTT_OVER_ALL_RESULT"
MISMATCH_COLUMN = "FTT_Verify_Serial_No_Mismatch"
PROVISIONING_COLUMN = "PROVISIONING_STATUS"
MCT_COLUMN = "FTT_MCT_Status"

# IMG provisioning values read back from the gateway (data -> before overall result)
IMG_DATA_COLUMNS = [
    'IMG ID', 'Gateway ID', 'WIREPAS_GW_ID', 'WIREPAS_NODE_ADDRESS',
    'WIREPAS_GW_KEY_ENC_KEY', 'WIREPAS_MTR_AUTH_KEY', 'WIREPAS_MTR_ENC_KEY',
    'WIREPAS_MTR_BAUD_RATE', 'WIREPAS_MTR_DLMS_MODE', 'WIREPAS_NODE_ROLE',
    'WIREPAS_ENCRYPTION_KEY', 'WIREPAS_AUTHENTICATION_KEY', 'WIREPAS_NETWORK_ADDRESS',
    'WIREPAS_NETWORK_CHANNEL', 'WIREPAS_SINK_ADDRESS', 'WIREPAS_SIM_SELECTION',
    'WIREPAS_SIM1_PDP_TYPE', 'WIREPAS_SIM1_BAND_LOCK', 'WIREPAS_SIM2_PDP_TYPE',
    'WIREPAS_SIM2_BAND_LOCK', 'WIREPAS_MQTT_HOSTNAME', 'WIREPAS_MQTT_PORT',
    'WIREPAS_MQTT_USERNAME', 'WIREPAS_MQTT_PASSWORD', 'WIREPAS_RESET_HOUR',
    'WIREPAS_RESET_MINUTE', 'WIREPAS_NTP_ADDR', 'WIREPAS_TZ_OFFSET_MIN',
    'WIREPAS_KEEPALIVE_INTVL_S', 'GW_IMEI', 'GW_SIM1_IMSI', 'GW_SIM1_ICCID',
    'GW_SIM2_IMSI', 'GW_SIM2_ICCID', 'GW_CORE_VER', 'GW_MAIN_VER',
    'GW_SINK_APP_VER', 'GW_MODEM_FIRMWARE_VER', 'GW_METER_LIB_VER', "Push_Control_Mode",
]
# IMG provisioning pass/fail columns (-> after overall result)
IMG_STATUS_COLUMNS = [
    'Set Debug Print Mode', 'GW_CORE_VER_STATUS', 'GW_MAIN_VER_STATUS',
    'GW_SINK_APP_VER_STATUS', 'GW_MODEM_FIRMWARE_VER_STATUS',
    'GW_METER_LIB_VER_STATUS', PROVISIONING_COLUMN, "Set_Push_Control", "Get_Push_Control",
]


_CALIB_SINGLE_COLUMNS = [
    'CalibStatus', 'FrequencyCoeff',
    'VCoeff[R]', 'VCoeff[Y]', 'VCoeff[B]',
    'ICoeff[R]', 'ICoeff[Y]', 'ICoeff[B]', 'ICoeff[N]',
    'ActPowerCoeff[R]', 'ActPowerCoeff[Y]', 'ActPowerCoeff[B]',
    'PhAngle[R]', 'PhAngle[Y]', 'PhAngle[B]',
    'VFCoeff[R]', 'VFCoeff[Y]', 'VFCoeff[B]',
    'IFCoeff[R]', 'IFCoeff[Y]', 'IFCoeff[B]', 'IFCoeff[N]',
    'PhAngleF[R]', 'PhAngleF[Y]', 'PhAngleF[B]',
]
_CALIB_MULTI_COLUMNS = (
    _CALIB_SINGLE_COLUMNS[:15]
    + ['FinalPhAngle[R]', 'FinalPhAngle[Y]', 'FinalPhAngle[B]']
    + _CALIB_SINGLE_COLUMNS[15:]
)

# multi-point acceptance window per coefficient: (low, high), both exclusive
_CALIB_MULTI_LIMITS = {}
for _phase in ('R', 'Y', 'B'):
    _CALIB_MULTI_LIMITS[f'VCoeff[{_phase}]'] = (0.00064, 0.00067)
    _CALIB_MULTI_LIMITS[f'ICoeff[{_phase}]'] = (0.000000200, 0.000000550)
    _CALIB_MULTI_LIMITS[f'ActPowerCoeff[{_phase}]'] = (0.000000000110, 0.000000000350)
    _CALIB_MULTI_LIMITS[f'PhAngle[{_phase}]'] = (0.11, 0.14)
    _CALIB_MULTI_LIMITS[f'FinalPhAngle[{_phase}]'] = (0.0020, 0.0030)
    _CALIB_MULTI_LIMITS[f'VFCoeff[{_phase}]'] = (0.00090, 0.00097)
    _CALIB_MULTI_LIMITS[f'IFCoeff[{_phase}]'] = (0.000000250, 0.000000750)
    _CALIB_MULTI_LIMITS[f'PhAngleF[{_phase}]'] = (0.11, 0.14)
_CALIB_MULTI_LIMITS['FrequencyCoeff'] = (0.99, 1.10)
_CALIB_MULTI_LIMITS['ICoeff[N]'] = (0.000000160, 0.000000550)
_CALIB_MULTI_LIMITS['IFCoeff[N]'] = (0.0000950, 0.00011)

# result column -> message shown when that step fails
FAIL_MESSAGES = {
    MCT_COLUMN: "Meter failed in MCT",
    "FTT_Live_version": "Fail in Live Version",
    "FTT_Get_duplicate_serial_num": "Fail in get duplicate serial number",
    "FTT_Calibration_Unlock": "Fail in calib unlock",
    "FTT_set_original_Meter_Serial_No": "Fail in set meter serial No",
    "FTT_get_serial_num_after_set": "Fail in get meter serial No after set",
    "FTT_Verify_meter_address": "Fail in Verify Meter Address",
    "FTT_Verify_DLMS_Activation": "Fail in Verify DLMS Activation",
    "FTT_Verify_Clear_Energy": "Fail in verify Clear Energy",
    "FTT_Get_Meter_PCB_Serial_No": "Fail in Get Meter PCB No",
    "FTT_Get_NIC_PCB_No": "Fail in Get NIC PCB No",
    "FTT_Get_Internal_Version": "Fail in Get Internal Version",
    "FTT_Verify_Meter_Calibration": "Fail in Meter Calibration",
    "FTT_Set_GPRS_Protocol": "Fail in Set GPRS Protocol",
    "FTT_Get_GPRS_Protocol": "Fail in Get GPRS Protocol",
    "FTT_Get_Apparent_Led_Status": "Fail in Get Apparent LED Status",
    "Set_Meter_Type_in_Amp": "Fail in set Meter Type in Amp",
    "FTT_factory_reset": "Fail in Factory Reset",
    "Get_Meter_Type_in_Amp": "Fail in Get Meter Type",
    "FTT_Set_Push_Interval": "Fail in set push interval",
    "FTT_Get_Push_Interval": "Fail in get push interval",
    "FTT_Set_Periodic_Push_IPv6_Address": "Fail in set periodic push ipv6 address",
    "FTT_Get_Periodic_Push_IPv6_Address": "Fail in get periodic push ipv6 address",
    "FTT_Set_Event_Push_IPv6_Address": "Fail in set event push ipv6 address",
    "FTT_Get_Event_Push_IPv6_Address": "Fail in get event push ipv6 address",
    MISMATCH_COLUMN: "Fail in Serial No Mismatch between Printed Meter Serial No and Inside Meter Serial No",
    PROVISIONING_COLUMN: "Fail in IMG Provisioning",
}


def get_log_columns(tool_type, meter_type, calib_type):
    """Return (meter_info_columns, test_result_columns) for this tool/meter/calibration."""
    is_4g = '4g' in tool_type.lower()
    is_wc = 'wc' in meter_type.lower()
    calib_columns = _CALIB_SINGLE_COLUMNS if 'single_point' in calib_type.lower() else _CALIB_MULTI_COLUMNS

    meter_cols = [
        INDEX_COLUMN, 'FTT_Date_time', SERIAL_COLUMN, 'FTT_Live_version',
        'FTT_Duplicate_Serial_No', 'FTT_Original_meter_address',
        'FTT_Active_Meter_Energy', 'FTT_Apparent_Meter_Energy', 'FTT_Reactive_Meter_Energy',
        'FTT_Meter_PCB_Serial_No', 'FTT_NIC_PCB_No', 'FTT_Internal_Version',
    ] + calib_columns + ['FTT_Get_GPRS_Protocol', 'FTT_Get_Apparent_Led_Status_Value']
    if is_wc:
        meter_cols.append('Meter_Type_Amp')
    if is_4g:
        meter_cols += ['FTT_Push_Interval', 'FTT_Periodic_Push_IPv6_Address', 'FTT_Event_Push_IPv6_Address']
    # all data columns go BEFORE the overall result ...
    if 'img' in tool_type.lower():
        meter_cols += IMG_DATA_COLUMNS
    meter_cols.append(OVERALL_COLUMN)

    # ... and all pass/fail columns go AFTER it
    result_cols = [
        MCT_COLUMN,
        "FTT_Live_version", "FTT_Get_duplicate_serial_num", "FTT_Calibration_Unlock",
        "FTT_set_original_Meter_Serial_No", "FTT_get_serial_num_after_set",
        "FTT_Verify_meter_address", "FTT_Verify_DLMS_Activation", "FTT_Verify_Clear_Energy",
        "FTT_Get_Meter_PCB_Serial_No", "FTT_Get_NIC_PCB_No", "FTT_Get_Internal_Version",
        "FTT_Verify_Meter_Calibration", "FTT_Set_GPRS_Protocol", "FTT_Get_GPRS_Protocol",
        "FTT_Get_Apparent_Led_Status",
    ]
    if is_wc:
        result_cols.append("Set_Meter_Type_in_Amp")
    result_cols.append("FTT_factory_reset")
    if is_wc:
        result_cols.append("Get_Meter_Type_in_Amp")
    if is_4g:
        result_cols += [
            "FTT_Set_Push_Interval", "FTT_Get_Push_Interval",
            "FTT_Set_Periodic_Push_IPv6_Address", "FTT_Get_Periodic_Push_IPv6_Address",
            "FTT_Set_Event_Push_IPv6_Address", "FTT_Get_Event_Push_IPv6_Address",
        ]
    result_cols.append(MISMATCH_COLUMN)
    if 'img' in tool_type.lower():
        result_cols += IMG_STATUS_COLUMNS
    return meter_cols, result_cols


def calib_in_range(calib, single_point):
    """True if every calibration coefficient in the dict `calib` is inside its window."""
    if single_point:
        for col in _CALIB_SINGLE_COLUMNS[1:]:          # skip CalibStatus
            # high = 1.05 if col == 'PhAngleF[B]' else 1.0
            if not (0.0 <= float(str(calib.get(col))) <= 1.0):
                return False
        return True
    for col, (low, high) in _CALIB_MULTI_LIMITS.items():
        if not (low < float(str(calib.get(col))) < high):
            return False
    return True


def build_log_entry(mac, meter_info, test_result, book_name, file_name, provisioning_reason=''):
    """One log record. meter_info / test_result are dicts keyed by Excel column name."""
    return {
        "mac_address": mac,
        "meter_info": meter_info,
        "test_result": test_result,
        "book_name": book_name,
        "file_name": file_name,
        "provisioning_reason": provisioning_reason,
    }


def add_log_xlsc(log, row_state):
    """Write one log record to the Excel workbook.

    row_state=True writes the header row (dict keys become the column names).
    Otherwise a data row is appended and every value is placed by looking up
    its column header, so a step that didn't run just leaves its cell blank
    instead of shifting every later value one column over. Keys that have no
    column yet (e.g. IMG provisioning fields) get a new header column.
    """
    mac_address = log["mac_address"]
    meter_info = log["meter_info"]
    test_result = log["test_result"]
    loc = log["book_name"]
    wb = openpyxl.load_workbook(loc)
    sheet = wb[log["file_name"]]

    if row_state:
        row = sheet.max_row
        sheet.cell(row=row, column=1).value = mac_address
        col = 2
        for key in list(meter_info) + list(test_result):
            sheet.cell(row=row, column=col).value = key
            col += 1
        wb.save(loc)
        return

    row = sheet.max_row + 1
    headers = [c.value for c in sheet[1]]
    while headers and headers[-1] is None:
        headers.pop()

    for key in list(meter_info) + list(test_result):
        if key not in headers:
            headers.append(key)
            sheet.cell(row=1, column=len(headers)).value = key

    meter_used = set()
    for col, header in enumerate(headers, start=1):
        if header is None:
            continue
        if col == 1:
            value = mac_address
        elif header == INDEX_COLUMN:
            value = row - 1
        elif header in meter_info and header not in meter_used:
            # some names (e.g. FTT_Live_version) are both a data column and a
            # result column: the first one is the data, the second the result
            meter_used.add(header)
            value = meter_info[header]
        elif header in test_result:
            value = test_result[header]
        else:
            value = None
        sheet.cell(row=row, column=col).value = str(value)
    wb.save(loc)


def addDefaultFttLog(bookName, fileName, TOOL_TYPE, meter_type, calib_type):
    if False == verify_log_xlsc(bookName, fileName):
        print("xlsx file for log not found. creating one to store test report")
        meter_cols, result_cols = get_log_columns(TOOL_TYPE, meter_type, calib_type)
        header_log = build_log_entry(
            MAC_COLUMN,
            {c: c for c in meter_cols},
            {c: c for c in result_cols},
            bookName, fileName,
        )
        close_excel_file(bookName)
        add_log_xlsc(header_log, True)

def enterSrNum_ftt(serial_cfg):
    if (serial_cfg.get("PROJECT", "").lower() == "gomati") or (serial_cfg.get("PROJECT", "").lower() == "saryu"):
        while(1):
            # scanning of barcode and taking serial no input
            try:
                serial_num = ''
                serial_num = input("Enter Meter Serial Num(ex-PO12345678): ")
                # match=re.match(r'^[a-zA-Z]{4}\d{6}$',serial_num)
                match = re.match(r'^PO\d{8}$', serial_num)
                # print "type of serial_num = ",type(serial_num)
                if  match:
                    last_EIGHT_digits=serial_num[-8:]
                    return last_EIGHT_digits
                else:
                    raise ValueError("invalid  format of serial num please  enter in this format  (ex-PO12345678)")
            except ValueError as e:
                print(e)
    elif((serial_cfg.get("PROJECT", "").lower() == "mn")):
        if ("wc" in serial_cfg.get("METER_TYPE", "").lower()):
            while(1):
                # scanning of barcode and taking serial no input
                try:
                    serial_num = ''
                    serial_num = input("Enter Meter Serial Num(ex-MN3P232345): ")
                    # match=re.match(r'^[a-zA-Z]{4}\d{6}$',serial_num)
                    match = re.match(r'^MN3P\d{6}$', serial_num)
                    # print "type of serial_num = ",type(serial_num)
                    if  match:
                        last_six_digits=serial_num[-6:]
                        return last_six_digits
                    else:
                        raise ValueError("invalid  format of serial num please  enter in this format  (ex-MN3P232345)")
                except ValueError as e:
                    print(e)
        else:
            while(1):
                # scanning of barcode and taking serial no input
                try:
                    serial_num = ''
                    serial_num = input("Enter Meter Serial Num(ex-MNCT234567): ")
                    # match=re.match(r'^[a-zA-Z]{4}\d{6}$',serial_num)
                    match = re.match(r'^MNCT\d{6}$', serial_num)
                    # print "type of serial_num = ",type(serial_num)
                    if  match:
                        last_EIGHT_digits=serial_num[-6:]
                        return last_EIGHT_digits
                    else:
                        raise ValueError("invalid  format of serial num please  enter in this format  (ex-MNCT234567)")
                except ValueError as e:
                    print(e)
    elif((serial_cfg.get("PROJECT", "").lower() == "wb")):
        while(1):
            # scanning of barcode and taking serial no input
            try:
                serial_num = ''
                serial_num = input("Enter Meter Serial Num(ex-PPD1234567): ")  # wb requirement to change PLL from PO
                # match=re.match(r'^[a-zA-Z]{4}\d{6}$',serial_num)
                match = re.match(r'^PPD\d{7}$', serial_num)
                # print "type of serial_num = ",type(serial_num)
                if  match:
                    last_Seven_digits=serial_num[-7:]
                    return last_Seven_digits
                else:
                    raise ValueError("invalid  format of serial num please  enter in this format  (ex-PPD1234567)")
            except ValueError as e:
                print(e)
    elif((serial_cfg.get("PROJECT", "").lower() == "tn")):
        while(1):
            # scanning of barcode and taking serial no input
            try:
                serial_num = ''
                serial_num = input("Enter Meter Serial Num(ex-PO12345678): ")
                # match=re.match(r'^[a-zA-Z]{4}\d{6}$',serial_num)
                match = re.match(r'^PO\d{8}$', serial_num)
                # print "type of serial_num = ",type(serial_num)
                if  match:
                    last_EIGHT_digits=serial_num[-8:]
                    return last_EIGHT_digits
                else:
                    raise ValueError("invalid  format of serial num please  enter in this format  (ex-PO12345678)")
            except ValueError as e:
                print(e)
    elif((serial_cfg.get("PROJECT", "").lower() == "others")):
        while(1):
            # scanning of barcode and taking serial no input
            try:
                serial_num = ''
                serial_num = input("Enter Meter Serial Num(ex-LR12345678 or any other identifier): ")
                # match=re.match(r'^[a-zA-Z]{4}\d{6}$',serial_num)
                # match = re.match(r'^PL\d{8}$', serial_num)
                # print "type of serial_num = ",type(serial_num)
                if len(serial_num) == 10:
                    last_EIGHT_digits=serial_num[-8:]
                    return last_EIGHT_digits
                else:
                    raise ValueError("invalid  format of serial num please  enter in this format  (ex-LR12345678 or any other identifier)")
            except ValueError as e:
                print(e)
    else:
        raise ValueError("invalid ----- format of Project name selected in config file please  enter in this format  (ex-gomati, saryu or manipur or wb)")

class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def set_push_control(serial_port, com):
    print("\nStarting Set Push Control Mode")
    logging.info(f"Sending Command To Set Push Control Mode")
    try:
        if not com.open():
            return None

        # Frame to send the command to Set Push Control Mode
        body = bytes([
            0xaa, 0x01, 0xCF, 0x62, 0xc9,
            0xff, 0xff, 0xff, 0xff,
            0x04, 0x04, 0x03, 0xCF, 0x62, 0x01, 0xE4, 0x22
        ])

        # Send the data
        com.send_data(body, expected_payload_len=2)
        print("\nCommand sent for Set Push Control Mode")

        # Wait for response
        response = com.read_response(timeout=5)

        pattern = bytes.fromhex("e8 03")
        print("\nRead response from meter to check Set Push Control Mode")
        if pattern in response:
            print("\nSuccessfully Set Push Control Mode: ", 1)
            logging.info(f"Successfully Set Push Control Mode: 1")
            return True
        else:
            print(f"\nError in Set Push Control Mode, Response{response}")
            logging.info(f"Error in Set Push Control Mode, Response{response}")
            return False
    except Exception as e:
        print(f"\nPort {serial_port}, Error in Set Push Control Mode: {e}")
        logging.error(f"Port {serial_port}, Error in Set Push Control Mode: {e}")
    return False

def get_push_control(serial_port, com):
    print("\nStarting Get Push Control Mode")
    logging.info(f"Sending Command To Get Push Control Mode")
    try:
        if not com.open():
            return None

        # Frame to send the command to Get Push Control Mode
        body = bytes([
            0xaa, 0x01, 0xCF, 0x63, 0xc9,
            0xff, 0xff, 0xff, 0xff,
            0x04, 0x04, 0x02, 0xCF, 0x63, 0xB2, 0xF3
        ])

        # Send the data
        com.send_data(body, expected_payload_len=2)
        print("\nCommand sent for Get Push Control Mode")

        # Wait for response
        response = com.read_response(timeout=5)
        get_push = int.from_bytes(response[12:13], 'big')

        print("\nRead response from meter to check Get Push Control Mode")
        if get_push == 1:
            print("Verify Push Control Mode: ",get_push)
            logging.info(f"Get Push Control Mode is Successfully done")
            return True
        else:
            print(f"\nError in Get Push Control Mode, Response{response}")
            logging.info(f"Error in Get Push Control Mode, Response{response}")
            return False
    except Exception as e:
        print(f"\nPort {serial_port}, Error in Get Push Control Mode: {e}")
        logging.error(f"Port {serial_port}, Error in Get Push Control Mode: {e}")
    return False



def set_push_interval(serial_port, com, interval):
    print("\nStarting Set Push Interval")
    # logging.info(f"Sending Command To Set Push Interval")
    retryCnt = 3
    while (retryCnt):
        try:
            if not com.open():
                return None

            # Frame to send the command to Get Push Interval
            body = bytes([
                0xAA, 0x01, 0xD3, 0x1B, 0xC9,
                0xFF, 0xFF, 0xFF, 0xFF,
                0x04, 0x04, 0x06, 0xD3,
                0x1B, 0x00, 0x00, 0x00, 0x3C, 0xE6, 0xCA
            ])

            # Send the data
            com.send_data(body, expected_payload_len=2)
            print("\nCommand sent for Set Push Interval")

            # Wait for response
            response = com.read_response(timeout=5)
            print("\nResponse received for Set Push Interval: ", response)
            pattern = bytes.fromhex("e8 03")
            print("\nRead response from meter to check Set Push Interval")
            if pattern in response:
                print("Default Push Interval is Successfully set to 60 seconds")
                return True
            else:
                print(f"\nError in Set Push Interval, Response{response}")
                # logging.info(f"Error in Set Push Interval, Response{response}")
                return False
        except Exception as e:
            print(f"\nPort {serial_port}, Error in Set Push Interval: {e}")
            # logging.error(f"Port {serial_port}, Error in Set Push Interval: {e}")
    return False

def get_push_interval(serial_port, com):
    print("\nStarting Get Push Interval")
    # logging.info(f"Sending Command To Get Push Interval ")
    retryCnt = 3
    while (retryCnt):
        try:
            if not com.open():
                return None

            # Frame to send the command to Get Push Control Mode
            body = bytes([
                0xAA, 0x01, 0xD3, 0x1A, 0xC9,
                0xFF, 0xFF, 0xFF, 0xFF,
                0x04, 0x04, 0x02, 0xD3, 0x1A, 0xB2, 0x1E
            ])

            # Send the data
            com.send_data(body, expected_payload_len=2)
            print("\nCommand sent for Get Push Interval")

            # Wait for response
            response = com.read_response(timeout=5)
            print("\nResponse received for Get Push Interval: ", response)
            get_push = int.from_bytes(response[12:16], 'big')

            print("\nRead response from meter to check Get Push Interval", get_push)
            if get_push == 60:
                print("Verify Push Interval: ",get_push)
                # logging.info(f"Get Push Interval is Successfully done")
                return True
            else:
                print(f"\nError in Get Push Interval, Response{response}")
                # logging.info(f"Error in Get Push Interval, Response{response}")
                return False
        except Exception as e:
            print(f"\nPort {serial_port}, Error in Get Push Interval: {e}")
            # logging.error(f"Port {serial_port}, Error in Get Push Interval: {e}")
    return False

def set_periodic_push_ipv6_address(serial_port, com, ipv6_address):
    print("\nStarting Set Periodic Push IPv6 Address")
    # logging.info(f"Sending Command To Set Periodic Push IPv6 Address")
    retryCnt = 3
    while (retryCnt):
        try:
            # if not com.open():
            #     return None

            body = ""
            # Frame to send the command to Set Periodic Push IPv6 Address
            if ipv6_address == "2406:da1a:565:f50d:c7ee:8336:ef46:ffc2,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1D, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF,0x04, 0x04, 0x2D, 0xD3, 0x1D,0x32, 0x34, 0x30, 0x36,0x3A, 0x64, 0x61, 0x31, 0x61,0x3A, 0x35, 0x36, 0x35,0x3A, 0x66, 0x35, 0x30, 0x64,0x3A, 0x63, 0x37, 0x65,0x65, 0x3A, 0x38, 0x33, 0x33,0x36, 0x3A, 0x65, 0x66,0x34, 0x36, 0x3A, 0x66, 0x66,0x63, 0x32, 0x2C, 0x34,0x30, 0x35, 0x39, 0x70, 0x70
                    ])

            elif ipv6_address == "2406:da1a:f52:c907:7a85:8dfe:a74d:c7da,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1D, 0xC9, 0xFF, 0xFF, 0xFF,0xFF, 0x04, 0x04, 0x2D, 0xD3, 0x1D, 0x32, 0x34, 0x30, 0x36, 0x3A, 0x64, 0x61, 0x31, 0x61, 0x3A, 0x66, 0x35, 0x32, 0x3A, 0x63, 0x39, 0x30, 0x37, 0x3A, 0x37, 0x61, 0x38, 0x35, 0x3A, 0x38, 0x64, 0x66, 0x65, 0x3A, 0x61, 0x37, 0x34, 0x64, 0x3A, 0x63, 0x37, 0x64, 0x61, 0x2C, 0x34, 0x30, 0x35, 0x39, 0xDA, 0xCA
                    ])
            
            elif ipv6_address == "2406:da1a:ccf:9500:eeaa:4c65:58ae:63bb,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1D, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF, 0x04, 0x04, 0x2D, 0xD3, 0x1D, 0x32, 0x34, 0x30, 0x36, 0x3A, 0x64, 0x61, 0x31, 0x61, 0x3A, 0x63, 0x63, 0x66, 0x3A, 0x39, 0x35, 0x30, 0x30, 0x3A, 0x65, 0x65, 0x61, 0x61, 0x3A, 0x34, 0x63, 0x36, 0x35, 0x3A, 0x35, 0x38, 0x61, 0x65, 0x3A, 0x36, 0x33, 0x62, 0x62, 0x2C, 0x34, 0x30, 0x35, 0x39, 0x64, 0xE6
                    ])
            
            elif ipv6_address == "2603:c021:4007:a000:db7a:c271:e6f8:c28d,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1D, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF, 0x04, 0x04, 0x2E, 0xD3, 0x1D, 0x32, 0x36, 0x30, 0x33, 0x3A, 0x63, 0x30, 0x32, 0x31, 0x3A, 0x34, 0x30, 0x30, 0x37, 0x3A, 0x61, 0x30, 0x30, 0x30, 0x3A, 0x64, 0x62, 0x37, 0x61, 0x3A, 0x63, 0x32, 0x37, 0x31, 0x3A, 0x65, 0x36, 0x66, 0x38, 0x3A, 0x63, 0x32, 0x38, 0x64, 0x2C, 0x34, 0x30, 0x35, 0x39, 0x4E, 0x41
                    ])


            elif ipv6_address == "2406:da1a:1bc9:cd03:0000:0000:0000:000a,4059":
                body = bytes([0xAA, 0x01, 0xD3, 0x1D, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF, 0x04, 0x04, 0x2E, 0xD3, 0x1D, 0x32, 0x34, 0x30, 0x36, 0x3A, 0x64, 0x61, 0x31, 0x61, 0x3A, 0x31, 0x62, 0x63, 0x39, 0x3A, 0x63, 0x64, 0x30, 0x33, 0x3A, 0x30, 0x30, 0x30, 0x30, 0x3A, 0x30, 0x30, 0x30, 0x30, 0x3A, 0x30, 0x30, 0x30, 0x30, 0x3A, 0x30, 0x30, 0x30, 0x61, 0x2C, 0x34, 0x30, 0x35, 0x39, 0xCA, 0xEA])
            

            # Send the data
            com.send_data(body, expected_payload_len=2)
            print("\nCommand sent for Set Periodic Push IPv6 Address")

            # Wait for response
            response = com.read_response(timeout=5)
            print("\nResponse received for Set Periodic Push IPv6 Address: ", response)
            pattern = bytes.fromhex("e8 03")
            print("\nRead response from meter to check Set Periodic Push IPv6 Address")
            if pattern in response:
                print("Default Periodic Push IPv6 Address is Successfully done")
                return True
            else:
                print(f"\nError in Set Periodic Push IPv6 Address, Response{response}")
                # logging.info(f"Error in Set Periodic Push IPv6 Address, Response{response}")
                return False
        except Exception as e:
            print(f"\nPort {serial_port}, Error in Set Periodic Push IPv6 Address: {e}")
            # logging.error(f"Port {serial_port}, Error in Set Periodic Push IPv6 Address: {e}")
    return False

def get_periodic_push_ipv6_address(serial_port, com, ipv6_address):
    print("\nStarting Get Periodic Push IPv6 Address")
    # logging.info(f"Sending Command To Get Periodic Push IPv6 Address")
    retryCnt = 3
    while (retryCnt):
        try:
            # if not com.open():
            #     return None

            # Frame to send the command to Get Periodic Push IPv6 Address
            body = bytes([
                0xAA, 0x01, 0xD3, 0x1C, 0xC9,
                0xFF, 0xFF, 0xFF, 0xFF,
                0x04, 0x04, 0x02, 0xD3, 0x1C, 0x13, 0x86
            ])

            # Send the data
            com.send_data(body, expected_payload_len=2)
            print("\nCommand sent for Get Periodic Push IPv6 Address")

            # Wait for response
            response = com.read_response(timeout=5)
            print("\nResponse received for Get Periodic Push IPv6 Address: ", response)
            get_push = response[12:56].decode('utf-8').rstrip('\x00')

            print("\nRead response from meter to check Get Periodic Push IPv6 Address", get_push)
            print("\nExpected Periodic Push IPv6 Address: ", ipv6_address)
            if get_push.strip() == ipv6_address:
                print("Verify Periodic Push IPv6 Address: ",get_push)
                # logging.info(f"Get Periodic Push IPv6 Address is Successfully done")
                return True
            else:
                print(f"\nError in Get Periodic Push IPv6 Address, Response{response}")
                # logging.info(f"Error in Get Periodic Push IPv6 Address, Response{response}")
                return False
        except Exception as e:
            print(f"\nPort {serial_port}, Error in Get Periodic Push IPv6 Address: {e}")
            # logging.error(f"Port {serial_port}, Error in Get Periodic Push IPv6 Address: {e}")
    return False

def set_event_push_ipv6_address(serial_port, com, ipv6_address):
    print("\nStarting Set Event Push IPv6 Address")
    # logging.info(f"Sending Command To Set Event Push IPv6 Address")
    retryCnt = 3
    while (retryCnt):
        try:
            # if not com.open():
            #     return None

            body = ""
            # Frame to send the command to Set Event Push IPv6 Address
            if ipv6_address == "2406:da1a:565:f50d:c7ee:8336:ef46:ffc2,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1F, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF,0x04, 0x04, 0x2D, 0xD3, 0x1F,0x32, 0x34, 0x30, 0x36,0x3A, 0x64, 0x61, 0x31, 0x61,0x3A, 0x35, 0x36, 0x35,0x3A, 0x66, 0x35, 0x30, 0x64,0x3A, 0x63, 0x37, 0x65,0x65, 0x3A, 0x38, 0x33, 0x33,0x36, 0x3A, 0x65, 0x66,0x34, 0x36, 0x3A, 0x66, 0x66,0x63, 0x32, 0x2C, 0x34,0x30, 0x35, 0x39, 0xD7, 0x47
                    ])

            elif ipv6_address == "2406:da1a:f52:c907:7a85:8dfe:a74d:c7da,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1F, 0xC9, 0xFF, 0xFF, 0xFF,0xFF, 0x04, 0x04, 0x2D, 0xD3, 0x1F, 0x32, 0x34, 0x30, 0x36, 0x3A, 0x64, 0x61, 0x31, 0x61, 0x3A, 0x66, 0x35, 0x32, 0x3A, 0x63, 0x39, 0x30, 0x37, 0x3A, 0x37, 0x61, 0x38, 0x35, 0x3A, 0x38, 0x64, 0x66, 0x65, 0x3A, 0x61, 0x37, 0x34, 0x64, 0x3A, 0x63, 0x37, 0x64, 0x61, 0x2C, 0x34, 0x30, 0x35, 0x39, 0x7D, 0xFD
                    ])
            
            elif ipv6_address == "2406:da1a:ccf:9500:eeaa:4c65:58ae:63bb,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1F, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF, 0x04, 0x04, 0x2D, 0xD3, 0x1F, 0x32, 0x34, 0x30, 0x36, 0x3A, 0x64, 0x61, 0x31, 0x61, 0x3A, 0x63, 0x63, 0x66, 0x3A, 0x39, 0x35, 0x30, 0x30, 0x3A, 0x65, 0x65, 0x61, 0x61, 0x3A, 0x34, 0x63, 0x36, 0x35, 0x3A, 0x35, 0x38, 0x61, 0x65, 0x3A, 0x36, 0x33, 0x62, 0x62, 0x2C, 0x34, 0x30, 0x35, 0x39, 0xC3, 0xD1
                    ])
            
            elif ipv6_address == "2603:c021:4007:a000:db7a:c271:e6f8:c28d,4059":
                body = bytes([
                    0xAA, 0x01, 0xD3, 0x1F, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF, 0x04, 0x04, 0x2E, 0xD3, 0x1F, 0x32, 0x36, 0x30, 0x33, 0x3A, 0x63, 0x30, 0x32, 0x31, 0x3A, 0x34, 0x30, 0x30, 0x37, 0x3A, 0x61, 0x30, 0x30, 0x30, 0x3A, 0x64, 0x62, 0x37, 0x61, 0x3A, 0x63, 0x32, 0x37, 0x31, 0x3A, 0x65, 0x36, 0x66, 0x38, 0x3A, 0x63, 0x32, 0x38, 0x64, 0x2C, 0x34, 0x30, 0x35, 0x39, 0x8C, 0x1C
                    ])  
                 

            elif ipv6_address == "2406:da1a:1bc9:cd03:0000:0000:0000:000a,4059":
                body = bytes([0xAA, 0x01, 0xD3, 0x1F, 0xC9, 0xFF, 0xFF, 0xFF, 0xFF, 0x04, 0x04, 0x2E, 0xD3, 0x1F, 0x32, 0x34, 0x30, 0x36, 0x3A, 0x64, 0x61, 0x31, 0x61, 0x3A, 0x31, 0x62, 0x63, 0x39, 0x3A, 0x63, 0x64, 0x30, 0x33, 0x3A, 0x30, 0x30, 0x30, 0x30, 0x3A, 0x30, 0x30, 0x30, 0x30, 0x3A, 0x30, 0x30, 0x30, 0x30, 0x3A, 0x30, 0x30, 0x30, 0x61, 0x2C, 0x34, 0x30, 0x35, 0x39, 0x08, 0xB7])
            # Send the data
            com.send_data(body, expected_payload_len=2)
            print("\nCommand sent for Set Event Push IPv6 Address")

            # Wait for response
            response = com.read_response(timeout=5)
            print("\nResponse received for Set Event Push IPv6 Address: ", response)
            pattern = bytes.fromhex("e8 03")
            print("\nRead response from meter to check Set Event Push IPv6 Address")
            if pattern in response:
                print("Default Event Push IPv6 Address is Successfully done")
                return True
            else:
                print(f"\nError in Set Event Push IPv6 Address, Response{response}")
                # logging.info(f"Error in Set Event Push IPv6 Address, Response{response}")
                return False
        except Exception as e:
            print(f"\nPort {serial_port}, Error in Set Event Push IPv6 Address: {e}")
            return False
            # logging.error(f"Port {serial_port}, Error in Set Event Push IPv6 Address: {e}")
    return False

def get_event_push_ipv6_address(serial_port, com, ipv6_address):
    print("\nStarting Get Periodic Push IPv6 Address")
    # logging.info(f"Sending Command To Get Event Push IPv6 Address")
    retryCnt = 3
    while (retryCnt):
        try:
            # if not com.open():
            #     return None

            # Frame to send the command to Get Event Push IPv6 Address
            body = bytes([
                0xAA, 0x01, 0xD3, 0x1E, 0xC9,
                0xFF, 0xFF, 0xFF, 0xFF,
                0x04, 0x04, 0x02, 0xD3, 0x1E, 0x73, 0x0E
            ])


            # Send the data
            com.send_data(body, expected_payload_len=2)
            print("\nCommand sent for Get Event Push IPv6 Address")

            # Wait for response
            response = com.read_response(timeout=5)
            print("\nResponse received for Get Event Push IPv6 Address: ", response)
            get_push = response[12:56].decode('utf-8').rstrip('\x00')

            print("\nRead response from meter to check Get Event Push IPv6 Address", get_push)
            print("\nExpected Event Push IPv6 Address: ", ipv6_address)
            if get_push.strip() == ipv6_address:
                print("Verify Event Push IPv6 Address: ",get_push)
                # logging.info(f"Get Event Push IPv6 Address is Successfully done")
                return True
            else:
                print(f"\nError in Get Event Push IPv6 Address, Response{response}")
                # logging.info(f"Error in Get Event Push IPv6 Address, Response{response}")
                return False
        except Exception as e:
            print(f"\nPort {serial_port}, Error in Get Event Push IPv6 Address: {e}")
            return False
            # logging.error(f"Port {serial_port}, Error in Get Event Push IPv6 Address: {e}")
    return False

def main_function(serial_cfg, com_port, stage_results, meter_serial_num, input_pcb_no, input_nic_pcb_no, result_queue, abort_flag, result_log):
    """Run the full FTT (+ IMG provisioning) sequence on one COM port.

    Data is kept in two dicts keyed by Excel column name:
      meter_info  - raw values read from the meter (versions, serials, coefficients ...)
      test_result - 'pass' / 'fail' / 'skip' per test step
    Both are packed into `result_log` (a dict) via build_log_entry() at the end.
    """
    ser = None
    try:
        # Per-port stage status (shared dict, read back by run() and the summary popup)
        stage = stage_results.setdefault(com_port.lower(), {})
        stage.update({"mct": "fail", "mct_reason": "", "prov": "fail", "prov_reason": ""})

        def stop_port(reason, ser_obj=None):
            """Stop the test for this port only and record why."""
            stage["mct_reason"] = stage["mct_reason"] or reason
            result_queue.append([reason])
            logging.error(f"{com_port}: {reason}")
            if ser_obj is not None:
                try:
                    ser_obj.close()
                except Exception:
                    pass

        try:
            ser = serial.Serial(com_port, baudrate=9600, timeout=10)
        except Exception as e:
            stop_port(f"COM port is unable to open: {e}")
            return 0

        portID = 4
        cases = TestCasePCTMCT(ser, portID, serial_cfg.get("RETRIES", 3), serial_cfg.get("NIC_PCB_LENGTH", 27))
        toolName = serial_cfg.get("TOOL_TYPE", "img_ftt").lower()
        is_4g = '4g' in toolName
        is_img = 'img' in toolName
        mac = get_system_mac_address(toolName)
        pcb_start_address = 3079
        nic_start_address = 3111
        meter_project = serial_cfg.get('PROJECT', 'gomati')
        current_rating = "(20-100)A"
        if '10-60' in serial_cfg.get('CURRENT_RATING', '10-100').lower():
            current_rating = "(10-60)A"
        elif '10-100' in serial_cfg.get('CURRENT_RATING', '10-100').lower():
            current_rating = "(10-100)A"
        elif '20-100' in serial_cfg.get('CURRENT_RATING', '10-100').lower():
            current_rating = "(20-100)A"
        interval = 60
        ipv6_address = {
            "gomati": "2406:da1a:565:f50d:c7ee:8336:ef46:ffc2,4059",
            "saryu": "2406:da1a:f52:c907:7a85:8dfe:a74d:c7da,4059",
            "mn": "2406:da1a:ccf:9500:eeaa:4c65:58ae:63bb,4059",
            "wb": "2603:c021:4007:a000:db7a:c271:e6f8:c28d,4059",
            "tn": "2406:da1a:1bc9:cd03:0000:0000:0000:000a,4059",
        }.get(meter_project, "")

        if 'wc' in serial_cfg.get("METER_TYPE", "3pwc").lower():
            meter_type = "3PWC"
        elif 'ltct' in serial_cfg.get("METER_TYPE", "3pltct").lower():
            meter_type = "3PLTCT"
        else:
            result_queue.append(["Wrong Project Selected"])
            return 0
        is_wc = 'wc' in meter_type.lower()
        calib_type = serial_cfg.get("CALIB_TYPE", 'single_point').lower()
        single_point = 'single_point' in calib_type
        calib_columns = _CALIB_SINGLE_COLUMNS if single_point else _CALIB_MULTI_COLUMNS

        bookName = meter_type.upper() + "_" + toolName.upper() + "_" + "{}".format(str(serial_cfg.get("FTT_TEST_STATION", 1))) + "_LOG.xlsx"
        fileName = toolName.upper() + "_DATA_LOG"
        starttime = datetime.datetime.now()
        print("\nStartTime:", starttime, com_port)

        # Every step starts as 'fail' so a step that never ran is reported as failed
        meter_cols, result_cols = get_log_columns(toolName, meter_type, calib_type)
        meter_info = {col: '' for col in meter_cols if col != INDEX_COLUMN}
        test_result = {col: '' for col in result_cols}
        test_result[MISMATCH_COLUMN] = 'pass'   # re-checked in run() after the meter is scanned again
        provisioning_fail_reason = ''

        meter_info['FTT_Date_time'] = datetime.datetime.now()
        meter_info[SERIAL_COLUMN] = str(meter_serial_num)
        close_excel_file(bookName)
        addDefaultFttLog(bookName, fileName, toolName, meter_type, calib_type)

        # Check Live Version
        retryCnt = 3
        check_port = None
        while retryCnt:
            try:
                logging.info(f"Checking live version for port: {com_port}, Attempt: {4 - retryCnt}")
                check_port = cases.get_live_version_val()
                logging.info(f"Live version check result for port: {com_port}: {check_port}")
                print(check_port)
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error checking live version for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                print(e)
                retryCnt -= 1

        # STEP 1: COM port / meter reachable?
        if check_port is None or str(check_port).lower() == 'fail':
            stop_port("COM port is unreachable (no live version)", ser)
            return 0

        # STEP 2: read PCB serial number from the meter (once)
        meter_pcb_serial = cases.Get_pcb_serial_num(pcb_start_address)
        if not meter_pcb_serial or str(meter_pcb_serial) == "0":
            stop_port("Unable to read PCB serial number from meter", ser)
            return 0

        # STEP 3: MCT must have passed (4G and IMG meters)
        if not db_connect.fetch_by_pcb_serial(meter_pcb_serial):
            stop_port("Meter failed in MCT", ser)
            return 0
        stage["mct"] = "pass"
        test_result[MCT_COLUMN] = 'pass'

        meter_info['FTT_Live_version'] = str(check_port)
        test_result['FTT_Live_version'] = 'pass' if str(check_port) == str(serial_cfg.get("LIVE_VERSION", 0)) else 'fail'

        # Verify Serial Number
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Verifying serial number for port: {com_port}, Attempt: {4 - retryCnt}")
                sr_num = cases.Verify_Serial_number()
                logging.info(f"Serial number verification result for port: {com_port}: {sr_num}")
                meter_info['FTT_Duplicate_Serial_No'] = 'fail' if 'fail' in sr_num.lower() else str(sr_num)
                Sr_num2 = cases.Verify_Serial_number2()
                logging.info(f"Serial number verification 2 result for port: {com_port}: {Sr_num2}")
                test_result['FTT_Get_duplicate_serial_num'] = 'pass' if Sr_num2.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error verifying serial number for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Calibration Unlock
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Performing calibration unlock for port: {com_port}, Attempt: {4 - retryCnt}")
                calib_unlock = cases.Calibration_unLock()
                logging.info(f"Calibration unlock result for port: {com_port}: {calib_unlock}")
                test_result['FTT_Calibration_Unlock'] = 'pass' if calib_unlock.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error performing calibration unlock for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Set Meter Serial Number
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Setting meter serial number for port: {com_port}, Attempt: {4 - retryCnt}")
                set_serial_num = cases.Set_Meter_serial_number(int(meter_serial_num))
                test_result['FTT_set_original_Meter_Serial_No'] = 'pass' if set_serial_num.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error setting meter serial number for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Verify Serial Number after set
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Verifying serial number after setting for port: {com_port}, Attempt: {4 - retryCnt}")
                sr_num = cases.Verify_Serial_number()
                logging.info(f"Serial number verification after setting result for port: {com_port}: {sr_num}")
                if sr_num == 'fail':
                    test_result['FTT_get_serial_num_after_set'] = 'fail'
                else:
                    test_result['FTT_get_serial_num_after_set'] = 'pass' if sr_num == str(meter_serial_num.lstrip('0')) else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error verifying serial number after setting for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Get Meter Address
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Getting meter address for port: {com_port}, Attempt: {4 - retryCnt}")
                Meter_address = cases.get_Meter_address()
                logging.info(f"Meter address retrieval result for port: {com_port}: {Meter_address}")
                print(Meter_address)
                meter_info['FTT_Original_meter_address'] = 'fail' if 'fail' in Meter_address.lower() else str(Meter_address)
                meter_addr2 = cases.get_Meter_address2(int(sr_num))
                logging.info(f"Meter address verification result for port: {com_port}: {meter_addr2}")
                test_result['FTT_Verify_meter_address'] = 'pass' if meter_addr2.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while getting meter address for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Check DLMS Activation
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Checking DLMS activation for port: {com_port}, Attempt: {4 - retryCnt}")
                CHECK_DLMS_ACTIVATION = cases.dlms_Activation_check_value(serial_cfg.get("DLMS_TYPE", "NEW_DLMS").lower())
                logging.info(f"DLMS activation check result for port: {com_port}: {CHECK_DLMS_ACTIVATION}")
                test_result['FTT_Verify_DLMS_Activation'] = 'pass' if CHECK_DLMS_ACTIVATION.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while checking DLMS activation for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Verify Energy
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Verifying energy for port: {com_port}, Attempt: {4 - retryCnt}")
                clear_energy = cases.Verify_energy()
                logging.info(f"Energy verification result for port: {com_port}: {clear_energy}")
                meter_info['FTT_Active_Meter_Energy'] = str(clear_energy.get('Active Energy'))
                meter_info['FTT_Apparent_Meter_Energy'] = str(clear_energy.get('Apparent Energy'))
                meter_info['FTT_Reactive_Meter_Energy'] = str(clear_energy.get('Reactive Energy Q1'))
                test_result['FTT_Verify_Clear_Energy'] = 'pass' if clear_energy.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while verifying energy for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1
                if retryCnt == 0:
                    for col in ('FTT_Active_Meter_Energy', 'FTT_Apparent_Meter_Energy', 'FTT_Reactive_Meter_Energy'):
                        meter_info[col] = 'fail'

        # Get PCB Serial number
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Getting PCB serial number for port: {com_port}, Attempt: {4 - retryCnt}")
                Pcb_serial_no = cases.Get_pcb_serial_num(pcb_start_address)
                logging.info(f"PCB serial number retrieval result for port: {com_port}: {Pcb_serial_no}")
                meter_info['FTT_Meter_PCB_Serial_No'] = str(Pcb_serial_no)
                same = str(Pcb_serial_no) in (str(input_pcb_no.lower()), str(input_pcb_no.upper()))
                test_result['FTT_Get_Meter_PCB_Serial_No'] = 'pass' if same else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while getting PCB serial number for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1
                print("Exception in get pcb serial numebr ", e)

        # Get NIC PCB Number
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Getting NIC PCB number for port: {com_port}, Attempt: {4 - retryCnt}")
                Nic_PCB_no = cases.Nic_PCB_No(nic_start_address)
                logging.info(f"NIC PCB number retrieval result for port: {com_port}: {Nic_PCB_no}")
                meter_info['FTT_NIC_PCB_No'] = str(Nic_PCB_no)
                same = str(Nic_PCB_no) in (str(input_nic_pcb_no.lower()), str(input_nic_pcb_no.upper()))
                test_result['FTT_Get_NIC_PCB_No'] = 'pass' if same else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while getting NIC PCB number for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Get Internal Version
        if serial_cfg.get('INTERNAL_VERSION', 0) == 0:
            print("\nSkipping to Get INTERNAL VERSION")
            logging.info(f"Skipping to get internal version for port: {com_port} as INTERNAL_VERSION is set to 0 in config")
            test_result['FTT_Get_Internal_Version'] = 'skip'
            meter_info['FTT_Internal_Version'] = '0'
        else:
            retryCnt = 3
            while retryCnt:
                try:
                    logging.info(f"Getting internal version for port: {com_port}, Attempt: {4 - retryCnt}")
                    int_version = cases.get_internal_version_val()
                    logging.info(f"Internal version retrieval result for port: {com_port}: {int_version}")
                    meter_info['FTT_Internal_Version'] = str(int_version)
                    test_result['FTT_Get_Internal_Version'] = 'pass' if str(int_version) == str(serial_cfg.get('INTERNAL_VERSION', 0)) else 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error occurred while getting internal version for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                    retryCnt = retryCnt - 1

        # Get 3P Cofficients
        retryCnt = 3
        while retryCnt:
            try:
                calib_cofficient = cases.get_3p_calib_coffi(calib_type)
                if 'fail' in calib_cofficient:
                    for col in calib_columns:
                        meter_info[col] = 'Fail'
                    test_result['FTT_Verify_Meter_Calibration'] = 'fail'
                else:
                    for col in calib_columns:
                        meter_info[col] = str(calib_cofficient.get(col))
                    ok = calib_in_range(calib_cofficient, single_point)
                    test_result['FTT_Verify_Meter_Calibration'] = 'pass' if ok else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while getting 3P coefficients for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1
                if retryCnt == 0:
                    for col in calib_columns:
                        meter_info[col] = 'Fail'
                    test_result['FTT_Verify_Meter_Calibration'] = 'fail'

        # Set GPRS Protocols Value
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Setting GPRS protocol for port: {com_port}, Attempt: {4 - retryCnt}")
                set_gprs_prot = cases.set_gprs_protocol_val(2)
                logging.info(f"GPRS protocol set result for port: {com_port}: {set_gprs_prot}")
                test_result['FTT_Set_GPRS_Protocol'] = 'pass' if set_gprs_prot.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while setting GPRS protocol for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        # Get GPRS Protocols Value
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Getting GPRS protocol for port: {com_port}, Attempt: {4 - retryCnt}")
                get_gprs_prot = cases.get_gprs_protocol_val()
                logging.info(f"GPRS protocol retrieval result for port: {com_port}: {get_gprs_prot}")
                meter_info['FTT_Get_GPRS_Protocol'] = str(get_gprs_prot.get('Protocol', 'None'))
                test_result['FTT_Get_GPRS_Protocol'] = 'pass' if get_gprs_prot.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while getting GPRS protocol for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1
                if retryCnt == 0:
                    meter_info['FTT_Get_GPRS_Protocol'] = "None"

        # Get Apparent Led Status
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Getting apparent LED status for port: {com_port}, Attempt: {4 - retryCnt}")
                get_app_led = cases.get_apparent_led_status()
                logging.info(f"Apparent LED status retrieval result for port: {com_port}: {get_app_led}")
                meter_info['FTT_Get_Apparent_Led_Status_Value'] = str(get_app_led.get('Apparent_LED_Status', 'None'))
                test_result['FTT_Get_Apparent_Led_Status'] = 'pass' if get_app_led.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred while getting apparent LED status for port: {com_port}, Error: {e}")
                retryCnt = retryCnt - 1
                if retryCnt == 0:
                    meter_info['FTT_Get_Apparent_Led_Status_Value'] = "None"

        if is_wc:
            # Set Meter Type Value (10-60 / 10-100)
            retryCnt = 3
            while retryCnt:
                try:
                    if '10-60' in serial_cfg.get('CURRENT_RATING', '10-100'):
                        set_ratting = 1
                    elif '10-100' in serial_cfg.get('CURRENT_RATING', '10-60'):
                        set_ratting = 2
                    else:
                        set_ratting = 0
                    set_meter_type = cases.set_meter_type(int(set_ratting))
                    test_result['Set_Meter_Type_in_Amp'] = 'pass' if set_meter_type.get('Result') == 'Pass' else 'fail'
                    retryCnt = 0
                except Exception as e:
                    print(f"Error in set meter type(eg: 10-60/10-100): {str(e)}, for com: {com_port}")
                    logging.error(f"Error in set meter type(eg: 10-60/10-100): {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

        # Factory reset
        retryCnt = 3
        while retryCnt:
            try:
                logging.info(f"Performing factory reset for port: {com_port}, Attempt: {4 - retryCnt}")
                FactoryReset = cases.Factory_reset_val()
                print(FactoryReset)
                logging.info(f"Factory reset result for port: {com_port}: {FactoryReset}")
                test_result['FTT_factory_reset'] = 'pass' if FactoryReset.get('Result').lower() == 'pass' else 'fail'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error occurred during factory reset for port: {com_port}, Attempt: {4 - retryCnt}, Error: {e}")
                retryCnt = retryCnt - 1

        reset_wait = serial_cfg.get("Fact_Reset_sleepTime", 5)
        logging.info(f"waiting for {reset_wait} sec for meter restart after factory reset")
        print(f"waiting for {reset_wait} sec for meter restart after factory reset")
        time.sleep(reset_wait)  # avoid conflict between factory reset and the set push interval command

        if is_wc:
            # Get Meter Type Value
            retryCnt = 3
            while retryCnt:
                try:
                    get_meter_type = cases.get_meter_type()
                    if current_rating.lower() in get_meter_type.lower():
                        meter_info['Meter_Type_Amp'] = get_meter_type
                        test_result['Get_Meter_Type_in_Amp'] = 'pass'
                    else:
                        meter_info['Meter_Type_Amp'] = ''
                        test_result['Get_Meter_Type_in_Amp'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in get meter type: {str(e)}")
                    print(f"Error in get meter type: {str(e)}")
                    retryCnt = retryCnt - 1

        if is_4g:
            # 4G pushes use their own Communication object, so free the port first
            ser.close()
            com = Communication(com_port)

            # Set Push Interval
            meter_info['FTT_Push_Interval'] = str(interval)
            ok = set_push_interval(com_port, com, interval)
            print("Set Push Interval is successful" if ok else "Set Push Interval is Failed")
            test_result['FTT_Set_Push_Interval'] = 'pass' if ok else 'fail'

            # Get Push Interval
            ok = get_push_interval(com_port, com)
            print("Get Push Interval is successful" if ok else "Get Push Interval is Failed")
            test_result['FTT_Get_Push_Interval'] = 'pass' if ok else 'fail'

            # Set Periodic Push IPv6 Address
            meter_info['FTT_Periodic_Push_IPv6_Address'] = str(ipv6_address)
            ok = set_periodic_push_ipv6_address(com_port, com, ipv6_address)
            print("Set Periodic Push IPv6 Address is successful" if ok else "Set Periodic Push IPv6 Address is Failed")
            test_result['FTT_Set_Periodic_Push_IPv6_Address'] = 'pass' if ok else 'fail'

            # Get Periodic Push IPv6 Address
            ok = get_periodic_push_ipv6_address(com_port, com, ipv6_address)
            print("Get Periodic Push IPv6 Address is successful" if ok else "Get Periodic Push IPv6 Address is Failed")
            test_result['FTT_Get_Periodic_Push_IPv6_Address'] = 'pass' if ok else 'fail'

            # Set Event Push IPv6 Address
            meter_info['FTT_Event_Push_IPv6_Address'] = str(ipv6_address)
            ok = set_event_push_ipv6_address(com_port, com, ipv6_address)
            print("Set Event Push IPv6 Address is successful" if ok else "Set Event Push IPv6 Address is Failed")
            test_result['FTT_Set_Event_Push_IPv6_Address'] = 'pass' if ok else 'fail'

            # Get Event Push IPv6 Address
            ok = get_event_push_ipv6_address(com_port, com, ipv6_address)
            print("Get Event Push IPv6 Address is successful" if ok else "Get Event Push IPv6 Address is Failed")
            test_result['FTT_Get_Event_Push_IPv6_Address'] = 'pass' if ok else 'fail'
            com.close()

        if is_img:
            # `ser` stays open on purpose: provisioning takes over this same
            # connection (com_ser) and the tunnel-mode close bytes go out on it.
            end_bytes = END_BYTES
            tunnel_ok = False
            retryCnt = 3
            while retryCnt > 0:
                logging.info(f"Set Tunnel Mode for com: {com_port}, attempt: {4 - retryCnt}")
                try:
                    debug_status = cases.set_tunnel_mode()
                    logging.info(f"Set Tunnel Mode for com: {com_port} = {debug_status}")
                    if debug_status.get("Result") == 'Fail':
                        raise RuntimeError("tunnel mode not set")
                    tunnel_ok = True
                    break
                except Exception as e:
                    logging.error(f"Error in set Tunnel Mode for com: {com_port}, error: {str(e)}")
                    retryCnt = retryCnt - 1
                    print("Tunnel Mode Fail")
                    time.sleep(0.5)
                    for _ in range(3):
                        ser.write(end_bytes)
                        time.sleep(0.1)
                    time.sleep(0.4)
            test_result['Set Debug Print Mode'] = 'pass' if tunnel_ok else 'fail'
            print('---------------',test_result,'--------------')

            if not tunnel_ok:
                logging.info(f"Skipping IMG Provisioning for com: {com_port} -- tunnel mode not set")
                test_result[PROVISIONING_COLUMN] = 'fail'
                provisioning_fail_reason = "Tunnel mode not set"
            elif 'fail' in test_result.values():
                logging.info(f"Skipping IMG Provisioning for com: {com_port} -- an earlier FTT step already failed")
                print(Fore.RED + "❌ Skipping IMG Provisioning -- earlier FTT step(s) failed")
                print(Style.RESET_ALL)
                test_result[PROVISIONING_COLUMN] = 'fail'
                provisioning_fail_reason = "Skipped -- an earlier FTT step already failed"
            else:
                img_id_str = str(meter_info['FTT_NIC_PCB_No'][-8:])
                img_id = str(int(img_id_str))
                gateway_id = serial_cfg.get('GATEWAY_TEXT_PREFIX', 'IMG') + img_id_str
                # img_id / gateway_id are data, not pass/fail -> meter_info
                meter_info['IMG ID'] = img_id
                meter_info['Gateway ID'] = gateway_id
                nic_parameters_data, prov_sucess, reason = img_provisioning(serial_cfg, img_id, gateway_id, com_port, ser)
                if prov_sucess:
                    # status_dict = pass/fail verification columns -> test_result
                    # nic_parameters_data = raw values read back from the gateway -> meter_info
                    status_dict, result_status, reason, nic_parameters_data = check_provisioning_status(nic_parameters_data, serial_cfg)
                    test_result.update(status_dict)
                    meter_info.update(nic_parameters_data)
                    overall_result = "pass" if result_status == "pass" else "fail"
                else:
                    overall_result = "fail"
                if overall_result == "fail":
                    print(Fore.RED + "❌ IMG Provisioning Failed!")
                    print(Style.RESET_ALL)
                # The provisioning outcome goes into test_result so it feeds the
                # overall result and the fail message list like every other step.
                # The reason text stays OUT of test_result (it would become an
                # unwanted Excel column) and travels in the log entry instead.
                test_result[PROVISIONING_COLUMN] = overall_result
                provisioning_fail_reason = reason if overall_result == 'fail' else ''

            # Close Tunnel Mode
            print("🔄 Sending end bytes...")
            retryCnt = 3
            while retryCnt > 0:
                try:
                    logging.info(f"Closing Tunnel mode for com: {com_port}, attempt: {4 - retryCnt}")
                    print("Sending Command to Close Tunnel Mode")
                    ser.write(end_bytes)
                    time.sleep(0.5)
                    retryCnt -= 1
                except Exception as e:
                    retryCnt = 0
                    print("Not Able to Close Tunnel Mode")
                    logging.info(f"Error in Closing Tunnel mode for com: {com_port}, error: {str(e)}")
                    result_queue.append([f"COM: {com_port} Not Able to Close Tunnel Mode"])
            print("✅ End bytes sent.")
            ser.close()

            stage["prov"] = test_result[PROVISIONING_COLUMN].lower()
            stage["prov_reason"] = provisioning_fail_reason

            com = Communication(com_port)
            set_push_control_status = set_push_control(com_port, com)
            if set_push_control_status:
                test_result['Set_Push_Control'] = "pass"
            else:
                test_result['Set_Push_Control'] = "fail"


            # Start Get Push Control Mode
            get_push_control_status = get_push_control(com_port, com)
            if get_push_control_status:
                test_result['Get_Push_Control'] = "pass"
                meter_info['Push_Control_Mode'] = '1'
            else:
                test_result['Get_Push_Control'] = "fail"
                meter_info['Push_Control_Mode'] = ''


        try:
            ser.close()
        except Exception:
            pass

        print(test_result)
        meter_info[OVERALL_COLUMN] = 'fail' if 'fail' in test_result.values() else 'pass'

        result_log.update(build_log_entry(mac, meter_info, test_result, bookName, fileName, provisioning_fail_reason))
        time.sleep(0.1)

        fail_messages = [
            FAIL_MESSAGES.get(col, f"Fail in {col}")
            for col, value in test_result.items() if value == 'fail'
        ]
        if fail_messages:
            result_queue.append(fail_messages)

        EndTime = datetime.datetime.now()
        print("\nStartTime:", starttime)
        print("EndTime:", EndTime)
        print("Diff : ", EndTime - starttime)

    except Exception as e:
        print("Error:", e)
        logging.error(f"Error in main_function for port: {com_port}, Error: {e}")
        result_queue.append(["com port is unreachable"])
        try:
            if ser is not None:
                ser.close()
        except Exception:
            pass
        return

def scan_serial_number(position, project, meter_type):
    """Scan and validate serial number based on project config."""
    project = project.lower()
    
    if project in ("gomati", "saryu"):
        pattern = r'^PO\d{8}$'
        example = "PO12345678"
        extract = lambda s: s[-8:]
    elif project == "mn":
        if 'wc' in meter_type.lower():
            pattern = r'^MN3P\d{6}$'
            example = "MN3P232345"
            extract = lambda s: s[-6:]
        else:
            pattern = r'^MNCT\d{6}$'
            example = "MNCT232345"
            extract = lambda s: s[-6:]
    elif project == "wb":
        pattern = r'^PPD\d{7}$'
        example = "PPD1234567"
        extract = lambda s: s[-7:]
    elif project == "tn":
        pattern = r'^PO\d{8}$'
        example = "PO12345678"
        extract = lambda s: s[-8:]
    elif project == "others":
        pattern = None
        example = "LR12345678"
        extract = lambda s: s[-8:]
    else:
        raise ValueError(
            "Invalid Project name in config file. Valid options: gomati, saryu, manipur, wb, others"
        )

    while True:
        try:
            serial_num = input(f"Enter Meter Serial Num for position {position} Meter (ex-{example}): ")
            if pattern:
                match = re.match(pattern, serial_num)
                if match:
                    return extract(serial_num)
                else:
                    raise ValueError(f"Invalid format. Enter in this format (ex-{example})")
            else:
                if len(serial_num) == 10:
                    return extract(serial_num)
                else:
                    raise ValueError(f"Invalid format. Enter in this format (ex-{example})")
        except ValueError as e:
            print(e)

def run(com_port_list, stage_results, serial_cfg, cpu_serial_num):
    print(stage_results)
    print(Fore.YELLOW + "<<<<<<<<<<<<<<<<<<<<<<<<<<<<...............3PLTCT/ 3PWC FTT.....................>>>>>>>>>>>>>>>>>>")
    print(Style.RESET_ALL)

    abort_flag=threading.Event()
    meter_project = serial_cfg.get('PROJECT', 'gomati').lower()
    meter_type = serial_cfg.get('METER_TYPE', '3PWC').lower()
    toolName=serial_cfg.get('TOOL_TYPE', 'IMG_FTT').lower()
    ipv6 = ""
    interval = 60
    if 'wc' in meter_type:
        meter_type = "3PWC"
    elif 'ltct' in meter_type:
        meter_type = "3PLTCT"
    else:
        meter_type = "3PWC"
        
    bookName = meter_type.upper() + "_" + toolName.upper() + "_" + "{}".format(str(serial_cfg.get('FTT_TEST_STATION', '1'))) + "_LOG.xlsx"

    fileName = toolName.upper() + "_DATA_LOG"

    close_excel_file(bookName)
    addDefaultFttLog(bookName,fileName, toolName.lower(), meter_type, serial_cfg.get("CALIB_TYPE", 'single_point').lower())
    list_port = com_port_list
    print (list_port)
    port_configs = []

    for i, com_port in enumerate(list_port):
        print(f"\nEnter Meter Configuration for {com_port}: ")

        meter_serial_num = enterSrNum_ftt(serial_cfg)

        while True:
            meter_pcb_serial_no = input("Enter Meter PCB serial No (Ex.P24101301000000100210000001...... etc): ")
            if str(meter_pcb_serial_no[9:16]) == str(serial_cfg.get('Main_PCB_SFG_Prefix', '0000000')):
                break
            else:
                print("Invalid Format of Meter PCB Serial Num, Enter in this Format (Ex. P24101301000000100210000001...... etc)")

        while True:
            nic_pcb_serial_no = input("Enter NIC PCB serial No (Ex- P24101301000000400310000001.......... etc): ")
            if (
                str(nic_pcb_serial_no[0:4]).lower() == 'r144' or
                str(nic_pcb_serial_no[9:16]) == str(serial_cfg.get('NIC_PCB_SFG_PREFIX', '0000000'))
            ):
                break
            else:
                print("Invalid Format of NIC PCB Serial Num, Enter in this Format (Ex.R144XXXX...... or P24101301000000400310000001 etc)")

        port_configs.append({
            'com_port': com_port,
            'meter_serial_num': meter_serial_num,
            'meter_pcb_serial_no': meter_pcb_serial_no,
            'nic_pcb_serial_no': nic_pcb_serial_no,
            'results': [],   # fail / pass messages for the popup
            'log': {}        # filled by main_function via build_log_entry()
        })
    
    logging.info(f"input_data: {port_configs}")

    start_time = datetime.datetime.now()
    enter_flag1 = True
    input("Press Enter to start the FTT........")


    threads_list = []
    for config in port_configs:
        thread = StoppableThread(
            target=main_function,
            args=(
                serial_cfg,
                config['com_port'],
                stage_results,
                config['meter_serial_num'],
                config['meter_pcb_serial_no'],
                config['nic_pcb_serial_no'],
                config['results'],
                abort_flag,
                config['log']
            )
        )
        threads_list.append(thread)

    # Start all threads
    for thread in threads_list:
        thread.start()

    # Wait for all threads to finish
    for thread in threads_list:
        thread.join()


    print("\n\nAgain Scan Meter Serial No to complete the process...........")
    sr_num_received = {}
    
    # Scan serial numbers for each port that has results
    for i, config in enumerate(port_configs):
        if config['log']:
            sr_num_received[config['com_port']] = scan_serial_number(
                i + 1, serial_cfg.get('PROJECT', 'gomati').lower(), meter_type
            )

    # Validate serial numbers against the logged meter serial number
    for config in port_configs:
        log = config['log']
        if not log:
            continue

        sr_num = sr_num_received.get(config['com_port'], '')
        target_value = log['meter_info'][SERIAL_COLUMN]
        print(target_value)
        if str(sr_num) == str(target_value):
            log['test_result'][MISMATCH_COLUMN] = 'pass'
        else:
            log['test_result'][MISMATCH_COLUMN] = 'fail'
            log['meter_info'][OVERALL_COLUMN] = 'fail'
            config['results'].append([FAIL_MESSAGES[MISMATCH_COLUMN]])

    # Determine colors and messages per port
    for config in port_configs:
        com_port = config['com_port']
        log = config['log']
        results = config['results']

        if log and str(log['meter_info'][OVERALL_COLUMN]).lower() == 'pass':
            results.append([f"COM Port {com_port}: Pass"])
            config['color'] = 'green'
        else:
            config['color'] = 'red'

        if results:
            flat = [item for sublist in results for item in sublist]
            config['msg_text'] = ", ".join(set(flat))
        else:
            config['msg_text'] = ''

    # Write to Excel logs
    for config in port_configs:
        if config['log']:
            try:
                close_excel_file(bookName)
                add_log_xlsc(config['log'], False)
            except Exception as e:
                print(f"unknown error in add logs in Excel: {e}")
                logging.error(f"Error adding log to Excel for {config['com_port']}: {e}")

    if serial_cfg.get("IS_DATA_CONN", 1) == 1:
        df_frame = pd.read_excel(bookName)
        print(df_frame)
        try:
            status = False
            error = ""
            if 'ltct' in meter_type.lower():
                status, error = db_connect.upload_dataframe(df_frame, 'ltct')
            else:
                status, error = db_connect.upload_dataframe(df_frame, 'wc')
            if not status:
                logging.error(f"DB upload failed . Saved locally for retry. Error: {error}")
                logging.info(f"status: {status}, error: {error}")
                print(f"DB upload failed . Saved locally for retry. Error: {error}")
            else:
                # Upload to S3 if any results exist
                any_results = any(bool(config['log']) for config in port_configs)

                if any_results:

                    import boto3
                    from botocore.exceptions import NoCredentialsError


                    def upload_to_aws(local_folder, bucket, s3_file, sub_folder, file_time, folder_name1, cpu_serial_num):
                        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
                        try:
                            key = f"{cpu_serial_num}_{file_time}_{s3_file}"
                            print(key)
                            s3.upload_file(s3_file, bucket, f"{folder_name}/{folder_name1}/{sub_folder}/{local_folder}/{key}")
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
                    txt = list(filter(lambda x: x[-5:] == '.xlsx', al))
                    print(txt)
                    if len(txt) == 0:
                        print("file doesn't exist")
                        return

                    for j in range(len(txt)):
                        time = datetime.datetime.now()
                        date_only = datetime.datetime.strftime(time, '%Y-%m-%d')
                        time_only = datetime.datetime.strftime(time, '%H_%M_%S')

                        xyx = str(txt[j])
                        sub_folder = "UNKNOWN"
                        if "pct2" in xyx:
                            sub_folder = "PCT2"
                        elif "ftt" in xyx.lower():
                            sub_folder = "4G_FTT"
                        elif "mct" in xyx:
                            sub_folder = "MCT"
                        elif "rtt" in xyx:
                            sub_folder = "RTT"
                        elif "pct" in xyx:
                            sub_folder = "PCT"
                        else:
                            print("improper file name given for tool type")
                            continue

                        folder_name1 = "UNKNOWN"
                        if "SM_1P" in xyx:
                            folder_name1 = "ISM_1P"
                        elif "SM_3P" in xyx:
                            folder_name1 = "ISM_3P"
                        elif "AP_3P" in xyx:
                            folder_name1 = "CAP_3P"
                        elif "CU_" in xyx:
                            folder_name1 = "DCU_"
                        elif "rud_" in xyx.lower():
                            folder_name1 = "Garud"
                        elif "3pwc" in xyx.lower():
                            folder_name1 = "3PWC"
                        elif "3pltct" in xyx.lower():
                            folder_name1 = "3PLTCT"
                        else:
                            print("improper file name given for Meter type")
                            continue

                        if serial_cfg.get("IS_OFFLINE", 0) == 1:
                            upload_to_aws(str(date_only), bucket_name, txt[j], sub_folder, time_only, folder_name1, cpu_serial_num)
                else:
                    print("Skipping to Upload the log file to server")

        except Exception as e:
            print(f"Error writing DB log: {e}")
            logging.error(f"Error writing DB log: {e}")
    
    else:
        # Upload to S3 if any results exist
        any_results = any(bool(config['log']) for config in port_configs)

        if any_results:

            import boto3
            from botocore.exceptions import NoCredentialsError


            def upload_to_aws(local_folder, bucket, s3_file, sub_folder, file_time, folder_name1, cpu_serial_num):
                s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
                try:
                    key = f"{cpu_serial_num}_{file_time}_{s3_file}"
                    print(key)
                    s3.upload_file(s3_file, bucket, f"{folder_name}/{folder_name1}/{sub_folder}/{local_folder}/{key}")
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
            txt = list(filter(lambda x: x[-5:] == '.xlsx', al))
            print(txt)
            if len(txt) == 0:
                print("file doesn't exist")
                return

            for j in range(len(txt)):
                time = datetime.datetime.now()
                date_only = datetime.datetime.strftime(time, '%Y-%m-%d')
                time_only = datetime.datetime.strftime(time, '%H_%M_%S')

                xyx = str(txt[j])
                sub_folder = "UNKNOWN"
                if "pct2" in xyx.lower():
                    sub_folder = "PCT2"
                elif "ftt" in xyx.lower():
                    sub_folder = "4G_FTT"
                elif "mct" in xyx.lower():
                    sub_folder = "MCT"
                elif "rtt" in xyx.lower():
                    sub_folder = "RTT"
                elif "pct" in xyx.lower():
                    sub_folder = "PCT"
                else:
                    print("improper file name given for tool type")
                    continue

                folder_name1 = "UNKNOWN"
                if "sm_1p" in xyx.lower():
                    folder_name1 = "ISM_1P"
                elif "sm_3p" in xyx.lower():
                    folder_name1 = "ISM_3P"
                elif "ap_3p" in xyx.lower():
                    folder_name1 = "CAP_3P"
                elif "cu_" in xyx.lower():
                    folder_name1 = "DCU_"
                elif "rud_" in xyx.lower():
                    folder_name1 = "Garud"
                elif "3pwc" in xyx.lower():
                    folder_name1 = "3PWC"
                elif "3pltct" in xyx.lower():
                    folder_name1 = "3PLTCT"
                else:
                    print("improper file name given for Meter type")
                    continue

                if serial_cfg.get("IS_OFFLINE", 0) == 1:
                    upload_to_aws(str(date_only), bucket_name, txt[j], sub_folder, time_only, folder_name1, cpu_serial_num)
        else:
            print("Skipping to Upload the log file to server")

    
    # Build ftt_result for all ports
    ftt_result = {}

    for config in port_configs:
        com_port = config['com_port'].lower()
        log = config['log']
        stage = stage_results.get(com_port, {})

        if log:
            ftt_cols = [c for c in log['test_result'] if c in FAIL_MESSAGES and c != PROVISIONING_COLUMN]
            ftt_ok = all(log['test_result'][c] != 'fail' for c in ftt_cols)
            ftt_result[com_port] = {
                'result': 'pass' if ftt_ok else 'fail',
                'msg': config.get('msg_text', '')
            }
        else:
            ftt_result[com_port] = {
                'result': 'fail',
                'msg': stage.get("mct_reason") or 'No Result Found for this COM Port'
            }

        # Stage status recorded by main_function (COM port / MCT / provisioning)
        ftt_result[com_port]['mct'] = stage.get('mct', 'fail')
        ftt_result[com_port]['mct_reason'] = stage.get('mct_reason', '')
        ftt_result[com_port]['prov'] = stage.get('prov', 'fail')
        ftt_result[com_port]['prov_reason'] = stage.get('prov_reason', '')

    return ftt_result
