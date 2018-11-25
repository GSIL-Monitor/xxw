import json
import logging
from uuid import uuid4
from src.apps.common.conn import redis_conn
from src.constant import Msg
from django.http import JsonResponse
from src.apps.model.models import User, Manager
from src.apps.common.func import make_response

#生成token
def generate_manager_token(manager) -> str:

    data = {
        "manager_code": manager.code
    }
    token = str(uuid4()).replace("-", "")
    redis_conn.set(token, ex=24*60*60, value=json.dumps(data))
    return token
#验证token
def manager_token_verify(token):
    try:
        data = json.loads(redis_conn.get(token))
        if not data:
            return "EXPIRED"
        manager_ins = Manager.objects.get(code=data["manager_code"])
        return  manager_ins
    except TypeError:
        # 代表没有从 redis 中取得数据
        return "INVALID"
    except Manager.DoesNotExist:
        return "NOT_EXIST"
    except Exception as e:
        logging.warn("obtain data error: {}".format(str(e)))
        return "INVALID"

def manager_token_required(func):
    """
    token 要求
    :param func:
    :return:
    """
    def decorator(*args, **kwargs):
        token = args[1].META.get("HTTP_JWT", None)
        if token is None:
            return make_response(code=Msg.NO_DATA, status=401)
        manager = manager_token_verify(token)
        if manager == "EXPIRED":
            return make_response(code=Msg.TOKEN_EXPIRATION, status=401)
        elif manager == "INVALID":
            return make_response(code=Msg.INVALID_TOKEN, status=401)
        elif manager == "NOT_EXIST":
            return make_response(code=Msg.MANAGER_NOT_EXISTS, status=401)
        # 为 request 修改默认 user 属性
        args[1].current_user = manager
        return func(*args, **kwargs)
    return decorator





#测试用

def user_test_token_required(func):
    """
    token 要求
    :param func:
    :return:
    """

    def decorator(*args, **kwargs):
        user = User.objects.get(code="1")
        # 为 request 修改默认 user 属性
        args[1].current_user = user
        return func(*args, **kwargs)
    return decorator    