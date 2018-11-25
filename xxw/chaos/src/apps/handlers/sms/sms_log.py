# 短信流水

from src.apps.models.sms import SMSAppTemplate, SmsLog
from src.comm.logger import logger
from src.comm.model_resource import SQLModelSchemaResource


class SmsLogAPI(SQLModelSchemaResource):
    """短信记录"""

    model = SmsLog
    allow_methods = ["get"]
    allow_query_all = True
    filter_fields = [
        ["merchant_code", "==", "merchant_code", str],
        ["production_code", "==", "production_code", str],
        ["production_name", "contains", "production_name", str],
        ["receiver", "==", "receiver", str],
        ["app_template_id", "==", "app_template_id", str],
        ["status", "==", "status", int],
        ["create_time", "<=", "create_time_end", int],
        ["create_time", ">=", "create_time_start", int],
        ["serial_number", "==", "serial_number", str],
        ["is_auto", "==", "is_auto", int],
        ["template_title", "==", "template_title", str],
        ["app_name", "contains", "app_name", str],
        ["channel_name", "contains", "channel_name", str],
    ]

    def get(self):
        return_results = super().get()
        if not isinstance(return_results, dict):
            return return_results
        results = return_results["results"]
        detail_results = []
        for item in results:
            app_template = SMSAppTemplate.query.get(int(item["app_template_id"]))
            if app_template:
                item["template"] = app_template.template
            else:
                logger.warning("Sms Log : tb_sms_app_template is error")
                item["template"] = "内容不存在"
            detail_results.append(item)

        return_results["results"] = detail_results

        return return_results
