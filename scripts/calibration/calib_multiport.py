import os
from collections import OrderedDict
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
import serial
import datetime
import time
import threading
import queue
from threading import Thread
import sys
from scripts.Test_cases_verificationClass import TestCase
import logging
import easygui
import openpyxl
import win32com.client
import pythoncom
from colorama import Fore, Style, init
import pandas as pd
from scripts.calibration import db_connect
import boto3
from botocore.exceptions import NoCredentialsError
global abort_threads


BUCKET_NAME = "PUT_YOUR_BUCKET_NAME_HERE"
FOLDER_NAME = "PUT_YOUR_FOLDER_NAME_HERE"
ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"

# Placeholder written to the excel log whenever a reading could not be
# captured (comms failure, exception, meter never answered, etc). Using one
# constant means add_log_xlsc always has *something* to write for every
# column, so a partial failure can never shift later columns out of
# alignment the way a short list used to.
MISSING_VALUE = 'N/A'

# CalibStatus value a meter reports once calibration has been committed.
CALIB_STATUS_OK = 3203391149

# ---------------------------------------------------------------------------
# Calibration coefficient limits, same scheme as mct_multiport.py:
#
#   * multi_point  -> MULTI_POINT_CALIB_LIMITS: per-coefficient (min, max),
#                     checked strictly (min < value < max), includes the
#                     FinalPhAngle[R/Y/B] coefficients.
#   * single_point -> no FinalPhAngle columns; every coefficient must be
#                     within 0..1 inclusive (PhAngleF[B] up to 1.05).
#
# get_calib_fields(calib_type) is the single source of truth for both the
# excel header columns and the pass/fail range check.
# ---------------------------------------------------------------------------
MULTI_POINT_CALIB_LIMITS = OrderedDict([
    ('FrequencyCoeff',       (0.99,            1.10)),
    ('VCoeff[R]',            (0.00064,         0.00067)),
    ('VCoeff[Y]',            (0.00064,         0.00067)),
    ('VCoeff[B]',            (0.00064,         0.00067)),
    ('ICoeff[R]',            (0.000000200,     0.000000550)),
    ('ICoeff[Y]',            (0.000000200,     0.000000550)),
    ('ICoeff[B]',            (0.000000200,     0.000000550)),
    ('ICoeff[N]',            (0.000000160,     0.000000550)),
    ('ActPowerCoeff[R]',     (0.000000000110,  0.000000000350)),
    ('ActPowerCoeff[Y]',     (0.000000000110,  0.000000000350)),
    ('ActPowerCoeff[B]',     (0.000000000110,  0.000000000350)),
    ('PhAngle[R]',           (0.11,            0.14)),
    ('PhAngle[Y]',           (0.11,            0.14)),
    ('PhAngle[B]',           (0.11,            0.14)),
    ('FinalPhAngle[R]',      (0.0020,          0.0030)),
    ('FinalPhAngle[Y]',      (0.0020,          0.0030)),
    ('FinalPhAngle[B]',      (0.0020,          0.0030)),
    ('VFCoeff[R]',           (0.00090,         0.00097)),
    ('VFCoeff[Y]',           (0.00090,         0.00097)),
    ('VFCoeff[B]',           (0.00090,         0.00097)),
    ('IFCoeff[R]',           (0.000000250,     0.000000750)),
    ('IFCoeff[Y]',           (0.000000250,     0.000000750)),
    ('IFCoeff[B]',           (0.000000250,     0.000000750)),
    ('IFCoeff[N]',           (0.0000950,       0.00011)),
    ('PhAngleF[R]',          (0.11,            0.14)),
    ('PhAngleF[Y]',          (0.11,            0.14)),
    ('PhAngleF[B]',          (0.11,            0.14)),
])


class _MainThreadDialogBridge(QObject):
    _request_enterbox = pyqtSignal(str, str, object)  # msg, title, response_queue
    _request_msgbox = pyqtSignal(str, str, object)     # msg, title, response_queue

    def __init__(self):
        super().__init__()
        self._request_enterbox.connect(self._show_enterbox, Qt.QueuedConnection)
        self._request_msgbox.connect(self._show_msgbox, Qt.QueuedConnection)

    def enterbox(self, msg, title):
        """Blocks the CALLING (worker) thread until the user answers a
        text-entry dialog shown on the main thread. Returns the entered
        text, or None if the dialog was cancelled."""
        response_queue = queue.Queue(maxsize=1)
        self._request_enterbox.emit(msg, title, response_queue)
        return response_queue.get()

    def msgbox(self, msg, title):
        """Blocks the calling thread until an info dialog shown on the main
        thread is dismissed."""
        response_queue = queue.Queue(maxsize=1)
        self._request_msgbox.emit(msg, title, response_queue)
        response_queue.get()

    def _show_enterbox(self, msg, title, response_queue):
        parent = QApplication.activeWindow()
        text, ok = QInputDialog.getText(parent, title, msg)
        response_queue.put(text if ok else None)

    def _show_msgbox(self, msg, title, response_queue):
        parent = QApplication.activeWindow()
        QMessageBox.information(parent, title, msg)
        response_queue.put(None)


# Constructed here, at module import time - this module is imported from
# main.py's top-level imports, which always run on the main thread, well
# before any FunctionThreadRunner worker thread is spawned. That guarantees
# this QObject's thread affinity is the main thread for the life of the
# process, so every emit() below - no matter which worker thread calls it -
# delivers its dialog on the main thread.
_dialog_bridge = _MainThreadDialogBridge()


def is_single_point(calib_type):
    return 'single_point' in str(calib_type).lower()


def get_calib_type(data_dict):
    return str(data_dict.get("CALIB_TYPE", "single_point")).lower()


def get_calib_fields(calib_type):
    """Ordered {coefficient: (min, max)} for this calibration type."""
    if is_single_point(calib_type):
        return OrderedDict(
            (name, (0.0, 1.0))
            for name in MULTI_POINT_CALIB_LIMITS
            if not name.startswith('FinalPhAngle')
        )
    return OrderedDict(MULTI_POINT_CALIB_LIMITS)


def get_meter_info_columns(calib_type):
    """Column order for the "meter info" half of the excel row."""
    return (
        ['Date_time', 'Meter_PCB_Serial_No', 'CalibStatus']
        + [c for field in get_calib_fields(calib_type) for c in (f'{field}_min', f'{field}_max', field)]
        + ['Overall_Result']
    )


# Column order for the pass/fail "checks" half of the excel row, and the
# human-readable message shown when that particular check fails. Keyed by
# name instead of position, so a worker that skips a step (e.g. never got a
# PCB serial) can't shift anyone else's column.
RESULT_COLUMNS = OrderedDict([
    ('Get_Meter_PCB_Serial_No',                     'Fail in Get Meter PCB Serial No'),
    ('PCT_Check',                                   'Fail in PCT Check'),
    ('Phase_Calibration_Started',                   'Fail in Phase Calibration'),
    ('Neutral_Calibration_Started',                 'Fail in Neutral Calibration'),
    ('Overall_Calibration_Status',                  'Fail in Calibration'),
    ('Calibration_Status',                          'Fail in Calib Status'),
])

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
CALIB_FOLDER = os.path.join(LOGS_FOLDER, "CALIB")

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

def ensure_logs_folder():
    """Create the Logs folder if it doesn't exist yet. Safe to call every
    time a workbook path is needed - os.makedirs(..., exist_ok=True) is a
    no-op if the folder is already there. Mirrors mct_multiport.py's
    ensure_logs_folder()."""
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    os.makedirs(CALIB_FOLDER, exist_ok=True)

def get_log_book_path(meter_type, project_name, tool_name):
    """Build the full path to this run's log workbook inside the Logs
    folder, the same way mct_multiport.py's get_log_book_path() does -
    one helper means the folder/name convention can't drift between the
    phase worker, the neutral worker, and run_calibration_test()."""
    ensure_logs_folder()
    return os.path.join(
        CALIB_FOLDER,
        f"{meter_type.title()}_{project_name.upper()}_{tool_name.upper()}_CALIB_LOG.xlsx",
    )

def _worker_context(data_dict):
    """Names every worker / skip entry derives from data_dict the same way,
    so the log path can never differ between them."""
    toolName = data_dict.get("TOOL_TYPE", "IMG").lower()
    meter_type = data_dict.get("METER_TYPE", "LTCT").lower()
    project_name = data_dict.get("PROJECT", 'up').lower()
    bookName = get_log_book_path(meter_type, project_name, toolName)
    fileName = toolName.upper() + "_DATA_LOG"
    return toolName, bookName, fileName

def close_excel_file(filepath):
    logging.info(f"Attempting to close Excel file: {filepath}")
    pythoncom.CoInitialize()
    filepath = os.path.abspath(filepath)
    try:
        excel = win32com.client.GetObject(Class="Excel.Application")
    except Exception:
        return  # Excel not open

    for wb in excel.Workbooks:
        if wb.FullName.lower() == filepath.lower():
            logging.info(f"Closing Excel file: {filepath}")
            wb.Close(SaveChanges=False)
            excel.Quit()
            time.sleep(1)
            return True
    return False

def get_header_column_map(sheet):
    """Read the header row (row 1) into {header_name: column_index}, so a
    row is written by header name instead of by position (same as
    mct_multiport.py)."""
    header_map = {}
    for col_idx, cell in enumerate(sheet[1], start=1):
        if cell.value is not None:
            header_map[cell.value] = col_idx
    return header_map

def add_log_xlsc(log_entry, calib_type):
    """Append one data row to the excel log.

    log_entry is a dict: {'mac', 'MeterInfo', 'result', 'bookName', 'fileName'}.
    Every value is written to the column matching its own header name; any
    column the entry has no value for is filled with MISSING_VALUE, and a
    column missing from the sheet (e.g. a log first created with another
    calib type) is appended instead of shifting anything.
    """
    bookName = log_entry['bookName']
    fileName = log_entry['fileName']
    meter_info = log_entry['MeterInfo']
    result = log_entry['result']

    wb = openpyxl.load_workbook(bookName)
    sheet = wb[fileName]

    numRows = sheet.max_row + 1
    header_map = get_header_column_map(sheet)

    def write(header_name, value):
        col_idx = header_map.get(header_name)
        if col_idx is None:
            col_idx = sheet.max_column + 1
            sheet.cell(row=1, column=col_idx).value = header_name
            header_map[header_name] = col_idx
        sheet.cell(row=numRows, column=col_idx).value = value

    write('MAC_ADDR', log_entry['mac'])
    write('Index', numRows - 1)
    for col_name in get_meter_info_columns(calib_type):
        write(col_name, meter_info.get(col_name, MISSING_VALUE))
    for col_name in RESULT_COLUMNS:
        write(col_name, result.get(col_name, MISSING_VALUE))

    wb.save(bookName)
    logging.info("Log entry added")

def verify_log_xlsc(bookName, fileName):
    loc = bookName
    try:
        wb = openpyxl.load_workbook(loc)
        sheet = wb.active
        _ = sheet.cell(row=1, column=1).value
    except Exception as e:
        logging.error(f"LOG XL file not found, creating one for you find error: {e}")
        wb = openpyxl.Workbook()
        wb.create_sheet(index=0, title=fileName)
        sheet = wb.active
        logging.error(f"sheet name = {sheet.title}")
        del wb['Sheet']
        wb.save(loc)
        logging.error("New xlsc file created")
        return False
    else:
        return True

def addDefaultCalibLog(bookName, fileName, calib_type="single_point"):
    """Create the log workbook (if missing) and write its header row. The
    header comes from get_meter_info_columns(calib_type) + RESULT_COLUMNS,
    so it always matches what the workers write."""
    if not verify_log_xlsc(bookName, fileName):
        logging.info("xlsx file for log not found. creating one to store test report")
        wb = openpyxl.load_workbook(bookName)
        sheet = wb[fileName]
        headers = ['MAC_ADDR', 'Index'] + get_meter_info_columns(calib_type) + list(RESULT_COLUMNS)
        for col_idx, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=col_idx).value = header
        wb.save(bookName)
        logging.info("New xlsx file created with headers")

def result_log_dump(mac, meter_info, result, bookName, fileName):
    """Bundle one worker's findings into the dict shape add_log_xlsc expects."""
    return {
        'mac': mac,
        'MeterInfo': meter_info,
        'result': result,
        'bookName': bookName,
        'fileName': fileName,
    }

class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def _get_pcb_serial(cases, com_port, meter_info, result):
    """Shared 'fetch PCB serial number' step used by every worker function.
    Autofills meter_info['Meter_PCB_Serial_No'] even on failure/exception."""
    retryCnt = 3
    Pcb_serial_no = None
    while retryCnt:
        try:
            logging.debug(f"Getting PCB serial number from COM port: {com_port}, Attempt: {4 - retryCnt}")
            Pcb_serial_no = cases.Get_pcb_serial_num(com_port)
            logging.debug(f"PCB serial number from COM port: {com_port}, Serial Number: {Pcb_serial_no}")
            retryCnt = 0
        except Exception as e:
            logging.error(f"Error while getting PCB serial number from COM port: {com_port}, "
                           f"Attempt: {4 - retryCnt}, Error: {str(e)}")
            retryCnt -= 1

    if Pcb_serial_no:
        meter_info['Meter_PCB_Serial_No'] = str(Pcb_serial_no)
        result['Get_Meter_PCB_Serial_No'] = 'pass'
    else:
        meter_info['Meter_PCB_Serial_No'] = MISSING_VALUE
        result['Get_Meter_PCB_Serial_No'] = 'fail'
    return Pcb_serial_no

def _check_com_port_live(cases, com_port, result_queue, abort_flag, ser):
    """Returns False (and closes ser / signals abort) if the port is dead."""
    retryCnt = 3
    while retryCnt:
        try:
            logging.debug(f"Checking COM port: {com_port}, Attempt: {4 - retryCnt}")
            check_port = cases.check_port(com_port)
            if str(check_port).lower() == 'fail':
                result_queue.append(["Meter is unreachable: {}".format(com_port)])
                abort_flag.set()
                logging.debug(f"COM port is unreachable: {com_port}")
                ser.close()
                return False
            return True
        except Exception as e:
            logging.error(f"Error while checking COM port: {com_port}, Attempt: {4 - retryCnt}, Error: {str(e)}")
            retryCnt -= 1
    return True

def _start_calibration(start_fn, label, com_port):
    """Run one 'start calibration' command with up to 3 attempts. Returns
    'pass' / 'fail'."""
    retryCnt = 3
    status = {}
    while retryCnt:
        try:
            logging.debug(f"Starting {label} on COM port: {com_port}, Attempt: {4 - retryCnt}")
            status = start_fn(com_port) or {}
            logging.debug(f"{label} result on COM port: {com_port}, Result: {status}")
            if str(status.get('status')).lower() == 'pass':
                retryCnt = 0
            else:
                retryCnt -= 1
        except Exception as e:
            logging.error(f"Error while starting {label} on COM port: {com_port}, "
                           f"Attempt: {4 - retryCnt}, Error: {str(e)}")
            retryCnt -= 1
    return 'pass' if str(status.get('status')).lower() == 'pass' else 'fail'

def _autofill_calib_fields(meter_info, calib_type):
    """Fill every coefficient with MISSING_VALUE (but always with min/max so
    the excel columns stay aligned) when a reading couldn't be captured."""
    meter_info['CalibStatus'] = MISSING_VALUE
    for field, (fmin, fmax) in get_calib_fields(calib_type).items():
        meter_info[f'{field}_min'] = str(fmin)
        meter_info[f'{field}_max'] = str(fmax)
        meter_info[field] = MISSING_VALUE

def _coefficients_in_range(calib_type, calib_cofficient, meter_info):
    """Copy every coefficient (+ its min/max) into meter_info and return
    True if all of them are inside the limits for this calib type:
    single_point -> 0 <= value <= max (inclusive),
    multi_point  -> min < value < max (strict, same as mct_multiport.py)."""
    single_point = is_single_point(calib_type)
    in_range = True
    for field, (fmin, fmax) in get_calib_fields(calib_type).items():
        meter_info[f'{field}_min'] = str(fmin)
        meter_info[f'{field}_max'] = str(fmax)
        value = calib_cofficient.get(field)
        meter_info[field] = str(value) if value is not None else MISSING_VALUE
        if value is None:
            in_range = False
            continue
        num = float(str(value))
        ok = (fmin <= num <= fmax) if single_point else (fmin < num < fmax)
        if not ok:
            in_range = False
    return in_range

def _make_skip_entry(data_dict, com_port, result_key, port_to_serial):
    """Build a "this port already failed PCT, so this step wasn't run"
    default-fail log entry. No serial hardware is touched here -- this is
    called from run_calibration_test for ports it never even spawned a
    worker thread for, using the PCB serial the phase worker already
    read (or MISSING_VALUE if that read failed too)."""
    logging.info(f"Skipping calibration for COM port: {com_port} due to previous PCT failure.")
    toolName, bookName, fileName = _worker_context(data_dict)
    mac = get_system_mac_address(toolName)
    meter_info = {
        'Date_time': datetime.datetime.now(),
        'COM_Port': com_port,
        'Meter_PCB_Serial_No': port_to_serial.get(com_port, MISSING_VALUE),
    }
    result = {result_key: 'fail'}
    return mac, meter_info, result, bookName, fileName

def worker_function(data_dict, com_port, portID, result_queue, abort_flag, result_log):
    """Phase calibration worker (includes the PCT gate)."""
    try:
        ser = serial.Serial(com_port, baudrate=9600, timeout=20)
        if not ser:
            result_queue.append(["com port is unable to open: {}".format(com_port)])
            return 0

        cases = TestCase(ser, portID, data_dict.get("RETRIES", 4), data_dict.get("NIC_PCB_LENGTH", 27))
        toolName, bookName, fileName = _worker_context(data_dict)
        mac = get_system_mac_address(toolName)
        starttime = datetime.datetime.now()
        logging.debug(f"Starting calibration on COM port: {com_port}, StartTime: {starttime}")

        meter_info = {'Date_time': datetime.datetime.now(), 'COM_Port': com_port}
        result = {}
        addDefaultCalibLog(bookName, fileName, get_calib_type(data_dict))

        if not _check_com_port_live(cases, com_port, result_queue, abort_flag, ser):
            return

        pcb_serial_no = _get_pcb_serial(cases, com_port, meter_info, result)

        # --- PCT gate -----------------------------------------------------
        # Only proceed into phase calibration if this PCB already has a
        # passing PCT record on file. A missing PCB serial or a failed/
        # absent PCT record stops this port right here -- no phase
        # calibration is attempted. run_calibration_test() reads this
        # port's PCT_Check result out of result_dict once this phase's
        # threads have all joined, and never spawns a neutral worker
        # thread for a port that failed here.
        pct_ok = False
        if pcb_serial_no:
            try:
                pct_ok = bool(db_connect.fetch_by_pcb_serial(str(pcb_serial_no)))
            except Exception as e:
                logging.error(f"PCT lookup failed for COM port: {com_port}, Serial: {pcb_serial_no}, "
                               f"Error: {str(e)}")
                pct_ok = False

        result['PCT_Check'] = 'pass' if pct_ok else 'fail'

        if not pct_ok:
            logging.error(f"PCT check failed for COM port: {com_port}, Serial: {pcb_serial_no} -- "
                           f"skipping phase calibration and all downstream steps for this port.")
            result['Phase_Calibration_Started'] = 'fail'
            ser.close()

            result_log.append(result_log_dump(mac, meter_info, result, bookName, fileName))
            time.sleep(0.1)

            if pcb_serial_no:
                # Serial was read fine; the meter simply has no passing PCT
                # record. Popup reports only that (excel log is unchanged).
                fail_messages = ["Meter Failed in PCT: {}".format(com_port)]
            else:
                # PCB serial could not be fetched at all -> meter not reachable
                fail_messages = ["Meter is unreachable: {}".format(com_port)]
            if fail_messages:
                result_queue.append(fail_messages)
            return
        # --- end PCT gate ---------------------------------------------------

        result['Phase_Calibration_Started'] = _start_calibration(
            cases.start_phase_calib, "Phase calibration", com_port)

        ser.close()

        result_log.append(result_log_dump(mac, meter_info, result, bookName, fileName))
        time.sleep(0.1)

        fail_messages = [RESULT_COLUMNS[k] + ": {}".format(com_port) for k, v in result.items() if v == 'fail']
        if fail_messages:
            result_queue.append(fail_messages)

        logging.info(f"Worker function completed for COM port: {com_port}, StartTime: {starttime}, EndTime: {datetime.datetime.now()}")

    except Exception as e:
        logging.error(f"Error in worker_function for COM port: {com_port}, Error: {str(e)}")
        result_queue.append(["com port is unreachable:{}".format(com_port)])
        return

def worker_function1(data_dict, com_port, portID, result_queue, abort_flag, result_log):
    """Neutral calibration worker: starts neutral calibration, waits, then
    reads back and range-checks every coefficient for the configured
    CALIB_TYPE (single_point / multi_point)."""
    try:
        ser = serial.Serial(com_port, baudrate=9600, timeout=20)
        if not ser:
            result_queue.append(["com port is unable to open: {}".format(com_port)])
            return 0

        cases = TestCase(ser, portID, data_dict.get("RETRIES", 4), data_dict.get("NIC_PCB_LENGTH", 27))
        toolName, bookName, fileName = _worker_context(data_dict)
        calib_type = get_calib_type(data_dict)
        mac = get_system_mac_address(toolName)
        starttime = datetime.datetime.now()
        logging.debug(f"Starting neutral calibration on COM port: {com_port}, StartTime: {starttime}")

        meter_info = {'Date_time': datetime.datetime.now(), 'COM_Port': com_port}
        result = {}
        addDefaultCalibLog(bookName, fileName, calib_type)

        if not _check_com_port_live(cases, com_port, result_queue, abort_flag, ser):
            return

        _get_pcb_serial(cases, com_port, meter_info, result)

        result['Neutral_Calibration_Started'] = _start_calibration(
            cases.start_nuetral_calib, "3P Neutral calibration", com_port)

        wait_time = data_dict.get("Neutral_after_bench_stab_time", 40)
        logging.info(f"Waiting {wait_time} sec for Neutral calibration completion, COM port: {com_port}")
        time.sleep(wait_time)

        retryCnt = 3
        while retryCnt:
            try:
                logging.debug(f"Getting 3P calib coefficients ({calib_type}), attempt: {4 - retryCnt}, for com: {com_port}")
                calib_cofficient = cases.get_3p_calib_coffi(com_port, calib_type)
                if not calib_cofficient or 'Fail' in calib_cofficient:
                    _autofill_calib_fields(meter_info, calib_type)
                    result['Overall_Calibration_Status'] = 'fail'
                    result['Calibration_Status'] = 'fail'
                else:
                    meter_info['CalibStatus'] = str(calib_cofficient.get('CalibStatus'))
                    in_range = _coefficients_in_range(calib_type, calib_cofficient, meter_info)
                    result['Overall_Calibration_Status'] = 'pass' if in_range else 'fail'
                    result['Calibration_Status'] = (
                        'pass' if str(calib_cofficient.get('CalibStatus')) == str(CALIB_STATUS_OK) else 'fail'
                    )
                logging.debug(f"3P calib coefficients from COM port: {com_port}, Coefficients: {calib_cofficient}")
                retryCnt = 0
            except Exception as e:
                logging.error(f"Error in get calib coefficient for COM: {com_port}, error: {str(e)}")
                retryCnt -= 1
                if retryCnt == 0:
                    # Reading never came through at all -- autofill rather
                    # than reference calib_cofficient, which may not even
                    # be assigned yet on this path.
                    _autofill_calib_fields(meter_info, calib_type)
                    result['Overall_Calibration_Status'] = 'fail'
                    result['Calibration_Status'] = 'fail'

        ser.close()

        result_log.append(result_log_dump(mac, meter_info, result, bookName, fileName))
        time.sleep(0.1)

        fail_messages = [RESULT_COLUMNS[k] + ": {}".format(com_port) for k, v in result.items() if v == 'fail']
        if fail_messages:
            result_queue.append(fail_messages)

        logging.debug(f"Neutral calibration completed for COM port: {com_port}, "
                      f"StartTime: {starttime}, EndTime: {datetime.datetime.now()}")

    except Exception as e:
        logging.error(f"Error in Neutral calibration for port: {com_port}, Error: {e}")
        result_queue.append(["com port is unreachable:{}".format(com_port)])
        return


def upload_to_aws(local_folder, bucket, s3_file, sub_folder, file_time, folder_name1, upload_bench,
                  local_file_path=None):
    if local_file_path is None:
        local_file_path = s3_file
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(
            local_file_path, bucket,
            FOLDER_NAME + "/{0}/{1}/{2}/{3}".format(
                folder_name1, sub_folder, local_folder,
                str(upload_bench + "_" + file_time + "_" + s3_file)
            )
        )
        logging.info("Upload Successful")
        os.remove(local_file_path)
        return True
    except NoCredentialsError:
        logging.error("Credentials not available")
        return False
    except Exception as e:
        logging.error(f"S3 upload failed for {local_file_path}: {e}")
        return False

def upload_logs_to_s3(upload_bench):
    """Push every local .xlsx log in the CALIB log folder to S3. Called
    unconditionally -- once the excel row has been written, the log gets
    uploaded whether the DB upload succeeded, failed, or the run had test
    failures in it."""
    ensure_logs_folder()
    txt = [f for f in os.listdir(CALIB_FOLDER) if f.endswith('.xlsx')]
    logging.info(f"Log files to upload: {txt}")
    if len(txt) == 0:
        logging.info("file doesn't exist")
        return

    for j in range(len(txt)):
        time_only1 = datetime.datetime.now()
        date_only = datetime.datetime.strftime(time_only1, '%Y-%m-%d')
        time_only = datetime.datetime.strftime(time_only1, '%H_%M_%S')

        xyx = str(txt[j])
        if "PCT" in xyx:
            sub_folder = "PCT"
        elif "calib" in xyx.lower():
            sub_folder = "CALIBRATION"

        else:
            logging.info("improper file name given for tool type")
            continue

        if "SM_1P" in xyx:
            folder_name1 = "ISM_1P"
        elif "SM_3P" in xyx:
            folder_name1 = "ISM_3P"
        elif "AP_3P" in xyx:
            folder_name1 = "CAP_3P"
        elif "CU_" in xyx:
            folder_name1 = "DCU_"
        elif "rud" in xyx.lower():
            folder_name1 = "Garud"
        elif "better" in xyx.lower():
            folder_name1 = "Better_Meter"
        elif "ltct" in xyx.lower():
            folder_name1 = "3PLTCT"
        elif "wc" in xyx.lower():
            folder_name1 = "3PWC"
        else:
            logging.info("improper file name given for Meter type")
            continue

        local_path = os.path.join(CALIB_FOLDER, txt[j])
        logging.info("Uploading file: {} to bucket: {} in folder: {}/{}/{}".format(
            str(txt[j]), BUCKET_NAME, FOLDER_NAME, folder_name1, date_only))

        upload_to_aws(str(date_only), BUCKET_NAME, txt[j], sub_folder, time_only, folder_name1, upload_bench,
                      local_file_path=local_path)

def run_calibration_test(data_dict, active_port_list, upload_bench):
    """Phase calibration (50 Hz, with PCT gate) -> switch bench -> Neutral
    calibration + coefficient check. Returns
    {com_port: {'phase': 'pass'/'fail', 'neutral': 'pass'/'fail'}}."""
    # upload_logs_to_s3(upload_bench)
    list_port = list(active_port_list)
    portID = data_dict.get("portID", 4)

    results = []
    results1 = []
    result_dict = []
    result_dict1 = []
    abort_flag = threading.Event()

    toolName, bookName, fileName = _worker_context(data_dict)
    calib_type = get_calib_type(data_dict)
    addDefaultCalibLog(bookName, fileName, calib_type)
    if 'wc' in toolName.lower():
        bench_low_pow = 7196.4
        bench_high_pow = 7203.6
    else:
        bench_low_pow = 3598.2
        bench_high_pow = 3601.8

    def _ask_float(prompt_text):
        while True:
            val = input(prompt_text)
            try:
                return val, float(val)
            except ValueError:
                logging.warning(f"Not a valid number: {val!r}")

    # def prompt_bench_power(low, high):
    #     while True:
    #         val, num = _ask_float("Enter the Active Power of Bench at 50 Hz(In Watt) : ")
    #         logging.info(f"User entered bench active power of Bench at 50 Hz(In Watt) : {val} W")
    #         if low <= num <= high:
    #             return
    #         logging.warning(f"Not Proper Active Power Given to Calibrate the Meter. It should be in range {low} W to {high} W, User entered: {val} W")

    def prompt_bench_power(prompt_text, title="Bench Power", min_value=7196.4, max_value=7203.6):
        """Popup-based replacement for the original input()-based bench power
        prompt (`float(input("Enter Bench Power..."))`). Loops until a valid
        numeric value within [min_value, max_value] is entered via a real
        dialog instead of blocking on stdin - necessary because
        run_calibration_test() runs on a background QThread with no attached
        console, where input() would hang forever with no visible prompt at all.

        Uses _dialog_bridge, which shows the dialog on the main Qt thread and
        blocks this (worker) thread until it's answered - see
        _MainThreadDialogBridge's docstring for why that replaced the previous
        easygui/Tkinter-based version."""
        while True:
            raw_value = _dialog_bridge.enterbox(
                msg=f"{prompt_text}\n\nValid range: {min_value} - {max_value}",
                title=title,
            )
            if raw_value is None:
                # Cancel/closed the dialog - re-prompt rather than silently
                # proceeding with no value, matching the original loop's
                # "never exits without a valid entry" behavior.
                _dialog_bridge.msgbox("A bench power value is required to continue.", title)
                continue
            try:
                value = float(raw_value)
            except ValueError:
                _dialog_bridge.msgbox(f"'{raw_value}' is not a valid number. Please try again.", title)
                continue

            logging.info(f"Input for {title}: {value}")
            if min_value <= value <= max_value:
                return value

            _dialog_bridge.msgbox(
                f"{value} is out of range. Please enter a value between {min_value} and {max_value}.",
                title,
            )


    def prompt_bench_frequency(prompt_text, title="Bench Frequency", min_value=49.97, max_value=50.02):
            """Popup-based replacement for the original input()-based bench frequency
            prompt (`float(input("Enter Bench Frequency..."))`). Loops until a valid
            numeric value within [min_value, max_value] is entered via a real
            dialog instead of blocking on stdin - necessary because
            run_calibration_test() runs on a background QThread with no attached
            console, where input() would hang forever with no visible prompt at all.
    
            Uses _dialog_bridge, which shows the dialog on the main Qt thread and
            blocks this (worker) thread until it's answered - see
            _MainThreadDialogBridge's docstring for why that replaced the previous
            easygui/Tkinter-based version."""
            while True:
                raw_value = _dialog_bridge.enterbox(
                    msg=f"{prompt_text}\n\nValid range: {min_value} - {max_value}",
                    title=title,
                )
                if raw_value is None:
                    # Cancel/closed the dialog - re-prompt rather than silently
                    # proceeding with no value, matching the original loop's
                    # "never exits without a valid entry" behavior.
                    _dialog_bridge.msgbox("A bench frequency value is required to continue.", title)
                    continue
                try:
                    value = float(raw_value)
                except ValueError:
                    _dialog_bridge.msgbox(f"'{raw_value}' is not a valid number. Please try again.", title)
                    continue
    
                logging.info(f"Input for {title}: {value}")
                if min_value <= value <= max_value:
                    return value
    
                _dialog_bridge.msgbox(
                    f"{value} is out of range. Please enter a value between {min_value} and {max_value}.",
                    title,
                )
    

    # ---- Phase calibration at 50 Hz (includes the PCT gate) ----
    # prompt_bench_power(bench_low_pow, bench_high_pow)
    phase_power = prompt_bench_power("Enter Bench Power for Phase Calibration", title="Phase Calibration Bench Power", min_value = bench_low_pow, max_value = bench_high_pow)
    phase_frequency = prompt_bench_frequency("Enter Bench Frequency for Phase Calibration (49.97 Hz to 50.02 Hz)", title="Phase Calibration Bench Frequency", min_value = 49.97, max_value = 50.02)
    # prompt_bench_frequency(49.97, 50.02, "49.97 Hz to 50.02 Hz")
    logging.info(f"Enter Bench Power for Phase Calibration: {phase_power}")
    logging.info(f"Enter Bench Frequency for Phase Calibration (49.97 Hz to 50.02 Hz): {phase_frequency}")
    logging.info(f"Starting CALIBRATION Testing on ports: {list_port}")

    wait = data_dict.get("Phase_before_bench_stab_time", 30)
    logging.info(f"Waiting {wait} sec for Bench Stablization before phase calibration...")
    time.sleep(wait)
    threads = [StoppableThread(target=worker_function,
                                args=(data_dict, port_name, portID, results, abort_flag, result_dict))
               for port_name in list_port]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    wait = data_dict.get("Phase_after_bench_stab_time", 40)
    logging.info(f"Waiting {wait} sec for Bench Stablization after phase calibration...")
    time.sleep(wait)

    # -----------------------------------------------------------------
    # PCT gate: decide, from the now-finished phase results, which ports
    # actually get a neutral worker thread at all. This reads result_dict
    # only after every phase thread has joined, so there's no
    # concurrent-write race to guard with a lock.
    # -----------------------------------------------------------------
    phase1_by_port = {entry['MeterInfo'].get('COM_Port'): entry for entry in result_dict}
    pct_failed_ports = [
        port_name for port_name in list_port
        if phase1_by_port.get(port_name, {}).get('result', {}).get('PCT_Check') != 'pass'
    ]
    if pct_failed_ports:
        logging.info(f"Skipping Neutral Calibration for PCT-failed ports: {pct_failed_ports}")
    next_port_list = [port_name for port_name in list_port if port_name not in pct_failed_ports]

    port_to_failed_serial = {
        port_name: phase1_by_port.get(port_name, {}).get('MeterInfo', {}).get('Meter_PCB_Serial_No', MISSING_VALUE)
        for port_name in pct_failed_ports
    }
    for port_name in pct_failed_ports:
        mac, meter_info, result, sBookName, sFileName = _make_skip_entry(
            data_dict, port_name, 'Neutral_Calibration_Started', port_to_failed_serial)
        result['Overall_Calibration_Status'] = 'fail'
        result['Calibration_Status'] = 'fail'
        _autofill_calib_fields(meter_info, calib_type)
        result_dict1.append(result_log_dump(mac, meter_info, result, sBookName, sFileName))

    # ---- Neutral calibration at 52.5 Hz ----
    # easygui.msgbox("Switch the Bench for Neutral Calibration at 52.5 Hz", "Action Required for Calibration")
    _dialog_bridge.msgbox("Swich the Bench for Neutral Calibration", "Action Required for Calibration")
    logging.info("Switch the Bench for Neutral Calibration at 52.5 Hz, Action Required for Calibration")
    neutral_power = prompt_bench_power("Enter Bench Power for Neutral Calibration", title="Neutral Calibration Bench Power", min_value=bench_low_pow, max_value=bench_high_pow)
    neutral_frequency = prompt_bench_frequency("Enter Bench Frequency for Neutral Calibration (49.97 Hz to 50.02 Hz)", title="Neutral Calibration Bench Frequency", min_value=49.97, max_value=50.02)
    # prompt_bench_frequency(49.97, 50.02, "49.97 Hz to 50.02 Hz")
    logging.info(f"Enter Bench Power for Neutral Calibration: {neutral_power}")
    logging.info(f"Enter Bench Frequency for Neutral Calibration (49.97 Hz to 50.02 Hz): {neutral_frequency}")
    logging.info(f"Starting CALIBRATION Testing on ports: {list_port}")
    wait = data_dict.get("Neutral_before_bench_stab_time", 30)
    logging.info(f"Waiting {wait} sec for Bench Stablization before neutral calibration...")
    time.sleep(wait)
    threads = [StoppableThread(target=worker_function1,
                                args=(data_dict, port_name, portID, results1, abort_flag, result_dict1))
               for port_name in next_port_list]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # -----------------------------------------------------------------
    # Merge both steps into one entry per meter. Prefer the PCB serial
    # number as the merge key; fall back to the COM port when the serial is
    # unknown (e.g. a port that failed before ever reading a serial), so
    # two different unreadable ports don't collapse into the same "N/A" row.
    # -----------------------------------------------------------------
    master = OrderedDict()
    for step_results in (result_dict, result_dict1):
        for entry in step_results:
            serial_no = entry['MeterInfo'].get('Meter_PCB_Serial_No', MISSING_VALUE)
            if serial_no != MISSING_VALUE:
                merge_key = serial_no
            else:
                merge_key = "PORT_{}".format(entry['MeterInfo'].get('COM_Port', id(entry)))
            if merge_key not in master:
                master[merge_key] = {
                    'mac': entry['mac'],
                    'MeterInfo': {},
                    'result': {},
                    'bookName': entry['bookName'],
                    'fileName': entry['fileName'],
                }
            master[merge_key]['MeterInfo'].update(entry['MeterInfo'])
            master[merge_key]['result'].update(entry['result'])

    results.extend(results1)

    for entry in master.values():
        entry['MeterInfo']['Overall_Result'] = 'fail' if 'fail' in entry['result'].values() else 'pass'

    for entry in master.values():
        try:
            close_excel_file(entry['bookName'])
            add_log_xlsc(entry, calib_type)
        except Exception as e:
            logging.error(f"unknown error in add logs in Excel: {e}")
            continue

    # Per-port pass/fail summary for the UI. Every requested port gets an
    # entry; a step that never produced a result counts as 'fail'.
    calib_pass_fail_by_com = {port: {'phase': 'fail', 'neutral': 'fail'} for port in list_port}
    for entry in result_dict:
        port = entry['MeterInfo'].get('COM_Port')
        if port in calib_pass_fail_by_com:
            calib_pass_fail_by_com[port]['phase'] = entry['result'].get('Phase_Calibration_Started', 'fail')
    for entry in result_dict1:
        port = entry['MeterInfo'].get('COM_Port')
        if port in calib_pass_fail_by_com:
            calib_pass_fail_by_com[port]['neutral'] = entry['result'].get('Neutral_Calibration_Started', 'fail')

    db_upload_ok = False
    if data_dict.get("IS_DATA_CONN", 1) == 1:
        try:
            df_frame = pd.read_excel(bookName)
            logging.info(f"\n{df_frame}")
            if 'ltct' in toolName.lower():
                db_upload_ok, error = db_connect.upload_dataframe(df_frame, 'ltct')
            else:
                db_upload_ok, error = db_connect.upload_dataframe(df_frame, 'wc')
            if not db_upload_ok:
                logging.error(f"DB upload failed . Saved locally for retry. Error: {error}")
        except Exception as e:
            logging.error(f"Error writing DB log: {e}")
    else:
        logging.info("IS_DATA_CONN disabled -- skipping DB upload")

    # Upload to S3 regardless of whether the DB upload succeeded and
    # regardless of whether any calibration check failed -- the log itself
    # should always end up in cloud storage.
    if len(master) != 0:
        try:
            upload_logs_to_s3(upload_bench)
        except Exception as e:
            logging.error(f"Error uploading log to S3: {e}")
    else:
        logging.info("Skipping to Upload the log file to server")

    logging.debug(f"Calibration results: {master}")
    if results:
        flat_results = [item for sublist in results for item in sublist]
        unique_results = list(set(flat_results))
        msg_text = "\n".join(unique_results)
        easygui.msgbox(msg_text, "Calibration Tool Failures Detected")

    return calib_pass_fail_by_com
