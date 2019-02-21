# -*- coding: utf-8 -*-
import logging
import logging.handlers

"""
线程安全的logger
"""

logger_dict = {}

CONSOLE_FORMAT = "%(asctime)s, %(levelname)s - " + "%(name)s %(filename)s:%(funcName)s - %(lineno)s: %(message)s"

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

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=DATEFMT))

    logger.addHandler(console_handler)

    # 字典保存logger对象
    logger_dict[name] = logger

    logging.basicConfig(level=level, handlers=[console_handler])
    logger.propagate = False
    return logger


logger = get_logger("support")

