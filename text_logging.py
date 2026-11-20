import logging
import os
from logging.handlers import TimedRotatingFileHandler
import sys

def setup_logger(enable_file_log=False):

    log_folder = "Logs"
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "FTT.log")

    logger = logging.getLogger()

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)  # DEBUG generates too many writes

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