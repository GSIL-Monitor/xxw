
"""
商户及其产品相关接口
"""

from datetime import datetime
from schema import Schema, And, Optional
from flask import request
from flask_restful import Resource, reqparse
from src import db, logger
from src.commons.constant import Msg
from src.commons.push_merchant import push_merchant
from src.models.user import TbMerchant, TbProduction, TbMerchantBusiness, TbOperation, TbMerchantPublic, TbUser
from src.commons.model_resource import ModelSchemaResource, get_data
from src.commons.utils import validate_schema
from src.commons.func import redis_delete

put_merchant_info = reqparse.RequestParser()
put_merchant_info.add_argument("merchant_code", location="json",  type=str,  trim=True, required=True)
put_merchant_info.add_argument("xw_code", location="json",  type=str,  trim=True, required=True)
put_merchant_info.add_argument("iba_loan_no", location="json",  type=str,  trim=True, required=True)
put_merchant_info.add_argument("iba_loan_name", location="json",  type=str, trim=True, required=True)
put_merchant_info.add_argument("iba_collection_no", location="json",  type=str, trim=True, required=True)
put_merchant_info.add_argument("iba_collection_name", location="json",  type=str, trim=True, required=True)
put_merchant_info.add_argument("iba_pre_deposit_no", location="json",  type=str, trim=True, required=True)
put_merchant_info.add_argument("iba_pre_deposit_name", location="json",  type=str, trim=True, required=True)
put_merchant_info.add_argument("org_no", location="json",  type=str, trim=True, required=True,)
put_merchant_info.add_argument("name", location="json",  type=str, trim=True)
put_merchant_info.add_argument("is_active", location="json",  type=str, trim=True)
put_merchant_info.add_argument("logo", location="json",  type=str, trim=True)
put_merchant_info.add_argument("icon", location="json",  type=str, trim=True)
put_merchant_info.add_argument("logo_no_word", location="json",  type=str, trim=True)
put_merchant_info.add_argument("icon_no_word", location="json",  type=str, trim=True)
put_merchant_info.add_argument("url", location="json",  type=str, trim=True)
put_merchant_info.add_argument("area_code", location="json",  type=str, trim=True)
put_merchant_info.add_argument("area_name", location="json",  type=str, trim=True)
put_merchant_info.add_argument("email", location="json",  type=str, trim=True)
put_merchant_info.add_argument("email_client", location="json",  type=str, trim=True)
put_merchant_info.add_argument("email_password", location="json",  type=str, trim=True)
put_merchant_info.add_argument("sys_url", location="json",  type=str, trim=True)
put_merchant_info.add_argument("push_flag", location="json",  type=str, trim=True)


class MerchantInfo(ModelSchemaResource):
    """
    商户管理相关接口
    """
    model = TbMerchant

    filter_fields = [["name", "contains", "name", str],
                     ["code", "==", "code", str], ]

    exclude = ["users", "business", "credit_interface", "domains", 'production', "roles", "id", "extra"]

    validate_schemas = {"put": put_merchant_info, "strict": True}
    
    def get(self):
        # 获取商户信息
        merchant_code = request.args.get("merchant_code")
        if merchant_code:
            merchant = TbMerchant.query.filter_by(code=merchant_code).first()
            if not merchant:
                return Msg.MERCHANT_NOT_EXIST, 400
            data = self.detail_schema.dump(merchant).data
            production = TbProduction.query.filter_by(merchant_code=merchant_code)
            data["production"] = [
                {"production_name": i.name, "production_code": i.code}
                for i in production]
            return {"results": data}
        return super().get()

    def put(self):
        req = self.validate_data
        core_req = request.json
        if not core_req.get("xw_code") and core_req.get("org_no")\
                and core_req.get("iba_loan_no") and core_req.get("iba_loan_name")\
                and core_req.get("iba_collection_no")and core_req.get("iba_collection_name")\
                and core_req.get("iba_pre_deposit_no") and core_req.get("iba_pre_deposit_name"):
            return "信贷核心相关参数为空", 400
        # 修改指定商户信息
        merchant_code = req["merchant_code"]
        merchant = TbMerchant.query.filter_by(code=merchant_code).first()
        if not merchant:
            return Msg.MERCHANT_NOT_EXIST, 400
        instance, errors = self.detail_schema.load(req, instance=merchant, partial=True)
        if errors:
            return (400, errors)
        if getattr(instance, "update_time", None):
            instance.update_time = int(datetime.utcnow().timestamp())
        db.session.commit()
        msg = "SUPPORT | MERCHANT | EDIT_INFO | SUCCESS | MERCHANT_CAODE: {} | MERCHANT_NAME: {}".format(
            merchant.code, merchant.name)
        logger.info(msg)
        status, error = push_merchant(merchant)
        if status is False:
            return "商户推送失败， 失败原因: " + error, 400
        data = self.detail_schema.dump(instance).data
        return data


class MerchantProductionFlag(Resource):
    """
    商户产品相关接口
    """
    model = TbProduction
    exclude = ["merchant", "id"]

    def get(self):
        # 获取商户产品开关列表
        merchant_code = request.args.get("merchant_code")
        if merchant_code:
            merchant = TbMerchant.query.filter_by(code=merchant_code).first()
            if not merchant:
                return Msg.MERCHANT_NOT_EXIST, 400
            production = TbProduction.query.filter_by(merchant_code=merchant_code)
            return get_data(production, TbProduction, exclude=self.exclude)
        return "缺少必须参数", 400

    def put(self):
        # 修改产品开关
        merchant_code = request.json.pop("merchant_code", None)
        production_code = request.json.pop("production_code", None)
        production_flag = request.json.pop("production_flag", None)
        request.json.pop("id", None)
        production = TbProduction.query.filter(TbProduction.code == production_code,
                                               TbMerchant.code == merchant_code).first()
        if not production:
            return Msg.PRODUCTION_NOT_EXIST, 400
        if not isinstance(production_flag, bool):
            return "参数错误", 400
        production.status = production_flag
        # 删除 redis 产品的缓存
        appid_key = "tb_production:merchant_code:{}".format(production.merchant_code)
        redis_delete(appid_key)
        db.session.commit()
        return get_data(production, TbProduction, exclude=self.exclude)


class MerchantBusines(Resource):
    """
    商户业务系统管理
    """

    def get(self):
        """
        获取商户业务系统信息
        """
        mer_code = request.args.get("merchant_code")
        if not mer_code:
            return "missing merchant_code in args", 400
        mer = TbMerchant.query.filter_by(code=mer_code).first()
        if not mer:
            return Msg.MERCHANT_NOT_EXIST, 400
        mer_biz = TbMerchantBusiness.query.filter_by(merchant_code=mer.code).all()
        return {
            "results": [{
                "business_name": i.business_name,
                "business_code": i.business_code,
                "alias": i.alias,
                "logo": i.logo if i.logo else ""
            } for i in mer_biz]
        }, 200

    def put(self):
        """
        对商户业务系统进行修改
        业务系统别名
        业务系统 logo
        """
        schema = Schema({
            "business": [{
                "business_code": And(str),
                "business_name": And(str),
                "alias": And(str),
                "logo": And(str)}],
            "merchant_code": And(str),
            "user_code": And(str)}
        )
        req, error = validate_schema(schema, request.json, remove_blank=True)
        if error:
            return error, 400
        query_set = TbMerchantBusiness.query.filter_by(merchant_code=req["merchant_code"])
        for i in req["business"]:
            biz_code = i["business_code"]
            mer_biz = query_set.filter_by(business_code=biz_code).first()
            if not mer_biz:
                return Msg.MERCHANT_BUSINESS_NOT_EXIST, 400
            mer_biz.alias = i["alias"]
            mer_biz.logo = i["logo"]
        msg = "SUPPORT | MARCHANT_MANAGE | EDIT_MARCHANT_BUSINESS | SUCCESS | USER: {} | BUSINESS: {}".format(
            req["user_code"], [(i["business_name"], i["alias"]) for i in req["business"]])
        operation = TbOperation(operator_code=req["user_code"], content=msg, type="EDIT", category="MARCHANT_MANAGE")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200


class MerchantProductionInfo(Resource):
    """
    商户商品信息
    """

    def get(self):
        """
        查询商户产品信息
        """

        schema = Schema({"merchant_code": str})
        req, error = validate_schema(schema, request.args.to_dict())
        if error:
            return error, 400
        mer = TbMerchant.query.filter_by(code=req["merchant_code"]).first()
        if not mer:
            return Msg.MERCHANT_NOT_EXIST, 400
        results = []
        for i in mer.production:
            official_account = TbMerchantPublic.query.filter_by(production_code=i.code).first()
            results.append({
                "name": i.name,
                "code": i.code,
                "logo": i.logo or "",
                "icon": i.icon or "",
                "face_flag": i.face_flag,
                "e_sign": i.e_sign,
                "amount_limit": i.amount_limit,
                "appid": official_account.appid if official_account else "",
                "official_account_name": official_account.name if official_account else ""
            })
        return {"results": results}, 200

    def put(self):
        """
        更新产品信息
        """
        schema = Schema({
            "production": [{
                Optional("appid"): And(str),
                Optional("official_account_name"): And(str),
                Optional("amount_limit"): And(int),
                "name": And(str),
                "code": And(str),
                "logo": And(str),
                "icon": And(str),
                "face_flag": And(bool),
                "e_sign": And(bool)}],
            "merchant_code": And(str),
            "user_code": And(str)}
        )
        req, error = validate_schema(schema, request.json, remove_blank=True)
        if error:
            return error, 400
        user = TbUser.query.filter_by(code=req["user_code"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        query_set = TbProduction.query.filter_by(merchant_code=req["merchant_code"])
        for i in req["production"]:
            pro = query_set.filter_by(code=i["code"]).first()
            if not pro:
                return Msg.PRODUCTION_NOT_EXIST, 400
            # 如果用户传了 appid
            if i.get("appid"):
                if TbMerchantPublic.query.filter(
                        TbMerchantPublic.production_code != pro.code, TbMerchantPublic.appid == i["appid"]).first():
                    return Msg.OFFICIAL_ACCOUNT_ALREADY_EXIST, 400
                public = TbMerchantPublic.query.filter_by(production_code=pro.code).first()
                # 如果没有检测到公众号，就创建一个，否则进行一次修改
                if not public:
                    pub = TbMerchantPublic(
                        name=i.get("official_account_name"),
                        appid=i["appid"],
                        creator_code=user.code,
                        merchant_code=req["merchant_code"],
                        production_code=pro.code)
                    db.session.add(pub)
                else:
                    public.appid = i["appid"]
                    public.name = i.get("official_account_name")
                    # 删除 redis 公众号的缓存
                    appid_key = "merchant_public:appid:{}".format(i.get("appid"))
                    redis_delete(appid_key)
            pro.name = i["name"]
            pro.logo = i["logo"]
            pro.icon = i["icon"]
            pro.face_flag = i["face_flag"]
            pro.e_sign = i["e_sign"]
            pro.amount_limit = i.get("amount_limit") if i["face_flag"] else 0
            # 删除 redis 产品的缓存
            pro_key = "tb_production:merchant_code:{}".format(req["merchant_code"])
            redis_delete(pro_key)
        msg = "SUPPORT | PRODUCTION | EDIT_PRODUCTION | SUCCESS | USER: {} {} | PRODUCTION: {}".format(
                user.code, user.name, req["production"], )
        try:
            operation = TbOperation(operator_code=req["user_code"], content=msg, type="EDIT", category="PRODUCTION")
            db.session.add(operation)
            db.session.commit()
            logger.info(msg)
            return {}, 200
        except Exception as e:
            logger.warn("SUPPORT PRODUCTION | EDIT_PRODUCTION | FAILED | USER: {} {} | ERROR: {}".format(
                user.code, user.name, str(e)))
            db.session.rollback()
            return Msg.UPDATE_PRODUCTION_FAILED, 400
