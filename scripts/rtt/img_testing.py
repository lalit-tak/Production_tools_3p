import sys
import os
from datetime import datetime, date
# import datetime
import re
from multiprocessing import Process, Queue
import openpyxl
import tkinter as tk
from tkinter import scrolledtext
from scripts.rtt import gprs_testing  # your test module
import json
import logging
import io
import time
import win32com.client as win32
import pythoncom
import psutil
from colorama import Fore, Style, init
import pandas as pd
from scripts.rtt import db_connect
import boto3
from botocore.exceptions import NoCredentialsError
init(autoreset=True)
# TIMEOUT_SECONDS = 600  # 10 minutes timeout per test

BUCKET_NAME = "PUT_YOUR_BUCKET_NAME_HERE"
FOLDER_NAME = "PUT_YOUR_FOLDER_NAME_HERE"
ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"


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

def get_log_book_path(excel_file_name):
    ensure_logs_folder()
    return os.path.join(RTT_FOLDER, f"{excel_file_name}")


def close_excel_file(filepath):
    filepath = os.path.abspath(filepath)

    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            if proc.info['name'] and 'EXCEL' in proc.info['name'].upper():
                for f in proc.info['open_files'] or []:
                    if os.path.abspath(f.path).lower() == filepath.lower():
                        print(f"Killing Excel PID {proc.pid}")
                        proc.kill()
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False

# ---------- EXCEL WRITER PROCESS ----------
def excel_writer(queue, EXCEL_FILE_RAW):
    LOCAL_EXCEL_FILE = get_log_book_path("rf_data.xlsx")
    EXCEL_FILE = get_log_book_path(EXCEL_FILE_RAW)
    close_excel_file(EXCEL_FILE)
    close_excel_file(LOCAL_EXCEL_FILE)
    # if os.path.exists(EXCEL_FILE):
    #     wb = openpyxl.load_workbook(EXCEL_FILE)
    #     ws = wb.active
    # else:
    #     wb = openpyxl.Workbook()
    #     ws = wb.active
    #     headers = [
    #         "Serial No", "Date_Time", "PCB Serial No", "NIC PCB Serial No",
    #         "PCB Serial No Test Status", "NIC PCB Serial No Test Status",
    #         "Transparent Mode status", 'RSSI-RX', 'RSSI-TX',"RF Test Status",
    #         "GPRS SIM1 TEST STATUS", "GPRS SIM2 TEST STATUS", "Overall Result"
    #     ]
    #     for col, header in enumerate(headers, start=1):
    #         ws.cell(row=1, column=col, value=header)

    # ---------- MAIN EXCEL ----------
    
    if os.path.exists(EXCEL_FILE):
        print("Using existing main Excel file")
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
    else:
        ensure_logs_folder()
        print("Creating new main Excel file")
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = [
            "Serial No", "Date_Time", "PCB Serial No", "NIC PCB Serial No",
            "PCB Serial No Test Status", "NIC PCB Serial No Test Status",
            "Transparent Mode status", "RF Test Status","RSSI-RX", "RSSI-TX",
            "GPRS SIM1 TEST STATUS", "GPRS SIM2 TEST STATUS", "IMG_VER","Overall Result", 'Calib_Status'
        ]
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)


    # ---------- RF EXCEL ----------
    if os.path.exists(LOCAL_EXCEL_FILE):
        print(F"Using existing {LOCAL_EXCEL_FILE}")
        wb_r = openpyxl.load_workbook(LOCAL_EXCEL_FILE)
        ws_r = wb_r.active
    else:
        print(F"Creating new {LOCAL_EXCEL_FILE}")
        wb_r = openpyxl.Workbook()
        ws_r = wb_r.active

        headers_r = [
            "Serial No", "Date_Time", "PCB Serial No", "NIC PCB Serial No",
            "PCB Serial No Test Status", "NIC PCB Serial No Test Status",
            "Transparent Mode status", "RF Test Status",
            "GPRS SIM1 TEST STATUS", "GPRS SIM2 TEST STATUS", "Overall Result",
            "RSSI-RX", "RSSI-TX", "IMG_VER", 'Calib_Status'
        ]
        for col, header in enumerate(headers_r, start=1):
            ws_r.cell(row=1, column=col, value=header)

    while True:
        data = queue.get()
        if data == "DONE":
            break

        next_row = ws.max_row + 1
        serial_no = next_row - 1

        next_row_r = ws_r.max_row + 1
        serial_no_r = next_row_r - 1

        def sanitize_excel_string(s):
            s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(s))
            return s[:100] if len(s) > 100 else s

        ws.cell(row=next_row, column=1, value=serial_no)
        ws.cell(row=next_row, column=2, value=sanitize_excel_string(data.get("timestamp")))
        ws.cell(row=next_row, column=3, value=sanitize_excel_string(data.get("pcb_serial_no")))
        ws.cell(row=next_row, column=4, value=sanitize_excel_string(data.get("nic_serial_no")))
        ws.cell(row=next_row, column=5, value=sanitize_excel_string(data.get("pcb_serial_test_status")))
        ws.cell(row=next_row, column=6, value=sanitize_excel_string(data.get("nic_serial_test_status")))
        ws.cell(row=next_row, column=7, value=sanitize_excel_string(data.get("debug_status")))
        ws.cell(row=next_row, column=8, value=sanitize_excel_string(data.get("rf_test_status")))
        ws.cell(row=next_row, column=9, value=str(data.get("rssi-rx")))
        ws.cell(row=next_row, column=10, value=str(data.get("rssi-tx")))
        ws.cell(row=next_row, column=11, value=sanitize_excel_string(data.get("sim1_status")))
        ws.cell(row=next_row, column=12, value=sanitize_excel_string(data.get("sim2_status")))
        ws.cell(row=next_row, column=13, value=sanitize_excel_string(data.get("img_ver")))
        ws.cell(row=next_row, column=14, value=sanitize_excel_string(data.get("overall_result")))
        if (data.get('calib_status', False) == True) or (data.get('calib_status', 'fail') == 'pass'):
            ws.cell(row=next_row, column=15, value=sanitize_excel_string('pass'))
        else:
            ws.cell(row=next_row, column=15, value=sanitize_excel_string('fail'))


        ws_r.cell(row=next_row_r, column=1, value=serial_no_r)
        ws_r.cell(row=next_row_r, column=2, value=sanitize_excel_string(data.get("timestamp")))
        ws_r.cell(row=next_row_r, column=3, value=sanitize_excel_string(data.get("pcb_serial_no")))
        ws_r.cell(row=next_row_r, column=4, value=sanitize_excel_string(data.get("nic_serial_no")))
        ws_r.cell(row=next_row_r, column=5, value=sanitize_excel_string(data.get("pcb_serial_test_status")))
        ws_r.cell(row=next_row_r, column=6, value=sanitize_excel_string(data.get("nic_serial_test_status")))
        ws_r.cell(row=next_row_r, column=7, value=sanitize_excel_string(data.get("debug_status")))
        ws_r.cell(row=next_row_r, column=8, value=sanitize_excel_string(data.get("rf_test_status")))
        ws_r.cell(row=next_row_r, column=9, value=sanitize_excel_string(data.get("sim1_status")))
        ws_r.cell(row=next_row_r, column=10, value=sanitize_excel_string(data.get("sim2_status")))
        ws_r.cell(row=next_row_r, column=11, value=sanitize_excel_string(data.get("overall_result")))
        ws_r.cell(row=next_row_r, column=12, value=str(data.get("rssi-rx")))
        ws_r.cell(row=next_row_r, column=13, value=str(data.get("rssi-tx")))
        ws_r.cell(row=next_row_r, column=14, value=str(data.get("img_ver")))
        if (data.get('calib_status', False) == True) or (data.get('calib_status', 'fail') == 'pass'):
            ws_r.cell(row=next_row_r, column=15, value=sanitize_excel_string('pass'))
        else:
            ws_r.cell(row=next_row_r, column=15, value=sanitize_excel_string('fail'))

    wb.save(EXCEL_FILE)
    wb.close()
    wb_r.save(LOCAL_EXCEL_FILE)
    wb_r.close()

# ---------- TEST WORKER PROCESS ----------
def run_test_worker(config, port, excel_queue, popup_queue):
    try:
        result = gprs_testing.run_test(str(port), config)

        if result is None:
            popup_queue.put((str(port), "Meter is unreachable"))
            return

        result["timestamp"] = datetime.now()
        result["port"] = port

        pcb_serial = result.get("pcb_serial_no")
        nic_serial = result.get("nic_serial_no")

        # Only a missing/invalid pcb_serial means the meter itself was
        # never reached (truly "Not Connected"). nic_serial can be blank
        # on its own - e.g. when pcb_serial reads fine but calibration
        # fails, nic_pcb_number() is never called (see gprs_testing.py's
        # tap_cmd_send: nic_pcb_Serial_no stays at its None default when
        # `if calibration_result:` is skipped) - so a blank nic_serial
        # alone must NOT drop this row before it reaches excel_queue.
        if not pcb_serial or pcb_serial == "None":
            popup_queue.put((str(port), "Meter is unreachable"))
            return

        excel_queue.put(result)
        # PCB serial was read, but the meter has no passing Calibration
        # record (RTT was skipped for it): popup reports only that. The
        # excel row queued above is unchanged.
        calib_status = result.get("calib_status")
        if str(result.get("pcb_serial_test_status", "")).lower() != "pass":
            # gprs_testing returned its early-exit placeholder (port could
            # not be opened / PCB serial not fetched) - not a calibration issue.
            popup_queue.put((str(port), "Meter is unreachable"))
        elif not calib_status or str(calib_status).lower() == "fail":
            popup_queue.put((str(port), "Meter Failed in Calibration"))
        else:
            popup_queue.put((str(port), result.get("overall_result", "Check Excel")))

    except Exception as e:
        error_msg = str(e)
        if "port" in error_msg.lower() or "serial" in error_msg.lower():
            popup_queue.put((str(port), "Meter is unreachable"))
            return

        error_result = {
            "port": port,
            "pcb_serial_no": "",
            "pcb_serial_test_status": "",
            "calib_status": False,
            "nic_serial_no": "",
            "nic_serial_test_status": "",
            "debug_status": "",
            "rssi-rx": "",
            "rssi-tx": "",
            "rf_test_status": "",
            "sim1_status": "",
            "sim2_status": "",
            "img_ver": "",
            "overall_result": f"Error: {str(e)}",
            "timestamp": datetime.now()
        }
        excel_queue.put(error_result)
        popup_queue.put((str(port), error_result["overall_result"]))

# ---------- POPUP ----------
def show_results_popup(results_list):
    root = tk.Tk()
    root.title("IMG Testing Summary")

    window_width, window_height = 700, 500
    x = (root.winfo_screenwidth() - window_width) // 2
    y = (root.winfo_screenheight() - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(False, False)

    tk.Label(root, text="IMG Testing Summary", font=("Arial", 20, "bold")).pack(pady=15)
    text_area = scrolledtext.ScrolledText(root, width=80, height=1, font=("Arial", 14), wrap=tk.WORD)
    text_area.pack(side='top', fill='both', expand=True, padx=20, pady=(0, 10))

    for port, result in results_list:
        text_area.insert(tk.END, f"{port} = {result}\n")

    text_area.config(state='disabled')

    button_frame = tk.Frame(root)
    button_frame.pack(side='bottom', fill='x', pady=(0, 20))
    ok_button = tk.Button(button_frame, text="OK", font=("Arial", 16, "bold"),
                          width=20, height=2, command=root.destroy)
    ok_button.pack(pady=0)

    root.mainloop()


def run(config, active_port_list, upload_bench="1"):
    """active_port_list: list of COM port name strings (e.g. ["COM6", "COM7"])
    passed in directly by the GUI, matching every other test script's
    calling convention (run_mct_test, run_calibration_test, run_rtt_test).
    Previously this read ports from editable_list_config["port_list"]
    (expected to be bare device numbers like '4','5','6', not full COM
    names) and pulled upload_bench from that same config dict - both
    replaced with direct parameters here."""
    logging.info(f"RTT Test started for IMG")
    tool_type = config.get('METER_TYPE','Garud_1PH').title()
    EXCEL_FILE = f"{tool_type.title()}_IMG_RTT_TESTING.xlsx"
    close_excel_file(EXCEL_FILE)

    port_list = list(active_port_list)
    if not port_list:
        logging.warning("No active ports provided to IMG RTT run()")
        return {}

    excel_queue = Queue()
    popup_queue = Queue()
    
    writer_process = Process(target=excel_writer, args=(excel_queue, EXCEL_FILE, ))
    writer_process.start()

    processes = []
    thread_delay = config.get("thread_delay", 3)  # default 3 seconds delay between starting threads
    for port in port_list:
        p = Process(target=run_test_worker, args=(config, port, excel_queue, popup_queue))
        p.start()
        processes.append((port, p))
        time.sleep(thread_delay)

    TIMEOUT_SECONDS = config.get("thread_timeout", 300)  # default 60 seconds timeout
    for port, p in processes:
        p.join(timeout=TIMEOUT_SECONDS)
        if p.is_alive():
            print(f"⏱️ Timeout reached for {port}. Terminating...")
            p.terminate()
            p.join()
            popup_queue.put((str(port), "Fail (Timeout)"))

    excel_queue.put("DONE")
    writer_process.join()

    results_for_popup = []
    print(popup_queue)
    while not popup_queue.empty():
        results_for_popup.append(popup_queue.get())

    # --------------------------------------------------------------
    # Dictionary-based pass/fail summary, matching run_rtt_test()'s
    # (rtt_multiport.py) return shape: {com_port: 'pass'/'fail'}.
    # results_for_popup already has one (port, overall_result_string)
    # tuple per port from run_test_worker/the timeout handler above - we
    # just need to classify each string and guarantee every requested
    # port ends up with a definitive entry.
    # --------------------------------------------------------------
    def classify(overall_result_text):
        text = str(overall_result_text).strip().lower()
        # Anything not unambiguously a pass is treated as a fail - same
        # "unclear = fail" safety net used by every other test script,
        # since gprs_testing.run_test()'s exact overall_result wording
        # isn't controlled here (this file doesn't define gprs_testing.py).
        if text == "pass" or text.startswith("pass"):
            return "pass"
        return "fail"

    img_rtt_pass_fail_by_com = {port: classify(result) for port, result in results_for_popup}

    # A process that dies before ever reaching a popup_queue.put(...) call
    # (a hard crash, not a timeout - the timeout path above already covers
    # that case) would otherwise leave its port missing entirely. Same
    # safety net pattern as fill_missing_fields() in the other scripts:
    # a port that never produced a real result is reported as a definite
    # fail, never silently absent.
    for port in port_list:
        img_rtt_pass_fail_by_com.setdefault(port, "fail")


    if config.get("IS_DATA_CONN", 1) == 1:
        toolName = config.get('TOOL_TYPE', 'img_rtt').lower()
        meter_type = config.get('METER_TYPE', 'garud').lower()
        local_excel_path = os.path.join(RTT_FOLDER, EXCEL_FILE)
        df_frame = pd.read_excel(local_excel_path)
        # print(df_frame,'------------')
        try:
            status = False
            error = ""
            # if '4g' in toolName.lower():
            #     status, error = db_connect.upload_dataframe_4g(df_frame, meter_type.lower(), toolName)
            # else:
            status, error = db_connect.upload_dataframe_img(df_frame, meter_type.lower(), toolName)
            if not status:
                logging.info(f"DB upload failed . Saved locally for retry. Error: {error}")
            else:

                def upload_to_aws(local_folder, bucket, s3_file,sub_folder, file_time,folder_name1, upload_bench, local_file_path=None):
                    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                    aws_secret_access_key=SECRET_KEY)
                    logging.info(f"Uploaded file: {str(upload_bench + "_" + file_time + "_" + s3_file)}")
                
                    try:
                        if local_file_path is None:
                            local_file_path = s3_file
                        s3.upload_file(local_file_path, bucket, FOLDER_NAME +  "/{0}/{1}/{2}/{3}".format(folder_name1,sub_folder,local_folder, str(upload_bench + "_" + file_time + "_" + s3_file)))
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
                logging.info(f"txt is: {txt}")
                if len(txt) == 0:
                    logging.info("file doesn't exist")#/dev/gp-gateway"
                    return

                for j in range(len(txt)):    
                    today = date.today()
                    logging.info(f"Today date is: {today}")

                    system_time = datetime.now()
                    logging.info(f"time = {system_time}")
                    date_only = datetime.strftime(system_time, '%Y-%m-%d')
                    time_only = datetime.strftime(system_time, '%H:%M:%S')
                    sub_folder = "UNKNOWN"
                    xyx =  str(txt[j])

                    if("PCT2" in xyx):
                        sub_folder = "PCT2"
                    elif("FTT" in xyx):
                        sub_folder = "FTT"
                    elif("MCT" in xyx):
                        sub_folder = "MCT"
                    elif("img" in xyx.lower()):
                        sub_folder = "RTT_IMG"    
                    elif("PCT" in xyx):
                        sub_folder = "PCT"
                    else:
                        logging.info("improper file name given for tool type")
                        continue
                    logging.info(f"sub_folder = {sub_folder}")

                    folder_name1 = "UNKNOWN"
                    if("SM_1P" in xyx):
                        folder_name1 = "ISM_1P"
                    elif("SM_3P" in xyx):
                        folder_name1 = "ISM_3P"
                    elif("AP_3P" in xyx):
                        folder_name1 = "CAP_3P"
                    elif("CU_" in xyx):
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
                    local_path = os.path.join(RTT_FOLDER, txt[j])
                    uploaded = upload_to_aws(str(date_only), BUCKET_NAME, txt[j],sub_folder, time_only,folder_name1, upload_bench, local_file_path = local_path )
        except Exception as e:
            logging.error(f"Error in store data into DB and send data to s3: {str(e)}")
    else:
        logging.info("Upload data to EMS db flag is disable")

        
        def upload_to_aws(local_folder, bucket, s3_file,sub_folder, file_time,folder_name1, upload_bench, local_file_path=None):
            s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
            logging.info(f"Uploaded file: {str(upload_bench + "_" + file_time + "_" + s3_file)}")
        
            try:
                if local_file_path is None:
                    local_file_path = s3_file
                s3.upload_file(local_file_path, bucket, FOLDER_NAME +  "/{0}/{1}/{2}/{3}".format(folder_name1,sub_folder,local_folder, str(upload_bench + "_" + file_time + "_" + s3_file)))
                logging.info("Upload Successful")
                os.remove(local_file_path)
                return True
            except NoCredentialsError:
                logging.error(f"Credentials not available")
                return False
            except Exception as e:
                logging.error(f"{str(e)}")
                logging.error("The file was not found")
                return False

        
        al = os.listdir(RTT_FOLDER)
        txt = list(filter(lambda x: x[-5:] == '.xlsx',al))
        logging.info(f"txt is : {txt}")
        if len(txt) == 0:
            logging.info("file doesn't exist")#/dev/gp-gateway"
            return

        for j in range(len(txt)):    
            today = date.today()
            logging.info(f"Today date is: {today}")

            system_time = datetime.now()
            logging.info(f"time = {system_time}")
            date_only = datetime.strftime(system_time, '%Y-%m-%d')
            time_only = datetime.strftime(system_time, '%H:%M:%S')
            sub_folder = "UNKNOWN"
            xyx =  str(txt[j])

            if("PCT2" in xyx):
                sub_folder = "PCT2"
            elif("FTT" in xyx):
                sub_folder = "FTT"
            elif("MCT" in xyx):
                sub_folder = "MCT"
            elif("img" in xyx.lower()):
                sub_folder = "RTT_IMG"    
            elif("pct" in xyx.lower()):
                sub_folder = "PCT"
            else:
                logging.info("improper file name given for tool type")
                continue
            logging.info(f"sub_folder = {sub_folder}")

            folder_name1 = "UNKNOWN"
            if("SM_1P" in xyx):
                folder_name1 = "ISM_1P"
            elif("SM_3P" in xyx):
                folder_name1 = "ISM_3P"
            elif("AP_3P" in xyx):
                folder_name1 = "CAP_3P"
            elif("CU_" in xyx):
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
            local_path = os.path.join(RTT_FOLDER, txt[j])
            uploaded = upload_to_aws(str(date_only), BUCKET_NAME, txt[j],sub_folder, time_only,folder_name1, upload_bench, local_file_path =  local_path)
            
    #*******************************************************************************************************************************************************

    # print("✅ All tests completed. Showing summary popup...")
    show_results_popup(results_for_popup)
    logging.info(f"Failed and passed port in rtt: {results_for_popup}")
    logging.info(f"IMG RTT Testing Completed with results: {img_rtt_pass_fail_by_com}")
    return img_rtt_pass_fail_by_com


# ---------- MAIN ENTRY ----------
def run_rtt_img_test(data_dict, active_port_list, upload_bench="1"):
    """Entry point called by MainWindow (via FunctionThreadRunner, exactly
    the way run_mct_test()/run_calibration_test()/run_rtt_test() are
    called) as:

        results = rtt_img(data_dict, ports, bench_number)

    Returns {com_port: 'pass'/'fail'} - the same shape run_rtt_test()
    (rtt_multiport.py) returns, so this plugs into the GUI's "rtt_test"
    handling identically regardless of whether the RF or IMG script ran.

    CAVEAT: show_results_popup() (called inside run()) opens a real
    Tkinter window with its own mainloop(). Tkinter is only officially
    supported on the main thread - showing it from the background thread
    FunctionThreadRunner uses is expected to work on Windows in practice
    but isn't guaranteed elsewhere, same accepted tradeoff already
    documented for the easygui dialogs in the other test scripts."""
    logging.info("....................IMG(3.2.7) RF-GPRS Testing Tool ................")
    return run(data_dict, active_port_list, upload_bench)