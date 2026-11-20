import logging
import os
from logging.handlers import TimedRotatingFileHandler
import sys

def setup_logger(debug_log_enable = True, enable_file_log = False):

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

    log_folder = os.path.join(BASE_DIR,"Logs/Debug_log")
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "debug_log.log")

    logger = logging.getLogger()

    if logger.hasHandlers():
        logger.handlers.clear()

    if debug_log_enable:
        logger.setLevel(logging.DEBUG)  # DEBUG generates too many writes
    else:
        logger.setLevel(logging.INFO)  # DEBUG generates too many writes

    # Console handler — always add (fast, no disk I/O)
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(logging.Formatter(
    #     "%(asctime)s - %(processName)s - %(levelname)s - %(message)s",
    #     datefmt="%H:%M:%S"
    # ))
    # logger.addHandler(console_handler)

    # File handler — only in main process
    if enable_file_log:
        handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1,
            backupCount=7, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(processName)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(handler)

setup_logger(enable_file_log=True)
logger = logging.getLogger(__name__)