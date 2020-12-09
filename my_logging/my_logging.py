# Python function to log information to the terminal

import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")


def get_stream_handler():
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(FORMATTER)
    return stream_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_stream_handler())
    return logger
