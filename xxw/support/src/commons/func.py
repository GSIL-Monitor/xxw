
import json
import jwt
from flask import request

from src import app, redis
from src.commons.constant import Msg
from src.commons.date_utils import utc_timestamp
from src.models.user import TbBusiness, TbUser, TbMerchantBusiness


def generate_token(user) -> str:

    token = jwt.encode({"code": user.code, "time": utc_timestamp()}, app.config["SECRET_KEY"]).decode()
    key = "support_jwt_{}".format(user.code)
    data = {
        "exp_time": utc_timestamp()+24*60*60,
        "token": token}
    redis.set(key, value=json.dumps(data), ex=24*60*60)
    return token


def token_verify(token):
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"])
        code = data["code"]
        key = "support_jwt_{}".format(code)
        data = json.loads(redis.get(key))
        if not data:
            return "EXPIRED"
        elif data.get("token") != token:
            return "OFFLINE"
        else:
            user = TbUser.query.filter_by(code=code).first()
            if not user:
                return "NOT_EXIST"
            request.token = data
            # 更新 token
            redis.set(
                key,
                value=json.dumps({
                    "exp_time": utc_timestamp()+24*60*60,
                    "token": token}),
                ex=24*60*60)
            return user
    except TypeError:
        # 代表没有从 redis 中取得数据
        return "EXPIRED"
    except Exception as e:
        app.logger.info("obtain data error: {}".format(str(e)))
        return "INVALID"


def permission_required(func):
    def decorator(*args, **kwargs):
        user = request.current_user
        path = request.path.replace("/api/v1", "")
        method = request.method.upper()
        roles = user.roles
        # 获取当前用户所有的接口地址
        permission_path = [(i.path, i.method.upper()) for j in roles for i in j.interface]
        if user.is_admin or (path, method) in permission_path:
            return func(*args, **kwargs)
        return Msg.PERMISSION_DENIED, 403

    return decorator


def superuser_required(func):
    def decorator(*args, **kwargs):
        user = request.current_user
        if not user.is_admin:
            return Msg.PERMISSION_DENIED, 403
        return func(*args, **kwargs)

    return decorator


def appid_required(func):
    """
    appid 要求
    :param func:
    :return:
    """

    def decorator(*args, **kwargs):
        appid = request.headers.get("Appid", None)
        biz = TbBusiness.query.filter_by(appid=appid, status=True).first()
        if appid is None or not biz:
            return Msg.USER_FORBIDDEN, 403
        try:
            user = request.current_user
            # 判断非 root 用户所在商户是否有访问改系统的权限
            if not user.is_admin:
                user_mer_biz = TbMerchantBusiness.query.filter_by(merchant_code=user.merchant.code).all()
                if biz.code not in [i.business_code for i in user_mer_biz]:
                    return Msg.USER_FORBIDDEN, 403
            return func(*args, **kwargs)
        except AttributeError as e:
            return func(*args, **kwargs)

    return decorator


def token_required(func):
    """
    token 要求
    :param func:
    :return:
    """

    def decorator(*args, **kwargs):
        token = request.headers.get("Jwt", None)
        if token is None:
            return Msg.NO_DATA, 401
        user = token_verify(token)
        if user == "EXPIRED":
            return Msg.TOKEN_EXPIRATION, 401
        elif user == "INVALID":
            return Msg.INVALID_TOKEN, 401
        elif user == "NOT_EXIST":
            return Msg.USER_NOT_EXISTS, 401
        elif user == "OFFLINE":
            return Msg.USER_OFFLINE, 401
        else:
            if not user.is_admin and not user.merchant:
                return Msg.NO_DATA, 403
            # 判断用户是否登录状态下被禁用
            if not user.active:
                return Msg.USER_IS_BANED, 403
            # 为 request 修改默认 user 属性
            request.current_user = user
            return func(*args, **kwargs)

    return decorator


def redis_delete(key):
    try:
        redis.delete(key)
        return True
    except Exception as e:
        return True


def token_appid_permission_required(func):

    @token_required
    @appid_required
    @permission_required
    def decorator(*args, **kwargs):
        return func(*args, **kwargs)
    return decorator
