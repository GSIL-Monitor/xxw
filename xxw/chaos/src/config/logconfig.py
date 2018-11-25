#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc: 日志配置
"""
import os

LOG_PATH = os.getenv("LOG_PATH", "")
FILE_FORMAT = (
    "%(asctime)s | %(levelname)s | %(process)s | %(threadName)s"
    " | %(name)s | %(pathname)s:%(funcName)s | %(lineno)s | %(message)s"
)
CONSOLE_FORMAT = (
    "%(asctime)s, %(levelname)s - "
    "%(name)s %(filename)s:%(funcName)s - %(lineno)s: %(message)s"
)
LOG_FILE_PATH = os.path.join(LOG_PATH, "{server_name}.log")
ROTATE_FILE_SIZE = 10000000
N_BACKUP_FILE = 5
DATEFMT = "%Y-%m-%d %H:%M:%S"
