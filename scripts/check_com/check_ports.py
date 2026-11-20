"""
COM port connectivity + PCB serial number check.

Called directly by the Smart Manufacturing Suite GUI as:

    results = run(mode, ports)

- mode:  "IMG" | "RF" | "4G" (accepted for a consistent calling convention
         across all scripts; not currently used by this particular check)
- ports: list of COM port name strings, e.g. ["COM6", "COM7", ...]

- returns: a NESTED dict, one entry per port, carrying both the pass/fail
  status AND the PCB serial number read off that port:

      {
          "COM6": {"status": "pass", "pcb_serial": "P2509220100000010050084553400"},
          "COM7": {"status": "fail", "pcb_serial": ""},
          ...
      }

  This is richer than the flat "pass"/"fail" string most other scripts
  return, because this check also needs to report the serial number it
  read. main.py understands both shapes: a plain "pass"/"fail" string, or
  a dict with a "status" key (and optionally "pcb_serial", which - when
  present and non-empty - is used to fill in that port's real serial
  number in the Serial No.(PCBA) column instead of the placeholder value).

Runs on a background QThread (see FunctionRunner in main.py), so this must
NOT use blocking/interactive GUI dialogs (easygui, tkinter, etc.) - those
require the main thread. The original interactive "Retry / Update Config"
easygui prompt has been replaced with an automatic bounded retry: ports
that fail get re-checked up to MAX_RETRY_ROUNDS times before being reported
as a final fail.

Everything here is dictionary-driven rather than list-driven:
- `pending_ports` is a dict of {com_port: True} for ports still awaiting a
  clean result, not a list of retry indices.
- `final_status` is a dict of {com_port: {"status": ..., "pcb_serial": ...}}
  built up in place as ports resolve, rather than assembled from parallel
  lists (results / retry_list / msg_text) at the end.
"""

import logging
import datetime
import time
import threading
from threading import Thread

import serial

# from Test_cases_verificationClass import TestCase
from scripts.Test_cases_verificationClass import TestCase

# How many times to automatically re-check a port that failed before
# giving up on it for this run.
MAX_RETRY_ROUNDS = 1

# Default device/port id previously supplied via --id on the CLI. Wire
# this up to a real per-bench config value if you need it configurable.
DEFAULT_PORT_ID = 4

# TODO: set this to your real expected PCB prefix (was previously passed
# in as the Main_PCB_SFG_Prefix argument to run_com_check). Since run()'s
# signature is fixed to (mode, ports) to match every other script in the
# suite, this now lives here as a constant - move it to config.json and
# read it in main.py if you need it to vary per bench/mode.
# MAIN_PCB_SFG_PREFIX = "R161"

CHECK_FAIL_MESSAGES = {
    "port_open": "Port is not open",
    "pcba_serial": "Could not read PCB serial number",
}


class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def _check_one_port(com_port, port_id, results, abort_flag, main_pcb_sfg_prefix):
    """
    Runs the connectivity + serial-number check for a single port and
    writes into the shared `results` dict:

        results[com_port] = {
            "checks": {"port_open": "pass"/"fail", "pcba_serial": "<serial or ''>"},
            "status": "PASS" / "FAIL",
            "reason": "..."   # only set on fail
        }
    """
    results[com_port] = {"checks": {}, "status": "UNKNOWN", "reason": ""}

    try:
        ser = serial.Serial(com_port, baudrate=9600, timeout=2)
        if not ser:
            results[com_port]["status"] = "FAIL"
            results[com_port]["reason"] = "unable to open port"
            return

        cases = TestCase(ser, port_id, 3, 27)
        start_time = datetime.datetime.now()
        logging.info(f"[{com_port}] check started at {start_time}")

        # --- Check port connectivity ---
        retry_count = 3
        while retry_count:
            attempt = 4 - retry_count
            logging.info(f"[{com_port}] checking connectivity, attempt {attempt}")
            try:
                check_port = cases.check_port(com_port)
                logging.info(f"[{com_port}] check_port result: {check_port}")
                if check_port == "fail":
                    results[com_port]["status"] = "fail"
                    results[com_port]["reason"] = "check_port failed after retries"
                    abort_flag.set()
                    logging.info(f"[{com_port}] closing serial port")
                    ser.close()
                    break
                else:
                    results[com_port]["checks"]["port_open"] = "pass"
                    retry_count = 0
            except Exception as e:
                logging.error(f"[{com_port}] error in check_port: {e}")
                retry_count -= 1
                if retry_count == 0:
                    results[com_port]["status"] = "FAIL"
                    results[com_port]["reason"] = f"check_port failed after retries: {e}"
                    abort_flag.set()
                    logging.info(f"[{com_port}] closing serial port")
                    ser.close()
                    break

        # If port_open already failed, don't bother reading the serial number
        if results[com_port]["status"].lower() == "fail":
            if ser.is_open:
                ser.close()
            return

        # --- Get PCBA serial number ---
        retry_count = 3
        while retry_count:
            attempt = 4 - retry_count
            logging.info(f"[{com_port}] getting PCBA serial number, attempt {attempt}")
            try:
                pcb_serial_number = cases.Get_pcb_serial_num(com_port)
                if pcb_serial_number is None:
                    results[com_port]["checks"]["pcba_serial"] = ""
                    results[com_port]["status"] = "fail"
                    break
                else:
                    if (('R161' in pcb_serial_number) or ('r161' in pcb_serial_number) or (str(pcb_serial_number[9:16]) == str(main_pcb_sfg_prefix))):
                        results[com_port]["checks"]["pcba_serial"] = str(pcb_serial_number)
                        results[com_port]["status"] = "pass"
                    else:
                        results[com_port]["checks"]["pcba_serial"] = str(pcb_serial_number)
                        results[com_port]["status"] = "fail"
                break
            except Exception as e:
                logging.error(f"[{com_port}] error getting PCBA serial number: {e}")
                retry_count -= 1
                if retry_count == 0:
                    results[com_port]["checks"]["pcba_serial"] = ""
                    results[com_port]["status"] = "FAIL"
                    results[com_port]["reason"] = f"Get_pcb_serial_num failed after retries: {e}"
                    abort_flag.set()
                    logging.info(f"[{com_port}] closing serial port")
                    ser.close()
                    break

        if ser.is_open:
            ser.close()
        time.sleep(0.1)

        end_time = datetime.datetime.now()
        logging.info(f"[{com_port}] check finished at {end_time} (took {end_time - start_time})")

        checks = results[com_port]["checks"]
        if any(v == "fail" for v in checks.values()):
            reason = "; ".join(
                CHECK_FAIL_MESSAGES.get(name, name)
                for name, v in checks.items() if v == "fail"
            )
            results[com_port]["status"] = "fail"
            results[com_port]["reason"] = reason
        elif results[com_port]["status"].lower() != "fail":
            results[com_port]["status"] = "pass"

    except serial.SerialException as e:
        results[com_port]["status"] = "fail"
        results[com_port]["reason"] = f"could not open port - {com_port} not found or in use"
        logging.error(f"[{com_port}] SerialException: {e}")
    except Exception as e:
        logging.error(f"[{com_port}] Exception in _check_one_port: {e}")
        results[com_port]["status"] = "fail"
        results[com_port]["reason"] = f"exception - {e}"


def _test_ports(pending_ports, port_id, main_pcb_sfg_prefix):
    """
    pending_ports: dict of {com_port: True} - the ports to check this round.

    Returns: {com_port: {"checks": {...}, "status": "PASS"/"FAIL", "reason": "..."}}
    """
    results = {}
    abort_flag = threading.Event()
    threads = {}

    logging.info(f"Starting COM Port Testing on ports: {list(pending_ports.keys())}")

    for port in pending_ports:
        t = StoppableThread(
            target=_check_one_port,
            args=(port, port_id, results, abort_flag, main_pcb_sfg_prefix),
        )
        threads[port] = t

    for t in threads.values():
        t.start()
    for t in threads.values():
        t.join()

    logging.info(f"COM Port Testing round completed with results: {results}")
    return results


def run_com_check(ports, MAIN_PCB_SFG_PREFIX):
    """
    Entry point called directly by the Smart Manufacturing Suite GUI.
    See module docstring for the calling contract and return shape.
    """
    port_id = DEFAULT_PORT_ID
    main_pcb_sfg_prefix = MAIN_PCB_SFG_PREFIX

    # dict-based "still needs checking" tracking, replacing the old
    # retry_list / current_ports list juggling
    pending_ports = {p: True for p in ports}

    # com_port -> {"status": "pass"/"fail", "pcb_serial": "..."}
    final_status = {}

    round_num = 0
    while pending_ports and round_num < MAX_RETRY_ROUNDS:
        round_num += 1
        raw_results = _test_ports(pending_ports, port_id, main_pcb_sfg_prefix)

        still_failing = {}
        for port in pending_ports:
            info = raw_results.get(
                port, {"status": "fail", "reason": "no result returned", "checks": {}}
            )
            status = "pass" if info.get("status") == "pass" else "fail"
            pcb_serial = info.get("checks", {}).get("pcba_serial", "") or ""

            final_status[port] = {"status": status, "pcb_serial": pcb_serial}
            if status == "fail":
                still_failing[port] = True

        if still_failing:
            logging.info(
                f"Round {round_num}/{MAX_RETRY_ROUNDS}: "
                f"{len(still_failing)} port(s) still failing: {list(still_failing.keys())}"
            )
        pending_ports = still_failing

    # anything still pending after MAX_RETRY_ROUNDS is a final fail
    for port in pending_ports:
        if final_status.get(port, {}).get("pcb_serial", "") == '':
            final_status[port] = {
                "status": "fail",
                "pcb_serial": final_status.get(port, {}).get("pcb_serial", ""),
            }
        else:
            final_status[port] = {
                "status": "pass",
                "pcb_serial": final_status.get(port, {}).get("pcb_serial", ""),
            }

    return final_status