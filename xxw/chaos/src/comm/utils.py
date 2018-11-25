#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc: 一些常用的工具函数
"""

import json
import socket
import time
from datetime import datetime

from flask import Response, request
from schema import Schema, SchemaError

from src.comm.logger import logger
from src.config.msgconfig import Msg


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def utc_timestamp():
    """返回utc时间戳（秒）"""
    return int(datetime.utcnow().timestamp())


def make_response(code=Msg.SUCCESS, msg=None, data=None):
    data = json.dumps(
        {
            "code": code,
            "msg": Msg.msg[code] if not msg else msg,
            "data": data if data else {},
        }
    )
    resp = Response(data)
    resp.headers["Seq"] = request.headers.get("Seq")
    resp.headers["Content-Type"] = "application/json"
    # 解决跨域问题
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "PUT,GET,POST,DELETE"
    allow_headers = "Referer,Accept,Origin,User-Agent"
    resp.headers["Access-Control-Allow-Headers"] = allow_headers
    return resp


def validate_schema(schema: Schema, data: dict, remove_blank=False):
    """schema验证,验证成功返回数据，验证失败返回错误信息
    Parameters
    ----------
    schema:Schema: 验证规则
    data: 验证数据
    remove_blank : 是否去除空白字段

    Returns (data,errors)
    -------

    """
    if not isinstance(data, dict):
        return {}, "Not found params"
    d = {}
    if remove_blank:
        for k, v in data.items():
            if v != "":
                d[k] = v
    else:
        d = data
    try:
        validate_data = schema.validate(d)
        return validate_data, []
    except SchemaError as e:
        return {}, str(e.autos)
    else:
        return validate_data, []


def print_run_time(func):
    """计算时间函数"""

    def wrapper(*args, **kw):
        local_time = time.time()
        result = func(*args, **kw)
        logger.info(
            "current Function [%s] run time is %.2f"
            % (func.__name__, time.time() - local_time)
        )
        return result

    return wrapper


def get_operation(op):
    """根据传入数学式的操作，获取python内置的操作"""
    return {
        ">": "__gt__",
        "<": "__lt__",
        ">=": "__ge__",
        "<=": "__le__",
        "!=": "__ne__",
        "==": "__eq__",
        "contains": "contains",
    }.get(op)
