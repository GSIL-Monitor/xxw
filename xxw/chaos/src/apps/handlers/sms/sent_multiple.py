# 发送多条短信
from schema import Optional, Schema

from src.apps.models.sms import SmsLog
from src.comm.model_resource import SQLModelSchemaResource

from . import XwSmsSingleSender


class SmsSentMultipleAPI(SQLModelSchemaResource):
    """群发短信"""

    model = SmsLog
    allow_methods = ["post"]
    validate_schemas = {
        "post": Schema(
            {
                "receivers_list": list,
                "template_type_code": int,
                "merchant_code": str,
                Optional("production_code"): str,
            }
        )
    }

    def post(self):

        receivers_list = self.validate_data.get("receivers_list")
        template_type_code = self.validate_data.get("template_type_code")
        merchant_code = self.validate_data.get("merchant_code")
        production_code = self.validate_data.get("production_code", "")
        sms_sent_multiple = XwSmsSingleSender(
            merchant_code, production_code, template_type_code
        )
        is_success, msg = sms_sent_multiple.send_mul_sms(receivers_list)
        if not isinstance(msg, tuple):
            return msg
        return {"serial_number": msg[1]}
