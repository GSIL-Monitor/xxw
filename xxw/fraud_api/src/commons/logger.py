#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
import os

"""
线程安全的logger
"""

logger_dict = {}
LOG_PATH = os.getenv('LOG_PATH', '')
FILE_FORMAT = (
        "%(asctime)s | %(levelname)s | %(process)s | %(threadName)s"
        + " | %(name)s | %(pathname)s:%(funcName)s | %(lineno)s | %(message)s"
)
CONSOLE_FORMAT = (
    "%(asctime)s | %(levelname)s | %(message)s"
)
LOG_FILE_PATH = os.path.join(LOG_PATH, '{server_name}.log')
ROTATE_FILE_SIZE = 10000000
N_BACKUP_FILE = 5
DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name, level=logging.INFO):
    """
    返回一个logger对象
    :param name:
    :return:logger对象
    """
    # 判断logger对象是否存在
    if name in logger_dict:
        return logger_dict[name]

    logger = logging.getLogger(name)

    logger.setLevel(level)
    # file Handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_PATH.format(server_name=name),
        maxBytes=ROTATE_FILE_SIZE,
        backupCount=N_BACKUP_FILE,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(
        logging.Formatter(fmt=FILE_FORMAT, datefmt=DATEFMT)
    )
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(
        logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=DATEFMT)
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 字典保存logger对象
    logger_dict[name] = logger

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])
    logger.propagate = False
    return logger


logger = get_logger("fraud_api")
