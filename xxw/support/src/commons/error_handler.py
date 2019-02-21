#!/usr/bin/env python
import functools
from flask import request

from src.commons.message import MESSAGE

DEFAULT_CODE = 1014000000
DEFAULT_MESSAGE = MESSAGE.get(DEFAULT_CODE) or ''



class RequestsError(BaseException):
    """
    错误处理
    """
    STANDARD_CODE = 200
    def __init__(self, code=0, http_code=None, **kwargs):
        self.http_code = http_code or self.STANDARD_CODE
        self.code = code
        self.message = ''
        message = kwargs.get('message', '')

        if message:
            self.message = MESSAGE.get(self.code, DEFAULT_MESSAGE) + message
        else:
            self.message = MESSAGE.get(self.code, DEFAULT_MESSAGE)
        super(RequestsError, self).__init__(self.message)


def http_basic_handler(func):
    """
    错误处理, 认证, 校验, 其它异常捕获等
    """
    @functools.wraps(func)
    def _decorator(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
            return resp
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'code': DEFAULT_CODE, 'msg': DEFAULT_MESSAGE, 'data': {}, 'is_simple': True}, 500
    return _decorator
    

def requests_error_handler(func):
    """
    定义错误处理
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        code = 200
        ret = {
            'code': 0,
            'msg': '',
            'data': {},
            'is_simple':True
        }
        try:
            result = func(*args, **kwargs)
        except RequestsError as e:
            code = e.http_code
            ret = {
                'code': e.code,
                'msg': e.message,
                'data': {},
                'is_simple':True
            }
        else:
            if isinstance(result, int):
                ret["code"] = int(result)
                ret["msg"] = MESSAGE.get(result, "未知错误")
            elif isinstance(result, tuple):
                assert isinstance(result[0], dict)
                assert isinstance(result[1], str)
                ret['data'] = result[0]
                ret['msg'] = result[1]
            elif isinstance(result, str):
                ret["msg"] = result
            else:
                ret["data"] = result
        return ret, code

    return wrapper
