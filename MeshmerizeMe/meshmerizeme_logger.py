import logging

logging.basicConfig(format="%(levelname)-8s | %(message)s", level=logging.INFO)

def debug(message):
    logging.debug(message)

def info(message):
    logging.info(message)

def warning(message):
    logging.warning(message)

def error(message):
    logging.error(message)

def critical(message):
    logging.critical(message)
