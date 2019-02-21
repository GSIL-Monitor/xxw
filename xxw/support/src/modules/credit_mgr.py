#!/usr/bin/env python
"""征信数据"""
import time
import datetime
import calendar
import re
from src import mongo_db
from flask import request
from flask_restful import Resource

from src.commons.error_handler import (
    requests_error_handler, RequestsError, http_basic_handler,
)
from src.commons.reqparse import RequestParser
from src.models.audit_log import TbCreditLog
from src.models.task_models import CreditConf
from src.models.user import TbMerchantCredit
from src.commons.regexp import (
    RE_PHONE,
    RE_IDENTIFICATION_NO,
)
from src.commons.params_utils import (
    get_page_no,
    dt_to_ts,
)


class CreditTypeApi(Resource):
    """
    征信接口配置
    """
    def __init__(self):
        self.reqparse = RequestParser()
    
    @http_basic_handler
    @requests_error_handler
    def get(self, *args, **kwargs):
        self.reqparse.add_argument(
            "merchant_code", type=str, required=True, code=1014010001, desc="商户代码"
        )
        self.reqparse.add_argument(
            "production_code", type=str, required=False, code=1014010001, desc="产品代码"
        )
        rq_args = self.reqparse.parse_args()
        
        merchant_code = rq_args.get('merchant_code')
        production_code = rq_args.get('production_code')
        filter_conditions = [(TbMerchantCredit.merchant_code==merchant_code)]
        if production_code:
            filter_conditions.append((TbMerchantCredit.production_code==production_code))

        interface_origin_list = TbMerchantCredit.query.filter(*filter_conditions)
        interface_query_list = [data.interface for data in interface_origin_list]
        interface_list = mongo_db["credit_conf"].find(
            {"interface": {'$in': interface_query_list}},
            {"interface": 1, "supplier": 1, "product": 1, "type": 1, "desc": 1, "_id": 0}
        ).sort([('interface', 1)])

        total = interface_list.count()
        return {
            'total': total,
            'data': list(interface_list)
        }


class CreditLogApi(Resource):
    """
    征信查询日志
    """
    max_page_size = 100

    def __init__(self):
        self.reqparse = RequestParser()
        self.page_size = 10

    @http_basic_handler
    @requests_error_handler
    def get(self, *args, **kwargs):
        self.reqparse.add_argument(
            "merchant_code", type=str, required=True, code=1014010001, desc="商户代码"
        )
        self.reqparse.add_argument(
            "production_code", type=str, required=False, code=1014010001, desc="产品代码"
        )
        self.reqparse.add_argument(
            "page", type=int, required=False, code=1014010001, desc="页码"
        )
        self.reqparse.add_argument(
            "page_size", type=int, required=False, code=1014010001, desc="页数"
        )
        self.reqparse.add_argument(
            "name", type=str, required=False, code=1014010001, desc="被查人姓名"
        )
        self.reqparse.add_argument(
            "phone", type=str, required=False, code=1014010001, desc="被查人手机号"
        )
        self.reqparse.add_argument(
            "id_card", type=str, required=False, code=1014010001, desc="被查人身份证号"
        )
        self.reqparse.add_argument(
            "start_time", type=int, required=True, code=1014010001, desc="开始时间"
        )
        self.reqparse.add_argument(
            "end_time", type=int, required=True, code=1014010001, desc="结束时间"
        )
        self.reqparse.add_argument(
            "interface", type=str, required=False, code=1014010001, desc="接口编码"
        )

        rq_args = self.reqparse.parse_args()
        
        filter_conditions = []

        merchant_code = rq_args.get('merchant_code')
        filter_conditions.append((TbCreditLog.merchant_code==merchant_code))

        production_code = rq_args.get('production_code')
        if production_code:
            filter_conditions.append((TbCreditLog.production_code==production_code))
        
        page = get_page_no(rq_args.get('page'))
        page_size = int(rq_args.get('page_size')) if rq_args.get('page_size') else self.page_size
        if page_size > self.max_page_size:
            raise RequestsError(code=1014010002, message=",每页查询超出最大限制")

        name = rq_args.get('name')
        if name:
            filter_conditions.append((TbCreditLog.name.contains(name)))
        
        phone_number = rq_args.get('phone')
        if phone_number:
            if not re.match(RE_PHONE, phone_number):
                raise RequestsError(code=1014010002, message=",手机号校验失败")
            filter_conditions.append((TbCreditLog.phone==phone_number))
        
        idcard_number = rq_args.get('id_card')
        if idcard_number:
            if not re.match(RE_IDENTIFICATION_NO, idcard_number):
                raise RequestsError(code=1014010002, message=",身份证号码校验失败")
            filter_conditions.append((TbCreditLog.id_card==idcard_number))

        start_time = rq_args.get('start_time')
        end_time = rq_args.get('end_time')
        if end_time < start_time:
            raise RequestsError(code=1014010002, message=",查询时间起始时间不能小于结束时间")

        try:
            start_time = datetime.datetime.utcfromtimestamp(start_time)
            end_time = datetime.datetime.utcfromtimestamp(end_time)
        except Exception as e:
            raise RequestsError(code=1014010002, message=",查询时间校验失败")
 
        end_time = end_time + datetime.timedelta(days=1)
        start_time, end_time = calendar.timegm(datetime.datetime.utctimetuple(start_time)), calendar.timegm(datetime.datetime.utctimetuple(end_time))

        filter_conditions.append((TbCreditLog.start_time>=start_time))
        filter_conditions.append((TbCreditLog.start_time<=end_time))
        supplier = rq_args.get('interface')
        if supplier:
            filter_conditions.append((TbCreditLog.interface==supplier))
        
        credit_log_list = TbCreditLog.query.filter(*filter_conditions).order_by(TbCreditLog.start_time.desc()).paginate(page, page_size, False)
        total = credit_log_list.total

        ret = []
        for r in credit_log_list.items:
            ret.append(r.to_pretty())
          
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'data': ret
        }

        





