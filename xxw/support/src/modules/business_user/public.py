"""
一些公共的查询接口
author: roywu
create at: 2018-08-24 14:29
"""

from schema import Schema, And, Optional
from flask import request
from flask_restful import Resource

from src import db
from src.commons.logger import logger
from src.commons.constant import Msg
from src.commons.utils import validate_schema
from src.commons.func import appid_required, token_required, token_appid_permission_required
from src.models.user import TbBusiness, TbMenu, TbMerchant, TbProduction, TbUser, TbOperation, TbMerchantBusiness
from src.modules.business_user.parser import query_production, verify_interface
from src.modules.business_user.util import get_business_code


# 公共接口-查询已启用的业务系统
class BusinessInquire(Resource):
    """
    查询已启用的业务系统
    """

    @token_appid_permission_required
    def get(self):
        # 返回对应的商户的业务系统, 已启用的业务系统
        user = request.current_user
        biz = TbBusiness.query.filter_by(status=1).order_by(TbBusiness.id.desc())
        result = [{"id": i.code, "name": i.name} for i in biz]
        if not user.is_admin:
            # 非 admin 用户只能查看所在商户除用户中心以外的业务系统
            mer_bizs = TbMerchantBusiness.query.filter(
                TbMerchantBusiness.merchant_code == user.merchant_code,
                TbMerchantBusiness.business_code != get_business_code()).all()
            mer_bizs = sorted(mer_bizs, key=lambda x: x.business_code)
            result = [{"id": i.business_code, "name": i.business_name} for i in mer_bizs]
        return {"result": result}, 200


# 公共接口 - 用户菜单
class UserMenu(Resource):
    @token_appid_permission_required
    def get(self):
        user = request.current_user
        appid = request.headers["Appid"]
        biz = TbBusiness.query.filter_by(appid=appid).first()
        roles = user.roles
        menus = sorted([j for i in roles for j in i.menu if i.business.id == biz.id], key=lambda x: x.id)
        if user.is_admin:
            menus = TbMenu.query.filter(TbMenu.business.has(appid=appid)).order_by(TbMenu.id).all()
        return {
            "name": user.name,
            "merchantId": str(user.merchant.code) if user.merchant else None,
            "merchantName": user.merchant.name if user.merchant else None,
            "menu": [{"id": str(i.code), "name": i.name, "path": i.path} for i in menus],
            "businessName": biz.name,
            "businessId": str(biz.code),
            "userId": user.code,
            "icon_no_word": user.merchant.icon_no_word if user.merchant else ""
        }, 200


class MerchantProduction(Resource):

    # 商户 code 查询所有的 产品
    def get(self):
        schema = Schema({
            Optional("merchant_code"): str
        })
        req, error = validate_schema(schema, request.args.to_dict())
        if error:
            return error, 400
        merchant_code = req.get("merchant_code")
        if merchant_code:
            mer = TbMerchant.query.filter_by(code=merchant_code).first()
            if not mer:
                return Msg.MERCHANT_NOT_EXIST, 400
            results = [{"production_code": i.code, "production_name": i.name} for i in mer.production]
        else:
            production = TbProduction.query.filter_by().all()
            results = [{"production_code": i.code, "production_name": i.name} for i in production]
        return {"results": results}, 200
        

class Production(Resource):

    def get(self):
        """获取产品列表"""
        req = query_production.parse_args(strict=True)
        condition = []
        if req.get("merchant_code"):
            condition.append(TbMerchant.code == req["merchant_code"])
        merchants = TbMerchant.query.filter(*condition).paginate(page=req["page"], per_page=req["page_size"])
        return {
            "results": [{
                "merchant_name": i.name,
                "merchant_code": i.code,
                "production": [{
                    "production_code": j.code,
                    "production_name": j.name,
                    "appkey": j.sms_appkey,
                    "appid": j.sms_appid,
                    "sign": j.sms_sign
                } for j in i.production]
            } for i in merchants.items],
            "total": merchants.total
        }, 200

    @token_required
    def put(self):
        """更新产品信息"""
        schema = Schema({
            "production_code": And(str),
            "appkey": And(str),
            "appid": And(str),
            "sign": And(str)
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        production = TbProduction.query.filter_by(code=req["production_code"]).first()
        if not production:
            return Msg.PRODUCTION_NOT_EXIST, 400
        production.sms_appkey = req["appkey"]
        production.sms_appid = req["appid"]
        production.sms_sign = req["sign"]
        msg = "SUPPORT | B_USER | UPDATE_PRODUCTION | SUCCESS | EDITOR: {} {} | PRODUCTION: {} {} | MERCHANT: {} {}".\
            format(request.current_user.code, request.current_user.name, production.code, production.name,
                   production.merchant.code, production.merchant.name)
        operation = TbOperation(operator_code=request.current_user.code,
                                content=msg,
                                category="PRODUCTION",
                                type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200


class VerifyToken(Resource):
    @token_required
    def get(self):
        token_data = request.token
        user = request.current_user
        return {
            "user_id": user.code,
            "exp_time": token_data["exp_time"],
            "user_name": user.name,
            "is_admin": user.is_admin,
            "merchant_name": user.merchant.name if user.merchant else "",
            "merchant_code": user.merchant.code if user.merchant else ""}, 200


class VerifyInterface(Resource):

    @token_required
    def post(self):
        """
        验证用户接口权限
        """
        req = verify_interface.parse_args(strict=True)
        user = request.current_user
        if user.is_admin:
            return {}, 200
        else:
            user_interface = [(j.path, j.method) for i in user.roles for j in i.interface]
            if (req["interface"], req["method"]) in user_interface:
                return {}, 200
            else:
                return Msg.USER_FORBIDDEN, 403


class UsersDetail(Resource):

    def post(self):
        """
        通过接受一个用户 code 列表，传递出数据
        """
        schema = Schema({
            "users": [str]
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        users_codes = req["users"]
        if len(users_codes) > 10:
            return {}, 200
        users = TbUser.query.filter(TbUser.code.in_(users_codes)).all()
        return {"results": [{
            "user_name": i.name,
            "user_code": i.code,
            "phone": i.phone,
            "merchant_name": i.merchant.name if i.merchant else "",
            "merchant_code": i.merchant.code if i.merchant else ""} for i in users]}, 200


class MerchantsDetail(Resource):

    def post(self):
        """
        通过接受一个商户 code 列表，返回商户详情数据
        """
        schema = Schema({
            Optional("merchants"): [str]
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        merchant_code = req.get("merchants")
        if not merchant_code:
            merchants = TbMerchant.query.all()
        else:
            merchants = TbMerchant.query.filter(TbMerchant.code.in_(merchant_code)).all()
        results = []
        for i in merchants:
            mer_biz = TbMerchantBusiness.query.filter_by(merchant_code=i.code).all()
            results.append({
                "merchant_code": i.code,
                "merchant_name": i.name,
                "production": [{"production_name": j.name, "production_code": j.code} for j in i.production],
                "business": [{
                    "business_code": j.business_code,
                    "business_name": j.business_name,
                    "domain": j.domain
                } for j in mer_biz]
            })
        return {"results": results}, 200


class BuzInterMe(Resource):
    """
    获取该业务系统下用户能访问的接口和菜单
    """

    @token_required
    @appid_required
    def get(self):
        appid = request.headers["Appid"]
        biz = TbBusiness.query.filter_by(appid=appid).first()
        user = request.current_user
        if user.is_admin:
            menu = biz.menu
        else:
            roles = user.roles
            menu = [j for i in roles for j in i.menu if i.business.id == biz.id]
        menu.sort(key=lambda x: x.id)
        return {
            "menu": [{"id": i.code, "name": i.name, "path": i.path} for i in menu]
        }, 200
