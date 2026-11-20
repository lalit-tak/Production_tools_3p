import os
import logging
import datetime
import time
import threading
import struct
from threading import Thread
import sys
import serial
import easygui
import openpyxl
import pandas as pd
from scripts.rtt import db_connect
from gp_node.network.network_api import NetworkAPI
from scripts.Test_cases_verificationClass import TestCase
import paho.mqtt.client as paho
from colorama import Fore, Style, init
import boto3
from botocore.exceptions import NoCredentialsError

init(autoreset=True)

BUCKET_NAME = "PUT_YOUR_BUCKET_NAME_HERE"
FOLDER_NAME = "PUT_YOUR_FOLDER_NAME_HERE"
ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"

# ----------------------------------------------------------------------
# Workaround for a known upstream easygui/Tkinter bug (see
# https://github.com/robertlugg/easygui/issues/170): pressing a
# navigation key inside an easygui dialog can fire tabRight()/tabLeft()
# AFTER boxRoot has already been torn down, raising AttributeError.
# Tkinter swallows exceptions raised inside its own callbacks, so this
# is cosmetic log noise rather than a functional bug - applied here too
# for consistency with calibration_multiport.py, since this file also
# shows easygui dialogs.
try:
    import easygui.boxes.base_boxes as _easygui_base_boxes

    def _safe_tab_right(event):
        if _easygui_base_boxes.boxRoot is not None:
            _easygui_base_boxes.boxRoot.event_generate("<Tab>")

    def _safe_tab_left(event):
        if _easygui_base_boxes.boxRoot is not None:
            _easygui_base_boxes.boxRoot.event_generate("<Shift-Tab>")

    _easygui_base_boxes.tabRight = _safe_tab_right
    _easygui_base_boxes.tabLeft = _safe_tab_left
except Exception:
    logging.warning("Could not apply easygui tabRight/tabLeft patch - a harmless upstream Tkinter warning may still appear.")


# ============================================================================
# DICTIONARY-BASED RESULT STORAGE
# ----------------------------------------------------------------------------
# Same pattern as mct_multiport.py / calibration_multiport.py:
#   meter_info : {'Meter_Address': ..., 'PCB_Serial_Num': ..., ...}
#   test_result: {'Get_Meter_Address': 'pass', 'Set_GPRS_Host': 'fail', ...}
#   rtt_results: {com_port: {'mac', 'meter_info', 'result', 'bookName',
#                             'fileName', 'com_port'}}
#
# The original script's final pass/fail decision was the most fragile
# part: after listening for RF broadcasts over MQTT, it matched each
# result entry against the received-address list using
# `meter_info = result[1]; meter_address = meter_info[3]` - a hardcoded
# positional index that happens to be correct for the RF field layout
# but silently wrong for 4G (which has extra fields inserted earlier in
# the list, shifting every index after them). This version looks up
# `entry['meter_info']['Meter_Address']` by name instead, so the RF vs
# 4G field-count difference can never point the match at the wrong
# value again.
#
# run_rtt_test() returns {com_port: 'pass'/'fail'} - the shape
# MainWindow._on_test_finished already expects for "rtt_test".
# ============================================================================



if getattr(sys, "frozen", False):
    # Running inside a PyInstaller --onefile .exe. This module gets
    # bundled INTO the exe, but "the exe's own folder" - where Logs/
    # actually needs to live so it persists and is findable - is
    # sys.executable's folder, NOT whatever the OS happens to set as the
    # current working directory when the exe is launched (double-clicking
    # an exe can set cwd to almost anywhere, e.g. System32, the user's
    # Desktop, wherever). A bare relative "Logs" path resolves against
    # that unpredictable cwd, not against the exe - which is exactly what
    # caused "the system cannot find the path specified" during the S3
    # upload step: the folder either never got created where expected,
    # or got created somewhere the later upload step couldn't find it
    # again. Same fix as main.py's BASE_DIR.
    _BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # Normal `python calibration_multiport.py` / imported-as-a-module
    # execution - unchanged, anchored to this file's own location.
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))


LOGS_FOLDER = os.path.join(_BASE_DIR, "Logs")
RTT_FOLDER = os.path.join(LOGS_FOLDER, "RTT")


# LOGS_FOLDER = "Logs"
# RTT_FOLDER = os.path.join(LOGS_FOLDER, "RTT")


def ensure_logs_folder():
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    os.makedirs(RTT_FOLDER, exist_ok=True)


def get_log_book_path(meter_type, tool_name):
    ensure_logs_folder()
    return os.path.join(RTT_FOLDER, f"{meter_type.title()}_{tool_name.upper()}_RTT_LOG.xlsx")


def get_rtt_field_templates(tool_name):
    """Named fields the RTT worker populates. The field list differs for
    4G (extra GPRS setup + reset steps) vs RF - returned dynamically
    based on tool_name so the header row and the worker always agree,
    instead of two independently hand-maintained lists (the original's
    MeterInfo/RTT_Fail_list) that only matched each other by coincidence
    of append order."""
    is_4g = '4g' in tool_name.lower()

    meter_info_keys = ['Date_time', 'Meter_Serial_Num', 'PCB_Serial_Num', 'Meter_Address']
    result_keys = ['Get_Meter_Serial_Num', 'Get_PCB_Serial_Num', 'Calibration_Check','Get_Meter_Address']
    fail_messages = {
        'Get_Meter_Serial_Num': 'Fail in Get Meter Serial Num',
        'Calibration_Check': 'Fail in Calibration Check - meter has not passed Calibration',
        'Get_PCB_Serial_Num': 'Fail in Get PCB Serial Num',
        'Get_Meter_Address': 'Fail in Get meter address',
    }

    if is_4g:
        meter_info_keys += ['GPRS_Host', 'GPRS_Port', 'GPRS_User_Name', 'GPRS_Pass']
        result_keys += ['Set_GPRS_Host', 'Set_GPRS_Cred', 'Get_GPRS_Cred', 'Get_GPRS_Host','Reset']
        fail_messages.update({
            'Set_GPRS_Host': 'Fail in Set GPRS Host',
            'Set_GPRS_Cred': 'Fail in Set GPRS Cred',
            'Get_GPRS_Cred': 'Fail in Get GPRS Cred',
            'Get_GPRS_Host': 'Fail in Get GPRS Host',
            'Reset': 'Fail in Reset',
        })

    meter_info_keys += ['Port_Name']
    return meter_info_keys, result_keys, fail_messages


def build_log_entry(mac, meter_info, test_result, bookName, fileName, com_port=None):
    """Identical shape to mct_multiport.py's / calibration_multiport.py's
    build_log_entry() - one self-describing dict instead of the
    positional 5-item list result_log_dump() used to build."""
    return {
        'mac': mac,
        'meter_info': meter_info,
        'result': test_result,
        'bookName': bookName,
        'fileName': fileName,
        'com_port': com_port,
    }


def build_fail_messages(com_port, test_result, fail_message_lookup):
    messages = []
    # A meter whose PCB serial was read (the caller already filters out
    # unreachable meters) but has no passing Calibration record is not
    # tested any further, so its popup reports only that - regardless of
    # the PCB-prefix check, which would otherwise hide this shortcut and
    # list every skipped step as a failure (the excel log is unchanged).
    if test_result.get('Calibration_Check') == 'fail':
        return ["Meter Failed in Calibration: {}".format(com_port)]
    for step_key, value in test_result.items():
        if value == 'fail':
            text = fail_message_lookup.get(step_key, f"Fail in {step_key}")
            messages.append("COM Port: {}, {}".format(com_port, text))
    return messages


def verify_log_xlsc(bookName, fileName):
    loc = bookName
    try:
        wb = openpyxl.load_workbook(loc)
        sheet = wb.active
        _ = sheet.cell(row=1, column=1).value
    except Exception:
        logging.info("LOG XL file not found, creating one for you")
        wb = openpyxl.Workbook()
        wb.create_sheet(index=0, title=fileName)
        sheet = wb.active
        del wb['Sheet']
        wb.save(loc)
        return False
    else:
        return True


def get_header_column_map(sheet):
    """Read the header row into {header_name: column_index}. Identical to
    mct_multiport.py's get_header_column_map()."""
    header_map = {}
    for col_idx, cell in enumerate(sheet[1], start=1):
        if cell.value is not None:
            header_map[cell.value] = col_idx
    return header_map


def add_log_xlsc(log_entry):
    """Append one row from a dictionary-shaped log_entry, writing each
    value to the column matching its own key/header name - looked up by
    name, not by a running column counter. Identical pattern to
    mct_multiport.py's add_log_xlsc()."""
    bookName = log_entry['bookName']
    fileName = log_entry['fileName']

    loc = bookName
    wb = openpyxl.load_workbook(loc)
    sheet1 = wb[fileName]

    numRows = sheet1.max_row + 1
    header_map = get_header_column_map(sheet1)

    def write(header_name, value):
        col_idx = header_map.get(header_name)
        if col_idx is None:
            col_idx = sheet1.max_column + 1
            sheet1.cell(row=1, column=col_idx).value = header_name
            header_map[header_name] = col_idx
        sheet1.cell(row=numRows, column=col_idx).value = value

    write('MAC_ADDR', log_entry['mac'])
    write('Index', numRows - 1)
    for key, value in log_entry['meter_info'].items():
        write(key, value)
    for key, value in log_entry['result'].items():
        write(key, value)

    wb.save(loc)


# def get_system_mac_address(toolName):
#     mac = "None"
#     try:
#         import sys
#         if sys.platform == 'win32':
#             for line in os.popen("ipconfig /all"):
#                 if line.lstrip().startswith('Physical Address'):
#                     mac = line.split(':')[1].strip().replace('-', ':')
#                     break
#         else:
#             for line in os.popen("/sbin/ifconfig"):
#                 if line.find('Ether') > -1:
#                     mac = line.split()[4]
#                     break
#     except Exception:
#         logging.error("MAC address lookup failed")
#     return mac

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
        logging.error("Error in get mac address")
    logging.info(f"In RTT, MAC Address of system: {mac}")
    return mac


def addDefaultRTTLog(bookName, fileName, tool_name):
    """Create the log workbook (if missing) and write its header row from
    get_rtt_field_templates() - headers always match what the worker
    will populate, no separate hand-maintained header list to keep in
    sync. Identical pattern to mct_multiport.py's addDefaultMctLog()."""
    if verify_log_xlsc(bookName, fileName):
        return

    logging.info("xlsx file for log not found. creating one to store test report")

    meter_info_keys, result_keys, _ = get_rtt_field_templates(tool_name)
    meter_info_keys = meter_info_keys + ['Overall_Result']

    wb = openpyxl.load_workbook(bookName)
    sheet = wb[fileName]

    headers = ['MAC_ADDR', 'Index'] + meter_info_keys + result_keys
    for col_idx, header in enumerate(headers, start=1):
        sheet.cell(row=1, column=col_idx).value = header

    wb.save(bookName)


class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def get_mqtt_broker_config(data_dict):
    """Extract broker host/port/username/password based on PROJECT.
    Pulled out into its own function because the original script had
    this exact if/elif chain duplicated verbatim in two places (once in
    worker_function for 4G GPRS setup, once again in run()'s nested MQTT
    subscribe function) - one copy can't drift out of sync with the
    other now."""
    project = data_dict.get('PROJECT', 'gomati').lower()
    brokers = {
        'gomati': ("Gomati-Broker", "G0m@ti-Br0k3r!2024$", "broker.gomatimvvnl.in", 1883),
        'saryu': ("Saryu-Broker", "S@ryu-Br0k3r!#V&2420$", "broker.saryumvvnl.in", 1883),
        'manipur': ("sangaibroker", "V3aSLGXkUy4o1CIBs", "broker.sangaimspdcl.in", 1883),
        'wb': ("wbsedcl", "nU4Eq5rE2e", "broker.hooghlywbsedcl.in", 1883),
        'tn': ("TNPDCL-Broker", "oJBUnxKCqPjXoWgCz3Jwojce", "broker.private.tnpdcl.in", 1883),
        'tn_public': ("TNPDCL-Broker", "oJBUnxKCqPjXoWgCz3Jwojce", "broker.tnpdcl.in", 1883),
        'public': ("gpbroker", "grampower4321@", "broker.grampower.com", 1883),
    }
    user_name, password, host, port = brokers.get(project, ("", "", "", 1883))
    return user_name, password, host, port


def worker_function(data_dict, com_port, portID, abort_flag, result_log):
    """Per-port RTT worker. Populates named meter_info/test_result dicts
    instead of positional MeterInfo/result_list, then stores the
    combined entry in result_log[com_port] (a dict, matching
    mct_multiport.py's phase1_results) instead of appending a 5-item
    list to a shared list."""
    try:
        ser = serial.Serial(com_port, baudrate=9600, timeout=15)
        if not ser:
            return

        cases = TestCase(ser, portID, data_dict.get("RETRIES", 4), data_dict.get("NIC_PCB_LENGTH", 27))
        toolName = data_dict.get("TOOL_TYPE", "rf").lower()
        mac = get_system_mac_address(toolName).lower()
        meter_type = data_dict.get("METER_TYPE", "Garud_1PH").lower()
        bookName = get_log_book_path(meter_type, toolName)
        fileName = toolName.upper() + "_DATA_LOG"
        starttime = datetime.datetime.now()
        METER_ADDRESS = "255.255.255.255"

        user_name, password, host, port = get_mqtt_broker_config(data_dict)

        meter_info = {}
        test_result = {}
        meter_info['Date_time'] = datetime.datetime.now()
        addDefaultRTTLog(bookName, fileName, toolName.lower())
        _, _, fail_message_lookup = get_rtt_field_templates(toolName)

        # Check COM port open/closed
        retryCnt = 3
        while retryCnt:
            logging.debug(f"Check com port is open or not attempt{4 - retryCnt} for com:{com_port}")
            try:
                check_port = cases.check_port(com_port)
                if 'Fail' == check_port:
                    # Only THIS meter stops; other ports keep testing, so the
                    # shared abort_flag is deliberately not set here.
                    ser.close()
                    return
                retryCnt = 0
            except Exception as e:
                logging.info(f"Error in rtt to check com port status attempt{4 - retryCnt}, error: {str(e)}, for com: {com_port}")
                retryCnt -= 1

        if abort_flag.is_set():
            return

        # Verify Serial Number
        retryCnt = 3
        while retryCnt:
            logging.debug(f"Verify Serial number attempt{4 - retryCnt} for com:{com_port}")
            try:
                Meter_Serial_Num = cases.Verify_Serial_number(com_port)
                if Meter_Serial_Num.get('status') == 'fail':
                    meter_info['Meter_Serial_Num'] = str(Meter_Serial_Num.get('sr_number', 'None'))
                    test_result['Get_Meter_Serial_Num'] = 'fail'
                else:
                    meter_info['Meter_Serial_Num'] = str(Meter_Serial_Num.get('sr_number', 'None'))
                    test_result['Get_Meter_Serial_Num'] = 'pass'
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in rtt in worker func in verify serial number: {str(e)}, for com: {com_port}")
                retryCnt -= 1

        # Get PCB Serial Number
        retryCnt = 3
        while retryCnt:
            logging.debug(f"Get PCB serial number attempt{4 - retryCnt} for com:{com_port}")
            try:
                PCB_Serial_Num = cases.Get_pcb_serial_num(com_port)
                meter_info['PCB_Serial_Num'] = str(PCB_Serial_Num)
                if PCB_Serial_Num is None:
                    meter_info['PCB_Serial_Num'] = ""
                    test_result['Get_PCB_Serial_Num'] = 'fail'
                else:
                    meter_info['PCB_Serial_Num'] = str(PCB_Serial_Num)
                    if (('R161' in PCB_Serial_Num) or ('r161' in PCB_Serial_Num) or (str(PCB_Serial_Num[9:16]) == str(data_dict.get('MAIN_PCB_SFG_PREFIX', '0000001')))):
                        test_result['Get_PCB_Serial_Num'] = 'pass'
                    else:
                        test_result['Get_PCB_Serial_Num'] = 'fail'

                logging.debug(f"PCBA serial number: {PCB_Serial_Num}, for com: {com_port}")

                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in rtt in worker func in get pcb serial number: {str(e)}, for com: {com_port}")
                retryCnt -= 1


        calibration_result = db_connect.fetch_by_pcb_serial(PCB_Serial_Num)
        # calibration_result = True  # For testing purposes, set calibration_result to True
        test_result['Calibration_Check'] = 'pass' if calibration_result else 'fail'

        if not calibration_result:
            logging.info(
                f"Calibration failed for com: {com_port}, PCB: {PCB_Serial_Num}, "
                f"Calibration overall_result: {calibration_result!r} -- skipping RTT test for this meter"
            )

        if calibration_result:
            # Get Meter Address - this is the key later matched against the
            # set of addresses actually heard broadcasting over MQTT
            # (see run_rtt_test()'s finalize step) - by NAME now, not by
            # positional index into a list.
            retryCnt = 3
            while retryCnt:
                logging.debug(f"Get Meter address attempt{4 - retryCnt} for com:{com_port}")
                try:
                    Meter_address = cases.get_Meter_address(com_port)
                    logging.debug(f"Meter address: {Meter_address}, for com: {com_port}")
                    if 'Fail' in Meter_address:
                        meter_info['Meter_Address'] = str(Meter_address.get('mtr_address', 'None'))
                        test_result['Get_Meter_Address'] = 'fail'
                    else:
                        meter_info['Meter_Address'] = str(Meter_address.get('mtr_address', 'None'))
                        test_result['Get_Meter_Address'] = 'pass'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in rtt in worker func in get meter address: {str(e)}, for com: {com_port}")
                    retryCnt -= 1

            if '4g' in toolName.lower():
                meter_info['GPRS_Host'] = host
                meter_info['GPRS_Port'] = port
                meter_info['GPRS_User_Name'] = user_name
                meter_info['GPRS_Pass'] = password

                # Set GPRS Host
                retryCnt = 3
                while retryCnt:
                    logging.debug(f"Set GPRS Protocol Host for 4G, attempt{4 - retryCnt} for com:{com_port}")
                    try:
                        set_gprs_host = cases.set_gprs_host(host, port, com_port)
                        logging.debug(f"Set gprs host result: {set_gprs_host}, for com: {com_port}")
                        test_result['Set_GPRS_Host'] = 'fail' if 'fail' in set_gprs_host.get("status", 'fail') else 'pass'
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in rtt in worker func in Set Gprs Protocol Host: {str(e)}, for com: {com_port}")
                        retryCnt -= 1

                # Set GPRS Credentials
                retryCnt = 3
                while retryCnt:
                    logging.debug(f"Set GPRS Credentials for 4G, attempt{4 - retryCnt} for com:{com_port}")
                    try:
                        set_gprs_cred = cases.set_gprs_cred(user_name, password, com_port)
                        logging.debug(f"Set gprs credentials: {set_gprs_cred}, for com: {com_port}")
                        test_result['Set_GPRS_Cred'] = 'fail' if 'fail' in set_gprs_cred.get('status', 'fail') else 'pass'
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in rtt in Set GPRS Credentials: {str(e)}, for com: {com_port}")
                        retryCnt -= 1


                # Get GPRS Host
                retryCnt = 3
                while retryCnt:
                    logging.debug(f"Get GPRS Protocol Host for 4G, attempt{4 - retryCnt} for com:{com_port}")
                    try:
                        get_gprs_host = cases.verify_Meter_gprs_broker(host, port, com_port)

                        logging.debug(f"Get gprs host result: {get_gprs_host}, for com: {com_port}")
                        test_result['Get_GPRS_Host'] = 'fail' if 'fail' in get_gprs_host.get("status", 'fail') else 'pass'
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in rtt in worker func in Get Gprs Protocol Host: {str(e)}, for com: {com_port}")
                        retryCnt -= 1

                # Get GPRS Credentials
                retryCnt = 3
                while retryCnt:
                    logging.debug(f"Get GPRS Credentials for 4G, attempt{4 - retryCnt} for com:{com_port}")
                    try:
                        get_gprs_cred = cases.Verify_Meter_gprs_credentials(user_name, password, com_port)
                        logging.debug(f"Get gprs credentials: {get_gprs_cred}, for com: {com_port}")
                        test_result['Get_GPRS_Cred'] = 'fail' if 'fail' in get_gprs_cred.get('status', 'fail') else 'pass'
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in rtt in Get GPRS Credentials: {str(e)}, for com: {com_port}")
                        retryCnt -= 1

                # Meter Reset
                retryCnt = 3
                while retryCnt:
                    logging.debug(f"Meter Reset for 4G, attempt{4 - retryCnt} for com:{com_port}")
                    try:
                        meter_reset = cases.meter_reset(com_port, 10)
                        logging.debug(f"Meter reset status: {meter_reset}, for com: {com_port}")
                        test_result['Reset'] = 'fail' if 'fail' in meter_reset.get('status', 'fail') else 'pass'
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in rtt in Meter reset: {str(e)}, for com: {com_port}")
                        retryCnt -= 1

        meter_info['Port_Name'] = str(com_port)
        ser.close()

        # Overall_Result is computed later by run_rtt_test(), after the
        # MQTT broadcast-matching step decides each port's true RTT
        # outcome (a port can pass every serial-comms step above and
        # still fail RTT overall if its meter is never actually heard
        # broadcasting on RF).
        result_log[com_port] = build_log_entry(mac, meter_info, test_result, bookName, fileName, com_port)

        EndTime = datetime.datetime.now()
        logging.info(f"RTT worker StartTime: {starttime}, EndTime: {EndTime}, Diff: {EndTime - starttime}")

    except Exception as e:
        logging.error(f"Error in worker_function for COM {com_port}: {e}")
        return


def listen_for_rtt_broadcasts(data_dict, tool_name, meter_type, timeout_seconds):
    """Runs the MQTT subscribe loop for timeout_seconds and returns the
    SET (not list - O(1) membership checks instead of repeated linear
    `in` scans) of meter addresses actually heard broadcasting over RF.
    Same protocol/topic logic as the original script's nested run()
    function and on_message() handler, just returning its result instead
    of leaving it in a closure-captured list."""
    user_name, password, host, port = get_mqtt_broker_config(data_dict)
    address_received = set()

    def on_connect(client, mosq, obj, rc):
        logging.info(f"MQTT connect rc: {rc}")

    def on_message(mosq, obj, msg):
        data = bytearray(msg.payload)
        print ("data = ",[x for x in data])
        if ('rf' in tool_name.lower()):
            for index, value in enumerate(data):
                if value == 170 and index + 9 < len(data) and data[index + 9] == 19:
                    addr = f"{data[index+1]}.{data[index+2]}.{data[index+3]}.{data[index+4]}"
                    address_received.add(addr)
        else:
            if len(data) >= 5:
                addr = f"{data[1]}.{data[2]}.{data[3]}.{data[4]}"
                address_received.add(addr)

    def on_subscribe(mosq, obj, mid, granted_qos):
        logging.info(f"MQTT subscribed: {mid} {granted_qos}")

    start_time_loop = datetime.datetime.now()
    while True:
        try:
            exit_flag = False
            mqttc = paho.Client()
            mqttc.on_message = on_message
            mqttc.on_connect = on_connect
            mqttc.on_subscribe = on_subscribe

            if "4g" in tool_name.lower():
                mqttc.username_pw_set(user_name, password)
                mqttc.connect(host, port)
                if 'ltct' in meter_type.lower():
                    logging.info("Subscribing to LTCT/# topic for MQTT")
                    mqttc.subscribe([("LTCT/#",1)])
                else:
                    logging.info("Subscribing to WC/# topic for MQTT")
                    mqttc.subscribe([("WC/#",1)])
            else:
                logging.info("Subscribing to WC/# topic for MQTT")
                mqttc.username_pw_set('gpbroker', 'grampower4321@')
                mqttc.connect('broker.grampower.com', 1883)
                mqttc.subscribe([("WC/#", 1)])

            rc = 0
            while rc == 0:
                rc = mqttc.loop()
                elapsed_time = (datetime.datetime.now() - start_time_loop).total_seconds()
                if elapsed_time > timeout_seconds:
                    exit_flag = True
                    break
        except Exception as err:
            logging.error(f"MQTT loop error: {err}")
        if exit_flag:
            break
        time.sleep(0.1)

    return address_received


# Sentinel values for fields a worker never got to write - a missing
# result step reads as 'fail', never a silent 'pass'. Identical to
# mct_multiport.py's NOT_TESTED_* constants.
NOT_TESTED_METER_VALUE = None
NOT_TESTED_RESULT_VALUE = 'fail'


def fill_missing_fields(entry, meter_info_keys, result_keys):
    for key in meter_info_keys:
        entry['meter_info'].setdefault(key, NOT_TESTED_METER_VALUE)
    for key in result_keys:
        entry['result'].setdefault(key, NOT_TESTED_RESULT_VALUE)


def run_rtt_test(data_dict, active_port_list, upload_bench):
    """Entry point called by MainWindow (via FunctionThreadRunner, exactly
    the way run_mct_test()/run_calibration_test() are called) as:

        results = run_rtt_test(data_dict, ports, bench_number)

    Returns {com_port: 'pass'/'fail'} - the shape MainWindow's
    _on_test_finished already expects for "rtt_test".

    A port's final RTT result is decided by TWO things, exactly like the
    original: (1) every serial-comms step in worker_function succeeding,
    AND (2) that meter's address actually being heard broadcasting over
    MQTT within the timeout window. What changed is HOW step (2) is
    matched: the original used a hardcoded positional index
    (`meter_info[3]` for RF, but 4G's extra fields shift that index and
    the code never accounted for it) - this version looks up
    `entry['meter_info']['Meter_Address']` by name, so it can never
    silently check the wrong field.

    NOTE - deviations from the original interactive run(), matching the
    same reasoning as calibration_multiport.py's run_calibration_test():
      - Ports are passed in directly (active_port_list) instead of
        auto-scanned from serial.tools.list_ports.comports().
      - No interactive input()/argparse - not used here to begin with,
        but confirmed there's nothing blocking on stdin in this path.
    """
    logging.info("Starting RTT Testing Script")

    portID = 4
    list_port = list(active_port_list)
    toolName = data_dict.get("TOOL_TYPE", "4G").lower()
    meter_type = data_dict.get("METER_TYPE", "3PLTCT").lower()
    bookName = get_log_book_path(meter_type, toolName)
    fileName = toolName.upper() + "_DATA_LOG"
    addDefaultRTTLog(bookName, fileName, toolName.lower())

    abort_flag = threading.Event()
    rtt_results = {}  # com_port -> build_log_entry(...)

    logging.info(f"Starting RTT Testing on ports: {list_port}")

    threads = [
        StoppableThread(target=worker_function, args=(data_dict, port_name, portID, abort_flag, rtt_results))
        for port_name in list_port
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Guarantee every requested port has a complete entry before matching
    # against RF broadcasts or writing to Excel - same placeholder +
    # fill_missing_fields approach as the other two scripts, so a port
    # whose worker crashed before ever writing to rtt_results still gets
    # a definitive fail rather than silently vanishing.
    meter_info_keys, result_keys, fail_message_lookup = get_rtt_field_templates(toolName)
    for port_name in list_port:
        if port_name not in rtt_results:
            placeholder = build_log_entry(
                mac='NOT_TESTED', meter_info={}, test_result={},
                bookName=bookName, fileName=fileName, com_port=port_name,
            )
            rtt_results[port_name] = placeholder
        fill_missing_fields(rtt_results[port_name], meter_info_keys, result_keys)

    comms_fail_messages = []
    logging.info(f"RTT test result before broadcasting: {rtt_results}")
    for port_name, entry in rtt_results.items():
        _pcb = entry['meter_info'].get('PCB_Serial_Num')
        if _pcb in (None, '', 'None'):
            # PCB serial never fetched (port check failed / no reply)
            comms_fail_messages.append("Meter is unreachable: {}".format(port_name))
            continue
        comms_fail_messages.extend(build_fail_messages(port_name, entry['result'], fail_message_lookup))
    if comms_fail_messages:
        easygui.msgbox("\n".join(comms_fail_messages), "RTT Faulty Ports list")

    # Listen for RF broadcasts - a meter that fails every comms step
    # above obviously won't be heard either, but we still listen once
    # for everyone that DID complete comms setup.
    received_addresses = listen_for_rtt_broadcasts(
        data_dict, toolName, meter_type, data_dict.get("RTT_TIME", 600)
    )
    logging.info(f"Addresses heard broadcasting over RF: {received_addresses}")

    rtt_pass_fail_by_com = {}
    broadcast_fail_messages = []

    for port_name, entry in rtt_results.items():
        comms_ok = all(v == 'pass' for v in entry['result'].values()) if entry['result'] else False
        meter_address = entry['meter_info'].get('Meter_Address')

        if comms_ok and meter_address and meter_address in received_addresses:
            entry['meter_info']['Overall_Result'] = 'pass'
            rtt_pass_fail_by_com[port_name] = 'pass'
        else:
            entry['meter_info']['Overall_Result'] = 'fail'
            rtt_pass_fail_by_com[port_name] = 'fail'
            if comms_ok:
                # comms were fine, meter just wasn't heard broadcasting -
                # matches the original's distinct "Meter Failed in RTT"
                # message for this specific case
                broadcast_fail_messages.append(f"Meter Failed in RTT: {port_name}")

    for port_name, entry in rtt_results.items():
        try:
            add_log_xlsc(entry)
        except Exception:
            logging.info("unknown error in add logs in Excel")
            continue

    if data_dict.get("IS_DATA_CONN", 1) == 1:
        try:
            df_frame = pd.read_excel(bookName)
            status, error = db_connect.upload_dataframe_img(df_frame, meter_type.lower(), toolName.lower())
            if not status:
                logging.info(f"DB upload failed. Saved locally for retry. Error: {error}")
            else:
                if(len(rtt_results) != 0):
                    logging.info("Uploading RTT Test Results to Cloud Storage")

                    # for uploADING DATA OF MCT TO DIRECT CLOUD
                # ****************************************************************************************


                    def upload_to_aws(local_folder, bucket, s3_file,sub_folder, file_time,folder_name1, local_file_path=None):
                        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                        aws_secret_access_key=SECRET_KEY)
                        logging.info(f"Uploaded file: {str(upload_bench + "_" + file_time + "_" + s3_file)}")
                        try:
                            if local_file_path is None:
                                local_file_path = s3_file
                            key = "/{0}/{1}/{2}/{3}".format(folder_name1,sub_folder,local_folder, str(upload_bench + "_" + file_time + "_" + s3_file))
                            s3.upload_file(local_file_path, bucket, FOLDER_NAME +  key)
                            logging.info("Upload Successful")
                            os.remove(local_file_path)
                            return True
                        except NoCredentialsError:
                            logging.error("Credentials not available")
                            return False
                        except Exception as e:
                            logging.error(str(e))
                            logging.error("The file was not found")
                            return False
                    

                    al = os.listdir(RTT_FOLDER)
                    txt = list(filter(lambda x: x[-5:] == '.xlsx',al))
                    logging.info(f"txt")
                    if len(txt) == 0:
                        logging.info("file doesn't exist")#/dev/gp-gateway"
                        return#args.baud_rate = 9600

                    for j in range(len(txt)):    
                        # today = date.today()
                        # print("Today date is: ", today)

                        file_time = datetime.datetime.now()
                        logging.info(f"time = {file_time}")
                        date_only = datetime.datetime.strftime(file_time, '%Y-%m-%d')
                        time_only = datetime.datetime.strftime(file_time, '%H_%M_%S')
                        logging.info(f"time is: {time_only}")
                        logging.info(f"date is: {date_only}")



                        sub_folder = "UNKNOWN"
                        xyx =  str(txt[j])
                        # print "args.new_name",xyx
                        # print xyx.find("RTT")
                        if("pct" in xyx.lower()):
                            sub_folder = "PCT"
                        elif("mct" in xyx.lower()):
                            sub_folder = "MCT"
                        elif("4g" in xyx.lower()):
                            sub_folder = "RTT"
                        else:
                            logging.info("improper file name given for tool type")
                            continue
                        logging.info(f"sub_folder = {sub_folder}")

                        # print (xyx.find("AP"))
                        folder_name1 = "UNKNOWN"
                        if "SM_1P" in xyx:
                            folder_name1 = "ISM_1P"
                        elif "SM_3P" in xyx:
                            folder_name1 = "ISM_3P"
                        elif "AP_3P" in xyx:
                            folder_name1 = "CAP_3P"
                        elif "CU_" in xyx:
                            folder_name1 = "DCU_"  
                        elif("garud" in xyx.lower()):
                            folder_name1 = "Garud"   
                        elif("better" in xyx.lower()):
                            folder_name1 = "Better_Meter"
                        elif("wc" in xyx.lower()):
                            folder_name1 = "3PWC"
                        elif("ltct" in xyx.lower()):
                            folder_name1 = "3PLTCT"
                        else:
                            logging.info("improper file name given for Meter type")
                            continue
                        logging.info(f"folder_name1 = {folder_name1}")

                        logging.info("Uploading file: {} to bucket: {} in folder: {}/{}/{}".format(str(txt[j]), BUCKET_NAME, FOLDER_NAME, folder_name1, date_only))
                        local_path = os.path.join(RTT_FOLDER, txt[j])
                        uploaded = upload_to_aws(str(date_only), BUCKET_NAME, txt[j],sub_folder, time_only,folder_name1,local_file_path=local_path)
                        logging.info("RTT DATA SUCCESSFULLY UPLOADED TO CLOUD")


                    # ****************************************************************************************************************
                else:
                    logging.info("Skipping to Upload the log file to server")

        except Exception as e:
            logging.error(f"Error writing DB log: {e}")
    else:
        logging.info("Upload data to EMS db flag is disable")
        if(len(rtt_results) != 0):
            logging.info("Uploading RTT Test Results to Cloud Storage")

            # for uploADING DATA OF MCT TO DIRECT CLOUD
        # ****************************************************************************************
            


            def upload_to_aws(local_folder, bucket, s3_file,sub_folder, file_time,folder_name1, local_file_path = None):
                s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                aws_secret_access_key=SECRET_KEY)
                logging.info(f"Uploaded file: {str(upload_bench + "_" + file_time + "_" + s3_file)}")

                try:
                    if local_file_path is None:
                        local_file_path = s3_file
                    key = "/{0}/{1}/{2}/{3}".format(folder_name1,sub_folder,local_folder, str(upload_bench + "_" + file_time + "_" + s3_file))
                    s3.upload_file(local_file_path, bucket, FOLDER_NAME +  key)
                    logging.info("Upload Successful")
                    os.remove(local_file_path)
                    return True
                except NoCredentialsError:
                    logging.error("Credentials not available")
                    return False
                except Exception as e:
                    logging.error(str(e))
                    logging.error("The file was not found")
                    return False
            

            al = os.listdir(RTT_FOLDER)
            txt = list(filter(lambda x: x[-5:] == '.xlsx',al))
            logging.info(f"txt")
            if len(txt) == 0:
                logging.info("file doesn't exist")#/dev/gp-gateway"
                return#args.baud_rate = 9600

            for j in range(len(txt)):    
                # today = date.today()
                # print("Today date is: ", today)

                file_time = datetime.datetime.now()
                logging.info(f"time = {file_time}")
                date_only = datetime.datetime.strftime(file_time, '%Y-%m-%d')
                time_only = datetime.datetime.strftime(file_time, '%H_%M_%S')
                logging.info(f"time is: {time_only}")
                logging.info(f"date is: {date_only}")



                sub_folder = "UNKNOWN"
                xyx =  str(txt[j])
                # print "args.new_name",xyx
                # print xyx.find("RTT")
                if("pct" in xyx.lower()):
                    sub_folder = "PCT"
                elif("mct" in xyx.lower()):
                    sub_folder = "MCT"
                elif("4g" in xyx.lower()):
                    sub_folder = "RTT"    

                else:
                    logging.info("improper file name given for tool type")
                    continue
                logging.info(f"sub_folder = {sub_folder}")

                # print (xyx.find("AP"))
                folder_name1 = "UNKNOWN"
                if "SM_1P" in xyx:
                    folder_name1 = "ISM_1P"
                elif "SM_3P" in xyx:
                    folder_name1 = "ISM_3P"
                elif "AP_3P" in xyx:
                    folder_name1 = "CAP_3P"
                elif "CU_" in xyx:
                    folder_name1 = "DCU_"
                elif("garud" in xyx.lower()):
                    folder_name1 = "Garud"
                elif("better" in xyx.lower()):
                    folder_name1 = "Better_Meter"
                elif("wc" in xyx.lower()):
                    folder_name1 = "3PWC"
                elif("ltct" in xyx.lower()):
                    folder_name1 = "3PLTCT"  
                else:
                    logging.info("improper file name given for Meter type")
                    continue
                logging.info(f"folder_name1 = {folder_name1}")

                logging.info("Uploading file: {} to bucket: {} in folder: {}/{}/{}".format(str(txt[j]), BUCKET_NAME, FOLDER_NAME, folder_name1, date_only))
                local_path = os.path.join(RTT_FOLDER, txt[j])
                uploaded = upload_to_aws(str(date_only), BUCKET_NAME, txt[j],sub_folder, time_only,folder_name1,local_file_path=local_path)
                logging.info("RTT DATA SUCCESSFULLY UPLOADED TO CLOUD")

    all_fail_messages = comms_fail_messages + broadcast_fail_messages
    if all_fail_messages:
        easygui.msgbox("\n".join(all_fail_messages), "RTT Failure List")

    logging.info(f"RTT Testing Completed with results: {rtt_pass_fail_by_com}")
    # print(rtt_pass_fail_by_com,'-------------------')
    return rtt_pass_fail_by_com