import json
import logging
from uuid import uuid4
from rest_framework.utils.serializer_helpers import ReturnDict
from django.http import JsonResponse
from src.constant import Msg
from src.apps.model.models import User, Business

from .conn import redis_conn


def make_response(code=10000, msg=None, data=None, status=200):
    if isinstance(msg, ReturnDict):
        # 将 serializer.errors 的数据构造成我们自己的错误数据
        # 他的数据格式：{"userId": ["此字段是必填项"]}
        # 构造的数据： "userId 是必填项"
        msg_list = [k + " 是必填项" for k in msg]
        msg = ",".join(msg_list)
    result = {
        "code": code,
        "message": Msg.msg.get(code) if not msg else msg,
        "data": data if data else {}
    }
    res = JsonResponse(result)
    res.status_code = status
    return res


def generate_token(user) -> str:

    data = {
        "user_code": user.code
    }
    token = str(uuid4()).replace("-", "")
    redis_conn.set(token, ex=24*60*60, value=json.dumps(data))
    return token


def token_verify(token):
    try:
        data = json.loads(redis_conn.get(token))
        if not data:
            return "EXPIRED"
        user_ins = User.objects.get(code=data["user_code"])
        return user_ins
    except TypeError:
        # 代表没有从 redis 中取得数据
        return "INVALID"
    except User.DoesNotExist:
        return "NOT_EXIST"
    except Exception as e:
        logging.warn("obtain data error: {}".format(str(e)))
        return "INVALID"


def permission_required(func):
    def decorator(*args, **kwargs):
        user = args[1].current_user
        path = args[1].path
        method = args[1].method.upper()
        roles = user.roles.all()
        # 获取当前用户所有的接口地址
        permission_path = [(i.path, i.method.upper()) for j in roles for i in j.interface.all()]
        if user.is_admin or (path, method) in permission_path:
            return func(*args, **kwargs)
        return make_response(code=Msg.PERMISSION_DENIED, status=403)
    return decorator


def superuser_required(func):
    def decorator(*args, **kwargs):
        user = args[1].current_user
        if not user.is_admin:
            return make_response(code=Msg.PERMISSION_DENIED, status=403)
        return func(*args, **kwargs)
    return decorator


def appid_required(func):
    """
    appid 要求
    :param func:
    :return:
    """

    def decorator(*args, **kwargs):
        appid = args[1].META.get("HTTP_APPID", None)
        if appid is None or not Business.objects.filter(appid=appid):
            return make_response(code=Msg.NO_DATA, status=403)
        return func(*args, **kwargs)
    return decorator


def token_required(func):
    """
    token 要求
    :param func:
    :return:
    """

    def decorator(*args, **kwargs):
        token = args[1].META.get("HTTP_JWT", None)
        if token is None:
            return make_response(code=Msg.NO_DATA, status=401)
        user = token_verify(token)
        if user == "EXPIRED":
            return make_response(code=Msg.TOKEN_EXPIRATION, status=401)
        elif user == "INVALID":
            return make_response(code=Msg.INVALID_TOKEN, status=401)
        elif user == "NOT_EXIST":
            return make_response(code=Msg.USER_NOT_EXISTS, status=401)
        # 判断用户能不能访问这个 appid 对应的业务系统
        if not user.is_admin and not user.merchant:
            return make_response(code=Msg.NO_DATA, status=403)
        # 为 request 修改默认 user 属性
        args[1].current_user = user
        return func(*args, **kwargs)
    return decorator
