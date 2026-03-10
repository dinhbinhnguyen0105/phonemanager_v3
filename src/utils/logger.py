# utils\logger.py
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, Back, init

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from src.utils.yaml_handler import settings

init(autoreset=True)
LOG_DIR = os.path.abspath(os.path.join(root_dir, "logs"))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
LOG_FILE = os.path.join(LOG_DIR, log_filename)

SUCCESS_LEVEL = 25
FAILED_LEVEL = 35

logging.SUCCESS = SUCCESS_LEVEL
logging.FAILED = FAILED_LEVEL

logging.addLevelName(SUCCESS_LEVEL, Fore.GREEN + "SUCCESS" + Style.RESET_ALL)
logging.addLevelName(FAILED_LEVEL, Fore.RED + "FAILED" + Style.RESET_ALL)

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL):
        kws.setdefault("stacklevel", 2)
        self._log(SUCCESS_LEVEL, message, args, **kws)

def failed(self, message, *args, **kws):
    if self.isEnabledFor(FAILED_LEVEL):
        kws.setdefault("stacklevel", 2)
        if sys.exc_info()[0] is not None:
            kws.setdefault("exc_info", True)
        self._log(FAILED_LEVEL, message, args, **kws)

logging.Logger.success = success
logging.Logger.failed = failed

class ColoredFormatter(logging.Formatter):
    FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d)] - %(message)s"
    DATE_FORMAT = "%H:%M:%S"

    COLORS = {
        logging.DEBUG: Fore.CYAN + Style.DIM,
        logging.INFO: Fore.WHITE,
        SUCCESS_LEVEL: Fore.GREEN + Style.BRIGHT,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        FAILED_LEVEL: Fore.MAGENTA + Style.BRIGHT,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_fmt = self.COLORS.get(record.levelno, Fore.WHITE) + self.FORMAT + Style.RESET_ALL
        formatter = logging.Formatter(log_fmt, datefmt=self.DATE_FORMAT)
        return formatter.format(record)

class PlainFormatter(logging.Formatter):
    FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d)] - %(message)s"
    DATE_FORMAT = "%H:%M:%S"

    def format(self, record):
        return logging.Formatter(self.FORMAT, datefmt=self.DATE_FORMAT).format(record)

def setup_logger():
    logger = logging.getLogger("PhoneFarmApp")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.SUCCESS)
    file_handler.setFormatter(PlainFormatter())
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
    

