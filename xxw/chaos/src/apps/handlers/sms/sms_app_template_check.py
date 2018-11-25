import json

from schema import Schema

from src.apps.models.sms import SMSApp, SMSAppTemplate, db
from src.comm.logger import logger
from src.comm.model_resource import BaseResource
from src.comm.sms_utils import single_sms_sender
from src.comm.utils import utc_timestamp
from src.config.msgconfig import Msg


class SMSAppTemplateCheckAPI(BaseResource):
    """验证应用模版"""

    allow_methods = ["post"]
    validate_schemas = {
        "post": Schema({"app_template_id": int, "params": list, "phone": str})
    }

    def post(self):
        app_template_id = self.validate_data.get("app_template_id")
        app_template, channel_code, config, sign_name = (
            SMSAppTemplate.query.join(SMSApp, SMSAppTemplate.app_id == SMSApp.id)
            .add_columns(SMSApp.channel_code, SMSApp.config, SMSApp.sign_name)
            .filter(SMSAppTemplate.id == app_template_id)
            .first()
        )
        if not app_template:
            return Msg.SMS_BUSSINESS_APP_TEMPLATE_IS_NOT_EXIST
        logger.info(
            json.dumps(
                {
                    "template": app_template.template,
                    "template_code": app_template.template_content_code,
                    "channel_code": channel_code,
                    "config": config,
                    "sign_name": sign_name,
                },
                ensure_ascii=False,
            )
        )
        # 参数获取成功，发送短信
        result, error = single_sms_sender(
            channel_code=channel_code,
            receiver=self.validate_data.get("phone"),
            template_content=app_template.template,
            params=self.validate_data.get("params"),
            template_content_code=app_template.template_content_code,
            conf_params=json.loads(config),
            sign_name=sign_name,
        )
        if result is False:
            logger.warning(error)
            return Msg.SMS_SENDER_FAILED

        app_template.last_check_time = utc_timestamp()
        app_template.is_check = 1
        db.session.add(app_template)
        db.session.commit()
        return Msg.SUCCESS
