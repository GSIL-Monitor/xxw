
"""
商户经理管理相关接口
"""

import json
from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from schema import Schema, Optional, And, Use
from src import app, db, redis
from src.commons.constant import Msg
from src.commons.date_utils import utc_timestamp
from src.commons.func import token_required
from src.models.manager import (TbBeServedMerchant, TbManager,
                                TbManagerWorkingAddress)
from src.models.user import TbMerchant
from werkzeug.security import check_password_hash, generate_password_hash
from src.commons.model_resource import get_data, post_data, put_data, BaseResource
from src.commons.logger import logger
# 使用到的方法


def generate_password(password: str) -> str:
    """
    生成密码
    """
    return generate_password_hash(password)


def check_password(old_password: str, new_password: str) -> bool:
    """
    验证密码
    """
    return check_password_hash(old_password, new_password)


def id_gender(id_card):
    gender = int(id_card[-2])
    if gender % 2 == 0:
        return "F"
    return "M"


def logger_req(req):
    for k in req:

        logger.info("[D] [入参 {} = {}]".format(k, req[k]))


class ManagerManage(BaseResource):
    validate_schemas = {
        "get": Schema(
            {
                "merchant_code": str,
                Optional("page", default=1): Use(int),
                Optional("page_size", default=10): Use(int),
                Optional("name"): str,
                Optional("phone"): str,
            }),
        "put": Schema(
            {
                "merchant_code": str,
                "manager_code": str,
                Optional("phone"): str,
                Optional("name"): str,
                Optional("id_img"): str,
                Optional("id_img_back"): str,
                Optional("head_img"): str,
                Optional("id_card"): str,
                Optional("working_address"): list,
                Optional("be_served_merchant"): list,
            }),
        "post": Schema(
            {
                "merchant_code": str,
                "user_code": str,
                "phone": str,
                "name": str,
                Optional("id_card"): str,
                Optional("id_img"): str,
                Optional("id_img_back"): str,
                Optional("head_img"): str,
                Optional("working_address"): list,
                Optional("be_served_merchant"): list,
            }),
        "delete": Schema(
            {
                "merchant_code": str,
                "manager_code": str,
            })}

    def post(self):
        # 新建商户客户经理
        logger.info("[D] [功能 新建商户客户经理]")
        req = self.validate_data
        logger_req(req)
        if not TbMerchant.query.filter_by(code=req["merchant_code"]).first():
            logger.info("[T] [Merchant_code is not find]")
            return Msg.MANAGER_MERCHANT_NOT_EXIST, -200
        if TbManager.query.filter_by(phone=req["phone"]).first():
            logger.info("[T] [phone is used]")
            return Msg.MANAGER_PHONE_EXIST, -200
        
        if req.get("id_card") and TbManager.query.filter_by(merchant_code=req["merchant_code"],id_card=req["id_card"],is_delete=False).first():
            logger.info("[T] [id_card is used]")
            return Msg.MANAGER_IDCARD_EXIST, -200
        # 存经理表
        password = req["phone"][-6:]
        req["password"] = generate_password(password)
        req["creator"] = req["user_code"]
        if req.get("id_card"):
            req["sex"] = id_gender(req["id_card"])  # 根据身份证-2位读取性别
        manager = post_data(json=req, model=TbManager)
        manager.code = str(2000000000 + manager.id)
        db.session.commit()
        logger.info("[T] [Insert into tb_manager is success. code= {} name= {}]"
                    .format(manager.code, manager.name))
        # 存工作地址表
        manager_code = manager.code
        if req.get("working_address"):
            for i in req.get("working_address"):
                working_address = post_data(json=i, model=TbManagerWorkingAddress)
                working_address.manager_code = manager.code
                db.session.commit()
                logger.info("[T] [Insert into tb_manager_working_address is success. manager_code= {}]"
                            .format(working_address.manager_code))
        # 存被服务商户关系表
        if req.get("be_served_merchant"):
            for i in req["be_served_merchant"]:
                be_served_merchant = post_data(json=i, model=TbBeServedMerchant)
                be_served_merchant.manager_code = manager.code
                db.session.commit()
                logger.info("[T] [Insert into tb_manager_served_merchant is success.  manager_code= {}]"
                            .format(be_served_merchant.manager_code))
        return {
                "merchant_code":manager.code
                }

    def get(self):
        # 获取商户经理
        logger.info("[D] [功能 获取商户经理信息]")
        req = self.validate_data
        logger_req(req)
        if req.get("page_size") == -1:
            all = TbManager.query.filter_by(merchant_code=req["merchant_code"], is_delete=False)\
                .order_by(-TbManager.create_time).count()
            managers = TbManager.query.filter_by(merchant_code=req["merchant_code"], is_delete=False)\
                .order_by(-TbManager.create_time)\
                .paginate(page=req["page"], per_page=all)
        else:
            a = (TbManager.phone == req.get("phone")) if req.get("phone") else True
            b = (TbManager.name.contains(req.get("name"))) if req.get("name") else True
            c = TbManager.is_delete == False
            d = TbManager.merchant_code == req["merchant_code"]
            kw = [a, b, c, d]
            try:
                managers = TbManager.query.filter(*kw)\
                    .order_by(-TbManager.create_time)\
                    .paginate(page=req["page"], per_page=req["page_size"])
            except Exception as e:
                logger.info(str(e))
                return str(e), 400
        try:
            data = [
                {
                    "name": i.name,
                    "phone": i.phone,
                    "sex": i.sex,
                    "address": i.address,
                    "merchant_code": i.merchant_code,
                    "create_time": str(i.create_time),
                    "update_time": str(i.update_time),
                    "creator": i.creator,
                    "status": i.status,
                    "id_card": i.id_card,
                    "id_img": i.id_img,
                    "head_img": i.head_img,
                    "id_img_back": i.id_img_back,
                    "code": i.code,
                    "be_served_merchant": get_data(
                        instance=TbBeServedMerchant.query.filter_by(manager_code=i.code),
                        model=TbBeServedMerchant, only=["merchant_code"], pure=True),
                    "working_address": get_data(
                        instance=TbManagerWorkingAddress.query.filter_by(manager_code=i.code),
                        model=TbManagerWorkingAddress, exclude=["id"], pure=True)
                }
                for i in managers.items
            ]
        except Exception as e:
            logger.info(str(e))
            return str(e), 400
        return {
            "total": managers.total,
            "pages": managers.pages,
            "page": managers.page,
            "page_size": managers.per_page,
            "results": data
        }

    def put(self):
        # 编辑商户经理

        logger.info("[D] [功能 编辑商户经理信息]")
        req = self.validate_data
        logger_req(req)
        manager = TbManager.query.filter_by(merchant_code=req["merchant_code"],
                                            code=req["manager_code"], is_delete=False).first()
        if not manager:
            logger.info("[T] [Merchant_code is not find]")
            return Msg.MANAGER_NOT_EXISTS, -200
        phone = req.get("phone")
        id_card = req.get("id_card")
        if phone and phone != manager.phone and TbManager.query.filter_by(phone=phone, is_delete=False).first():
            logger.info("[T] [phone is used]")
            return Msg.MANAGER_PHONE_EXIST, -200
        if id_card and id_card != manager.id_card and TbManager.query.\
        filter_by(merchant_code=manager.merchant_code,id_card=id_card, is_delete=False).first():
            logger.info("[T] [id_card is used]")
            return Msg.MANAGER_IDCARD_EXIST, -200
        manager = put_data(instance=manager, json=req, model=TbManager)
        # 修改经理服务商户信息
        if req.get("be_served_merchant"):
            # 删除之前信息再新增
            delete_served_merchant = TbBeServedMerchant.query.filter_by(manager_code=manager.code)
            for i in delete_served_merchant:
                db.session.delete(i)
                db.session.commit()
                logger.info("[T] [Delete from tb_manager_served_merchant where manager_code= {}]".format(manager.code))
            for i in req.get("be_served_merchant"):
                be_served_merchant = post_data(json=i, model=TbBeServedMerchant)
                be_served_merchant.manager_code = manager.code
                db.session.commit()
                logger.info("[T] [Update tb_manager_served_merchant where manager_code= {}]".format(manager.code))
        # 修改工作地址表信息
        if req.get("working_address"):
            manager_delete_address = TbManagerWorkingAddress.query.filter_by(manager_code=manager.code)
            for i in manager_delete_address:
                db.session.delete(i)
                db.session.commit()
                logger.info("[T] [Delete from tb_manager_working_address where manager_code= {}]".format(manager.code))
            for i in req.get("working_address"):
                working_address = post_data(json=i, model=TbManagerWorkingAddress)
                working_address.manager_code = manager.code
                db.session.commit()
                logger.info("[T] [Update tb_manager_working_address where manager_code= {}]".format(manager.code))
        db.session.commit()
        return ""

    def delete(self):
        # 删除客户经理
        logger.info("[D] [功能 删除商户经理]")
        req = self.validate_data
        logger_req(req)
        merchant_code = req.get("merchant_code")
        manager_code = req.get("manager_code")
        manager = TbManager.query.filter_by(code=manager_code, merchant_code=merchant_code, is_delete=False).first()
        if not manager:
            logger.info("[T] [Merchant_code is not find]")
            return Msg.MANAGER_NOT_EXISTS, -200
        manager.is_delete = True
        manager.phone = None
        db.session.commit()
        logger.info("[T] [Update tb_manager where manager_code= {}]".format(manager.code))
        return ""


class ResetManagerPassword(BaseResource):
    validate_schemas = {
        "put": Schema({
            "manager_code": str,
            "merchant_code": str
        })
    }

    def put(self):
        # 重置商户经理密码
        req = self.validate_data
        manager_code = req.get("manager_code")
        merchant_code = req.get("merchant_code")
        manager = TbManager.query.filter_by(merchant_code=merchant_code, code=manager_code, is_delete=False).first()
        if not manager:
            return Msg.MANAGER_NOT_EXISTS, -200
        manager.password = generate_password("123456")
        db.session.commit()
        return ""
