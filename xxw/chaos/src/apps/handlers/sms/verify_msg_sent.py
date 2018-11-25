#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/03
@desc: template_id = 154105  # {1}为您的验证码，请于{2}分钟内填写。如非本人操作，请忽略本短信
        appid = os.environ.get("APPID", 1400110865)
        appkey = os.environ.get("APPKEY", "80ee786d8502c360ccd7157b3ab07c1e")
"""
import random

from schema import Optional, Schema

from src import redis_conn
from src.apps.handlers.sms import XwSmsSingleSender
from src.comm.logger import logger
from src.comm.model_resource import BaseResource
from src.config.config import VERIFY_CODE_EXPIRE, cur_env
from src.config.msgconfig import Msg


class SendMsg(BaseResource):
    validate_schemas = {
        "post": Schema(
            {
                "phone": str,
                "type": str,
                "merchant_code": str,
                Optional("product_code"): str,
            }
        )
    }

    def post(self):
        req = self.validate_data
        merchant_code = req["merchant_code"]
        product_code = req.get("product_code", "")
        phone = req["phone"]
        type_id = int(req["type"])
        verify_code = self.gen_verify_code()
        params = [verify_code, str(VERIFY_CODE_EXPIRE)]
        key = "sms-{}-{}".format(phone, type_id)

        if redis_conn.exists(key):
            logger.info("Repeat sending. redis key: [{}]".format(key))
            return Msg.SMS_REPEAT_SEND

        # 请求发送短信接口
        ret, msg = self.send_verify_code(
            merchant_code, product_code, type_id, phone, params
        )

        if not ret:
            logger.warning("Send Verify Code Failed, msg: [{}]".format(msg))
            return Msg.SMS_SEND_FAIL
        redis_conn.set(key, verify_code, ex=VERIFY_CODE_EXPIRE * 60)
        logger.info(
            "Send Verify Code Success merchant_code[%s] product_code[%s] type_id[%s] phone[%s] params[%s]"
            % (merchant_code, product_code, type_id, phone, params)
        )

    def send_verify_code(self, merchant_code, product_code, type_id, phone, params):
        """开发环境和测试环境不请求短信接口，模拟返回结果
        """
        if cur_env in ("local", "dev"):
            logger.info("Sent a test Verify code")
            return True, ""
        sender = XwSmsSingleSender(merchant_code, product_code, type_id)
        return sender.send_single_sms(phone, params)

    def gen_verify_code(self):
        """
        开发环境和测试环境模拟验证码
        """
        if cur_env in ("local", "dev"):
            return "123456"
        return str(random.randint(100000, 999999))
