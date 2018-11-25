#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/03
@desc: 短信验证
"""
from schema import Schema

from src import cur_env, redis_conn
from src.comm.logger import logger
from src.comm.model_resource import BaseResource
from src.config.msgconfig import Msg


class VerifyMsg(BaseResource):
    validate_schemas = {"post": Schema({"phone": str, "type": int, "verify_code": str})}

    def post(self):
        req = self.validate_data
        if cur_env in ("local", "dev", "test") and req["verify_code"] == "111111":
            return

        phone, verify_code, type_id = req["phone"], req["verify_code"], req["type"]
        key = "sms-{}-{}".format(phone, type_id)
        code = redis_conn.get(key)
        if code != verify_code:
            logger.info(
                "SMS Verify Failed. phone: [%s] verify_code: [%s] type_id: [%s] code: [%s]"
                % (phone, verify_code, type_id, code)
            )
            logger.info("SMS Verify Failed. redis key: [{}]".format(key))
            return Msg.SMS_VERIFY_CODE_NOT_MATCH
        logger.info(
            "SMS Verify Success. phone: [%s] verify_code: [%s]" % (phone, verify_code)
        )
        redis_conn.delete(key)
