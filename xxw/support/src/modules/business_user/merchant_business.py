"""
商户和业务系统管理
author: roywu
create at: 2018-08-24 14:41
"""

from schema import Schema, And
from flask import request
from flask_restful import Resource
from uuid import uuid4
from src import db, app, logger
from src.commons.utils import validate_schema
from src.commons.constant import Msg
from src.commons.func import token_appid_permission_required, redis_delete
from src.models.user import TbBusiness, TbMerchant, TbProduction, TbMerchantBusiness, TbOperation, TbRole, TbUser
from src.modules.business_user.parser import (obtain_mer_biz, biz_query, add_biz, edit_biz, active_biz, asign_appid,
                                              mer_query)


# 获取商户名和系统名
class MerBizName(Resource):
    def get(self):
        req = obtain_mer_biz.parse_args(strict=True)
        domain = req.get("domain")
        appid = req["appid"]
        mer_biz = TbMerchantBusiness.query.filter_by(domain=domain).first()
        biz = TbBusiness.query.filter_by(appid=appid).first()
        alias = biz.name
        if mer_biz:
            alias = mer_biz.alias or alias
        if not biz:
            return Msg.BUSINESS_NOT_EXIST, 400
        return {
            "merchantName": mer_biz.merchant_name if mer_biz else None,
            "businessName": alias,
            "logo": mer_biz.logo if mer_biz else None}, 200


# 业务接入管理
class BusinessViewSet(Resource):

    # 业务接入管理 - 查询
    @token_appid_permission_required
    def get(self):
        req = biz_query.parse_args(strict=True)
        page = req["page"]
        count = req["count"]
        name = req.get("name")
        user = request.current_user
        condition = [TbBusiness.name.contains("%{}%".format(name if name else ""))]
        if not user.is_admin:
            condition.append(TbMerchant.code == user.merchant.code)
        biz = TbBusiness.query.filter(*condition).order_by(TbBusiness.id.desc()).paginate(page=page, per_page=count)
        return {
            "result": [{"id": str(i.code), "name": i.name, "appid": i.appid, "status": i.status} for i in biz.items],
            "total": biz.total,
        }, 200

    # 添加业务系统
    @token_appid_permission_required
    def post(self):
        req = add_biz.parse_args(strict=True)
        user = request.current_user
        name = req["name"]
        appid = req["appid"]
        if TbBusiness.query.filter_by(name=name).first():
            return Msg.BUSINESS_NAME_ALREADY_EXIST, 400
        business = TbBusiness(name=name, appid=str(uuid4()).replace("-", "") if appid else None, creator=user)
        if user.merchant:
            mer_biz = TbMerchantBusiness(
                merchant_code=user.merchant.code,
                business_code=business.code
            )
            db.session.add(mer_biz)
            business.merchant.add(user.merchant)
        db.session.add(business)
        db.session.commit()
        business.code = str(business.id + 1200000000)
        msg = "SUPPORT | B_USER | ADD_BUSINESS | SUCCESS | USER: {} {} | BUSINESS: {} {}".format(
            user.code, user.name, business.code, business.code, business.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="BUSINESS", type="ADD")
        db.session.add(operation)
        db.session.commit()
        app.logger.info(msg)
        return {}, 200

    # 编辑业务系统
    @token_appid_permission_required
    def put(self):
        req = edit_biz.parse_args(strict=True)
        bid = req["id"]
        name = req["name"]
        appid = req.get("appid")
        # 业务系统不允许重名
        # 查询一下这个 name 存不存在
        if name and TbBusiness.query.filter(TbBusiness.name == name, TbBusiness.code != bid).first():
            return Msg.BUSINESS_NAME_ALREADY_EXIST, 400
        business = TbBusiness.query.filter_by(code=bid).first()
        if not business:
            return Msg.BUSINESS_NOT_EXIST, 400
        business.name = name
        business.appid = str(uuid4()).replace("-", "") if appid else business.appid
        msg = "SUPPORT | B_USER | EDIT_BUSINESS | SUCCESS | USER: {} {} | BUSINESS: {} {}".format(
            request.current_user.code, request.current_user.name, business.code, business.name)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="BUSINESS", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        app.logger.info(msg)
        return {}, 200


# 业务接入管理 - 激活或禁用业务系统
class ActiveBusiness(Resource):
    @token_appid_permission_required
    def put(self):
        req = active_biz.parse_args(strict=True)
        business = TbBusiness.query.filter_by(code=req["id"]).first()
        if not business:
            return Msg.BUSINESS_NOT_EXIST, 400
        if not business.appid:
            return Msg.ASSIGN_APPID_FIRST, 400
        business.status = req["status"]
        msg = "SUPPORT | B_USER | ACTIVE_BUSINESS | SUCCESS | USER: {} {} | BUSINESS: {} {} | STATUS: {}".format(
            request.current_user.code, request.current_user.name, business.code, business.name, req["status"])
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="BUSINESS", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        app.logger.info(msg)
        return {}, 200


# 业务接入管理 - 分配 appid
class BusinessAppid(Resource):
    @token_appid_permission_required
    def put(self):
        req = asign_appid.parse_args(strict=True)
        business = TbBusiness.query.filter_by(code=req["id"]).first()
        if not business:
            return Msg.BUSINESS_NOT_EXIST, 400
        business.appid = str(uuid4()).replace("-", "") if not business.appid else business.appid
        msg = "SUPPORT | B_USER | ASSIGN_APPID | SUCCESS | USER: {} {} | BUSINESS: {} {}".format(
            request.current_user.code, request.current_user.name, business.code, business.code, business.name)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="BUSINESS", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        app.logger.info(msg)
        return {}, 200


# 商户管理
class MerchantManage(Resource):
    @token_appid_permission_required
    def get(self):
        req = mer_query.parse_args(strict=True)
        page, count, name, production = (req["page"], req["count"], req.get("name"), req.get("production"))
        merchant = (
            TbMerchant.query.filter(
                TbMerchant.name.contains("%{}%".format(name if name else ""))
            )
            .order_by(TbMerchant.id.desc()).all()
        )
        if production:
            merchant = [i for i in merchant for j in i.production if production in j.name]
        total = len(merchant)
        return {
            "result": [{
                "id": i.code,
                "name": i.name,
                "production": " ".join([j.name for j in i.production]),
                "domains": [{
                    "businessId": j.business_code,
                    "businessName": j.business_name,
                    "domain": j.domain,
                    "domainId": j.id,
                } for j in TbMerchantBusiness.query.filter_by(merchant_code=i.code).all()
                ],
            } for i in merchant[(page-1)*count: count*page]],
            "total": total
        }, 200

    @token_appid_permission_required
    def post(self):
        schema = Schema({"name": And(str, len), "production": And(str, len)})
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        name = req["name"]
        if TbMerchant.query.filter_by(name=name).first():
            return Msg.MERCHANT_NAME_ALREADY_EXIST, 400
        mer = TbMerchant(name=name)
        db.session.add(mer)
        db.session.commit()
        mer.code = "{:08}".format(mer.id)
        pro = TbProduction(name=req["production"], merchant_code=mer.code, status=True)
        mer.production.append(pro)
        db.session.add(pro)
        db.session.commit()
        pro.code = str(pro.id + 1600000000)
        msg = "SUPPORT | B_USER | ADD_MERCHAT | SUCCESS | USER: {} {} | MERCHAT: {} {} | PRODUCTION: {} {}".format(
            request.current_user.code, request.current_user.name, mer.code, mer.name, pro.code, pro.name)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="MERCHANT", type="ADD")
        db.session.add(operation)
        db.session.commit()
        app.logger.info(msg)
        return {}, 200

    @token_appid_permission_required
    def put(self):
        schema = Schema({"id": And(str), "name": And(str, len), "production": And(str, len)})
        req, error = validate_schema(schema, request.json, remove_blank=True)
        if error:
            return error, 400
        mer = TbMerchant.query.filter_by(code=req["id"]).first()
        dup_mer = TbMerchant.query.filter_by(name=req["name"]).first()
        if dup_mer and dup_mer.code != mer.code:
            return Msg.MERCHANT_NAME_ALREADY_EXIST, 400
        mer.name = req["name"]
        production = TbProduction.query.filter_by(merchant_code=req["id"]).first()
        if not production:
            return Msg.PRODUCTION_NOT_EXIST, 400
        production.name = req.get("production")
        msg = "SUPPORT | B_USER | EDIT_MERCHAT | SUCCESS | USER: {} {} | MERCHAT: {} {} | PRODUCTION: {} {}".format(
            request.current_user.code, request.current_user.name, mer.code, mer.name, production.code, production.name)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="MERCHANT", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        app.logger.info(msg)
        # 删除 redis 商户的缓存
        key = "tb_merchant:code:{}".format(mer.code)
        redis_delete(key)
        # 删除 redis 产品的缓存
        key = "tb_production:merchant_code:{}".format(mer.code)
        redis_delete(key)
        return {}, 200


# 商户管理 - 分配系统
class MerchantSystem(Resource):
    @token_appid_permission_required
    def put(self):
        schema = Schema({
            "id": And(str),
            "system": [{
                "domain": And(str, len),
                "businessId": And(str)
            }]
        })
        req, error = validate_schema(schema, request.json, remove_blank=True)
        if error:
            return error, 400
        mer = TbMerchant.query.filter_by(code=req["id"]).first()
        if not mer:
            return Msg.MERCHANT_NOT_EXIST, 400
        input_biz_codes = [i["businessId"] for i in req["system"]]
        domains = set(i["domain"] for i in req["system"])
        if len(domains) != len(input_biz_codes):
            return Msg.DOMAIN_DUNPLICATE, 400
        # 检测域名是否重复
        if TbMerchantBusiness.query.filter(
                TbMerchantBusiness.domain.in_(domains),
                TbMerchantBusiness.merchant_code != req["id"]).first():
            return Msg.DOMAIN_ALREADY_EXIST, 400
        # 获取所有的用户以添加的业务系统
        mer_bizs = TbMerchantBusiness.query.filter_by(merchant_code=mer.code).all()
        # 该商户下所有用户
        users = TbUser.query.filter_by(merchant_code=mer.code).all()
        # 该商户下所有角色
        roles = TbRole.query.filter_by(merchant_code=mer.code).all()
        # 检测录入的系统是否有删除的
        for i in mer_bizs:
            if i.business_code not in input_biz_codes:
                # 对应删除该商户下业务系统下的角色和用户授权的角色
                for role in roles:
                    if role.business_code == i.business_code:
                        db.session.delete(role)
                for user in users:
                    user_roles = user.roles
                    for role in user_roles:
                        if role.business_code == i.business_code:
                            user.roles.remove(role)
                db.session.delete(i)
        mer_biz_list = []
        for i in req["system"]:
            biz = TbBusiness.query.filter_by(code=i["businessId"]).first()
            if not biz:
                return Msg.BUSINESS_NOT_EXIST, 400
            mer_biz = TbMerchantBusiness.query.filter_by(business_code=biz.code, merchant_code=mer.code).first()
            if not mer_biz:
                new_mer_biz = TbMerchantBusiness(
                    domain=i["domain"],
                    business_code=biz.code,
                    merchant_code=mer.code,
                    merchant_name=mer.name,
                    business_name=biz.name
                )
                mer_biz_list.append(new_mer_biz)
            else:
                mer_biz.domain = i["domain"]
        try:
            db.session.add_all(mer_biz_list)
            msg = "SUPPORT | B_USER | ASSGIN_BUSINESS | SUCCESS | USER: {} {} | MERCHANT: {} {} | BUSINESS {}".format(
                request.current_user.code, request.current_user.name, mer.code, mer.name, req["system"])
            operation = TbOperation(operator_code=request.current_user.code,
                                    content=msg,
                                    category="MERCHANT BUSINESS",
                                    type="EDIT")
            db.session.add(operation)
            db.session.commit()
            logger.info(msg)
            return {}, 200
        except Exception as e:
            app.logger.warn("""SUPPORT | B_USER | ASSGIN_BUSINESS |
                               FAILED | USER: {} {} | MERCHANT: {} {} | ERROR: {}""".format(
                request.current_user.code, request.current_user.name, mer.code, mer.name, str(e)))
            db.session.rollback()
            return Msg.ASSIGN_FAILED, 400
