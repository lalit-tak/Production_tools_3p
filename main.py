"""
Production Tools B1 - PyQt5 recreation

- COM ports are loaded from config.json (not hardcoded).
- RF/4G toggle replaced with an IMG / RF / 4G dropdown. The currently
  selected value is available reliably at any time via
  MainWindow.get_current_mode(), and also via the `mode_changed` signal.
- Every toolbar button runs its mapped script (see config.json -> scripts)
  as a subprocess (QProcess), non-blocking, and updates the tables live.
- Bottom bar shows: per test-case total time + pass/fail counts,
  overall elapsed time, and total executed cycles.
- "Calibration" is a single button / single script run, but it reports
  into two separate table columns - Phase and Neutral - instead of one
  combined column. See TEST_SCRIPT_COLUMNS below for how a script/test
  key maps onto one-or-more display columns, and the calibration_test
  branch in `_on_test_finished` for the expected RESULT_JSON shape.
- While a test is running, its toolbar button turns RUNNING_BUTTON_COLOR
  (purple) and every other toolbar button is disabled; once that test
  finishes, its button reverts to its normal color and every button is
  re-enabled. See RUNNING_BUTTON_COLOR / _apply_button_colors /
  _start_script_run / _on_test_finished.

Run:
    pip install PyQt5
    python3 main.py
"""

import sys
import os
import json
import time
import logging
import threading
import subprocess
import re
import ast
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from scripts.check_com.check_ports import run_com_check
from scripts.mct.mct_multiport import run_mct_test
from scripts.rtt.rtt import run_rtt_test
from scripts.rtt.img_testing import run_rtt_img_test
from scripts.calibration.calib_multiport import run_calibration_test
from utility.config import Config
from utility.ui_logger import setup_logger

setup_logger(enable_file_log=True)


from PyQt5.QtCore import Qt, QProcess, QThread, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QSizePolicy
)

if getattr(sys, "frozen", False):
    # Running as a PyInstaller --onefile .exe. __file__ here would
    # resolve to the temporary extraction folder (sys._MEIPASS) that
    # PyInstaller unpacks the bundle into at startup - that folder is
    # wiped the moment the exe process exits, and isn't something the
    # user can find/edit anyway. config.json, the assets/ images, the
    # Logs/ output folder, and the DLMS .exe path all need to live next
    # to the REAL production_tool.exe on disk instead, so they persist
    # across runs and can actually be edited/found. sys.executable is
    # the real .exe's own path in a frozen build (unlike __file__).
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # Normal `python main.py` execution - unchanged.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
DROPDOWN_ARROW_PATH = os.path.join(BASE_DIR, "assets", "dropdown_arrow.png").replace("\\", "/")

# The real DLMS activation tool - launched as a subprocess by run_dlms_test
# (via ExeTestRunner) instead of calling dlms_activation.py's Python
# reimplementation in-process. Its cmd-window output is appended to
# DLMS_LOG_FILE on every run (see ExeTestRunner._append_exe_log).
DLMS_EXE_PATH = os.path.join(BASE_DIR, "scripts", "dlms", "DLMS_ACTIVATION_TOOL_FOR_BENCH_V_1.21.exe")
DLMS_LOG_DIR = os.path.join(BASE_DIR, "dlms_logs")
DLMS_LOG_FILE = os.path.join(DLMS_LOG_DIR, "dlms_res_cmd.txt")
# The exe reads this file via a RELATIVE path from its own working
# directory (see cwd= in ExeTestRunner.run()), so it must live next to the
# exe itself, not anywhere else.
DLMS_EXE_CONFIG_PATH = os.path.join(os.path.dirname(DLMS_EXE_PATH), "config.json")

# S3 destination for the per-bench overall Test_Report_*.xlsx, uploaded
# once a full test cycle completes (see _upload_report_to_s3). Same
# bucket/credentials already used by the RTT/MCT/Calibration uploaders
# (scripts/rtt/rtt.py, scripts/mct/mct_multiport.py, etc.).
S3_ACCESS_KEY = "PUT_YOUR_ACCESS_KEY_HERE"
S3_SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"
S3_BUCKET_NAME = "PUT_YOUR_BUCKET_NAME_HERE"
S3_FOLDER_NAME = "PUT_YOUR_FOLDER_NAME_HERE"

# Height the logo image is scaled to inside the 64px-tall header.
LOGO_HEIGHT = 36

# Columns shown in each results table (key -> display header).
#
# NOTE: "Calibration" is still a single button and a single script run
# (see TEST_SCRIPT_COLUMNS just below), but it is displayed as two
# separate columns here - Phase and Neutral - instead of one combined
# "Calibration" column.
TEST_COLUMNS = [
    ("phase_test", "Phase"),
    ("neutral_test", "Neutral"),
    ("rtt_test", "RTT"),
    ("dlms_test", "DLMS"),
    ("mct_test", "MCT"),
]

# Maps each toolbar/script test key (what actually gets run as a
# subprocess) to the display column(s) it writes results into.
# calibration_test is one script execution that fills two columns
# (phase_test, neutral_test); every other test key maps to itself.
TEST_SCRIPT_COLUMNS = {
    "calibration_test": ["phase_test", "neutral_test"],
    "rtt_test": ["rtt_test"],
    "dlms_test": ["dlms_test"],
    "mct_test": ["mct_test"],
}

# Bottom-bar stat chips are keyed per test RUN (script), not per display
# column - so Calibration gets one combined Pass/Fail/Time chip even
# though it fills two table columns. "check_port" has no table column of
# its own (it's a separate action, not a TEST_COLUMNS entry) but still
# gets a chip here so its consumed time/pass/fail shows in the footer.
TEST_SCRIPTS = [
    ("check_port", "Check Ports"),
    ("calibration_test", "Calibration"),
    ("rtt_test", "RTT"),
    ("dlms_test", "DLMS"),
    ("mct_test", "MCT"),
]

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_PASS = "pass"
STATUS_FAIL = "fail"

# Toolbar button color shown while its test is actively running (and
# while it's disabled during that run - see _apply_button_colors, which
# uses this same color for the disabled state too so it doesn't flash
# back to grey the moment the toolbar gets locked).
RUNNING_BUTTON_COLOR = "#8e24aa"
DISABLED_BUTTON_BG = "#b0bec5"
DISABLED_BUTTON_FG = "#eceff1"

# --------------------------------------------------------------------
# COLUMN WIDTH CONTROL
# --------------------------------------------------------------------
# One ratio per column, in the same left-to-right order as the table:
#   [COM Port, Serial No.(PCBA), Phase, Neutral, RTT, DLMS, MCT, Status]
#
# Ratios should sum to (roughly) 1.0 - each column simply gets that
# fraction of the table's current width. Edit these numbers to change
# column widths; everything reflows automatically on resize (no
# scrollbar needed). Any rounding remainder is absorbed by the last
# column, so it doesn't need to be perfectly exact.
COLUMN_WIDTH_RATIOS = [
    0.10,   # COM Port
    0.33,   # Serial No.(PCBA)
    0.09,   # Phase
    0.09,   # Neutral
    0.10,   # RTT
    0.07,   # DLMS
    0.10,   # MCT
    0.07,   # Status
]


ICONS = {
    STATUS_PENDING: "",
    STATUS_RUNNING: "\u29D6",
    STATUS_PASS: "\u2713",
    STATUS_FAIL: "\u2717",
}

# Icons for the WHOLE-TEST status indicators next to each toolbar button
# (see _set_test_status_icon) - deliberately separate from ICONS (used for
# per-COM-port table cells), so "not run yet" can get a visible glyph here
# without also changing what an untested port's own cell looks like.
TEST_LEVEL_ICONS = dict(ICONS)
TEST_LEVEL_ICONS[STATUS_PENDING] = "\u25CB"  # hollow circle - "this test hasn't run yet"

COLORS = {
    STATUS_PENDING: QColor("#ffffff"),
    STATUS_RUNNING: QColor("#ffffff"),
    STATUS_PASS: QColor("#ffffff"),
    STATUS_FAIL: QColor("#d93025"),
}
DEFAULT_PORT_TEXT_COLOR = QColor("#ffffff")
COM_PORT_COLORS = {
    STATUS_PENDING: DEFAULT_PORT_TEXT_COLOR,   # normal text, not white
    STATUS_RUNNING: QColor("#ac8b56"),
    STATUS_PASS: QColor("#1e8e3e"),
    STATUS_FAIL: QColor("#d93025"),
}

TEST_LEVEL_COLORS = dict(COLORS)

# ACTIVE_PORT_BG = QColor("#c8e6c9")      # light green
# INACTIVE_PORT_BG = QColor(0, 0, 0, 0)   # transparent - back to normal

ACTIVE_PORT_TEXT_COLOR = QColor("#1e8e3e")     # green
INACTIVE_PORT_TEXT_COLOR = QColor("#1a1a1a")   # normal/default text color

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def _coerce_bool(value, default=True):
    """Encrypted/JSON config values for a flag like this aren't always
    already a clean Python bool (could be "true"/"false" strings, 1/0,
    etc.) - this normalizes any of those, falling back to `default` if
    the key is simply absent (None) or an unrecognized type."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def load_data_config(file_name):
    config_obj = Config()
    try:
        data_config, ok = config_obj.check_encrypted_json(file_name)
        logging.info(f"Loaded encrypted config from {file_name}: {data_config}")
        if ok:
            return data_config
        else:
            logging.info(f"Error: Failed to load encrypted config from {file_name}")
            return {}
    except Exception as e:
        logging.error(f"Error: Exception while loading encrypted config from {file_name}: {e}")
        return {}

DATA_CONFIG = load_data_config("config_file.enc")
logging.debug(f"Encrypted config: {DATA_CONFIG}")

setup_logger(
    debug_log_enable=_coerce_bool(DATA_CONFIG.get("DEBUG_LOG_ENABLE", False), default=True),
    enable_file_log=True,
)

# TN's bench flow doesn't include a DLMS test at all - only Calibration
# (Phase/Neutral), RTT and MCT run there. Every other project keeps DLMS
# as before. Strip "dlms_test" out of the shared column/script/ratio
# lists right here so the rest of the app (table columns, toolbar,
# stat chips, per-port overall result, Excel report) never sees it for
# a TN bench, instead of special-casing PROJECT in a dozen places.
# IS_DLMS_NEW = str(DATA_CONFIG.get("DLMS_TYPE", "")).strip().lower() == "new_dlms"
if "new_dlms" in str(DATA_CONFIG.get("DLMS_TYPE", "old_dlms")).strip().lower():
    IS_DLMS_NEW = True
else:
    IS_DLMS_NEW = False
if IS_DLMS_NEW:
    TEST_COLUMNS = [c for c in TEST_COLUMNS if c[0] != "dlms_test"]
    TEST_SCRIPTS = [c for c in TEST_SCRIPTS if c[0] != "dlms_test"]
    TEST_SCRIPT_COLUMNS = {k: v for k, v in TEST_SCRIPT_COLUMNS.items() if k != "dlms_test"}
    # COLUMN_WIDTH_RATIOS order is [COM Port, Serial, Phase, Neutral,
    # RTT, DLMS, MCT, Status] - drop index 5 (DLMS) to match the
    # 7-column header row TN now has.
    COLUMN_WIDTH_RATIOS = COLUMN_WIDTH_RATIOS[:5] + COLUMN_WIDTH_RATIOS[6:]


def fmt_seconds(total_seconds: float) -> str:
    total_seconds = int(total_seconds)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class FunctionThreadRunner(QThread):
    """Generic QThread wrapper for running ANY blocking test function
    (MCT, Calibration, RTT, DLMS, or anything else with the same shape)
    on a background thread, so the main Qt event loop - and therefore
    elapsed_timer's 1-second tick - keeps running for the whole duration
    of the test, no matter which one it is.

    Usage - pass a string identifying the test, the function to call, and
    whatever positional/keyword args that function needs:

        runner = FunctionThreadRunner("mct_test", run_mct_test,
                                       self.data_config, ports, bench_number)
        runner = FunctionThreadRunner("calibration_test", run_calibration_test,
                                       self.data_config, ports)
        runner = FunctionThreadRunner("rtt_test", run_rtt_test,
                                       self.data_config, ports)
        runner = FunctionThreadRunner("dlms_test", run_dlms_test,
                                       self.data_config, ports)

    On completion it emits finished_with_result with:
        test_key   - exactly what you passed in, so one shared slot can
                     tell which test just finished and branch accordingly
        result     - whatever the function returned (or {} if it raised
                     or didn't return a dict)
        ok         - False if the function raised or didn't return a
                     dict, True otherwise
        error_msg  - the exception message if ok is False, else ""

    The function's own return-value shape (e.g. MCT's flat
    {port: 'pass'/'fail'/'unreachable'} vs. Calibration's possible
    per-port sub-dict {'phase': ..., 'neutral': ...}) is left entirely to
    whoever handles finished_with_result - this class only guarantees
    "you get a dict back, or ok=False if something went wrong."

    CAVEAT: some test functions (e.g. run_mct_test for RF/IMG meters)
    show a blocking easygui.msgbox() dialog mid-run. Tkinter (which
    easygui wraps) is only officially supported on the main thread -
    showing it from a background thread like this is expected to work on
    Windows in practice but isn't guaranteed elsewhere. If a specific
    test's dialog causes problems, that call is what to look at - it
    would need to signal back to the main thread instead of calling
    easygui directly from here."""

    finished_with_result = pyqtSignal(str, dict, float, bool, str)  # test_key, result, ok, error_message

    def __init__(self, test_key, func, *args, parent=None, **kwargs):
        super().__init__(parent)
        self.test_key = test_key
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Executes on the background thread (QThread's entry point)."""
        start = time.time()
        try:
            result = self.func(*self.args, **self.kwargs)
            elapsed = time.time() - start
            if not isinstance(result, dict):
                self.finished_with_result.emit(
                    self.test_key, {}, elapsed, False,
                    f"{getattr(self.func, '__name__', 'function')}() did not return a dict"
                )
                return
            self.finished_with_result.emit(self.test_key, result, elapsed, True, "")
        except Exception as e:
            elapsed = time.time() - start
            logging.error(f"Error running {self.test_key}: {e}")
            self.finished_with_result.emit(self.test_key, {}, elapsed, False, str(e))


class ExeTestRunner(QThread):
    """Runs an external .exe ONCE (not once per port) - the exe reads its
    own serial_config.json to know which ports/settings to test, so
    instead of passing ports on the command line, this writes that
    config file from the active port list first and then launches the
    exe with the config file's PATH as its argument.

    Lives on its own QThread purely so waiting for the process to finish
    doesn't block the Qt event loop - same reason FunctionThreadRunner
    runs Python test functions on a background thread.
    finished_with_result has the EXACT same signature as
    FunctionThreadRunner's, so an exe-based test (like DLMS) flows
    through an _on_..._finished handler exactly like every
    Python-function-based test does:

        test_key, {port: 'pass'/'fail'}, elapsed_seconds, ok, error_message

    Usage:
        runner = ExeTestRunner(
            "dlms_test", exe_path=r"C:\\Tools\\DlmsTest.exe", ports=ports,
            mode=self.get_current_mode(),
            config_path=r"C:\\Tools\\serial_config.json",
            timeout_s=120,
        )
        runner.finished_with_result.connect(self._on_dlms_finished)
        runner.start()

    Configure via:
      exe_path      - full path to the .exe. If it doesn't exist,
                      ok=False is reported immediately (nothing is
                      launched) - matching FunctionThreadRunner's
                      "exception -> ok=False" behavior.
      config_path   - where to write the exe's serial_config.json.
                      Defaults to "serial_config.json" next to the exe.
      write_config  - callable(config_path, ports, mode) that writes the
                      config file. DEFAULT WRITES {"port_list": [...],
                      "mode": ...} - ADJUST THIS to match your exe's
                      actual expected serial_config.json shape (key
                      names, extra fields, etc).
      build_args    - callable(config_path, mode) -> list[str], the
                      command-line arguments for the ONE exe invocation.
                      Default: [config_path] (i.e. "DlmsTest.exe
                      <config_path>"). Adjust if your exe expects e.g.
                      "--config <path>" instead of a bare positional arg.
      parse_results - callable(ports, exit_code, stdout, stderr,
                      config_path) -> {port: 'pass'/'fail'}. DEFAULT
                      applies the exe's single exit code UNIFORMLY to
                      every port (no per-port granularity, since the exe
                      only gives one overall result unless told
                      otherwise) - REPLACE THIS once you know how the
                      exe actually reports per-port results (e.g. reading
                      a results.json file it writes - see the example in
                      run_dlms_test's comments below).
      timeout_s     - timeout in seconds for the single exe run (default
                      120s). If it doesn't finish in time, it's killed
                      and every port is reported as a fail.
    """

    finished_with_result = pyqtSignal(str, dict, float, bool, str)

    def __init__(self, test_key, exe_path, ports, mode="", config_path=None,
                 write_config=None, build_args=None, parse_results=None,
                 stdin_input=None, timeout_s=120, output_log_path=None, parent=None):
        super().__init__(parent)
        self.test_key = test_key
        self.exe_path = exe_path
        self.ports = list(ports)
        self.mode = mode
        # If set, the exe's raw stdout/stderr for this run is appended to
        # this file path (creating its parent folder if needed) - see
        # _append_exe_log. None (default) skips log-file writing entirely.
        self.output_log_path = output_log_path
        # config_path/write_config are both optional now - some exes (like
        # the real DLMS activation tool) take no config file and no CLI
        # args at all, just stdin input. Only auto-fill a default
        # config_path if a write_config callable was actually supplied.
        self.config_path = config_path
        if self.config_path is None and write_config is not None:
            self.config_path = os.path.join(
                os.path.dirname(exe_path) if exe_path else ".", "config.json"
            )
        self.write_config = write_config  # None = skip writing any config file
        self.build_args = build_args or (lambda config_path, mode: ([config_path] if config_path else []))
        self.parse_results = parse_results or self._default_parse_results
        self.stdin_input = stdin_input  # e.g. "\n" if the exe expects input to proceed
        self.timeout_s = timeout_s

    def _default_parse_results(self, ports, exit_code, stdout, stderr, config_path):
        """No per-port granularity known by default - the exe's single
        exit code is applied to every port uniformly (0 = every port
        pass, non-zero = every port fail). This is a safe, honest
        default when nothing more specific is known - it does NOT
        pretend to distinguish ports the exe doesn't distinguish itself.
        Replace this with real per-port parsing (see
        parse_dlms_exe_output below for DLMS's actual mechanism) once you
        know your exe's real reporting format."""
        status = "pass" if exit_code == 0 else "fail"
        return {p: status for p in ports}

    def _append_exe_log(self, stdout, stderr, exit_label):
        """Appends this run's raw cmd-window output (exactly what
        parse_results also works from) to self.output_log_path, preceded
        by a timestamp/ports header so a growing log file stays readable
        across many runs. No-op if output_log_path wasn't set. Logging
        failures are swallowed (just logged) - a broken log file must
        never fail the actual test run."""
        if not self.output_log_path:
            return
        try:
            os.makedirs(os.path.dirname(self.output_log_path), exist_ok=True)
            with open(self.output_log_path, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(
                    f"{self.test_key} run at "
                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                    f"(exit={exit_label}) ports={self.ports}\n"
                )
                f.write("=" * 80 + "\n")
                if stdout:
                    f.write(stdout)
                    if not stdout.endswith("\n"):
                        f.write("\n")
                if stderr:
                    f.write("--- stderr ---\n")
                    f.write(stderr)
                    if not stderr.endswith("\n"):
                        f.write("\n")
        except Exception as e:
            logging.error(f"Failed to append {self.test_key} exe output to {self.output_log_path}: {e}")

    def run(self):
        """Executes on the background thread (QThread's entry point)."""
        start = time.time()
        results = {}
        ok = True
        error_message = ""
        try:
            if not self.exe_path or not os.path.exists(self.exe_path):
                raise FileNotFoundError(f"DLMS exe not found: {self.exe_path!r}")

            if self.write_config is not None:
                self.write_config(self.config_path, self.ports, self.mode)

            args = [self.exe_path] + list(self.build_args(self.config_path, self.mode))
            try:
                proc = subprocess.Popen(
                    args,
                    stdin=subprocess.PIPE if self.stdin_input is not None else None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    # The exe reads its OWN config.json via a relative
                    # path, not an absolute one - without cwd set here it
                    # inherits this app's working directory and silently
                    # picks up whatever unrelated config.json lives there
                    # instead (e.g. this project's own top-level
                    # config.json), producing a confusing KeyError deep in
                    # the exe rather than a "file not found".
                    cwd=os.path.dirname(self.exe_path) if self.exe_path else None,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0,
                )
                stdout, stderr = proc.communicate(input=self.stdin_input, timeout=self.timeout_s)
                results = self.parse_results(self.ports, proc.returncode, stdout, stderr, self.config_path)
                self._append_exe_log(stdout, stderr, proc.returncode)
                # Real DLMS exe output is extremely verbose (hundreds of
                # send/rec/[1, 1, 1] lines per run - confirmed against an
                # actual captured log) - keep INFO concise (just which
                # ports failed, if any), and push the full raw dump down
                # to DEBUG only, so routine failures don't bloat the log
                # file on every run.
                failed_ports = [p for p, v in results.items() if v != "pass"]
                if failed_ports:
                    logging.info(f"{self.test_key} exe finished with failures: {failed_ports} (exit={proc.returncode})")
                else:
                    logging.info(f"{self.test_key} exe finished successfully (exit={proc.returncode})")
                logging.debug(
                    f"{self.test_key} exe full output - exit={proc.returncode} "
                    f"stdout={stdout!r} stderr={stderr!r} results={results}"
                )
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                self._append_exe_log(stdout, stderr, f"TIMEOUT after {self.timeout_s}s")
                logging.error(f"{self.test_key} exe timed out after {self.timeout_s}s")
                results = {p: "fail" for p in self.ports}

            # Defensive backstop: guarantee every requested port has SOME
            # entry, even if parse_results returned a partial dict.
            for port in self.ports:
                results.setdefault(port, "fail")

        except Exception as e:
            ok = False
            error_message = str(e)
            logging.error(f"Error running {self.test_key}: {e}")

        elapsed = time.time() - start
        self.finished_with_result.emit(self.test_key, results, elapsed, ok, error_message)

def parse_dlms_exe_output(ports, exit_code, stdout, stderr, config_path):
    """Real per-port result parser for DLMS_ACTIVATION_TOOL_FOR_BENCH.
    Ports directly the exact logic from the original dlms_report()
    Tkinter tool's own DLMS handling - VERIFIED against a real captured
    run of the exe (dlms_res_cmd.txt), not just a guessed example.

    Real output is extremely verbose - hundreds of send/rec/"result is: 1"/
    "[1, 1, 1]" lines while it works through each meter - but ends with
    ONE final Python-list LITERAL summarizing every port, e.g. (this is
    an actual excerpt, not invented):

        ['succesfully activated in com port: 30', 'succesfully activated in com port: 31',
         'Failed in DLMS Activation in COM Port: 6', ...]

    Every bracketed "[...]" run in the combined output is found via
    regex (this also matches the many "[1, 1, 1]" ack noise lines
    scattered throughout - harmless, since only the LAST bracketed run
    is used, and the real summary list is always printed last),
    ast.literal_eval'd into an actual Python list. Each item's format is
    "<output_text>: <port_number>" - port_number is a bare number (not
    "COMx" - the "COM" prefix is added back here, matching the original
    tool's f"COM{port}" construction).

    A port passes if its output text contains "succesfully" (spelled
    exactly as the exe itself outputs it - confirmed in the real log,
    not "corrected" to "successfully" here, since matching the real
    string is what matters). A failed port's real text is "Failed in
    DLMS Activation in COM Port: <n>" - doesn't contain "succesfully",
    so it's correctly caught by the same single check.

    Same fail-safe rules as the original tool:
      - no bracketed list found anywhere in the output -> every
        requested port is a fail (the exe gave no parseable result)
      - a requested port that simply isn't mentioned in the parsed list
        at all -> that port is a fail (matches the original's "still
        Pending -> fail" cleanup at the end of dlms_report())
    """
    combined_output = (stdout or "") + (stderr or "")
    results = {}

    matches = re.findall(r"\[.*?\]", combined_output, re.DOTALL)
    if matches:
        try:
            output_list = ast.literal_eval(matches[-1])
            for item in output_list:
                try:
                    output_text, port_number = item.split(":")
                    port_name = f"COM{port_number.strip()}"
                    results[port_name] = "pass" if "succesfully" in output_text.strip().lower() else "fail"
                except ValueError:
                    logging.warning(f"Could not parse DLMS result item: {item!r}")
        except Exception as e:
            logging.error(f"Could not parse DLMS exe output list {matches[-1]!r}: {e}")
    else:
        logging.error("DLMS exe produced no parseable [...] result list in its output")

    # Any requested port the exe's own output never mentioned at all is
    # a fail - matches the original tool's "still Pending" cleanup.
    for port in ports:
        results.setdefault(port, "fail")

    return results


def _dlms_port_number(com_port):
    """'COM30' -> 30 - the exe's config.json and its own printed output
    (see parse_dlms_exe_output) both use the bare numeric suffix, never
    the 'COM' prefix."""
    match = re.search(r"(\d+)\s*$", str(com_port))
    if not match:
        raise ValueError(f"Cannot extract a port number from {com_port!r}")
    return int(match.group(1))


def write_dlms_exe_config(config_path, ports, dongle_ports):
    """Writes DLMS_EXE_CONFIG_PATH (scripts/dlms/config.json, sitting next
    to the exe) with the CURRENTLY ACTIVE ports for this run, replacing
    whatever port_list1/port_list2/dongle1/dongle2 test values were left
    there before. Required keys were reverse-engineered from a real
    KeyError('port_list1') the exe raised when this file was missing/wrong
    - {"port_list1": [...], "port_list2": [...], "dongle1": N, "dongle2": N}.

    port_list1 goes to dongle1/TEST_DLL.dll, port_list2 to
    dongle2/TEST_DLL1.dll - split evenly in two (first half/second half of
    the sorted active ports), mirroring the same 50/50 split
    scripts/dlms_activation.py's own run_dlms_test() performs for its
    2-dongle case. If dongle_ports has only one entry, every active port
    goes to port_list1 and port_list2 is left empty (single-dongle run).
    """
    port_numbers = sorted(_dlms_port_number(p) for p in ports)
    dongle1 = dongle_ports[0] if len(dongle_ports) > 0 else 3
    dongle2 = dongle_ports[1] if len(dongle_ports) > 1 else 4
    if len(dongle_ports) > 1:
        half = len(port_numbers) // 2
        port_list1, port_list2 = port_numbers[:half], port_numbers[half:]
    else:
        port_list1, port_list2 = port_numbers, []
    config = {
        "port_list1": port_list1,
        "port_list2": port_list2,
        "dongle1": dongle1,
        "dongle2": dongle2,
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


class MainWindow(QMainWindow):
    mode_changed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.config = load_config()
        # self.data_config = load_data_config("config_file.enc")
        self.data_config = DATA_CONFIG
        self.com_ports = list(self.config.get("com_ports", []))
        self.active_ports = {port: False for port in self.com_ports}
        self.test_results = {port: {"check_port": False, "pcba_serial": "", "phase_test": False, "neutral_test": False, "dlms_test": False, "rtt_test": False, "mct_test": False, "overall": False} for port in self.com_ports}
        self.test_completion_status = {"check_port": False, "calibration_test": False, "dlms_test": False, "rtt_test": False, "mct_test": False, "overall": False}
        self.bench_number = self.config.get("bench_number", "Bench 1")
        # One persistent Excel report per bench, appended to for the
        # whole lifetime of the app (see _push_row_to_excel /
        # _get_report_file_path) - not tied to individual test cycles.
        self.report_file_path = self._get_report_file_path()

        # self.modes = ["IMG", "RF", "4G"]
        self._current_mode = str(self.data_config.get("TOOL_TYPE", ""))

        # row index -> com port, tracked per table (left/right)
        self.row_lookup = {}  # com_port -> (table_widget, row_index)

        # stats per test RUN (script key) - e.g. calibration_test gets one
        # combined chip even though it fills two columns (phase/neutral).
        self.stats = {key: {"time": 0.0, "pass": 0, "fail": 0} for key, _ in TEST_SCRIPTS}
        self.total_cycles = 0
        # Cycle timer: starts the moment "Check Ports" is clicked, ticks
        # every second continuously, and freezes once every active port's
        # overall status has settled to pass/fail (see
        # _maybe_stop_batch_timer / _check_all_tests_done).
        self.batch_start_time = None
        self.batch_end_time = None
        self._active_runners = []
        # Which toolbar button (if any) is currently showing the
        # "running" (purple) style, so _on_test_finished knows which one
        # to revert once that test completes.
        self._running_button = None
        self._upload_report_to_s3()
        self.setWindowTitle(f"Production Tool Bench - {self.bench_number}")
        self.resize(1900, 1000)
        self._build_ui()
        self._populate_tables()

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.timeout.connect(self._tick_elapsed)
        self.elapsed_timer.start(1000)

        # Viewport height isn't final until the window is actually shown,
        # so refit row heights right after show too.
        QTimer.singleShot(0, self._fit_table_to_view)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._fit_table_to_view)

    def _clear_serial_number(self, port: str):
        """Explicitly blanks the Serial No.(PCBA) cell. Used when a port
        FAILS Check Ports (as opposed to _update_serial_number's no-op on
        empty, which is for the pass path only) - otherwise a serial
        number read on a previous successful cycle would keep showing on
        screen even after the port stops being confirmed active."""
        table, row = self.row_lookup[port]
        table.setItem(row, 1, self._plain_item(""))

    def _style_port_row(self, port, status: str):
        """Colors just the COM Port cell's TEXT green when active - no
        background fill on the cell/block, just the text itself changes
        color. Reverts to the normal text color when inactive."""
        if port not in self.row_lookup:
            return
        table, row = self.row_lookup[port]
        # color = ACTIVE_PORT_TEXT_COLOR if active else INACTIVE_PORT_TEXT_COLOR
        color = COM_PORT_COLORS.get(status, DEFAULT_PORT_TEXT_COLOR)
        item = table.item(row, 0)  # COM Port column only
        if item is not None:
            item.setForeground(color)

    # -------------------------------------------------------- Excel export

    def _normalize_report_status(self, value):
        """test_results[port][key] starts out as the literal boolean
        False (see __init__) until a real test writes a
        'pass'/'fail' string into it via _record_test_result. This turns
        that into a clean report label: a port that was simply never
        tested reads as "NOT TESTED", never as a blank cell or a raw
        Python False."""
        if value == STATUS_PASS:
            return "PASS"
        if value == STATUS_FAIL:
            return "FAIL"
        return "NOT TESTED"

    def _compute_overall_status(self, test_statuses):
        """test_statuses: the six normalized PASS/FAIL/NOT TESTED labels
        for one port. Mirrors the on-screen Status column's own rule
        (_recompute_row_status): a port isn't called PASS or FAIL until
        every one of its tests has actually run - any NOT TESTED test
        makes the port INCOMPLETE, never a false PASS just because
        nothing has failed yet."""
        if any(s == "FAIL" for s in test_statuses):
            return "FAIL"
        if any(s == "NOT TESTED" for s in test_statuses):
            return "INCOMPLETE"
        return "PASS"

    def _get_report_file_path(self):
        """One persistent report workbook per bench, created once and
        appended to for the lifetime of the app - not recreated per
        batch/cycle, so it accumulates a full history the same way the
        MCT/RTT/Calibration Excel logs already do."""
        reports_folder = os.path.join(BASE_DIR, "Logs", "Reports")
        os.makedirs(reports_folder, exist_ok=True)
        safe_bench = str(self.bench_number).replace(" ", "_")
        return os.path.join(reports_folder, f"Test_Report_{safe_bench}.xlsx")

    def _push_row_to_excel(self, port):
        """Appends ONE row for `port` to the persistent Excel report the
        moment its overall Status finalizes to PASS or FAIL on screen -
        called only from _recompute_row_status, and only for that final
        transition, never while the port is still PENDING/RUNNING.

        Appends a NEW row rather than overwriting a previous one, so
        retesting the same port later (e.g. after fixing a fault) keeps
        the earlier attempt in the file instead of losing it - the
        Timestamp column is what makes each attempt distinguishable."""
        entry = self.test_results.get(port, {})
        check_port = self._normalize_report_status(entry.get("check_port"))
        phase = self._normalize_report_status(entry.get("phase_test"))
        neutral = self._normalize_report_status(entry.get("neutral_test"))
        rtt = self._normalize_report_status(entry.get("rtt_test"))
        mct = self._normalize_report_status(entry.get("mct_test"))

        # TN has no DLMS test - its overall result (and the Excel report
        # column) is based only on Check Port/Phase/Neutral/RTT/MCT. Every
        # other project keeps DLMS in both, same as before.
        statuses = [check_port, phase, neutral, rtt]
        headers = ["Timestamp", "COM Port", "PCBA Serial No.", "Check Port", "Phase", "Neutral", "RTT"]
        row_data = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "COM Port": port,
            "PCBA Serial No.": entry.get("pcba_serial") or "N/A",
            "Check Port": check_port,
            "Phase": phase,
            "Neutral": neutral,
            "RTT": rtt,
        }
        if not IS_DLMS_NEW:
            dlms = self._normalize_report_status(entry.get("dlms_test"))
            statuses.append(dlms)
            headers.append("DLMS")
            row_data["DLMS"] = dlms

        statuses.append(mct)
        headers.append("MCT")
        row_data["MCT"] = mct

        headers.append("Overall Status")
        overall = self._compute_overall_status(statuses)
        row_data["Overall Status"] = overall

        center = Alignment(horizontal="center")
        pass_fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
        fail_fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
        incomplete_fill = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")
        bold_font = Font(bold=True)

        try:
            if os.path.exists(self.report_file_path):
                wb = openpyxl.load_workbook(self.report_file_path)
                sheet = wb.active
            else:
                wb = openpyxl.Workbook()
                sheet = wb.active
                sheet.title = "Test Report"
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
                for col_idx, header in enumerate(headers, start=1):
                    cell = sheet.cell(row=1, column=col_idx, value=header)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = center
                for col_idx in range(1, len(headers) + 1):
                    sheet.column_dimensions[get_column_letter(col_idx)].width = 20

            next_row = sheet.max_row + 1
            for col_idx, header in enumerate(headers, start=1):
                value = row_data.get(header, "")
                cell = sheet.cell(row=next_row, column=col_idx, value=value)
                cell.alignment = center
                if value == "PASS":
                    cell.fill = pass_fill
                elif value == "FAIL":
                    cell.fill = fail_fill
                elif value == "INCOMPLETE":
                    cell.fill = incomplete_fill
                if header == "Overall Status":
                    cell.font = bold_font

            wb.save(self.report_file_path)
            logging.info(f"Pushed {port} overall result ({overall}) to {self.report_file_path}")
        except Exception as e:
            logging.error(f"Failed to push {port}'s result to Excel report: {e}")

    def _upload_report_to_s3(self):
        """Kicks off a background upload of the bench's persistent
        Test_Report_*.xlsx to S3.

        Called once per completed cycle, from _maybe_stop_batch_timer
        right after it determines every active port's overall status has
        finalized - i.e. once all the overall test-status data for this
        bench is complete, not on every individual row append.

        Runs on a plain daemon thread (not the UI thread) since
        s3.upload_file() is a blocking network call and this fires from
        inside the main Qt event loop - blocking there would freeze the
        UI for the duration of the upload."""
        report_path = self.report_file_path
        if not os.path.exists(report_path):
            return
        threading.Thread(
            target=self._upload_report_to_s3_worker,
            args=(report_path,),
            daemon=True,
        ).start()

    def _upload_report_to_s3_worker(self, report_path):
        """Background-thread body for _upload_report_to_s3. Re-uploads to
        the same key for the whole day (one date folder per day), so
        within a given day S3 always holds the latest full history for
        this bench rather than a pile of partial snapshots, while still
        keeping each day's cycles separated. The local file is left in
        place afterwards - unlike the RTT/MCT/Calibration uploaders, this
        report keeps accumulating rows for the lifetime of the app."""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError

            s3 = boto3.client(
                's3',
                aws_access_key_id=S3_ACCESS_KEY,
                aws_secret_access_key=S3_SECRET_KEY,
            )
            safe_bench = str(self.bench_number).replace(" ", "_")
            filename = os.path.basename(report_path)
            date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
            bucket_folder = "Garud"
            if 'ltct' in self.data_config.get("METER_TYPE","ltct").lower():
                bucket_folder = "3PLTCT"
            else:
                bucket_folder = "3PWC"

            key = f"{S3_FOLDER_NAME}/{bucket_folder}/Test_Bench_Reports/{safe_bench}/{date_folder}/{filename}"
            s3.upload_file(report_path, S3_BUCKET_NAME, key)
            os.remove(report_path)
            logging.info(f"Uploaded {filename} to s3://{S3_BUCKET_NAME}/{key}")
        except NoCredentialsError:
            logging.error("S3 upload failed: credentials not available")
        except Exception as e:
            logging.error(f"Failed to upload {report_path} to S3: {e}")

    # ------------------------------------------------------------------ UI

    def _make_info_label(self, title, value):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 4px;
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        title_label = QLabel(f"{title}:")
        title_label.setStyleSheet("""
            color: #e3f2fd;
            font-size: 12px;
            font-weight: 600;
            border: none;
            background: transparent;
        """)

        value_label = QLabel(str(value if value not in (None, "") else "N/A"))
        value_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: transparent;
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return container

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_toolbar())

        tables_row = QHBoxLayout()
        tables_row.setContentsMargins(8, 8, 8, 8)
        tables_row.setSpacing(12)
        self.left_table = self._make_table()
        self.right_table = self._make_table()
        tables_row.addWidget(self.left_table)
        tables_row.addWidget(self.right_table)
        tables_container = QWidget()
        tables_container.setLayout(tables_row)
        root.addWidget(tables_container, stretch=1)

        root.addWidget(self._build_footer())

    def _build_header(self):
        header = QFrame()
        header.setStyleSheet("background-color: #1565c0;")
        header.setFixedHeight(64)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH)
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaledToHeight(LOGO_HEIGHT, Qt.SmoothTransformation))
        else:
            # Fallback so the app still runs if the image is missing/moved.
            logo.setText("POLARIS")
            logo.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        layout.addWidget(logo)
        layout.addSpacing(16)
        title = QLabel(f"Production Tool Bench - {self.bench_number}")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: 600;")
        # layout.addWidget(title)
        # layout.addStretch(1)

        layout.addWidget(title)
        layout.addStretch(1)

        # Get project/version information from data_config
        # project = self.data_config.get("PROJECT", "N/A")
        project = self.data_config.get("PROJECT", "N/A")
        live_version = self.data_config.get("LIVE_VERSION", "N/A")
        internal_version = self.data_config.get("INTERNAL_VERSION", "N/A")

        layout.addWidget(
            self._make_info_label("Project", project)
        )

        layout.addSpacing(6)

        layout.addWidget(
            self._make_info_label("Live", live_version)
        )

        layout.addSpacing(6)

        layout.addWidget(
            self._make_info_label("Internal", internal_version)
        )

        layout.addSpacing(16)

        mode_label = QLabel("Meter Type:")
        mode_label.setStyleSheet("color: white; font-size: 14px; font-weight: 600;")
        layout.addWidget(mode_label)
        self.tool_type_label = QLabel(self._current_mode or "N/A")
        self.tool_type_label.setFixedHeight(30)
        self.tool_type_label.setAlignment(Qt.AlignCenter)
        self.tool_type_label.setStyleSheet("""
            background-color: white;
            color: #1a1a1a;
            border: 1px solid #cfd8dc;
            border-radius: 4px;
            padding: 0px 16px;
            font-size: 14px;
            font-weight: 600;
        """)
        layout.addWidget(self.tool_type_label)

        return header

    def _on_mode_changed(self, text):
        # Single reliable source of truth for "current mode" used anywhere
        # in the app (and passed to every script invocation).
        self._current_mode = text
        self.mode_changed.emit(text)

    def get_current_mode(self) -> str:
        """Reliable accessor for the currently selected IMG/RF/4G mode."""
        return self._current_mode

    def _build_toolbar(self):
        bar = QFrame()
        bar.setStyleSheet("background-color: #1976d2;")
        bar.setFixedHeight(56)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        def sep():
            lbl = QLabel("✓")
            lbl.setStyleSheet("color: #c8e6c9; font-size: 16px; font-weight: bold;")
            return lbl

        self.test_status_labels = {}

        def make_status_icon(test_key):
            lbl = QLabel()
            lbl.setFixedWidth(24)
            lbl.setAlignment(Qt.AlignCenter)
            self.test_status_labels[test_key] = lbl
            self._set_test_status_icon(test_key, STATUS_PENDING)
            return lbl

        self.btn_new_batch = self._make_button("New Batch", "#00796b", self.on_new_batch)
        layout.addWidget(self.btn_new_batch)
        # layout.addWidget(sep())

        self.btn_check_ports = self._make_button("Check Ports", "#37474f", self.on_check_ports)
        layout.addWidget(self.btn_check_ports)
        layout.addWidget(make_status_icon("check_port"))
        # layout.addWidget(sep())

        # Single button / single script run ("calibration_test") that
        # reports into two columns: Phase and Neutral.
        self.btn_phase_cal = self._make_button("Calibration", "#37474f", lambda: self.run_calib_test("calibration_test"))
        layout.addWidget(self.btn_phase_cal)
        layout.addWidget(make_status_icon("calibration_test"))
        # layout.addWidget(sep())

        self.btn_rtt = self._make_button("RTT Test", "#37474f", lambda: self.run_rtt_test("rtt_test"))
        layout.addWidget(self.btn_rtt)
        layout.addWidget(make_status_icon("rtt_test"))
        # layout.addWidget(sep())


        self.btn_dlms = self._make_button("DLMS Test", "#37474f", lambda: self.run_dlms_test("dlms_test"))
        layout.addWidget(self.btn_dlms)
        dlms_status_icon = make_status_icon("dlms_test")
        layout.addWidget(dlms_status_icon)
        if IS_DLMS_NEW:
            # TN has no DLMS test - keep the button/icon around (other
            # code still references self.btn_dlms) but hide them.
            self.btn_dlms.setVisible(False)
            dlms_status_icon.setVisible(False)
        # layout.addWidget(sep())

        self.btn_mct = self._make_button("MCT Test", "#37474f", lambda: self.run_mct_test("mct_test"))
        layout.addWidget(self.btn_mct)
        layout.addWidget(make_status_icon("mct_test"))
        # layout.addWidget(sep())

        layout.addStretch(1)

        version_text = (
            f"Tool Version: 3.0"
        )
        self.version_info_label = QLabel(version_text)
        self.version_info_label.setStyleSheet("color: white; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.version_info_label)

        # Maps each async test key to the button that should turn purple
        # while it's running (Check Ports isn't in here - it runs
        # synchronously and isn't part of the running-highlight flow).
        self.test_buttons = {
            "calibration_test": self.btn_phase_cal,
            "rtt_test": self.btn_rtt,
            "dlms_test": self.btn_dlms,
            "mct_test": self.btn_mct,
        }
        return bar

    def _set_test_status_icon(self, test_key, status):
        """Updates the ONE icon representing test_key's overall state as a
        whole - never per-COM-port. Only three states are ever used here:
          - STATUS_PENDING (\u25CB) - not run yet (startup / at the start
            of a fresh cycle, or reverted back to this if the run errored
            out entirely without completing)
          - STATUS_RUNNING (\u29D6) - the moment that test starts
          - STATUS_PASS (\u2713) - once it finishes running to completion,
            REGARDLESS of whether any individual port passed or failed -
            this icon means "the test ran," not "everything passed."
        STATUS_FAIL is deliberately never used for this whole-test icon -
        per-port pass/fail still shows in each port's own table cell."""
        label = self.test_status_labels.get(test_key)
        if label is None:
            return
        label.setText(TEST_LEVEL_ICONS.get(status, ""))
        color = TEST_LEVEL_COLORS.get(status, DEFAULT_PORT_TEXT_COLOR)
        label.setStyleSheet(f"color: {color.name()}; font-size: 18px; font-weight: bold;")

    def _make_button(self, text, color, handler):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        # Remember its normal/base color so the running-highlight can be
        # reverted back to exactly this color once the test finishes.
        btn.base_color = color
        self._apply_button_colors(btn, color, running=False)
        btn.clicked.connect(handler)
        return btn

    def _apply_button_colors(self, btn, base_color, running=False):
        """(Re)builds a toolbar button's stylesheet. When running=True the
        button shows RUNNING_BUTTON_COLOR (purple) for both its normal AND
        its disabled state - that second part matters because the button
        gets disabled (via _set_toolbar_enabled) the instant a test starts,
        and without a matching disabled-state color it would otherwise
        flash straight to the generic grey disabled look instead of
        staying purple for the whole run."""
        bg = RUNNING_BUTTON_COLOR if running else base_color
        disabled_bg = RUNNING_BUTTON_COLOR if running else DISABLED_BUTTON_BG
        disabled_fg = "white" if running else DISABLED_BUTTON_FG
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                font-weight: 600;
                font-size: 15px;
                padding: 10px 20px;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #263238; }}
            QPushButton:disabled {{ background-color: {disabled_bg}; color: {disabled_fg}; }}
        """)

    def _make_table(self):
        headers = ["COM Port", "Serial No.(PCBA)"] + [h for _, h in TEST_COLUMNS] + ["Status"]
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                font-size: 15px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #1976d2;
                color: white;
                font-weight: 600;
                padding: 6px;
                border: 1px solid #1565c0;
            }
            QTableWidget::item:alternate { background-color: #f5f7fa; }
        """)
        header = table.horizontalHeader()
        # Fixed mode = widths are set entirely by us (via COLUMN_WIDTH_RATIOS
        # in _fit_columns_to_view), not auto-guessed from content. This is
        # what lets columns always fill the window with no horizontal
        # scrollbar, at any window size.
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Fixed)

        # No scrollbars anywhere: rows are height-fitted and columns are
        # width-fitted to the viewport on every resize (see
        # _fit_rows_to_view / _fit_columns_to_view).
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.verticalHeader().setMinimumSectionSize(1)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return table

    def _build_footer(self):
        footer = QFrame()
        footer.setStyleSheet("background-color: #eceff1; ")
        footer.setFixedHeight(96)
        outer = QVBoxLayout(footer)
        outer.setContentsMargins(12, 6, 12, 6)
        outer.setSpacing(4)

        # Row of per-test-run stat chips (one per script, e.g. one
        # combined "Calibration" chip even though it fills two columns).
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.stat_labels = {}
        for key, header_text in TEST_SCRIPTS:
            name = header_text.replace("\n", " ")
            chip = QLabel()
            chip.setStyleSheet("""
                background-color: white;
                border: 1px solid #cfd8dc;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
            """)
            self.stat_labels[key] = chip
            stats_row.addWidget(chip)
        stats_row.addStretch(1)
        outer.addLayout(stats_row)

        bottom_row = QHBoxLayout()
        self.elapsed_label = QLabel("Elapsed Time: 00:00:00")
        self.elapsed_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #37474f;")
        bottom_row.addWidget(self.elapsed_label)

        bottom_row.addStretch(1)

        self.cycles_label = QLabel("Total Executed Cycles: 0")
        self.cycles_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1565c0;")
        bottom_row.addWidget(self.cycles_label)
        outer.addLayout(bottom_row)

        self._refresh_stat_chips()
        return footer

    def _refresh_stat_chips(self):
        for key, header_text in TEST_SCRIPTS:
            name = header_text.replace("\n", " ")
            s = self.stats[key]
            if 'port' in key.lower():
                self.stat_labels[key].setText(
                    f"<b>{name}</b> &nbsp; Time: {fmt_seconds(s['time'])} &nbsp; "
                )
            else:
                # self.stat_labels[key].setText(
                #     f"<b>{name}</b> &nbsp; Time: {fmt_seconds(s['time'])} &nbsp; "
                #     f"<span style='color:#1e8e3e;'>Pass: {s['pass']}</span> &nbsp; "
                #     f"<span style='color:#d93025;'>Fail: {s['fail']}</span>"
                # )
                self.stat_labels[key].setText(f"<b>{name} Time:</b> {fmt_seconds(s['time'])} Pass: {s['pass']} Fail: {s['fail']}")

    def _tick_elapsed(self):
        if self.batch_start_time is None:
            return
        # Once batch_end_time is set the cycle is done - keep showing the
        # frozen final time instead of continuing to count up.
        end = self.batch_end_time if self.batch_end_time is not None else time.time()
        elapsed = end - self.batch_start_time
        self.elapsed_label.setText(f"Elapsed Time: {fmt_seconds(elapsed)}")

    def _check_all_tests_done(self) -> bool:
        """True once every active port's overall Status cell has settled
        to pass/fail (i.e. no port is still pending/running). Ports that
        failed Check Ports are excluded - they never run any test, so
        they shouldn't hold the timer open. If Check Ports hasn't
        finished yet, this is never "done".

        If there are currently NO active ports (e.g. every port failed
        Check Ports), this deliberately returns False rather than True -
        that used to short-circuit to "nothing left to test, so the cycle
        is done" and froze the elapsed timer at ~0s the instant Check
        Ports finished, even though nothing had actually run yet. Now the
        timer just keeps counting until either a port goes active and
        finishes testing, or Check Ports is run again to start a fresh
        cycle."""
        if not self.test_completion_status.get("check_port"):
            return False
        active = self._get_active_ports()
        if not active:
            return False
        status_col = 2 + len(TEST_COLUMNS)
        for port in active:
            if port not in self.row_lookup:
                return False
            table, row = self.row_lookup[port]
            overall_text = table.item(row, status_col).text()
            if overall_text not in (ICONS[STATUS_PASS], ICONS[STATUS_FAIL]):
                return False
        return True

    def _maybe_stop_batch_timer(self):
        """Freezes the cycle timer the instant every active port's overall
        status has been updated to a final pass/fail - i.e. all tests for
        this cycle have completed. Also where Total Executed Cycles is
        bumped - the guard above (batch_end_time is not None -> return)
        makes this fire exactly once per completed cycle, no separate
        "New Batch" action needed to count it."""
        if self.batch_start_time is None or self.batch_end_time is not None:
            return
        if self._check_all_tests_done():
            self.batch_end_time = time.time()
            self._tick_elapsed()
            self.total_cycles += 1
            self.cycles_label.setText(f"Total Executed Cycles: {self.total_cycles}")
            self._upload_report_to_s3()

    def _populate_tables(self):
        self.left_table.setRowCount(0)
        self.right_table.setRowCount(0)
        self.row_lookup = {}

        half = (len(self.com_ports) + 1) // 2
        left_ports = self.com_ports[:half]
        right_ports = self.com_ports[half:]

        for ports, table in ((left_ports, self.left_table), (right_ports, self.right_table)):
            for port in ports:
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, self._plain_item(port))
                table.setItem(row, 1, self._plain_item(self.test_results.get(port).get("pcba_serial", "")))
                for col_idx, (key, _h) in enumerate(TEST_COLUMNS, start=2):
                    table.setItem(row, col_idx, self._status_item(STATUS_PENDING))
                status_col = 2 + len(TEST_COLUMNS)
                table.setItem(row, status_col, self._status_item(STATUS_PENDING))
                self.row_lookup[port] = (table, row)

        self._fit_table_to_view()

    def _fit_rows_to_view(self):
        """Shrink/grow row heights so every row fits inside the table's
        viewport with no vertical scrollbar, regardless of window size
        or how many COM ports are configured."""
        for table in (self.left_table, self.right_table):
            row_count = table.rowCount()
            if row_count == 0:
                continue
            viewport_height = table.viewport().height()
            row_height = max(14, viewport_height // row_count)
            table.verticalHeader().setDefaultSectionSize(row_height)
            for r in range(row_count):
                table.setRowHeight(r, row_height)

    def _fit_columns_to_view(self):
        """Apply COLUMN_WIDTH_RATIOS against the table's current width so
        columns always fill the available space with no horizontal
        scrollbar, at any window size."""
        for table in (self.left_table, self.right_table):
            total_width = table.viewport().width()
            if total_width <= 0:
                continue
            n = table.columnCount()
            ratios = COLUMN_WIDTH_RATIOS
            if len(ratios) != n:
                # fall back to equal split if the ratio list doesn't match
                ratios = [1.0 / n] * n
            widths = [int(total_width * r) for r in ratios]
            # give any leftover/rounding pixels to the last column so the
            # row exactly fills the viewport width (no gap, no overflow)
            widths[-1] += total_width - sum(widths)
            for i, w in enumerate(widths):
                table.setColumnWidth(i, max(20, w))

    def _fit_table_to_view(self):
        self._fit_rows_to_view()
        self._fit_columns_to_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_table_to_view()

    def _plain_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def _status_item(self, status):
        item = QTableWidgetItem(ICONS[status])
        item.setTextAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        item.setFont(font)
        item.setForeground(COM_PORT_COLORS[status])
        return item

    def _set_cell_status(self, port, col_key, status):
        if port not in self.row_lookup:
            return
        table, row = self.row_lookup[port]
        if col_key == "status":
            col_idx = 2 + len(TEST_COLUMNS)
        else:
            col_idx = 2 + [k for k, _ in TEST_COLUMNS].index(col_key)
        table.setItem(row, col_idx, self._status_item(status))

    def _recompute_row_status(self, port):
        """
        Overall per-port Status is updated ONLY after all test columns
        (Phase, Neutral, RTT, DLMS, MCT) have completed.

        While any test is pending or running, the overall Status remains
        pending.

        Once every test has completed:
            - FAIL if any test failed
            - PASS if all tests passed
        """

        table, row = self.row_lookup[port]

        col_statuses = []

        for col_idx, (key, _h) in enumerate(TEST_COLUMNS, start=2):
            text = table.item(row, col_idx).text()

            status = STATUS_PENDING

            for s, icon in ICONS.items():
                if icon == text:
                    status = s
                    break

            col_statuses.append(status)

        # ---------------------------------------------------------
        # IMPORTANT:
        # Do NOT show RUNNING in the overall Status column.
        #
        # If ANY test is still pending OR running, keep Status
        # as pending.
        # ---------------------------------------------------------
        if any(
            s in (STATUS_PENDING, STATUS_RUNNING)
            for s in col_statuses
        ):
            overall = STATUS_PENDING

        # ---------------------------------------------------------
        # All tests have completed.
        # Now calculate final overall result.
        # ---------------------------------------------------------
        else:
            if any(s == STATUS_FAIL for s in col_statuses):
                overall = STATUS_FAIL
            else:
                overall = STATUS_PASS

            # Push this port's row to the persistent Excel report the
            # instant its overall result actually finalizes on screen -
            # never while still PENDING/RUNNING (that branch is handled
            # above and never reaches here). No button needed - this is
            # the only place a row ever gets written.
            self._push_row_to_excel(port)

        self._set_cell_status(
            port,
            "status",
            overall
        )

    # -------------------------------------------------- result / port tracking

    def _record_test_result(self, port: str, test_key: str, status: str):
        """Writes a normalized 'pass'/'fail' string into
        test_results[port][test_key]. Anything not explicitly STATUS_PASS
        is coerced to STATUS_FAIL, so a test is never left ambiguous.

        This was being CALLED from on_check_ports without ever being
        DEFINED anywhere - that's bug #1 from the review (AttributeError
        the instant Check Ports was clicked)."""
        if status not in (STATUS_PASS, STATUS_FAIL):
            status = STATUS_FAIL
        self.test_results.setdefault(port, {})[test_key] = status

    def _update_serial_number(self, port: str, serial_number: str):
        """Overwrites the placeholder Serial No.(PCBA) cell with the real
        value read off hardware by check_ports.py. Also called from
        on_check_ports without ever being defined - bug #3 from the review.
        No-ops on an empty/falsy serial so a passing port never has its
        cell blanked out by mistake."""
        if not serial_number:
            return
        if port not in self.row_lookup:
            return
        table, row = self.row_lookup[port]
        table.setItem(row, 1, self._plain_item(serial_number))

    def _get_active_ports(self):
        """Ports currently eligible for testing (active_ports[port] is True).
        Populated by on_check_ports - a port stays ineligible for every
        other test until Check Ports has confirmed it."""
        return [p for p in self.com_ports if self.active_ports.get(p, False)]

    # ---------------------------------------------------------- actions

    def _set_toolbar_enabled(self, enabled: bool):
        for btn in (self.btn_new_batch, self.btn_check_ports, self.btn_phase_cal,
                    self.btn_rtt, self.btn_dlms, self.btn_mct):
            btn.setEnabled(enabled)

    # Start a fresh batch/cycle
    def on_new_batch(self):
        """Clears all TEST-run data (per-port active/pass-fail state, the
        results tables, per-test-run stat chips, and the elapsed-time
        clock) so a new batch starts from a clean slate instead of
        carrying over the previous batch's results.

        Total Executed Cycles is deliberately left untouched - it counts
        how many batches have completed over the app's whole lifetime,
        not anything scoped to the current batch, so a "new batch" must
        never reset it.

        The button is only enabled while _set_toolbar_enabled(True) is in
        effect - i.e. no test is currently running (mirrors every other
        toolbar button) - but _active_runners is checked again here as a
        defensive backstop against starting a new batch mid-test."""
        if self._active_runners:
            QMessageBox.warning(self, "Test Running",
                                 "Cannot start a new batch while a test is running.")
            return

        self.active_ports = {port: False for port in self.com_ports}
        self.test_results = {
            port: {
                "check_port": False, "pcba_serial": "", "phase_test": False,
                "neutral_test": False, "dlms_test": False, "rtt_test": False,
                "mct_test": False, "overall": False,
            }
            for port in self.com_ports
        }
        self.test_completion_status = {
            "check_port": False, "calibration_test": False, "dlms_test": False,
            "rtt_test": False, "mct_test": False, "overall": False,
        }
        self.stats = {key: {"time": 0.0, "pass": 0, "fail": 0} for key, _ in TEST_SCRIPTS}

        self.batch_start_time = None
        self.batch_end_time = None
        self.elapsed_label.setText("Elapsed Time: 00:00:00")

        self._populate_tables()
        self._refresh_stat_chips()
        for test_key in self.test_status_labels:
            self._set_test_status_icon(test_key, STATUS_PENDING)

    # Check COM Port status
    def on_check_ports(self):
        """Kicks off the COM port + PCB serial check on a background
        FunctionThreadRunner - same pattern as Calibration/RTT/DLMS/MCT -
        instead of calling run_com_check() directly on the main thread.

        run_com_check() used to be called inline here, which blocked the
        Qt event loop for its whole duration - during that time the
        elapsed_timer QTimer couldn't fire, so "Elapsed Time" appeared
        frozen while Check Ports ran and then jumped forward all at once
        once it returned. Running it on its own QThread keeps the main
        thread (and therefore the 1-second tick) free the whole time,
        matching every other test's behavior.

        Reflects the outcome per port once _on_check_ports_finished runs:
        passed -> active + green highlight + real serial shown; failed ->
        inactive, excluded from every subsequent test run."""
        # Cycle timer starts here - the moment Check Ports is clicked.
        # Only (re)start if it isn't already running.
        self._apply_button_colors(self.btn_check_ports, self.btn_check_ports.base_color, running=True)
        self._set_test_status_icon("check_port", STATUS_RUNNING)
        self._set_toolbar_enabled(False)
        if self.batch_start_time is None or self.batch_end_time is not None:
            self.batch_start_time = time.time()
            self.batch_end_time = None
            self.elapsed_label.setText("Elapsed Time: 00:00:00")

        list_port = [port for port, active in self.active_ports.items() if not active]
        if not list_port:
            # Nothing left to (re)check - finish immediately, no need to
            # spin up a background thread for zero work.
            self._finish_check_ports({}, 0.0)
            return

        runner = FunctionThreadRunner(
            "check_port", run_com_check,
            list(self.active_ports.keys()), self.data_config.get('MAIN_PCB_SFG_PREFIX', ''),
            parent=self,
        )
        runner.finished_with_result.connect(self._on_check_ports_finished)
        self._active_runners.append(runner)
        runner.start()

    def _on_check_ports_finished(self, test_key, com_status, elapsed, ok, error_message):
        self._active_runners = [r for r in self._active_runners if r.isRunning()]
        if not ok:
            logging.error(f"Error running check_ports: {error_message}")
            QMessageBox.warning(self, "Script Error", "'check_ports' did not complete successfully.")
            self.test_completion_status["check_port"] = False
            self.stats["check_port"]["time"] += elapsed
            self._refresh_stat_chips()
            self._set_test_status_icon("check_port", STATUS_PENDING)
            self._apply_button_colors(self.btn_check_ports, self.btn_check_ports.base_color, running=False)
            self._set_toolbar_enabled(True)
            return
        self._finish_check_ports(com_status, elapsed)

    def _finish_check_ports(self, com_status, elapsed):
        """Shared tail end of a Check Ports run, whether it went through
        the background runner (com_status/elapsed from the thread) or the
        "nothing left to check" fast path (empty dict / 0.0)."""
        pass_count = 0
        fail_count = 0

        for port, port_res in com_status.items():
            if port_res.get("status", "Fail").lower() == "pass":
                serial_number = port_res.get('pcb_serial', "")
                self.active_ports[port] = True
                self.test_results[port]["pcba_serial"] = serial_number
                self._record_test_result(port, "check_port", STATUS_PASS)
                self._update_serial_number(port, serial_number)
                self._style_port_row(port, STATUS_PASS)
                pass_count += 1
            else:
                self.active_ports[port] = False
                self.test_results[port]["pcba_serial"] = ""
                self._record_test_result(port, "check_port", STATUS_FAIL)
                self._clear_serial_number(port)
                self._style_port_row(port, STATUS_FAIL)
                fail_count += 1
        self.test_completion_status["check_port"] = True

        self.stats["check_port"]["time"] += elapsed
        self.stats["check_port"]["pass"] += pass_count
        self.stats["check_port"]["fail"] += fail_count
        self._refresh_stat_chips()

        # Covers the edge case where every port fails Check Ports (nothing
        # left to test) or every port was already fully tested - the
        # timer should stop immediately rather than run forever.
        if pass_count > 0 or fail_count > 0:
            self._set_test_status_icon("check_port", STATUS_PASS)
        else:
            self._set_test_status_icon("check_port", STATUS_PENDING)
        self._maybe_stop_batch_timer()
        self._apply_button_colors(self.btn_check_ports, self.btn_check_ports.base_color, running=False)
        self._set_toolbar_enabled(True)
        # print(f"active_ports after check_ports: {self.active_ports}")

    # Run CALIBRATION Test
    def run_calib_test(self, test_key, meter_key=None):
            list_port = self._get_active_ports()
            if not list_port:
                QMessageBox.warning(self, "No Active Ports",
                                        "No ports are marked active yet. Run 'Check Ports' first.")
                return
    
            # if self.batch_start_time is None:
            if self.batch_start_time is None or self.batch_end_time is not None:
                self.batch_start_time = time.time()
                self.batch_end_time = None
    
            # for p in list_port:
            #     self._set_cell_status(p, "calibration_test", STATUS_RUNNING)
            #     self._recompute_row_status(p)
            columns = TEST_SCRIPT_COLUMNS.get("calibration_test", [])
            for p in list_port:
                for col in columns:
                    self._set_cell_status(p, col, STATUS_RUNNING)
                self._recompute_row_status(p)
    
            self._apply_button_colors(self.btn_phase_cal, self.btn_phase_cal.base_color, running=True)
            self._running_button = self.btn_phase_cal
            self._set_test_status_icon("calibration_test", STATUS_RUNNING)
            self._set_toolbar_enabled(False)
    
            runner = FunctionThreadRunner(
                "calibration_test", run_calibration_test,
                self.data_config, list_port, self.config.get("bench_number", "1"),
                parent=self,
            )
            runner.finished_with_result.connect(self._on_calib_finished)
            self._active_runners.append(runner)
            runner.start()
    
    def _on_calib_finished(self, test_key, calib_results_by_com, elapsed, ok, error_message):
        self._set_toolbar_enabled(True)
        self.stats["calibration_test"]["time"] += elapsed
        
        if self._running_button is not None:
            self._apply_button_colors(self._running_button, self._running_button.base_color, running=False)
            self._running_button = None
        self._active_runners = [r for r in self._active_runners if r.isRunning()]

        active_ports = self._get_active_ports()
        inactive_ports = [p for p in self.com_ports if p not in active_ports]
        columns = TEST_SCRIPT_COLUMNS.get("calibration_test", [])
        if not ok:
            QMessageBox.warning(self, "Script Error",
                                    f"'calibration_test' did not complete successfully: {error_message}")
            for p in self.com_ports:
                # self._set_cell_status(p, "calibration_test", STATUS_FAIL)
                for col in columns:
                    self._set_cell_status(p, col, STATUS_FAIL)
                self._record_test_result(p, "phase_test", STATUS_FAIL)
                self._record_test_result(p, "neutral_test", STATUS_FAIL)
                self._record_test_result(p, "calibration_test", STATUS_FAIL)
                self._recompute_row_status(p)
            self.stats["calibration_test"]["fail"] += len(self.com_ports)
            self._refresh_stat_chips()
            self._set_test_status_icon("calibration_test", STATUS_PENDING)
            self.test_completion_status["calibration_test"] = False
            self._maybe_stop_batch_timer()
            return

        pass_count = 0
        fail_count = 0

        for port in active_ports:
            sub = calib_results_by_com.get(port)
            sub = sub if isinstance(sub, dict) else {}
            phase_status = STATUS_PASS if sub.get("phase") == "pass" else STATUS_FAIL
            neutral_status = STATUS_PASS if sub.get("neutral") == "pass" else STATUS_FAIL
            if (phase_status == STATUS_PASS) and (neutral_status == STATUS_PASS):
                pass_count += 1
            else:
                fail_count += 1
            self._set_cell_status(port, "phase_test", phase_status)
            self._set_cell_status(port, "neutral_test", neutral_status)
            self._record_test_result(port, "phase_test", phase_status)
            self._record_test_result(port, "neutral_test", neutral_status)
            overall_calib_status = STATUS_FAIL if STATUS_FAIL in (phase_status, neutral_status) else STATUS_PASS
            self._record_test_result(port, "calibration_test", overall_calib_status)
            self._recompute_row_status(port)

        for port in inactive_ports:
            self._set_cell_status(port, "phase_test", STATUS_FAIL)
            self._set_cell_status(port, "neutral_test", STATUS_FAIL)
            self._record_test_result(port, "phase_test", STATUS_FAIL)
            self._record_test_result(port, "neutral_test", STATUS_FAIL)
            self._record_test_result(port, "calibration_test", STATUS_FAIL)
            self._recompute_row_status(port)
            # fail_count += 1
            fail_count += 1

        self.stats["calibration_test"]["pass"] = pass_count
        self.stats["calibration_test"]["fail"] = fail_count
        self._refresh_stat_chips()
        self._set_test_status_icon("calibration_test", STATUS_PASS)
        self._maybe_stop_batch_timer()
        self.test_completion_status["calibration_test"] = True

    # Run RTT Test
    def run_rtt_test(self, test_key, meter_key=None):
        list_port = self._get_active_ports()
        if not list_port:
            QMessageBox.warning(self, "No Active Ports",
                                    "No ports are marked active yet. Run 'Check Ports' first.")
            return

        # if self.batch_start_time is None:
        #     self.batch_start_time = time.time()
        if self.batch_start_time is None or self.batch_end_time is not None:
            self.batch_start_time = time.time()
            self.batch_end_time = None

        for p in list_port:
            self._set_cell_status(p, "rtt_test", STATUS_RUNNING)
            self._recompute_row_status(p)

        self._apply_button_colors(self.btn_rtt, self.btn_rtt.base_color, running=True)
        self._running_button = self.btn_rtt
        self._set_test_status_icon("rtt_test", STATUS_RUNNING)
        self._set_toolbar_enabled(False)

        if self._current_mode.lower() == 'img':
            runner = FunctionThreadRunner(
                "rtt_test", run_rtt_img_test,
                self.data_config, list_port, self.config.get("bench_number", "1"),
                parent=self,
            )
        else:
            runner = FunctionThreadRunner(
                "rtt_test", run_rtt_test,
                self.data_config, list_port, self.config.get("bench_number", "1"),
                parent=self,
            )
        runner.finished_with_result.connect(self._on_rtt_finished)
        self._active_runners.append(runner)
        runner.start()
    
    def _on_rtt_finished(self, test_key, rtt_pass_fail_by_com, elapsed, ok, error_message):
        self._set_toolbar_enabled(True)
        self.stats["rtt_test"]["time"] += elapsed
        
        if self._running_button is not None:
            self._apply_button_colors(self._running_button, self._running_button.base_color, running=False)
            self._running_button = None
        self._active_runners = [r for r in self._active_runners if r.isRunning()]

        active_ports = self._get_active_ports()
        inactive_ports = [p for p in self.com_ports if p not in active_ports]

        if not ok:
            QMessageBox.warning(self, "Script Error",
                                    f"'rtt_test' did not complete successfully: {error_message}")
            for p in self.com_ports:
                self._set_cell_status(p, "rtt_test", STATUS_FAIL)
                self._record_test_result(p, "rtt_test", STATUS_FAIL)
                self._recompute_row_status(p)
            self.stats["rtt_test"]["time"] = elapsed
            self.stats["rtt_test"]["fail"] += len(self.com_ports)
            self._refresh_stat_chips()
            self._set_test_status_icon("rtt_test", STATUS_PENDING)
            self.test_completion_status["rtt_test"] = False
            self._maybe_stop_batch_timer()
            return

        pass_count = 0
        fail_count = 0

        for port in active_ports:
            raw_status = rtt_pass_fail_by_com.get(port)
            st = STATUS_PASS if raw_status == "pass" else STATUS_FAIL
            if st == STATUS_PASS:
                pass_count += 1
            else:
                fail_count += 1
            self._set_cell_status(port, "rtt_test", st)
            self._record_test_result(port, "rtt_test", st)
            self._recompute_row_status(port)

        for port in inactive_ports:
            self._set_cell_status(port, "rtt_test", STATUS_FAIL)
            self._record_test_result(port, "rtt_test", STATUS_FAIL)
            self._recompute_row_status(port)
            fail_count += 1

        self.stats["rtt_test"]["pass"] = pass_count
        self.stats["rtt_test"]["fail"] = fail_count
        self._refresh_stat_chips()
        self._set_test_status_icon("rtt_test", STATUS_PASS)
        self._maybe_stop_batch_timer()
        self.test_completion_status["rtt_test"] = True

    # Run DLMS Test
    def run_dlms_test(self, test_key, meter_key=None):
        """Runs DLMS_ACTIVATION_TOOL_FOR_BENCH_V_1.21.exe (DLMS_EXE_PATH)
        as a subprocess via ExeTestRunner, instead of calling
        dlms_activation.py's Python reimplementation in-process.

        The exe takes no CLI args - it reads its port/dongle assignment
        from a config.json sitting NEXT TO IT (DLMS_EXE_CONFIG_PATH),
        which write_dlms_exe_config() (re)writes with the currently active
        ports before every run (see that function's docstring for the
        config.json schema this was reverse-engineered from). It then
        prompts "Press Enter to start the script..." on launch, so
        stdin_input="\n" is sent to let it proceed unattended.

        Its combined stdout/stderr is parsed by parse_dlms_exe_output (the
        bracketed-list format verified against a real captured run - see
        dlms_logs/dlms_res_cmd.txt) and separately appended in full to
        DLMS_LOG_FILE for a persistent history of every run's raw cmd
        output.
        """
        if IS_DLMS_NEW:
            # No DLMS test in TN's flow - the button is hidden, but guard
            # here too in case this is ever reached some other way.
            return
        list_port = self._get_active_ports()
        if not list_port:
            QMessageBox.warning(self, "No Active Ports",
                                    "No ports are marked active yet. Run 'Check Ports' first.")
            return

        # Restart the timer if EITHER it's never been started this cycle
        # (batch_start_time is None) OR a previous cycle already fully
        # completed and froze it (batch_end_time is not None) - matching
        # on_check_ports' own guard. Checking only batch_start_time left
        # the elapsed timer permanently frozen after re-running a test
        # once a cycle had already finished.
        if self.batch_start_time is None or self.batch_end_time is not None:
            self.batch_start_time = time.time()
            self.batch_end_time = None

        columns = TEST_SCRIPT_COLUMNS.get("dlms_test", [])
        for p in list_port:
            for col in columns:
                self._set_cell_status(p, col, STATUS_RUNNING)
            self._recompute_row_status(p)

        self._apply_button_colors(self.btn_dlms, self.btn_dlms.base_color, running=True)
        self._running_button = self.btn_dlms
        self._set_test_status_icon("dlms_test", STATUS_RUNNING)
        self._set_toolbar_enabled(False)

        dongle_ports = self.config.get("DLMS_DONGLE_PORTS") or [3, 4]

        runner = ExeTestRunner(
            "dlms_test",
            exe_path=DLMS_EXE_PATH,
            ports=list_port,
            config_path=DLMS_EXE_CONFIG_PATH,
            write_config=lambda config_path, ports, mode: write_dlms_exe_config(
                config_path, ports, dongle_ports
            ),
            # The exe takes no CLI args at all (config.json is read via a
            # relative path from its own cwd, not passed on the command
            # line) - override ExeTestRunner's default build_args, which
            # would otherwise append config_path as a bare positional arg.
            build_args=lambda config_path, mode: [],
            stdin_input="\n",
            parse_results=parse_dlms_exe_output,
            output_log_path=DLMS_LOG_FILE,
            timeout_s=300,
            parent=self,
        )
        runner.finished_with_result.connect(self._on_dlms_finished)
        self._active_runners.append(runner)
        runner.start()

    def _on_dlms_finished(self, test_key, dlms_pass_fail_by_com, elapsed, ok, error_message):
        """dlms_pass_fail_by_com is {port: 'pass'/'fail'} - ExeTestRunner's
        return shape, identical to what run_mct_test/run_rtt_test return.
        DLMS is a single-column test (just "dlms_test"), so this mirrors
        _on_mct_finished exactly rather than Calibration's two-column
        handling."""
        self._set_toolbar_enabled(True)
        self.stats["dlms_test"]["time"] += elapsed

        if self._running_button is not None:
            self._apply_button_colors(self._running_button, self._running_button.base_color, running=False)
            self._running_button = None
        self._active_runners = [r for r in self._active_runners if r.isRunning()]

        active_ports = self._get_active_ports()
        inactive_ports = [p for p in self.com_ports if p not in active_ports]

        if not ok:
            QMessageBox.warning(self, "Script Error",
                                 f"'dlms_test' did not complete successfully: {error_message}")
            for p in self.com_ports:
                self._set_cell_status(p, "dlms_test", STATUS_FAIL)
                self._record_test_result(p, "dlms_test", STATUS_FAIL)
                self._recompute_row_status(p)
            self.stats["dlms_test"]["fail"] += len(self.com_ports)
            self._refresh_stat_chips()
            self._set_test_status_icon("dlms_test", STATUS_PENDING)
            self.test_completion_status["dlms_test"] = False
            self._maybe_stop_batch_timer()
            return

        pass_count = 0
        fail_count = 0

        for port in active_ports:
            raw_status = dlms_pass_fail_by_com.get(port)
            st = STATUS_PASS if raw_status == "pass" else STATUS_FAIL
            if st == STATUS_PASS:
                pass_count += 1
            else:
                fail_count += 1
            self._set_cell_status(port, "dlms_test", st)
            self._record_test_result(port, "dlms_test", st)
            self._recompute_row_status(port)

        for port in inactive_ports:
            self._set_cell_status(port, "dlms_test", STATUS_FAIL)
            self._record_test_result(port, "dlms_test", STATUS_FAIL)
            self._recompute_row_status(port)
            fail_count += 1

        self.stats["dlms_test"]["pass"] += pass_count
        self.stats["dlms_test"]["fail"] += fail_count
        self._refresh_stat_chips()
        self._set_test_status_icon("dlms_test", STATUS_PASS)
        self._maybe_stop_batch_timer()
        self.test_completion_status["dlms_test"] = True

    # Run MCT Test    
    def run_mct_test(self, test_key, meter_key=None):
        list_port = self._get_active_ports()
        if not list_port:
            QMessageBox.warning(self, "No Active Ports",
                                    "No ports are marked active yet. Run 'Check Ports' first.")
            return

        # Restart the timer if EITHER it's never been started this cycle
        # (batch_start_time is None) OR a previous cycle already fully
        # completed and froze it (batch_end_time is not None) - matching
        # on_check_ports' own guard. Checking only batch_start_time left
        # the elapsed timer permanently frozen after re-running a test
        # once a cycle had already finished.
        if self.batch_start_time is None or self.batch_end_time is not None:
            self.batch_start_time = time.time()
            self.batch_end_time = None

        for p in list_port:
            self._set_cell_status(p, "mct_test", STATUS_RUNNING)
            self._recompute_row_status(p)

        self._apply_button_colors(self.btn_mct, self.btn_mct.base_color, running=True)
        self._running_button = self.btn_mct
        self._set_test_status_icon("mct_test", STATUS_RUNNING)
        self._set_toolbar_enabled(False)

        runner = FunctionThreadRunner(
            "mct_test", run_mct_test,
            self.data_config, list_port, self.config.get("bench_number", "1"),
            parent=self,
        )
        runner.finished_with_result.connect(self._on_mct_finished)
        self._active_runners.append(runner)
        runner.start()

    def _on_mct_finished(self, test_key, mct_pass_fail_by_com, elapsed, ok, error_message):
        self._set_toolbar_enabled(True)
        self.stats["mct_test"]["time"] += elapsed
        
        if self._running_button is not None:
            self._apply_button_colors(self._running_button, self._running_button.base_color, running=False)
            self._running_button = None
        self._active_runners = [r for r in self._active_runners if r.isRunning()]

        active_ports = self._get_active_ports()
        inactive_ports = [p for p in self.com_ports if p not in active_ports]

        if not ok:
            QMessageBox.warning(self, "Script Error",
                                 f"'mct_test' did not complete successfully: {error_message}")
            for p in self.com_ports:
                self._set_cell_status(p, "mct_test", STATUS_FAIL)
                self._record_test_result(p, "mct_test", STATUS_FAIL)
                self._recompute_row_status(p)
            self.stats["mct_test"]["time"] = elapsed
            self.stats["mct_test"]["fail"] += len(self.com_ports)
            self._refresh_stat_chips()
            self._set_test_status_icon("mct_test", STATUS_PENDING)
            self.test_completion_status["mct_test"] = False
            self._maybe_stop_batch_timer()
            return

        pass_count = 0
        fail_count = 0

        for port in active_ports:
            raw_status = mct_pass_fail_by_com.get(port)
            st = STATUS_PASS if raw_status == "pass" else STATUS_FAIL
            if st == STATUS_PASS:
                pass_count += 1
            else:
                fail_count += 1
            self._set_cell_status(port, "mct_test", st)
            self._record_test_result(port, "mct_test", st)
            self._recompute_row_status(port)

        for port in inactive_ports:
            self._set_cell_status(port, "mct_test", STATUS_FAIL)
            self._record_test_result(port, "mct_test", STATUS_FAIL)
            self._recompute_row_status(port)
            fail_count += 1

        self.stats["mct_test"]["pass"] += pass_count
        self.stats["mct_test"]["fail"] += fail_count
        self._refresh_stat_chips()
        self._set_test_status_icon("mct_test", STATUS_PASS)
        self._maybe_stop_batch_timer()
        self.test_completion_status["mct_test"] = True

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
