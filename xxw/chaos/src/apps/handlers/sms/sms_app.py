"""
短信应用管理
"""
import json

from schema import And, Optional, Schema, Use

from src.apps.models.sms import SMSApp, SMSAppTemplate
from src.comm.model_resource import SQLModelSchemaResource
from src.config.msgconfig import Msg


class SMSAppAPI(SQLModelSchemaResource):
    """应用管理"""

    model = SMSApp
    business_unique_fields = ("app_name",)
    allow_query_all = True
    has_is_delete = True
    filter_fields = (
        ("id", "==", "id", int),
        ("app_name", "contains", "app_name", str),
        ("sign_name", "contains", "sign_name", str),
        ("channel_code", "==", "channel_code", str),
        ("channel_name", "contains", "channel_name", str),
        ("operator_id", "==", "operator_id", str),
        ("operator", "contains", "operator", str),
        ("is_valid", "==", "is_valid", int),
        ("is_delete", "==", "is_delete", int),
    )

    can_not_be_empty = And(Use(lambda s: str(s).strip()), len)
    is_json_str = And(lambda c: json.loads(c))
    is_bool = And(Use(int), lambda n: n in (0, 1))
    validate_schemas = {
        "post": Schema(
            {
                "sign_name": can_not_be_empty,
                "app_name": can_not_be_empty,
                "channel_code": can_not_be_empty,
                "channel_name": can_not_be_empty,
                "config": is_json_str,
                "operator_id": can_not_be_empty,
                "operator": can_not_be_empty,
            }
        ),
        "put": Schema(
            {
                "id": Use(int),
                Optional("app_name"): can_not_be_empty,
                Optional("sign_name"): can_not_be_empty,
                Optional("channel_name"): can_not_be_empty,
                Optional("config"): is_json_str,
                Optional("operator_id"): can_not_be_empty,
                Optional("operator"): can_not_be_empty,
                Optional("is_valid"): is_bool,
            }
        ),
        "delete": Schema({"id": Use(int)}),
    }

    def delete(self):
        """如果应用模板中引用了相关应用，则禁止删除该应用
        """

        pk = self.validate_data.get(self.pk_name)
        if SMSAppTemplate.query.filter_by(app_id=pk, is_delete=0).count() > 0:
            return Msg.SMS_APP_DEPENDENT_DELETE

        return super().delete()
