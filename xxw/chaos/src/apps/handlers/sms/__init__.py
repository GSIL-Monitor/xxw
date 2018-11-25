#!usr/bin/env python
# coding=utf-8
"""
@author: 
@time: 
@desc:
"""
from src.apps.models.sms import SmsBussinessTemplate, SMSAppTemplate, SMSApp, SmsLog
from src.comm import sms_utils
import json
import uuid
from src import db
import traceback
from src.comm.logger import logger
from src.comm.utils import print_run_time
from src.config.msgconfig import Msg
from src import ma


class SmsLogSchema(ma.ModelSchema):
    class Meta:
        model = SmsLog


detail_schema = SmsLogSchema()


class XwSmsSingleSender:
    def __init__(self, merchant_code, production_code, template_type_code):
        self.merchant_code = merchant_code
        self.production_code = production_code
        self.template_type_code = template_type_code
        self.sms_bus_template = None
        self.app_templates = None
        self.app_templates_list = None

    def get_bussiness_templates(self):
        sms_bus_tem = SmsBussinessTemplate.query.filter_by(
            merchant_code=self.merchant_code,
            production_code=self.production_code,
            template_type_code=self.template_type_code,
            is_valid=1,
        ).all()
        if not sms_bus_tem:
            return None
        return sms_bus_tem[0]

    def get_app_templates(self, channel_templates):
        """选择发送短信的通道模版"""
        app_templates = (
            SMSAppTemplate.query.join(SMSApp, SMSAppTemplate.app_id == SMSApp.id)
            .filter(SMSApp.is_valid.__eq__(1))
            .filter(SMSApp.is_delete.__eq__(0))
            .filter(SMSAppTemplate.id.in_(channel_templates))
            .filter(SMSAppTemplate.is_valid.__eq__(1))
            .filter(SMSAppTemplate.is_delete.__eq__(0))
        ).all()
        return app_templates

    def get_sms_app(self, app_id):
        app = SMSApp.query.filter(SMSApp.id.__eq__(app_id)).one_or_none()
        return app

    @print_run_time
    def get_sms_config(self):
        self.sms_bus_template = self.get_bussiness_templates()
        if not self.sms_bus_template:
            logger.info("Sms Sender: bussiness template is not exist")
            return Msg.SMS_SENDER_BUSS_TEMPLATE_NOT_EXIST

        self.app_templates = self.sms_bus_template.app_templates
        if not self.app_templates:
            logger.info("Sms Sender: app template is not exist")
            return Msg.SMS_SENDER_APP_TEMPLATE_NOT_EXIST

        self.app_templates = [int(t) for t in json.loads(self.app_templates)]
        self.app_templates_list = self.get_app_templates(self.app_templates)

        if not self.app_templates_list:
            logger.info("Sms Sender: app template is not exist")
            return Msg.SMS_SENDER_APP_TEMPLATE_NOT_EXIST
        return ""

    def send_single_sms(self, receiver, params):
        receivers_list = [{"receiver": receiver, "params": params}]
        return self.send_mul_sms(receivers_list)

    @print_run_time
    def send_mul_sms(self, receivers_list):
        error = self.get_sms_config()
        if error:
            return False, error
        is_success = False
        msg = ""
        sms_log_list = []
        serial_number = uuid.uuid1().hex
        for receivers_params in receivers_list:
            receiver = receivers_params["receiver"]
            params = receivers_params["params"]
            for app_template in self.app_templates_list:
                app = self.get_sms_app(app_template.app_id)
                if not app:
                    logger.info("Sms Sender: sms config is not exist")
                    return False, Msg.SMS_SENDER_CONFIG_NOT_EXIST
                channel_code = app.channel_code
                is_success, msg = sms_utils.single_sms_sender(
                    channel_code,
                    receiver,
                    app_template.template,
                    params,
                    app_template.template_content_code,
                    json.loads(app.config),
                    app.sign_name,
                )
                sms_log = SmsLog(
                    serial_number=serial_number,
                    merchant_code=self.merchant_code,
                    production_code=self.production_code,
                    production_name=self.sms_bus_template.production_name,
                    app_template_id=app_template.id,
                    app_name=app.app_name,
                    channel_name=app.channel_name,
                    template_title=app_template.template_title,
                    template_content_code=app_template.template_content_code,
                    template_type_code=self.sms_bus_template.template_type_code,
                    receiver=receiver,
                    params=json.dumps(params),
                    status=1 if is_success else 0,
                    remarks=msg,
                    price=app_template.price,
                    is_auto=self.sms_bus_template.is_auto,
                )
                sms_log_list.append(sms_log)
                if is_success:
                    logger.info(
                        "Sms Sender Success! content:{}".format(
                            json.dumps(detail_schema.dump(sms_log).data)
                        )
                    )
                    break
                logger.info(
                    "Sms Sender Failed! content:{}".format(
                        json.dumps(detail_schema.dump(sms_log).data)
                    )
                )
        try:
            db.session.add_all(sms_log_list)
            db.session.commit()
        except Exception as e:
            logger.error("Sms Sender: %s" % traceback.format_exc())
            return False, Msg.DB_COMMIT_ERROR
        return is_success, (msg, serial_number)
