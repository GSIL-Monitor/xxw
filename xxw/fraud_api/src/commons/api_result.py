# -*-coding:utf-8-*-
# !/usr/bin/env python


import functools
import logging
import traceback

from flask import jsonify

logger = logging.getLogger(__name__)


def handle_exception(function):
    """
    异常处理
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """捕获异常，记录错误日志"""
        try:
            logger.debug(f"IN :{function.__name__},Arguments:{args},{kwargs}")
            result = function(*args, **kwargs)
            logger.debug(
                f"OUT :{function.__name__},Arguments:{args},{kwargs},Result:{result}"
            )
            return result
        except BaseException:
            # 记录日志
            logger.exception(traceback.format_exc())
            return generate_response(
                code=ErrorCode.UNKOWN_ERROR[0], msg=ErrorCode.UNKOWN_ERROR[1]
            )

    return wrapper


def generate_response(code=0, msg=None, data=None, paging=None):
    """APi Response"""
    result = ApiResult(code, msg, data, paging)
    return jsonify(result.response)


class ApiResult:
    """Api general result"""

    def __init__(self, code=0, msg=None, data=None, paging=None):
        self.code = code
        self.msg = msg
        self.data = data
        self.paging = paging

    @property
    def response(self):
        ret = {"code": self.code, "msg": self.msg, "data": self.data}
        if self.paging:
            ret["paging"] = self.paging
        return ret


class ErrorCode:
    """Error Code"""

    ERROR_ARGS = (10001, "参数错误")
    UNKOWN_ERROR = (30001, "服务器错误")
