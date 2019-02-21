
"""
商户经理端
"""
import json
from flask import request
from flask_restful import Resource, reqparse
from src import app, db, redis, ma
from schema import Schema, Optional, And, Use
from src.commons.sms import verify_code
from src.commons.constant import Msg
from src.commons.date_utils import utc_timestamp
from src.models.manager import (TbManager, TbFaceSignUser)
from src.models.user import (TbMerchant, TbProduction, TbUser)
from src.models.log_db import LogRegister, LogLoading
from src.commons.model_resource import get_data, BaseResource, SQLModelResource
from src.commons.manager_utils import generate_password, check_password, re_address_code,\
    status_to_list, manager_generate_token, manager_token_verify, manager_token_required,\
    refresh_face_sign, logger_req
from src.commons.logger import logger
# 使用到的方法

PWD_ERR_COUNT = 5  # 登录时，密码错误被冻结的次数
PWD_FROZEN_TIME = 24*60*60  # 登录密码错误时，被冻结时间
PWD_ERR_REFRESH_TIME = 24*60*60 # 密码错误后，刷新错误次数的时间间隔
FACE_SIGN_VERIFY = 31*24*60*60  # 面签审核量占比查询 时间限制


class ManagerSignIn(BaseResource):
    """
    商户经理登录
    """
    validate_schemas = {
        "post": Schema(
            {"phone": str,
             "wx_openid": str,
             "pwd": str})}

    def post(self):
        # 商户经理登录
        logger.info("[D] [功能 商户经理登录]")
        req = self.validate_data
        logger_req(req)
        phone = req.get("phone")
        wx_openid = req.get("wx_openid")
        password = req.get("pwd")
        manager = TbManager.query.filter_by(phone=phone, is_delete=False).first()
        if not manager:
            logger.info("[T] [phone is not regist]")
            return Msg.MANAGER_PHONE_NOT_EXIST, -200
        if manager.wx_openid and manager.wx_openid != wx_openid:
            logger.info("[T] [phone is not bind wx_openid]")
            return Msg.MANAGER_BINDING_ERROR, -200
        if manager.pwd_err_count >= PWD_ERR_COUNT or \
                (manager.pwd_frozen_time and (manager.pwd_frozen_time + PWD_ERR_REFRESH_TIME) <= utc_timestamp()):
            manager.pwd_err_count = 0
            db.session.commit()
        if manager.pwd_frozen_time and manager.pwd_frozen_time >= utc_timestamp():
            logger.info("[T] [manager:{} is frozen, time:{}]"
                        .format(manager.code, manager.pwd_frozen_time))
            return {
                "error_name": "MANAGER_PASSWORD_ERROR_FROZEN",
                "data": {
                    "pwd_err_count_all": PWD_ERR_COUNT,
                    "pwd_err_count": PWD_ERR_COUNT,
                    "pwd_frozen_time": manager.pwd_frozen_time
                }}, -200
        if not check_password(manager.password, password):
            manager.pwd_err_count += 1
            manager.pwd_frozen_time = utc_timestamp()
            db.session.commit()
            logger.info("[T] [manager:{} pwd is error]".format(manager.code))
            if manager.pwd_err_count >= PWD_ERR_COUNT:
                manager.pwd_frozen_time = utc_timestamp() + PWD_FROZEN_TIME
                db.session.commit()
                logger.info("[T] [manager:{} is frozen time:{}]"
                            .format(manager.code, manager.pwd_frozen_time))
            return {
                "error_name": "MANAGER_PASSWORD_ERROR",
                "data": {
                    "pwd_err_count_all": PWD_ERR_COUNT,
                    "pwd_err_count": manager.pwd_err_count,
                    "pwd_frozen_time": manager.pwd_frozen_time
                }}, -200
        if not manager.wx_openid:
            manager.wx_openid = wx_openid
            db.session.commit()
            logger.info("[T] [phone:{} bind wx_openid:{}]"
                        .format(manager.phone, manager.wx_openid))
        manager.pwd_err_count = 0
        manager.pwd_frozen_time = 0
        db.session.commit()
        safe = False
        if not check_password(manager.password, phone[-6:]):
            safe = True
        production = TbProduction.query.filter_by(merchant_code=manager.merchant_code).first()
        if production:
            production_code = production.code
        merchant = TbMerchant.query.filter_by(code=manager.merchant_code).first()
        return {
            "token": manager_generate_token(manager.code).decode(),
            "name": manager.name,
            "manager_code": manager.code,
            "safe": safe,
            "phone": phone,
            "merchant_code": manager.merchant_code,
            "production_code": production_code or "",
            "merchant_logo": merchant.logo

        }


class ManagerForgetPassword(BaseResource):
    """
    商户经理忘记密码
    """
    validate_schemas = {
        "get": Schema({
            "wx_openid": str,
        }),
        "put": Schema({
            "phone": str,
            "verify_code": str,
            "new_password": str,
        })
    }

    def get(self):
        # 根据openid获取手机号
        logger.info("[D] [功能 根据openid获取手机号]")
        req = self.validate_data
        logger_req(req)
        wx_openid = req["wx_openid"]
        manager = TbManager.query.filter_by(wx_openid=wx_openid, is_delete=False).first()
        if not manager:
            logger.info("[D] [phone is not bind wx_openid]")
            return Msg.MANAGER_WECHET_NOT_BINDING, -200
        production = TbProduction.query.filter_by(merchant_code=manager.merchant_code).first()
        if production:
            production_code = production.code
        return {"phone": manager.phone,
                "production_code": production_code or "",
                "merchant_code": manager.merchant_code
                }

    def put(self):
        # 忘记密码，短信验证后修改
        logger.info("[D] [功能 忘记密码-短信验证后修改]")
        req = self.validate_data
        logger_req(req)
        phone = req["phone"]
        code = req["verify_code"]
        new_password = req["new_password"]

        if not verify_code(phone=phone, verify_type=4, verify_code=code):
            logger.info("[D] [verify_code is errors]")
            return Msg.MANAGER_VERIFY_CODE_ERROR, -200
        manager = TbManager.query.filter_by(phone=phone, is_delete=False).first()
        if not manager:
            logger.info("[T] [manager is not find]")
            return Msg.MANAGER_NOT_EXISTS, -200
        manager.password = generate_password(new_password)
        manager.pwd_frozen_time = None
        db.session.commit()
        logger.info("[T] [Update tb_manager where manager_code= {}]"
                    .format(manager.code))

        return ""


class ManagerModifyPassword(BaseResource):
    """
    商户经理修改密码
    """
    validate_schemas = {"put": Schema({
        "old_password": str,
        "new_password": str,
        "verify_password": str,
    })}

    @manager_token_required
    def put(self):
        # 修改商户经理密码
        logger.info("[D] [功能 忘记密码-短信验证后修改]")
        req = self.validate_data
        logger_req(req)
        old_password = req.get("old_password")
        new_password = req.get("new_password")
        verify_password = req.get("verify_password")
        manager = request.current_user
        if new_password != verify_password:
            logger.info("[T] [verify_password is'not new_password ]")
            return Msg.MANAGER_PASSWORD_DIFFERENT, -200
        if not check_password(manager.password, old_password):
            logger.info("[T] [old_password error]")
            return Msg.MANAGER_OLD_PASSWORD_ERROR, -200
        manager.password = generate_password(new_password)
        db.session.commit()
        logger.info("[T] [Update tb_manager where manager_code= {}]"
                    .format(manager.code))
        return ""


class ManagerInfo(BaseResource):
    """
    商户经经经理信息获取和修改
    """
    validate_schemas = {"put": Schema({
        Optional("address"): str,
        Optional("id_img"): str,
        Optional("head_img"): str,
    })}

    @manager_token_required
    def get(self):
        # 获取当前客户经理相关信息
        manager = request.current_user

        data = {
            "name": manager.name,
            "phone": manager.phone,
            "merchant_code": manager.merchant_code,
            "address": manager.address,
            "id_card": manager.id_card,
            "id_img": manager.id_img,
            "head_img": manager.head_img,
        }
        return data

    @manager_token_required
    def put(self):
        # 修改当前客户经理相关信息
        logger.info("[D] [功能 修改当前客户经理相关信息]")
        req = self.validate_data
        logger_req(req)
        manager = request.current_user
        manager.address = req.get("address", manager.address)
        manager.head_img = req.get("head_img", manager.head_img)
        db.session.commit()
        logger.info("[T] [Update tb_manager where manager_code= {}]"
                    .format(manager.code))
        return ""


class FacesignInfo(BaseResource):
    """
    商户经理面签单信息相关
    """
    # 参数校验
    validate_schemas = {"get": Schema({
        Optional("status"): str,
        Optional("username_phone"): str,
        Optional("select_all"): str,
        Optional("time_start"): str,
        Optional("time_end"): str,
        Optional("orderby_time"): str,
        Optional("page", default=1): Use(int),
        Optional("page_size", default=10): Use(int),
    })}

    @manager_token_required
    def get(self):
        # 获取商户面签单信息，抢单之后的信息
        logger.info("[D] [功能 获取商户面签单信息]")
        req = self.validate_data
        logger_req(req)
        manager = request.current_user
        refresh_face_sign(manager.code)
        status = status_to_list(req.get("status"))
        username_phone = req.get("username_phone", "")
        select_all = req.get("select_all", "")
        time_start = req.get("time_start", "")
        time_end = req.get("time_end", "")
        orderby_time = req.get("orderby_time", "")
        try:
            u_p = int(username_phone)
        except ValueError:
            u_p = username_phone
        if isinstance(u_p, int):
            search = (TbFaceSignUser.phone.contains(username_phone))
        else:
            search = (TbFaceSignUser.username.contains(username_phone))
        # 筛选条件
        a = TbFaceSignUser.merchant_code == manager.merchant_code  # 只查当前商户条件
        b = (search) if username_phone else True  # C端用户姓名模糊查询
        c = (TbFaceSignUser.status.in_(status)) if status else (TbFaceSignUser.status != 0)  # 状态status 选择查询
        d = (TbFaceSignUser.manager_code == manager.code) if select_all != "1" else True  # 是否全查询：1为全查询
        e = (TbFaceSignUser.order_time >= time_start) if time_start else True  # 预约起始起始时间
        f = (TbFaceSignUser.order_time <= time_end) if time_end else True  # 预约结束时间
        h = (TbFaceSignUser.update_time) if orderby_time == "1" else (-TbFaceSignUser.update_time)  # 时间正反序
        ke = [a, b, c,  d, e, f]

        facesign = TbFaceSignUser.query.filter(*ke).order_by(h)
        return get_data(facesign, TbFaceSignUser, exclude=["id", "extend"])


class FacesignVerify(BaseResource):
    """
    商户经理面签单审核占比
    """
    # 参数校验
    validate_schemas = {"get": Schema({
        Optional("days"): And(Use(int), lambda x: 0 <= x <= 31),
    })}

    @manager_token_required
    def get(self):
        logger.info("[D] [功能 商户经理面签单审核占比获取]")
        req = self.validate_data
        logger_req(req)
        days = req.get("days") or 30
        time_start = utc_timestamp() - (days*24*60*60)
        time_end = utc_timestamp()
        manager = request.current_user
        # 面签审核条件
        a = TbFaceSignUser.manager_code == manager.code  # 商户编码
        b = (TbFaceSignUser.update_time >= time_start)  # 预约起始起始时间
        c = (TbFaceSignUser.update_time <= time_end)  # 预约结束时间
        d = TbFaceSignUser.status.in_([2, 3, 4])  # 审核总数
        e = TbFaceSignUser.status == 3  # 面签成功
        e_f = TbFaceSignUser.status == 4
        # 扫码量条件
        f = LogLoading.manager_id == manager.code
        g = LogLoading.load_time >= time_start  # 起始时间
        h = LogLoading.load_time >= time_start  # 结束时间
        # 注册量条件
        i = LogRegister.manager_id == manager.code
        j = LogRegister.reg_time >= time_start
        k = LogRegister.reg_time >= time_start
        # 面签总数
        ke = [a, b, c, d]
        all_facesign = TbFaceSignUser.query.filter(*ke).count()
        # 面签审核成功
        ke_p = [a, b, c, e]
        pass_facesign = TbFaceSignUser.query.filter(*ke_p).count()
        # 面签审核失败
        ke_p = [a, b, c, e_f]
        refuse_facesign = TbFaceSignUser.query.filter(*ke_p).count()        
        # 扫码量
        ke_sc = [f, g, h]
        scan_code = LogLoading.query.filter(*ke_sc).count()
        # 注册量
        ke_r = [i, j, k]
        register = LogRegister.query.filter(*ke_r).count()
        return {
            "all_number": all_facesign,
            "pass_number": pass_facesign,
            "refuse_number": refuse_facesign,
            "scan_code_number": scan_code,
            "register_number": register

        }


class RushFacesign(BaseResource):
    """
    客户经理抢单
    """
    validate_schemas = {
        "get": Schema({
            Optional("page", default=1): Use(int),
            Optional("page_size", default=10): Use(int),
            Optional("address_code"): str,
            Optional("time_start"): str,
            Optional("time_end"): str,
            Optional("orderby_time"): str,
        }),
        "put": Schema({
            "facesign_code": str
        })
    }

    @manager_token_required
    def get(self):
        # 刷新商户经理获取抢单列表
        logger.info("[D] [功能 刷新商户经理获取抢单列表]")
        req = self.validate_data
        logger_req(req)
        manager = request.current_user
        refresh_face_sign(manager.code)
        # 筛选条件
        time_start = req.get("time_start", "")
        time_end = req.get("time_end", "")
        address_code = req.get("address_code", "")
        orderby_time = req.get("orderby_time", "")

        a = TbFaceSignUser.merchant_code == manager.merchant_code  # 商户编码
        b = (TbFaceSignUser.order_time >= time_start) if time_start else True  # 预约起始起始时间
        c = (TbFaceSignUser.order_time <= time_end) if time_end else True  # 预约结束时间
        d = (TbFaceSignUser.order_address_code.op("regexp")
             (r"^"+re_address_code(address_code))) if address_code else True  # 省市区筛选
        e = TbFaceSignUser.status == 0  # 状态为待面签条件
        f = (TbFaceSignUser.update_time) if orderby_time == "1" else (-TbFaceSignUser.update_time)  # 时间正反序
        ke = [a, b, c, d, e]
        facesign = TbFaceSignUser.query.filter(*ke).order_by(f)

        return get_data(facesign, TbFaceSignUser, exclude=["id", "manager_code", "manager_name", "extend"])

    @manager_token_required
    def put(self):
        # 抢单动作
        logger.info("[D] [功能 客户经理抢单动作]")
        req = self.validate_data
        logger_req(req)
        manager = request.current_user
        facesign_code = req["facesign_code"]
        facesign = TbFaceSignUser.query.filter_by(code=facesign_code, status=0).first()
        if not facesign:
            logger.info("[T] [The facesign does not exist]")
            return Msg.MANAGER_FACESIGN_NOT_EXIST, -200
        if redis.zadd("support_facesign_order", facesign.update_time, facesign.code) == 0:
            logger.info("[T] [The redis.zadd is fail]")
            return Msg.MANAGER_FACESIGN_NOT_EXIST, -200
        if facesign.status != 0:
            logger.info("[T] [Check status is not 0 ]")
            return Msg.MANAGER_FACESIGN_NOT_EXIST, -200
        try:
            facesign.manager_code = manager.code
            facesign.manager_name = manager.name
            facesign.status = 1
            facesign.update_time = utc_timestamp()
            db.session.commit()
            logger.info("[T] [Update tb_manager where manager_code= {}]"
                        .format(manager.code))
        except Exception as e:
            logger.info("[T] {}".format(str(e)))
            return str(e)
        redis.zremrangebyscore("support_facesign_order", 0, utc_timestamp())
        return get_data(facesign, TbFaceSignUser, exclude=["id", "extend"])
