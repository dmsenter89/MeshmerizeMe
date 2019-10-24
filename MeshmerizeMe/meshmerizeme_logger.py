import logging

class LevelFilter(logging.Filter):
    def __init__(self, low, high):
        self._low = low
        self._high = high
        logging.Filter.__init__(self)
    def filter(self, record):
        if self._low <= record.levelno <= self._high:
            return True
        return False

logger = logging.getLogger("MeshmerizeMe-main-logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)-8s | %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
console_handler.addFilter(LevelFilter(10,20)) # 10 = DEBUG, 20 = INFO
logger.addHandler(console_handler)

file_handler = None

def init_file_handler(full_file_name_without_exention):
    fileName = full_file_name_without_exention + ".log"
    file_handler = logging.FileHandler(fileName, mode="w")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def debug(message):
    logger.debug(message)

def info(message):
    logger.info(message)

def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)

def critical(message):
    logger.critical(message)
