"""短信管理"""
import uuid
from schema import Schema
from src.commons.logger import logger

from src import db
from flask import request
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError


from src.commons.model_resource import ModelSchemaResource
from src.models.sms import SmsLog, SmsTemplate, SmsTemplateType
from src.models.user import TbProduction


class SmsTemplateAPI(ModelSchemaResource):
    """短信模板"""

    model = SmsTemplate
    exclude = ["is_delete"]
    allow_query_all = True
    has_is_delete = True
    business_unique_fields = ["template_content_code", "template_type_code"]
    filter_fields = [
        ["merchant_code", "==", "merchant_code", str],
        ["production_code", "==", "production_code", str],
        ["template_type_code", "==", "template_type_code", int],
        ["production_name", "contains", "production_name", str],
        ["template_content_code", "==", "template_content_code", str],
        ["template_title", "contains", "template_title", str],
    ]
    update_exclude_fields = ["production_code", "merchant_code", "create_time",
                             "template_content_code", "template", "production_name"]


class SmsLogAPI(ModelSchemaResource):
    """短信记录"""

    model = SmsLog
    allow_methods = ["get"]
    allow_query_all = True
    filter_fields = [

        ["merchant_code", "==", "merchant_code", str],
        ["production_code", "==", "production_code", str],
        ["production_name", "contains", "production_name", str],
        ["template_type", "==", "template_type", str],
        ["receiver", "==", "receiver", str],
        ["status", "==", "status", str],
        ["create_time", "<=", "create_time_end", int],
        ["create_time", ">=", "create_time_start", int],
        ["serial_number", "==", "serial_number", str]
    ]

    def get(self):
        try:
            page = request.args.get("page")
            if page:
                page = int(page)
            else:
                page = 1
        except:
            return "page should be int", 400
        try:
            page_size = request.args.get("page_size")
            if page_size:
                page_size = int(page_size)
            else:
                page_size = self.default_page_size
            if page_size > self.max_page_size:
                page_size = self.max_page_size
        except:
            return "page_size should be int", 400

        queryset = self.get_queryset(request.args)

        if self.allow_query_all and page_size == -1:
            page_size = queryset.count()

        pagination = queryset.paginate(page=page, per_page=page_size)
        results = [item.to_dict() for item in pagination.items]

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": results,
        }


class SmsTemplateTypeAPI(ModelSchemaResource):
    """短信模板类型"""

    model = SmsTemplateType
    allow_query_all = True
    filter_fields = [
        ["code", "==", "code", str],
        ["template_type", "==", "template_type", str]
    ]
    business_unique_fields = ["code"]
    update_exclude_fields = ["code"]


class SmsTemplateSenderAPI(ModelSchemaResource):
    """群发短信"""

    model = SmsLog
    allow_methods = ["post"]
    validate_schemas = {
        "post": Schema(
            {
             "receivers_list": list,
             "template_type_code": int,
             "template_content_code": str}
        )}

    def post(self):

        serial_number = str(uuid.uuid1())

        receivers_list = self.validate_data.get("receivers_list")
        template_type_code = self.validate_data.get("template_type_code")
        template_content_code = self.validate_data.get("template_content_code")

        temp = SmsTemplate.query.filter_by(template_content_code=template_content_code, template_type_code=template_type_code, is_delete=False).first()
        temp_type = SmsTemplateType.query.filter_by(code=template_type_code).first()
        if not all([temp, temp_type]):
            logger.info("Sms Sender: template is not exist")
            return "template is not exist", 400

        prod = TbProduction.query.filter_by(code=temp.production_code).first()

        if not prod.sms_appid or not prod.sms_appkey:
            return "not found appid or appkey", 400

        ssender = SmsSingleSender(prod.sms_appid, prod.sms_appkey)

        sms_log_lists = []
        for receivers_params in receivers_list:
            receiver = receivers_params["receiver"]
            params = receivers_params["params"]
            try:
                result = ssender.send_with_param("86", receiver, int(template_content_code), params, sign=prod.sms_sign)
            except HTTPError as e:
                logger.info("Sms Sender:", str(e))
                return str(e), 400
            except Exception as e:
                logger.info("Sms Sender:", str(e))
                return str(e), 400

            sms_log = SmsLog()
            sms_log.params = str(params)
            sms_log.template_code = temp.id
            sms_log.production_code = temp.production_code
            sms_log.production_name = prod.name
            sms_log.template_type = temp_type.template_type
            sms_log.serial_number = serial_number
            sms_log.merchant_code = temp.merchant_code
            sms_log.template_content_code = template_content_code
            sms_log.receiver = receiver
            if result.get("result") == 0:
                sms_log.status = 1
                logger.info('Sms Sender Success! receiver {}'.format(receiver))
            else:
                sms_log.status = 0
                logger.warning("receivers_params: {}, template_type_code: {}, template_content_code: {}".format(
                    receivers_params,
                    template_type_code,
                    template_content_code))
                logger.warning('Sms Sender Failed! receiver {}, result: {}'.format(receiver, result))
            sms_log.remarks = result.get("errmsg")
            sms_log_lists.append(sms_log)
        try:
            db.session.add_all(sms_log_lists)
            db.session.commit()
        except Exception as e:
            logger.warning("Sms Sender:", str(e))
            return str(e), 400
        return {"serial_number": serial_number}

