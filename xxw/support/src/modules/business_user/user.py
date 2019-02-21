""" B 端用户模块 """

from flask import request
from flask_restful import Resource

from schema import Schema, Optional
from src import db, redis
from src.commons.logger import logger
from src.commons.constant import Msg
from src.commons.date_utils import utc_timestamp
from src.commons.func import (generate_token, redis_delete, token_appid_permission_required, appid_required,
                              token_required)
from src.models.user import TbBusiness, TbInterface, TbMenu, TbMerchant, TbUser, TbMerchantBusiness, TbOperation
from src.modules.business_user.parser import (
    sign_in, user_info, modify_password, query_user, add_user, reset_pwd, active_user)
from src.commons.utils import validate_schema


class SignIn(Resource):
    @appid_required
    def post(self):
        req = sign_in.parse_args(strict=True)
        mobile = req["mobile"]
        if len(mobile) != 11:
            return Msg.PARAMS_ERROR, 400
        # 检测用户是否存在
        user = TbUser.query.filter_by(phone=mobile).first()
        if not user:
            return Msg.MOBILE_NOT_REGISTER_OR_PASSWORD_ERROR, 400
        if not user.active:
            return Msg.USER_NOT_ACTIVE, 403
        # 验证用户的密码和用户是否启用
        if user.verify_password(req["password"]):
            appid = request.headers["Appid"]
            token = generate_token(user)
            # 用户的接口和权限，超级用户返回所有的接口和菜单
            if user.is_admin:
                menu = [{"id": i.code, "name": i.name} for i in TbMenu.query.filter_by()]
                interface = [{"id": i.code, "name": i.name} for i in TbInterface.query.filter_by()]
            else:
                biz = TbBusiness.query.filter_by(appid=appid).first()
                if biz.id not in [i.business.id for i in user.roles]:
                    return Msg.PERMISSION_DENIED, 403
                # 用户所在商户下的系统
                if not TbMerchantBusiness.query.filter_by(merchant_code=user.merchant.code,
                                                          business_code=biz.code).first():
                    return Msg.PERMISSION_DENIED, 403
                roles = user.roles
                menu = [{"id": i.code, "name": i.name} for j in roles for i in j.menu]
                interface = [{"id": i.code, "name": i.name} for j in roles for i in j.interface]
            msg = "SUPPORT | B_USER | SIGN_IN | SUCCESS | USER_CODE: {} | USER_NAME: {}".format(user.code, user.name)
            operation = TbOperation(operator_code=user.code, content=msg, category="USER", type="LOGIN")
            db.session.add(operation)
            db.session.commit()
            logger.info(msg)
            return {
                "token": token,
                "name": user.name,
                "merchantId": user.merchant.code if user.merchant else None,
                "merchantName": user.merchant.name if user.merchant else None,
                "menu": menu,
                "interface": interface,
            }, 200
        logger.info(
            "SUPPORT | B_USER | SIGN_IN | FAILED | USER_CODE: {} | USER_NAME: {} | REASON: PASSWORD_ERROR".format(
                user.code, user.name))
        return Msg.MOBILE_NOT_REGISTER_OR_PASSWORD_ERROR, 400


class SignOut(Resource):
    """
    用户登出
    """

    @token_required
    def get(self):
        key = "support_jwt_{}".format(request.current_user.code)
        redis_delete(key)
        return {}, 200


class UserInfo(Resource):
    """
    用户信息相关
    """

    @token_required
    def get(self):
        """
        获取用户信息
        """
        user = request.current_user
        return {
            "name": user.name,
            "mobile": user.phone,
            "sex": user.sex,
            "mail": user.mail,
            "wechat": user.wechat,
            "address": user.address,
            "qq": user.qq,
            "avatar": user.avatar,
        }, 200

    @token_required
    def put(self):
        """
        修改用户信息
        """
        req = user_info.parse_args(strict=True)
        user = request.current_user
        user.name = req.get("name")
        user.sex = req.get("sex") if req.get("sex") else "unknown"
        user.address = req.get("address")
        user.wechat = req.get("wechat")
        user.qq = req.get("qq")
        user.avatar = req.get("avatar")
        user.mail = req.get("mail")
        user.update_time = utc_timestamp()
        msg = "SUPPORT | B_USER | EDIT_SELF_INFO | SUCCESS | USER_CODE: {} | USER_NAME: {}".format(user.code, user.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="USER", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200


class Password(Resource):
    """
    密码相关
    """

    @token_required
    def put(self):
        """
        修改用户密码
        """

        req = modify_password.parse_args(strict=True)
        if req["newPassword"] != req["verifyPassword"]:
            return Msg.PARAMS_ERROR, 400
        user = request.current_user
        if user.verify_password(req["oldPassword"]):
            user.generate_password(req["newPassword"])
            db.session.commit()
            key = "support_jwt_{}".format(request.current_user.code)
            redis_delete(key)
            msg = "SUPPORT | B_USER | MODIFY_PASSOWRD | SUCCESS | USER_CODE: {} | USER_NAME: {}".format(
                user.code, user.name)
            operation = TbOperation(operator_code=user.code, content=msg, category="USER", type="EDIT")
            db.session.add(operation)
            db.session.commit()
            logger.info(msg)
            return {}, 200
        return Msg.OLD_PASSWORD_ERROR, 400


# 用户管理
class UserManage(Resource):

    # 获取用户信息
    @token_appid_permission_required
    def get(self):
        req = query_user.parse_args(strict=True)
        page = req.get("page")
        count = req.get("count")
        name = req.get("name")
        phone = req.get("mobile")
        user = request.current_user
        condition = [TbUser.name.contains("%{}%".format(name if name else "")),
                     TbUser.phone.contains("%{}%".format(phone if phone else ""))]
        if not user.is_admin:
            # 非 admin 用户需要添加 merchant 筛选
            condition.append(TbUser.merchant_code == user.merchant.code)
        users = TbUser.query.filter(*condition).order_by(TbUser.id.desc()).paginate(page=page, per_page=count)
        res = [{
            "name": i.name,
            "mobile": i.phone,
            "sex": i.sex,
            "mail": i.mail,
            "wechat": i.wechat,
            "address": i.address,
            "status": i.active,
            "id": i.code,
            "qq": i.qq,
            "merchantId": i.merchant.code if i.merchant else None,
            "merchantName": i.merchant.name if i.merchant else None,
        } for i in users.items
        ]
        return {"result": res, "total": users.total}, 200

    # 编辑用户
    @token_appid_permission_required
    def put(self):
        schema = Schema({
            Optional("sex"): str,
            Optional("address"): str,
            Optional("wechat"): str,
            Optional("qq"): str,
            Optional("mail"): str,
            "name": str,
            "id": str,
            "mobile": str
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        current_user = request.current_user
        user = TbUser.query.filter_by(code=req["id"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        phone = req["mobile"]
        if len(phone) != 11:
            return Msg.PARAMS_ERROR, 400
        elif TbUser.query.filter(TbUser.code != req["id"], TbUser.phone == phone).first():
            return Msg.PHONE_USED, 400
        user.phone = phone
        user.name = req["name"]
        user.sex = req.get("sex", user.sex)
        user.mail = req.get("mail", user.mail)
        user.wechat = req.get("wechat", user.wechat)
        user.qq = req.get("qq", user.qq)
        user.address = req.get("address", user.address)
        user.update_time = utc_timestamp()
        msg = "SUPPORT | B_USER | EDIT_USER | SUCCESS | EDITOR: {} {} | USER: {} {} | MERCHANT: {} {}".format(
            current_user.code, current_user.name, user.code, user.name, user.merchant.code, user.merchant.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="USER_MANAGE", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200

    # 添加用户
    @token_appid_permission_required
    def post(self):
        req = add_user.parse_args(strict=True)
        merchant = TbMerchant.query.filter_by(code=req["merchantId"]).first()
        if not TbMerchant:
            return Msg.MERCHANT_NOT_EXIST, 400
        phone = req["mobile"]
        if len(phone) != 11 or TbUser.query.filter_by(phone=phone).first():
            return Msg.PHONE_USED, 400
        user = TbUser(
            phone=phone,
            name=req.get("name"),
            sex=req.get("sex"),
            wechat=req.get("wechat"),
            qq=req.get("qq"),
            mail=req.get("mail"),
            address=req.get("address"),
            merchant_code=merchant.code,
        )
        user.generate_password("123456")
        merchant.users.append(user)
        db.session.add(user)
        db.session.commit()
        user.code = str(1000000000 + user.id)
        msg = "SUPPORT | B_USER | EDIT_USER | SUCCESS | EDITOR: {} {} | USER: {} {} | MERCHANT: {} {}".format(
            request.current_user.code, request.current_user.name, user.code, user.name, merchant.code, merchant.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="USER_MANAGE", type="ADD")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200


# 用户管理 - 重置密码
class ResetPassword(Resource):
    @token_appid_permission_required
    def put(self):
        req = reset_pwd.parse_args(strict=True)
        user = TbUser.query.filter_by(code=req["id"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        user.generate_password("123456")
        msg = "SUPPORT | B_USER | RESET_PASSWORD | SUCCESS | EDITOR: {} {} | USER: {} {}".format(
            request.current_user.code, request.current_user.name, user.code, user.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="USER_MANAGE", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        redis.delete("support_jwt_{}".format(user.code))
        logger.info(msg)
        return {}, 200


# 用户管理 - 获取商户信息
class MerchantView(Resource):
    @token_appid_permission_required
    def get(self):
        merchant = TbMerchant.query.filter_by(is_active=True).order_by(TbMerchant.id.desc())
        data = [{"id": i.code, "name": i.name} for i in merchant]
        return {"result": data}, 200


# 用户管理 - 启用禁用用户
class UserActivation(Resource):
    @token_appid_permission_required
    def put(self):
        req = active_user.parse_args(strict=True)
        user = TbUser.query.filter_by(code=req["id"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        user.active = req["status"]
        if req["status"] is False:
            redis_delete("support_jwt_{}".format(user.code))
        msg = "SUPPORT | B_USER | ACTIVE_USER | SUCCESS | EDITOR: {} {} | USER: {} {} | STATUS: {}".format(
            request.current_user.code, request.current_user.name, user.code, user.name, req["status"])
        operation = TbOperation(operator_code=user.code, content=msg, category="USER_MANAGE", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200
