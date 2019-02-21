import jwt
from flask import request
from src import app, db, redis, ma
from datetime import datetime, timedelta
from src.models.manager import (TbManager, TbFaceSignUser)
from werkzeug.security import check_password_hash, generate_password_hash
from src.commons.constant import Msg
from src.commons.logger import logger

def logger_req(req):
    for k in req:
        if not ((k == "pwd") or ("password" in k)):
            logger.info("[D] [入参 {} = {}]".format(k, req[k]))

def generate_password(password: str) -> str:
    return generate_password_hash(password)


def check_password(old_password: str, new_password: str) -> bool:
    return check_password_hash(old_password, new_password)


def re_address_code(code: str):
    # 地区编码处理
    if code[2:] == "0000":
        return code[:2]
    if code[4:] == "00":
        return code[:4]
    return code


def status_to_list(status: str):
    # status列表处理
    if not status:
        return ""
    status_list = []
    for i in status.split(","):
        i = int(i)
        status_list.append(i)
    return status_list


def manager_generate_token(code):
    """
    生成 token
    :param manager_code:
    :return:token
    """
    headers = {
        "typ": "JWT",
        "alg": "HS256",
        "manager_code": code
    }

    playload = {
        "headers": headers,
        "iss": 'zs',
        "exp": datetime.utcnow() + timedelta(days=7, hours=0, minutes=0, seconds=30),
        'iat': datetime.utcnow()
    }

    signature = jwt.encode(playload, app.config["SECRET_KEY"], algorithm='HS256')
    return signature


def manager_token_verify(token):
    """
    验证 token
    """

    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], options={'verify_exp': True})
        if payload:
            logger.info("[D] [Token Verification is passed]")
            return payload
        else:
            raise jwt.InvalidTokenError
    except jwt.ExpiredSignatureError:    
        logger.info("[D] [Token Verification is expired]")
        return 'EXPIRED'
    except jwt.InvalidTokenError:
        logger.info("[D] [Token Verification is invalid]")
        return 'INVALID'

def manager_token_required(func):
    """
    token 验证装饰器
    """

    def decorator(*args, **kwargs):
        token = request.headers.get("Jwt", None)
        if token is None:
            return Msg.NO_DATA, 401
        data = manager_token_verify(token)
        if data == "EXPIRED":
            return Msg.TOKEN_EXPIRATION, 401
        elif data == "INVALID":
            return Msg.INVALID_TOKEN, 401
        else:
            code = data.get("headers").get("manager_code")
            manager = TbManager.query.filter_by(code=code, is_delete=False).first()
            if not manager:
                return Msg.USER_NOT_EXISTS, 401
            # 为 request 修改默认 user 属性
            request.current_user = manager
            return func(*args, **kwargs)

    return decorator


def refresh_face_sign(manager_code):
    """
    刷新面签状态
    """
    exp_time = 60*60*24  # 面签单有效时间
    a = TbFaceSignUser.status == 1
    b = TbFaceSignUser.manager_code == manager_code
    c = TbFaceSignUser.update_time + exp_time < int(datetime.utcnow().timestamp())
    k = [a, b, c]
    be_rush_facesign = TbFaceSignUser.query.filter(*k)
    if be_rush_facesign:
        for i in be_rush_facesign:  # 判断有效时间，并更改状态
            i.manager_code = None
            i.manager_name = None
            i.status = 0
            i.update_time = int(datetime.utcnow().timestamp())
            db.session.commit()
            logger.info("[T] [Facesign code={} is refreshed]".format(i.code))    
