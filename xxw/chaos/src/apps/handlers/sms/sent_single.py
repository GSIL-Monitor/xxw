# 发送单条短信

from schema import Optional, Schema

from src.apps.models.sms import SmsLog
from src.comm.logger import logger
from src.comm.model_resource import SQLModelSchemaResource
from src.config.msgconfig import Msg

from . import XwSmsSingleSender


class SmsSentSingleAPI(SQLModelSchemaResource):
    """单发短信"""

    model = SmsLog
    allow_methods = ["post"]
    validate_schemas = {
        "post": Schema(
            {
                "receiver": str,
                "params": list,
                "template_type_code": int,
                "merchant_code": str,
                Optional("production_code"): str,
            }
        )
    }

    def post(self):

        receiver = self.validate_data.get("receiver")
        params = self.validate_data.get("params")
        template_type_code = self.validate_data.get("template_type_code")
        merchant_code = self.validate_data.get("merchant_code")
        production_code = self.validate_data.get("production_code", "")
        sms_sent_multiple = XwSmsSingleSender(
            merchant_code, production_code, template_type_code
        )
        is_success, msg = sms_sent_multiple.send_single_sms(receiver, params)
        if not isinstance(msg, tuple):
            return msg
        if is_success:
            return {"serial_number": msg[1]}
        logger.info(msg[0])
        return Msg.SMS_SENDER_FAILED
