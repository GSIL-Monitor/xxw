# 动码类型
from src.apps.models.sms import SmsTemplateType
from src.comm.model_resource import SQLModelSchemaResource


class SmsTemplateTypeAPI(SQLModelSchemaResource):
    """短信模板类型"""

    pk_name = "code"
    model = SmsTemplateType
    allow_query_all = True
    filter_fields = [
        ["code", "==", "code", str],
        ["template_type", "==", "template_type", str],
    ]
    business_unique_fields = ["code"]
