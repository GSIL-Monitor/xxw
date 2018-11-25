#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc:
"""

from src import api, app
from src.apps.handlers.bussiness_alert import alert
from src.apps.handlers.health_check import health_check
from src.apps.handlers.ip import ip_address
from src.apps.handlers.phone import phone_address
from src.apps.handlers.sms import (bussiness_template, sent_multiple,
                                   sent_single, sms_app, sms_app_template,
                                   sms_app_template_check, sms_channel,
                                   sms_log, template_type, verify_msg_check,
                                   verify_msg_sent)

# api.add_resource(, "")  #

# 健康检查
api.add_resource(health_check.Health, "/health_check")  # 健康检查

# 短信服务
api.add_resource(
    bussiness_template.SmsBussinessTemplateAPI, "/sms/sms_bussiness_template"
)
api.add_resource(sent_single.SmsSentSingleAPI, "/sms/sms_sent_single")
api.add_resource(sent_multiple.SmsSentMultipleAPI, "/sms/sms_sent_multiple")
api.add_resource(sms_log.SmsLogAPI, "/sms/sms_log")
api.add_resource(template_type.SmsTemplateTypeAPI, "/sms/sms_template_type")
api.add_resource(sms_app.SMSAppAPI, "/sms/app")
api.add_resource(sms_app_template.SMSAppTemplateAPI, "/sms/app_template")
api.add_resource(sms_channel.SMSChannelAPI, "/sms/channel")
api.add_resource(
    sms_app_template_check.SMSAppTemplateCheckAPI, "/sms/app_template_check"
)
# 短信验证码
api.add_resource(verify_msg_check.VerifyMsg, "/sms/verification/run_verify_code")
api.add_resource(verify_msg_sent.SendMsg, "/sms/verification/run_send_code")
# 手机归属地服务
api.add_resource(phone_address.PhoneAddressAPI, "/phone_address")
# ip归属地服务
api.add_resource(ip_address.IPAddressAPI, "/ip_address")

# 业务监控
api.add_resource(alert.AlertAPI, "/bussiness/alert")
