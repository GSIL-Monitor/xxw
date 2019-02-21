import json
from flask import request
from flask_restful import Resource, reqparse
from src.commons.model_resource import get_data, BaseResource
from schema import Schema, Optional, And, Use
from src.models.log_db import  LogCase 
from src.commons.logger import logger
from src.commons.manager_utils import logger_req


class CaseListInfo(BaseResource):
    """案件信息-列表"""
    validate_schemas = {"get": Schema({
        Optional("merchant_code"): str,
        Optional("phone"): Use(int),
        Optional("name"): str,
        Optional("case_type"): str,
        Optional("id_card"): str,
        Optional("time_start"): str,
        Optional("time_end"): str,
        Optional("page", default=1): Use(int),
        Optional("page_size", default=10): Use(int),
        Optional("trx"): str,
        Optional("production_code"): str,         
    })}
    def get(self):
        logger.info("[D] [功能 案件信息展示]")
        req = self.validate_data
        logger_req(req)
        phone = req.get("phone","") 
        name = req.get("name","") 
        case_type = req.get("case_type")
        id_card = req.get("id_card")  
        merchant_code = req.get("merchant_code")              
        time_start = req.get("time_start","") 
        time_end = req.get("time_end","")
        trx = req.get("trx","")
        production_code = req.get("production_code","") 

        #筛选
        a = LogCase.merchant_code == merchant_code if merchant_code else True  # 商户编码
        b = LogCase.phone == phone if phone else True # 电话号码
        c = LogCase.name.contains(name) if name else True # 用户姓名模糊查询
        d = LogCase.case_type == case_type if case_type else True # 事件类型
        e = LogCase.id_card == id_card if id_card else True # 身份证
        f = (LogCase.trigger_time >= time_start) if time_start else True  # 起始起始时间
        g = (LogCase.trigger_time <= time_end) if time_end else True  # 结束时间  
        h = (LogCase.trx == trx) if trx else True  # 单号查询
        i = (LogCase.production_code == production_code) if production_code else True  # 产品号查询
        ke = [a, b, c, d, e, f, g, h,i]
        case  = LogCase.query.filter(*ke).order_by(-LogCase.trigger_time)

        return get_data(case, LogCase, exclude=["id","data"])

class CaseSingleInfo(BaseResource):
    """案件信息-单独"""
    validate_schemas = {"get": Schema({"trx": str,})}
    def get(self):
        logger.info("[D] [功能 案件信息展示]")
        req = self.validate_data
        logger_req(req)
        case  = LogCase.query.filter_by(trx=req["trx"]).first()        
        return get_data(case, LogCase, exclude=["id"])





