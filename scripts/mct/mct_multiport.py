import os
import argparse
from gp_node.utils.address import Address
import serial
import json
import logging
import datetime
import time
import threading
from threading import Thread
import time
import socket
import signal
import sys
from scripts.Test_cases_verificationClass import TestCase
import easygui
import xlrd
import openpyxl
from scripts.mct import db_connect
import pandas as pd
from colorama import Fore, Style, init
init(autoreset=True)
global abort_threads


BUCKET_NAME = "PUT_YOUR_BUCKET_NAME_HERE"
FOLDER_NAME = "PUT_YOUR_FOLDER_NAME_HERE"
ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"

# ============================================================================
# DICTIONARY-BASED RESULT STORAGE
# ----------------------------------------------------------------------------
# The original script tracked every test step positionally: MeterInfo /
# result_list were built with .append() in a fixed hand-maintained order,
# MCT_Fail_list had to line up with result_list by index to produce readable
# failure text, and the two-phase (main test + No-Load-Test) merge matched
# meters up using raw list indices (l1[1][0], l2[1][3], ...). Any of those
# lists gaining/losing an entry silently shifted every column/message after
# it.
# This version stores everything in named dictionaries instead:
#   meter_info : {'Live_Version': ..., 'Meter_PCB_Serial_No': ..., ...}
#   test_result: {'Meter_Serial_Num': 'pass', 'Factory_Reset': 'fail', ...}
#   result_log : {com_port: {'mac', 'meter_info', 'result', 'bookName',
#                             'fileName', 'com_port'}, ...}   <- keyed by COM
#                 port instead of being a plain list of entries.

# run_mct_test() now also returns a dict of {com_port: 'pass'/'fail'/
# 'unreachable'} summarizing every port that was tested.
# ============================================================================



# ----------------------------------------------------------------------------
# LOGS FOLDER
# ----------------------------------------------------------------------------
# All log workbooks (<Meter>_<Tool>_LOG.xlsx) are now written inside a
# dedicated "Logs" folder instead of directly in the script's working
# directory, so log files stay grouped in one place regardless of where the
# tool is launched from. get_log_book_path() is the single place that
# decides the on-disk location of a log workbook -- every worker function
# and run_mct_test() call it instead of hand-building the "<Meter>_<Tool>_LOG.xlsx"
# string themselves, so the folder can't drift out of sync between them.
# ----------------------------------------------------------------------------

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
MCT_FOLDER = os.path.join(LOGS_FOLDER, "MCT")

# LOGS_FOLDER = "Logs"
# MCT_FOLDER = os.path.join(LOGS_FOLDER, "MCT")

def ensure_logs_folder():
    """Create the Logs folder if it doesn't exist yet. Safe to call every
    time a workbook path is needed -- os.makedirs(..., exist_ok=True) is a
    no-op if the folder is already there."""
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    os.makedirs(MCT_FOLDER, exist_ok=True)


def get_log_book_path(meter_type, toolName):
    """Build the full path to this run's log workbook inside the Logs
    folder. This replaces the old
        bookName = meter_type.title() + "_" + toolName.upper() + "_LOG.xlsx"
    line that was previously repeated in worker_function,
    worker_function and run_mct_test -- one helper
    means the folder can't be added to some call sites and forgotten in
    others."""
    ensure_logs_folder()
    return os.path.join(MCT_FOLDER, f"{meter_type.title()}_{toolName.upper()}_MCT_LOG.xlsx")



def get_mct_field_templates(meter_type, toolName, calib_type='single_point'):
    """
    Returns (meter_info_keys, result_keys, fail_messages) for the 3P
    (LTCT / WC) MCT, matching the field layout of the 3P MCT tool.

    * toolName containing '4g' -> 4G layout (adds IMEI, signal strength,
      dual-SIM columns plus Check_GPRS_Connection / sim check results).
    * any other toolName (img)  -> IMG layout (no SIM columns/results).
    * calib_type 'single_point' -> no FinalPhAngle[R/Y/B] columns, and the
      4G sim check is named Check_Dual_Sim; any other calib_type (multi
      point) -> FinalPhAngle columns, sim check is named Check_Sim.

    'Index' is written separately by add_log_xlsc and 'Overall_Result' is
    appended last by addDefaultMctLog, so neither is part of these lists.
    These key lists double as the Excel header order.
    """
    is_4g = '4g' in str(toolName).lower()
    single_point = 'single_point' in str(calib_type).lower()
    sim_check_key = 'Check_Dual_Sim' if single_point else 'Check_Sim'

    meter_info_keys = [
        'Date_time', 'Duplicate_Serial_No', 'Live_Version', 'Meter_PCB_Serial_No',
        'Nic_PCB_No', 'Meter_IP_Address', 'CalibStatus', 'FrequencyCoeff',
        'VCoeff[R]', 'VCoeff[Y]', 'VCoeff[B]',
        'ICoeff[R]', 'ICoeff[Y]', 'ICoeff[B]', 'ICoeff[N]',
        'ActPowerCoeff[R]', 'ActPowerCoeff[Y]', 'ActPowerCoeff[B]',
        'PhAngle[R]', 'PhAngle[Y]', 'PhAngle[B]',
    ]
    if not single_point:
        meter_info_keys += ['FinalPhAngle[R]', 'FinalPhAngle[Y]', 'FinalPhAngle[B]']
    meter_info_keys += [
        'VFCoeff[R]', 'VFCoeff[Y]', 'VFCoeff[B]',
        'IFCoeff[R]', 'IFCoeff[Y]', 'IFCoeff[B]', 'IFCoeff[N]',
        'PhAngleF[R]', 'PhAngleF[Y]', 'PhAngleF[B]',
        'Internal_Version', 'Set_Time_Value',
    ]
    if is_4g:
        meter_info_keys += ['IMEI', 'Signal_Strength', 'SIM_NUM1', 'APN1', 'SIM_NUM2', 'APN2']
    meter_info_keys += ['Led_Apparent_Value']

    result_keys = [
        'Meter_Serial_Num', 'live_version', 'Get_Meter_PCB_No', 'Get_Nic_PCB_No',
        'Get_Meter_Address', 'Get_3p_calib_cofficient', 'Get_Internal_Version',
        'Set_Time', 'Verify_time', 'Calibration_Unlock', 'Clear_Energy',
        'Verify_DLMS_Activation',
    ]
    if is_4g:
        result_keys += ['Check_GPRS_Connection', sim_check_key]
    result_keys += ['Factory_Reset', 'Check_Num_Events', 'Check_Apparent_Led']

    fail_messages = {
        'Meter_Serial_Num': 'Fail in Meter Serial No',
        'live_version': 'Fail in Get Live Version',
        'Get_Meter_PCB_No': 'Fail in Get Meter PCB No',
        'Get_Nic_PCB_No': 'Fail in NIC PCB No',
        'Get_Meter_Address': 'Fail in Get meter address',
        'Get_3p_calib_cofficient': 'Fail in get 3p calib cofficent',
        'Get_Internal_Version': 'Fail in Get Internal Version',
        'Set_Time': 'Fail in Set Time',
        'Verify_time': 'Fail in Verify Time',
        'Calibration_Unlock': 'Fail in Calib Unlock',
        'Clear_Energy': 'Fail in Clear Energy',
        'Verify_DLMS_Activation': 'Fail in DLMS Activation',
        'Factory_Reset': 'Fail in Factory Reset',
        'Check_Num_Events': 'Fail in Check Num Events',
        'Check_Apparent_Led': 'Fail in Checking Apparent Led',
    }
    if is_4g:
        fail_messages['Check_GPRS_Connection'] = 'Fail in GPRS Signal Strength'
        fail_messages[sim_check_key] = 'Fail in Checking Sim'
    return meter_info_keys, result_keys, fail_messages


def build_log_entry(mac, meter_info, test_result, bookName, fileName, com_port=None):
    """Bundle one port's results into a single dictionary instead of the
    old positional 5-item list. Keys are self-describing, and com_port
    travels with the entry so run_mct_test() can key its return value by
    COM port without needing a second parallel structure."""
    return {
        'mac': mac,
        'meter_info': meter_info,
        'result': test_result,
        'bookName': bookName,
        'fileName': fileName,
        'com_port': com_port,
    }


def build_fail_messages(com_port, test_result, fail_message_lookup, meter_info=None):
    """Named-key replacement for the old `MCT_Fail_list[idx] for idx in
    fail_indexes` pattern -- there is no positional index to keep in sync
    with result_list any more, so a step's failure text can never attach to
    the wrong step."""
    messages = []
    # PCB serial could not be fetched at all -> meter is not reachable.
    if meter_info is not None and meter_info.get('Meter_PCB_Serial_No') in (None, '', 'None'):
        return ["COM Port: {}, Meter is unreachable".format(com_port)]
    # PCB serial was fetched but is wrong (bad prefix) -> report that, not RTT.
    if test_result.get('Get_Meter_PCB_No') == 'fail':
        return ["COM Port: {}, Meter failed in Meter PCB Serial Number".format(com_port)]
    # A meter that failed RTT is not tested any further, so its popup must
    # report only the RTT failure (earlier steps like serial/version/PCB
    # checks are not repeated for it).
    if test_result.get('RTT_Check') == 'fail':
        return ["COM Port: {}, Fail in RTT Test".format(com_port)]
    for step_key, value in test_result.items():
        if value == 'fail':
            text = fail_message_lookup.get(step_key, f"Fail in {step_key}")
            messages.append("COM Port: {}, {}".format(com_port, text))
    return messages


def verify_log_xlsc(bookName, fileName):
    loc = bookName  # self.LOG_FILE_NAME

    try:
        wb = openpyxl.load_workbook(loc)
        sheet = wb.active
        cell_value = sheet.cell(row=1, column=1).value
    except Exception as e:
        logging.info("LOG XL file not found, creating one for you")
        wb = openpyxl.Workbook()
        wb.create_sheet(index=0, title=fileName)  # MRI_DATA_LOG
        sheet = wb.active
        logging.info(f"sheet name = {sheet.title}")
        del (wb['Sheet'])
        wb.save(loc)
        logging.info("New xlsc file created")
        return False
    else:
        return True


def get_header_column_map(sheet):
    """Read the header row (row 1) into {header_name: column_index}. Writing
    a row then becomes a name -> column lookup instead of relying on dict
    insertion order lining up with header order -- the last bit of implicit
    ordering coupling left over from the initial list->dict refactor."""
    header_map = {}
    for col_idx, cell in enumerate(sheet[1], start=1):
        if cell.value is not None:
            header_map[cell.value] = col_idx
    return header_map


def add_log_xlsc(log_entry):
    """Append one row to the log workbook from a dictionary-shaped
    log_entry (see build_log_entry). Every value is written to the column
    matching its own key/header name -- looked up by name, not position --
    so a row's data can never land under the wrong header even if a
    branch's field order or count changes later (e.g. after a No-Load-Test
    merge). If a key isn't in the header yet, the sheet is extended with a
    new column instead of silently dropping the value."""
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
    logging.info(f"In MCT, MAC Address of system: {mac}")
    return mac


def addDefaultMctLog(bookName, fileName, meter_type="3pltct", tool_type="img", calib_type="single_point"):
    """Create the log workbook (if missing) and write its header row.
    Headers come from get_mct_field_templates(), so they always match the
    keys the 4G worker will populate -- no separate hand-maintained
    header list to keep in sync."""
    if not verify_log_xlsc(bookName, fileName):
        logging.info("xlsx file for log not found. creating one to store test report")

        meter_info_keys, result_keys, _ = get_mct_field_templates(meter_type, tool_type, calib_type)

        meter_info_keys = meter_info_keys + ['Overall_Result']

        wb = openpyxl.load_workbook(bookName)
        sheet = wb[fileName]

        headers = ['MAC_ADDR', 'Index'] + meter_info_keys + result_keys
        for col_idx, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=col_idx).value = header

        wb.save(bookName)
        logging.info("New xlsx file created with headers")


class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


# (low, high) limits for the multi-point 3P calibration coefficients.
MULTI_POINT_CALIB_LIMITS = {
    'FrequencyCoeff': (0.99, 1.10),
    'VCoeff[R]': (0.00064, 0.00067), 'VCoeff[Y]': (0.00064, 0.00067), 'VCoeff[B]': (0.00064, 0.00067),
    'ICoeff[R]': (0.000000200, 0.000000550), 'ICoeff[Y]': (0.000000200, 0.000000550),
    'ICoeff[B]': (0.000000200, 0.000000550), 'ICoeff[N]': (0.000000160, 0.000000550),
    'ActPowerCoeff[R]': (0.000000000110, 0.000000000350),
    'ActPowerCoeff[Y]': (0.000000000110, 0.000000000350),
    'ActPowerCoeff[B]': (0.000000000110, 0.000000000350),
    'PhAngle[R]': (0.11, 0.14), 'PhAngle[Y]': (0.11, 0.14), 'PhAngle[B]': (0.11, 0.14),
    'FinalPhAngle[R]': (0.0020, 0.0030), 'FinalPhAngle[Y]': (0.0020, 0.0030),
    'FinalPhAngle[B]': (0.0020, 0.0030),
    'VFCoeff[R]': (0.00090, 0.00097), 'VFCoeff[Y]': (0.00090, 0.00097), 'VFCoeff[B]': (0.00090, 0.00097),
    'IFCoeff[R]': (0.000000250, 0.000000750), 'IFCoeff[Y]': (0.000000250, 0.000000750),
    'IFCoeff[B]': (0.000000250, 0.000000750), 'IFCoeff[N]': (0.0000950, 0.00011),
    'PhAngleF[R]': (0.11, 0.14), 'PhAngleF[Y]': (0.11, 0.14), 'PhAngleF[B]': (0.11, 0.14),
}


def _is_pass(result):
    """True if a test-case result dict reports pass. Accepts both the
    {'status': 'pass'} and the {'Result': 'Pass'} conventions."""
    if not isinstance(result, dict):
        return False
    return str(result.get('status', result.get('Result', ''))).lower() == 'pass'


def worker_function(data_dict, com_port, portID, result_queue, abort_flag, result_log):

    try:
        ser = serial.Serial(com_port, baudrate=9600, timeout=20)
        if not ser:
            msg = ["com port is unable to open:{}".format(com_port)]
            result_queue.append(msg)
            return 0

        cases = TestCase(ser, portID, data_dict.get("RETRIES", 4),data_dict.get("NIC_PCB_LENGTH", 27))
        toolName = data_dict.get("TOOL_TYPE", "4G_MCT").lower()
        mac = get_system_mac_address(toolName)

        meter_info = {}
        test_result = {}
        meterType = data_dict.get("METER_TYPE", "3PWC").lower()
        if 'ltct' in meterType:
            meter_type = "3pltct"
        elif 'wc' in meterType:
            meter_type = "3pwc"
        else:
            msg = ["Wrong Project Selected"]
            result_queue.append(msg)
            ser.close()
            return 0
        calib_type = data_dict.get("CALIB_TYPE", "single_point").lower()
        single_point = 'single_point' in calib_type
        is_4g = '4g' in toolName
        sim_check_key = 'Check_Dual_Sim' if single_point else 'Check_Sim'

        bookName = get_log_book_path(meter_type, toolName)
        fileName = toolName.upper() + "_DATA_LOG"
        starttime = datetime.datetime.now()
        Main_PCB_SFG_Prefix = data_dict.get("MAIN_PCB_SFG_PREFIX", "0000001")
        Nic_PCB_SFG_PREFIX = data_dict.get("NIC_PCB_SFG_PREFIX", "0000004")
        METER_ADDRESS = "255.255.255.255"

        Date_time = datetime.datetime.now()
        meter_info['Date_time'] = Date_time
        addDefaultMctLog(bookName, fileName, meter_type.lower(), toolName.lower(), calib_type)

        # Fail-message lookup and calibration field names for this branch
        template_info_keys, _, fail_message_lookup = get_mct_field_templates(meter_type, toolName, calib_type)
        calib_keys = template_info_keys[template_info_keys.index('CalibStatus'):template_info_keys.index('Internal_Version')]

        # Check com port status using check live version
        retryCnt = 3
        while retryCnt:
            logging.info(f"Checking COM port connectivity, attempt: {4 - retryCnt}, for com: {com_port}")
            try:
                check_port = cases.check_port(com_port)
                if 'Fail' == check_port:
                    msg = ["Meter is unreachable: {}".format(com_port)]
                    result_queue.append(msg)
                    # Only THIS meter stops; the shared abort_flag is
                    # deliberately not set so other ports keep testing.
                    logging.info(f"ser close for port : {com_port}")
                    ser.close()
                    return
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in worker func in check com port connectivity: {str(e)}, for com: {com_port}")
                retryCnt -= 1

        if abort_flag.is_set():
            return

        # Verify meter serial number
        sr_num = {}
        retryCnt = 3
        while (retryCnt):
            logging.debug(f"Verifying Meter Serial Number, attempt: {4 - retryCnt}, for com: {com_port}")
            try:
                sr_num = cases.Verify_Serial_number(com_port)
                meter_info['Duplicate_Serial_No'] = str(sr_num.get("sr_number", "None"))
                Sr_num2 = cases.Verify_Serial_number2(com_port)
                if Sr_num2.get('status') == 'pass':
                    test_result['Meter_Serial_Num'] = 'pass'
                else:
                    test_result['Meter_Serial_Num'] = 'fail'
                logging.debug(f"Meter Serial Number: {sr_num}, for com: {com_port}")
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in MCT in worker func in verify meter serial number: {str(e)}, for com: {com_port}")
                retryCnt = retryCnt - 1

        # Get live version
        retryCnt = 3
        while (retryCnt):
            logging.debug(f"Getting Live Version, attempt: {4 - retryCnt}, for com: {com_port}")
            try:
                version_live = cases.get_live_version_val(com_port)
                meter_info['Live_Version'] = str(version_live)
                if version_live == data_dict.get("LIVE_VERSION", 0000):
                    test_result['live_version'] = 'pass'
                else:
                    test_result['live_version'] = 'fail'
                logging.debug(f"Live Version: {version_live}, for com: {com_port}")
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in MCT in worker func in live version check: {str(e)}, for com: {com_port}")
                retryCnt = retryCnt - 1

        # Get pcb serial number
        retryCnt = 3
        while (retryCnt):
            logging.debug(f"Getting Meter PCB Serial Number, attempt: {4 - retryCnt}, for com: {com_port}")
            try:
                Pcb_serial_no = cases.Get_pcb_serial_num(com_port)
                meter_info['Meter_PCB_Serial_No'] = str(Pcb_serial_no)
                if str(Pcb_serial_no[9:16]) == str(Main_PCB_SFG_Prefix):
                    test_result['Get_Meter_PCB_No'] = 'pass'
                else:
                    test_result['Get_Meter_PCB_No'] = 'fail'
                logging.debug(f"Meter PCB Serial Number: {Pcb_serial_no}, for com: {com_port}")
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in worker func in get pcb serial number: {str(e)}, for com: {com_port}")
                retryCnt = retryCnt - 1

        rtt_result = db_connect.fetch_by_pcb_serial(Pcb_serial_no, toolName.lower())
        # rtt_result = True
        test_result['RTT_Check'] = 'pass' if rtt_result else 'fail'

        if not rtt_result:
            logging.info(
                f"RTT failed for com: {com_port}, PCB: {Pcb_serial_no}, "
                f"RTT overall_result: {rtt_result!r} -- skipping MCT test for this meter"
            )

        if rtt_result:
            # Get Nic PCB serial number
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Getting NIC PCB Serial Number, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    Nic_PCB_no = cases.Nic_PCB_No(com_port)
                    logging.debug(f"NIC PCB Serial Number: {Nic_PCB_no}, for com: {com_port}")
                    Nic_PCB_no = Nic_PCB_no.get("nic_pcb_number", None)
                    meter_info['Nic_PCB_No'] = str(Nic_PCB_no)
                    if ((('R144' == str(Nic_PCB_no[0:4])) or ('r144' == str(Nic_PCB_no[0:4])) or
                        (str(Nic_PCB_no[9:16]) == str(Nic_PCB_SFG_PREFIX))) and (not Nic_PCB_no.endswith('\x00'))):
                        test_result['Get_Nic_PCB_No'] = 'pass'
                    else:
                        test_result['Get_Nic_PCB_No'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in getting NIC PCB No: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Get meter address
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Getting Meter Address, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    Meter_address = cases.get_Meter_address( com_port)
                    meter_info['Meter_IP_Address'] = str(Meter_address.get('mtr_address', 'None'))
                    meter_addr2 = cases.get_Meter_address2(int(sr_num.get("sr_number", "None")), com_port)
                    if meter_addr2.get('status', 'fail') == 'pass':
                        test_result['Get_Meter_Address'] = 'pass'
                    else:
                        test_result['Get_Meter_Address'] = 'fail'
                    logging.debug(f"Meter Address: {Meter_address}, for com: {com_port}")
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in get meter address: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Check 3P Calib cofficient
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Getting 3P Calibration Coefficients, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    calib_cofficient = cases.get_3p_calib_coffi(com_port, data_dict.get("CALIB_TYPE", "single_point"))
                    if 'Fail' in calib_cofficient:
                        for key in calib_keys:
                            meter_info[key] = 'Fail'
                        test_result['Get_3p_calib_cofficient'] = 'fail'
                    else:
                        for key in calib_keys:
                            meter_info[key] = str(calib_cofficient.get(key))
                        if single_point:
                            # every coefficient must be within 0..1 (PhAngleF[B] up to 1.05)
                            calib_ok = True
                            for key in calib_keys:
                                if key == 'CalibStatus':
                                    continue
                                # upper = 1.05 if key == 'PhAngleF[B]' else 1.0
                                if not (0.0 <= float(str(calib_cofficient.get(key))) <= 1.0):
                                    calib_ok = False
                                    break
                        else:
                            calib_ok = all(
                                float(low) < float(str(calib_cofficient.get(key))) < float(high)
                                for key, (low, high) in MULTI_POINT_CALIB_LIMITS.items()
                            )
                        if calib_ok:
                            test_result['Get_3p_calib_cofficient'] = 'pass'
                            logging.debug(f"Pass in get 3p calib cofficient for com: {com_port}")
                        else:
                            test_result['Get_3p_calib_cofficient'] = 'fail'
                            logging.debug(f"Fail in get 3p calib cofficient for com: {com_port}")
                    logging.debug(f"3P Calibration Coefficients: {calib_cofficient}, for com: {com_port}")
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in check 3p calib cofficient: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1
                    if retryCnt == 0:
                        for key in calib_keys:
                            meter_info[key] = 'Fail'
                        test_result['Get_3p_calib_cofficient'] = 'fail'

            # Get Internal Version
            if str(data_dict.get("INTERNAL_VERSION", 0)) == str(0):
                logging.info(f"Skipping Internal Version check as per configuration, for com: {com_port}")
                test_result['Get_Internal_Version'] = 'skip'
                meter_info['Internal_Version'] = '0'
            else:
                retryCnt = 3
                while (retryCnt):
                    logging.debug(f"Getting Internal Version, attempt: {4 - retryCnt}, for com: {com_port}")
                    try:
                        int_version = cases.get_internal_version_val(com_port)
                        if str(int_version.get("int_version", "0")) == str(data_dict.get("INTERNAL_VERSION", "0")):
                            test_result['Get_Internal_Version'] = 'pass'
                        else:
                            test_result['Get_Internal_Version'] = 'fail'
                        meter_info['Internal_Version'] = str(int_version.get('int_version', 'None'))
                        logging.debug(f"Internal Version: {int_version}, for com: {com_port}")
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in MCT in worker func in get internal verison: {str(e)}, for com: {com_port}")
                        retryCnt = retryCnt - 1

            # Set time
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Setting Meter Time, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    Set_ip_time = cases.Set_time_val(com_port)
                    meter_info['Set_Time_Value'] = "now"
                    if Set_ip_time.get('status') == 'pass':
                        test_result['Set_Time'] = 'pass'
                    else:
                        test_result['Set_Time'] = 'fail'
                    logging.debug(f"Set Time Result: {Set_ip_time}, for com: {com_port}")
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in Setting meter time: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Get meter time
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Verifying Meter Time, attempt: {4 - retryCnt} for com: {com_port}")
                try:
                    meter_time = cases.Verify_time_val(com_port)
                    logging.debug(f"Meter time: {meter_time}, for com: {com_port}")
                    if meter_time.get('status') == 'pass':
                        test_result['Verify_time'] = 'pass'
                    else:
                        test_result['Verify_time'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in get time: {str(e)} for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Calib Unlock
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Performing Calibration Unlock, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    calib_unlock = cases.Calibration_unLock(com_port)
                    logging.debug(f"Calib unlock status: {calib_unlock}, for com: {com_port}")
                    if calib_unlock.get('status') == 'pass':
                        test_result['Calibration_Unlock'] = 'pass'
                    else:
                        test_result['Calibration_Unlock'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in calib unlock: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Clear Energy
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Clearing Energy Values, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    Meter_energy = cases.Clear_Energy_Value(com_port)
                    logging.debug(f"Meter Energy: {Meter_energy} for com: {com_port}")
                    if Meter_energy.get('status') == 'pass':
                        test_result['Clear_Energy'] = 'pass'
                    else:
                        test_result['Clear_Energy'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in clear energy: {str(e)} for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Check DLMS activation
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Checking DLMS Activation, attempt: {4 - retryCnt} for com: {com_port}")
                try:
                    CHECK_DLMS_ACTIVATION = cases.dlms_Activation_check_value(com_port, data_dict.get('DLMS_TYPE', 'old_dlms').lower())
                    logging.debug(f"DLMS Activation status: {CHECK_DLMS_ACTIVATION}, for com: {com_port}")
                    if CHECK_DLMS_ACTIVATION.get('status') == 'pass':
                        test_result['Verify_DLMS_Activation'] = 'pass'
                    else:
                        test_result['Verify_DLMS_Activation'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in checking DLMS activation: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Check GPRS connection and dual SIM (4G only)
            if is_4g:
                retryCnt = 3
                while (retryCnt):
                    logging.debug(f"Checking GPRS Connection and SIM, attempt: {4 - retryCnt}, for com: {com_port}")
                    try:
                        logging.info(f"Wait for 40 sec for sim1 connection in meter, for com: {com_port}")
                        time.sleep(40)
                        sim = cases.get_meter_sim_and_sim_number(com_port)
                        logging.debug(f"Result of getting SIM details: {sim}, for com: {com_port}")
                        if sim.get('Result').lower() == 'fail':
                            for key in ('IMEI', 'Signal_Strength', 'SIM_NUM1', 'APN1', 'SIM_NUM2', 'APN2'):
                                meter_info[key] = 'Fail'
                            test_result['Check_GPRS_Connection'] = 'fail'
                            test_result[sim_check_key] = 'fail'
                        else:
                            meter_info['IMEI'] = str(sim.get('sim_result_value')[3])
                            meter_info['Signal_Strength'] = str(sim.get('sim_result_value')[4])
                            signal = int(sim.get('sim_result_value')[4])
                            if (10 <= signal) and (signal != 99) and (signal != 255) and (int(sim.get('sim_result_value')[0]) in (1, 2)):
                                test_result['Check_GPRS_Connection'] = 'pass'
                            else:
                                test_result['Check_GPRS_Connection'] = 'fail'

                            if data_dict.get('sim_fetch_count', 1) == 1:
                                if (str(sim.get('sim_result_value')[1]) != str(sim.get('sim_result_value')[5])) and ((str(sim.get('sim_result_value')[5]) != '0') or (str(sim.get('sim_result_value')[1]) != '0')):
                                    test_result[sim_check_key] = 'pass'
                                    final_sim = sim
                                else:
                                    cases.set_sim_toggle(com_port)
                                    toggle_wait = data_dict.get('Sim_Toggle_Time', 5)
                                    logging.info(f"Waiting for Sim Toggle for {toggle_wait} sec, for com: {com_port}")
                                    time.sleep(toggle_wait)
                                    final_sim = cases.get_meter_sim_and_sim_number(com_port)
                                    logging.debug(f"SIM details after toggle: {final_sim}, for com: {com_port}")
                                    if final_sim.get('Result').lower() == 'fail':
                                        test_result[sim_check_key] = 'fail'
                                    elif (str(final_sim.get('sim_result_value')[1]) != str(final_sim.get('sim_result_value')[5])) and ((str(final_sim.get('sim_result_value')[5]) != '0') or (str(final_sim.get('sim_result_value')[1]) != '0')):
                                        test_result[sim_check_key] = 'pass'
                                    else:
                                        test_result[sim_check_key] = 'fail'
                            else:
                                if (str(sim.get('sim_result_value')[1]) != str(sim.get('sim_result_value')[5])) and (str(sim.get('sim_result_value')[5]) != '0') and (str(sim.get('sim_result_value')[1]) != '0'):
                                    test_result[sim_check_key] = 'pass'
                                    final_sim = sim
                                else:
                                    cases.set_sim_toggle(com_port)
                                    toggle_wait = data_dict.get('Sim_Toggle_Time', 5)
                                    logging.info(f"Waiting for Sim Toggle for {toggle_wait} sec, for com: {com_port}")
                                    time.sleep(toggle_wait)
                                    final_sim = cases.get_meter_sim_and_sim_number(com_port)
                                    logging.debug(f"SIM details after toggle: {final_sim}, for com: {com_port}")
                                    if final_sim.get('Result').lower() == 'fail':
                                        test_result[sim_check_key] = 'fail'
                                    elif (str(final_sim.get('sim_result_value')[1]) != str(final_sim.get('sim_result_value')[5])) and (str(final_sim.get('sim_result_value')[5]) != '0') and (str(final_sim.get('sim_result_value')[1]) != '0'):
                                        test_result[sim_check_key] = 'pass'
                                    else:
                                        test_result[sim_check_key] = 'fail'

                            if final_sim.get('Result').lower() == 'fail':
                                for key in ('SIM_NUM1', 'APN1', 'SIM_NUM2', 'APN2'):
                                    meter_info[key] = 'Fail'
                            else:
                                meter_info['SIM_NUM1'] = str(final_sim.get('sim_result_value')[1])
                                meter_info['APN1'] = str(final_sim.get('sim_result_value')[2])
                                meter_info['SIM_NUM2'] = str(final_sim.get('sim_result_value')[5])
                                meter_info['APN2'] = str(final_sim.get('sim_result_value')[6])
                        retryCnt = 0
                    except Exception as e:
                        logging.error(f"Error in MCT in worker func in checking GPRS connection: {str(e)}, for com: {com_port}")
                        retryCnt = retryCnt - 1
                        if retryCnt == 0:
                            for key in ('IMEI', 'Signal_Strength', 'SIM_NUM1', 'APN1', 'SIM_NUM2', 'APN2'):
                                meter_info[key] = 'fail'
                            test_result['Check_GPRS_Connection'] = 'fail'
                            test_result[sim_check_key] = 'fail'

            # Factory reset
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Performing Factory Reset, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    FactoryReset = cases.Factory_reset_val(com_port)
                    logging.debug(f"Factory reset result: {FactoryReset}, for com: {com_port}")
                    if FactoryReset.get('status') == 'pass':
                        test_result['Factory_Reset'] = 'pass'
                    else:
                        test_result['Factory_Reset'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in factory reset: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            logging.info(f"Wait for meter start after factory reset: {data_dict.get('Fact_Reset_sleepTime', 5)}, for com: {com_port}")
            time.sleep(data_dict.get("Fact_Reset_sleepTime", 5))

            # Check num events
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Checking Number of Events after Factory Reset, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    check_num_event = cases.check_num_events(com_port)
                    logging.debug(f"Check num events result: {check_num_event}, for com: {com_port}")
                    if check_num_event.get('status') == 'pass':
                        test_result['Check_Num_Events'] = 'pass'
                    else:
                        test_result['Check_Num_Events'] = 'fail'
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in checking number of events: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1

            # Get apparent LED status
            retryCnt = 3
            while (retryCnt):
                logging.debug(f"Checking Apparent LED status, attempt: {4 - retryCnt}, for com: {com_port}")
                try:
                    CHECK_APP_LED = cases.get_apparent_led_status(com_port)
                    logging.debug(f"Apparent LED status result: {CHECK_APP_LED}, for com: {com_port}")
                    if CHECK_APP_LED.get('status') == 'pass':
                        test_result['Check_Apparent_Led'] = 'pass'
                    else:
                        test_result['Check_Apparent_Led'] = 'fail'
                    meter_info['Led_Apparent_Value'] = CHECK_APP_LED.get('value', 'None')
                    retryCnt = 0
                except Exception as e:
                    logging.error(f"Error in MCT in worker func in checking apparent led: {str(e)}, for com: {com_port}")
                    retryCnt = retryCnt - 1
                    if retryCnt == 0:
                        meter_info['Led_Apparent_Value'] = 'None'
                        test_result['Check_Apparent_Led'] = 'fail'

        ser.close()

        # Overall_Result is computed once by run_mct_test().
        result_log[com_port] = build_log_entry(mac, meter_info, test_result, bookName, fileName, com_port)

        time.sleep(0.1)

        EndTime = datetime.datetime.now()
        logging.info(f"Test time for MCT StartTime: {starttime}, for com: {com_port}")
        logging.info(f"Test time for MCT EndTime: {EndTime}, for com: {com_port}")
        logging.info(f"Test time for MCT Diff : {EndTime - starttime}, for com: {com_port}")

        fail_messages = build_fail_messages(com_port, test_result, fail_message_lookup, meter_info)
        if fail_messages:
            result_queue.append(fail_messages)

    except Exception as e:
        msg = ["com port is unreachable:{}".format(com_port)]
        logging.error(f"Exception in worker_function: {str(e)}")
        result_queue.append(msg)
        return


def finalize_overall_results(results):
    """Compute Overall_Result for every entry from its (possibly merged)
    result dict, and set it last so it always lands as the final Excel
    column regardless of what got merged in beforehand."""
    for entry in results.values():
        entry['meter_info']['Overall_Result'] = 'fail' if 'fail' in entry['result'].values() else 'pass'


# Sentinel values written into the log when a step's real data was never
# recorded (worker crashed/aborted before reaching that step). A missing
# result step reads as 'fail', never a silent 'pass' -- untested must never
# look identical to tested-and-passed.
NOT_TESTED_METER_VALUE = None
NOT_TESTED_RESULT_VALUE = 'fail'


def fill_missing_fields(entry, meter_info_keys, result_keys):
    """Ensure every field in meter_info_keys/result_keys exists on `entry`,
    filling in NOT_TESTED_* defaults for anything a worker never got to
    write.

    This is what actually prevents the Excel "column mismatch" the old
    list-based script suffered from: if worker_function2 aborted (e.g.
    failed its own COM-port check) before ever writing a phase-2 entry,
    merge_no_load_result() has nothing to merge into the matching phase-1
    row, so that row would otherwise be missing the No-Load-Test fields
    entirely. add_log_xlsc() already writes by header *name* rather than
    position (see get_header_column_map), so a short entry no longer shifts
    later columns out of alignment the way the original positional writer
    did -- but a field that's simply absent from the dict still left a
    blank, unexplained cell. Calling this right before finalize_overall_results()
    guarantees every row has a value under every header, so a genuinely
    untested step shows up as an explicit 'fail' in the log instead of an
    empty cell someone has to notice and investigate."""
    for key in meter_info_keys:
        entry['meter_info'].setdefault(key, NOT_TESTED_METER_VALUE)
    for key in result_keys:
        entry['result'].setdefault(key, NOT_TESTED_RESULT_VALUE)


def run_mct_test(data_dict, active_port_list, upload_bench):
    parser = argparse.ArgumentParser()
    logging.info("Starting MCT Testing Script")

    parser.add_argument('-p', action="store", dest="hex_file",
                        help="programs new hex file")
    parser.add_argument("--id", action="store", dest="portID",
                      help="device id")

    args = parser.parse_args()
    if args.portID is None:
        args.portID = 4

    list_port = active_port_list

    results = []
    results1 = []
    phase1_results = {}   # worker_function, keyed by COM port
    abort_flag = threading.Event()

    toolName = data_dict.get("TOOL_TYPE", "RF").lower()
    meter_type = data_dict.get("METER_TYPE", "Garud_1PH").lower()
    calib_type = data_dict.get("CALIB_TYPE", "single_point").lower()
    # bookName = meter_type.title() + "_" + toolName.upper() + "_LOG.xlsx"
    bookName = get_log_book_path(meter_type, toolName)
    fileName = toolName.upper() + "_DATA_LOG"
    addDefaultMctLog(bookName, fileName, meter_type.lower(), toolName.lower(), calib_type)

    
    logging.info("Starting MCT Testing on ports: {}".format(list_port))
    threads = [StoppableThread(target=worker_function, args=(data_dict, port_name, args.portID, results, abort_flag, phase1_results)) for port_name in list_port]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # -----------------------------------------------------------------
    # Guarantee every requested port has a COMPLETE row before writing to
    # Excel: if a worker crashes before ever calling
    # result_log[com_port] = ... that port never gets an entry in
    # phase1_results in the first place.
    #
    # get_mct_field_templates() is the same
    # template used to build the header row, so "every field the header
    # expects" and "every field we fill a default for" can never drift
    # apart. Any port missing entirely gets a placeholder entry (marked
    # fully_untested so the returned pass/fail summary can still say
    # 'unreachable' instead of 'fail'); any port with a partial entry gets
    # its missing fields defaulted in place.
    # -----------------------------------------------------------------
    meter_keys, result_keys, _ = get_mct_field_templates(meter_type, toolName, calib_type)
    for port_name in list_port:
        if port_name not in phase1_results:
            placeholder = build_log_entry(
                mac='NOT_TESTED', meter_info={}, test_result={},
                bookName=bookName, fileName=fileName, com_port=port_name,
            )
            placeholder['fully_untested'] = True
            phase1_results[port_name] = placeholder

        entry = phase1_results[port_name]
        fill_missing_fields(entry, meter_keys, result_keys)

    # Overall_Result is computed once here, from each entry's
    # fully-populated result dict, so it's always the last
    # column regardless of whether a No-Load-Test merge happened.
    finalize_overall_results(phase1_results)

    for com_port_key, entry in phase1_results.items():
        try:
            add_log_xlsc(entry)
        except Exception:
            logging.info("unknown error in add logs in Excel")
            continue

    # Dictionary-based pass/fail summary keyed by COM port -- every port
    # that was asked for gets an entry (thanks to the placeholder fill-in
    # above), including ones that never produced any real result, which are
    # reported as 'unreachable' rather than a possibly-misleading 'fail'.
    mct_pass_fail_by_com = {}
    for port_name in list_port:
        entry = phase1_results[port_name]
        if entry.get('fully_untested'):
            mct_pass_fail_by_com[port_name] = 'unreachable'
        else:
            mct_pass_fail_by_com[port_name] = entry['meter_info'].get('Overall_Result', 'fail')

    if data_dict.get("IS_DATA_CONN", 1) == 1:
        df_frame = pd.read_excel(bookName)
        try:
            status = False
            error = ""
            # rf / img / 4g all use the 4G tables and test cases
            if '4g' in toolName.lower():
                status, error = db_connect.upload_dataframe(df_frame, meter_type.lower(), '4g')
            else:
                status, error = db_connect.upload_dataframe(df_frame, meter_type.lower(), 'img')
            if not status:
                logging.info(f"DB upload failed . Saved locally for retry. Error: {error}")
            else:
                if (len(phase1_results) != 0):  # if the result file is empty then don't upload to server
                    logging.info("Uploading MCT Test Results to Cloud Storage")


                    import boto3
                    from botocore.exceptions import NoCredentialsError


                    def upload_to_aws(local_folder, bucket, s3_file, sub_folder, file_time, folder_name1, local_file_path = None):
                        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                        aws_secret_access_key=SECRET_KEY)
                        local_path = os.path.join(MCT_FOLDER, s3_file)
                        logging.info(f"Uploaded file: {str(upload_bench + "_" + file_time + "_" + s3_file)}")
                        try:
                            if local_file_path is None:
                                local_file_path = s3_file
                            s3.upload_file(local_file_path, bucket, folder_name + "/{0}/{1}/{2}/{3}".format(folder_name1, sub_folder, local_folder, str(upload_bench + "_" + file_time + "_" + s3_file)))
                            logging.info("Upload Successful")
                            os.remove(local_file_path)
                            return True
                        except NoCredentialsError:
                            logging.info("Credentials not available")
                            return False
                        except Exception as e:
                            logging.info(e)
                            logging.info("The file was not found")
                            return False

                    al = os.listdir(MCT_FOLDER)
                    txt = list(filter(lambda x: x[-5:] == '.xlsx', al))
                    if len(txt) == 0:
                        return mct_pass_fail_by_com

                    for j in range(len(txt)):
                        temp_time = datetime.datetime.now()
                        date_only = datetime.datetime.strftime(temp_time, '%Y-%m-%d')
                        time_only = datetime.datetime.strftime(temp_time, '%H_%M_%S')

                        sub_folder = "UNKNOWN"
                        xyx = str(txt[j])
                        if ("PCT" in xyx):
                            sub_folder = "PCT"
                        elif ("4g" in xyx.lower()):
                            sub_folder = "4G_MCT"
                        elif ("img" in xyx.lower()):
                            sub_folder = "IMG_MCT"

                        else:
                            logging.info("improper file name given for tool type")
                            continue
                        logging.info(f"sub_folder = {sub_folder}")

                        folder_name1 = "UNKNOWN"
                        if "SM_1P" in xyx:
                            folder_name1 = "ISM_1P"
                        elif "SM_3P" in xyx:
                            folder_name1 = "ISM_3P"
                        elif "AP_3P" in xyx:
                            folder_name1 = "CAP_3P"
                        elif "CU_" in xyx:
                            folder_name1 = "DCU_"
                        elif ("garud" in xyx.lower()):
                            folder_name1 = "Garud"
                        elif ("better" in xyx.lower()):
                            folder_name1 = "Better_Meter"
                        elif('ltct' in xyx.lower()):
                            folder_name1 = "3PLTCT" 
                        elif('wc' in xyx.lower()):
                            folder_name1 = "3PWC" 
                        else:
                            logging.info("improper file name given for Meter type")
                            continue
                        logging.info(f"Uploading file: {str(txt[j])} to bucket: {bucket_name} in folder: {folder_name}/{folder_name1}/{date_only}")
                        local_path = os.path.join(MCT_FOLDER, txt[j])
                        uploaded = upload_to_aws(str(date_only), bucket_name, txt[j], sub_folder, time_only, folder_name1, local_file_path=local_path)
                        logging.info("MCT DATA SUCCESSFULLY UPLOADED TO CLOUD")
                else:
                    logging.info("Skipping to Upload the log file to server")
        except Exception as e:
            logging.error(f"Error writing DB log: {str(e)}")
    else:
        logging.info("Upload data to EMS db flag is disable")
        try:
            if (len(phase1_results) != 0):  # if the result file is empty then don't upload to server
                logging.info("Uploading MCT Test Results to Cloud Storage")


                import boto3
                from botocore.exceptions import NoCredentialsError


                def upload_to_aws(local_folder, bucket, s3_file, sub_folder, file_time, folder_name1, local_file_path = None):
                    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                    aws_secret_access_key=SECRET_KEY)
                    local_path = os.path.join(MCT_FOLDER, s3_file)
                    logging.info(f"Uploaded file: {str(upload_bench + "_" + file_time + "_" + s3_file)}")
                    try:
                        if local_file_path is None:
                            local_file_path = s3_file
                        s3.upload_file(local_file_path, bucket, folder_name + "/{0}/{1}/{2}/{3}".format(folder_name1, sub_folder, local_folder, str(upload_bench + "_" + file_time + "_" + s3_file)))
                        logging.info("Upload Successful")
                        os.remove(local_file_path)
                        return True
                    except NoCredentialsError:
                        logging.info("Credentials not available")
                        return False
                    except Exception as e:
                        logging.info(e)
                        logging.info("The file was not found")
                        return False

                al = os.listdir(MCT_FOLDER)
                txt = list(filter(lambda x: x[-5:] == '.xlsx', al))
                logging.info(txt)
                if len(txt) == 0:
                    logging.info("file doesn't exist")
                    return mct_pass_fail_by_com

                for j in range(len(txt)):
                    temp_time = datetime.datetime.now()
                    date_only = datetime.datetime.strftime(temp_time, '%Y-%m-%d')
                    time_only = datetime.datetime.strftime(temp_time, '%H_%M_%S')

                    sub_folder = "UNKNOWN"
                    xyx = str(txt[j])
                    if ("PCT" in xyx):
                        sub_folder = "PCT"
                    elif ("4g" in xyx.lower()):
                        sub_folder = "4G_MCT"
                    elif ("img" in xyx.lower()):
                        sub_folder = "IMG_MCT"

                    else:
                        logging.info("improper file name given for tool type")
                        continue
                    logging.info(f"sub_folder = {sub_folder}")

                    folder_name1 = "UNKNOWN"
                    if "SM_1P" in xyx:
                        folder_name1 = "ISM_1P"
                    elif "SM_3P" in xyx:
                        folder_name1 = "ISM_3P"
                    elif "AP_3P" in xyx:
                        folder_name1 = "CAP_3P"
                    elif "CU_" in xyx:
                        folder_name1 = "DCU_"
                    elif ("garud" in xyx.lower()):
                        folder_name1 = "Garud"
                    elif ("better" in xyx.lower()):
                        folder_name1 = "Better_Meter"
                    elif('ltct' in xyx.lower()):
                        folder_name1 = "3PLTCT" 
                    elif('wc' in xyx.lower()):
                        folder_name1 = "3PWC" 
                    else:
                        logging.info("improper file name given for Meter type")
                        continue

                    logging.info(f"Uploading file: {str(txt[j])} to bucket: {bucket_name} in folder: {folder_name}/{folder_name1}/{date_only}")
                    local_path = os.path.join(MCT_FOLDER, txt[j])
                    uploaded = upload_to_aws(str(date_only), bucket_name, txt[j], sub_folder, time_only, folder_name1, local_file_path=local_path)
            else:
                logging.info("Skipping to Upload the log file to server")
        except Exception as e:
            logging.error(f"Error Uploading log: {str(e)}")

    logging.info("MCT Testing Completed with results: {}".format(phase1_results))
    if results:
        # Flatten and remove duplicates
        flat_results = [item for sublist in results for item in sublist]
        unique_results = list(set(flat_results))
        msg_text = "\n".join(unique_results)
        easygui.msgbox(msg_text, title="MCT Test Failures")   # <-- popup added
        
    # return {'COM157': 'pass'} 
    return mct_pass_fail_by_com
