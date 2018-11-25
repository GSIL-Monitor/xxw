# 通道模版管理
"""
短信应用模版管理
"""

from schema import And, Optional, Schema, Use

from src.apps.models.sms import SMSApp, SMSAppTemplate, SmsBussinessTemplate
from src.comm.model_resource import SQLModelSchemaResource
from src.config.msgconfig import Msg


class SMSAppTemplateAPI(SQLModelSchemaResource):
    """短信应用模版管理"""

    model = SMSAppTemplate
    business_unique_fields = ("template_title",)
    allow_query_all = True
    has_is_delete = True
    filter_fields = (
        ("id", "==", "id", int),
        ("app_id", "==", "app_id", int),
        ("template_content_code", "==", "template_content_code", str),
        ("template_title", "contains", "template_title", str),
        ("operator", "contains", "operator", str),
        ("operator_id", "==", "operator_id", str),
        ("is_valid", "==", "is_valid", int),
        ("is_delete", "==", "is_delete", int),
        ("channel_name", "contains", "channel_name", str),
    )

    can_not_be_empty = And(Use(lambda s: str(s).strip()), len)
    is_bool = And(Use(int), lambda n: n in (0, 1))
    validate_schemas = {
        "post": Schema(
            {
                "app_id": Use(int),
                Optional("template_content_code"): And(str),
                "template_title": can_not_be_empty,
                "channel_name": can_not_be_empty,
                "template": can_not_be_empty,
                "price": can_not_be_empty,
                "operator_id": can_not_be_empty,
                "operator": can_not_be_empty,
            }
        ),
        "put": Schema(
            {
                "id": Use(int),
                Optional("app_id"): Use(int),
                Optional("template_content_code"): And(str),
                Optional("template_title"): can_not_be_empty,
                Optional("channel_name"): can_not_be_empty,
                Optional("template"): can_not_be_empty,
                Optional("price"): can_not_be_empty,
                Optional("operator_id"): can_not_be_empty,
                Optional("operator"): can_not_be_empty,
                Optional("is_valid"): is_bool,
            }
        ),
        "delete": Schema({"id": Use(int)}),
    }

    def get_queryset(self, args):
        queryset = super().get_queryset(args)
        return queryset.join(SMSApp, SMSAppTemplate.app_id == SMSApp.id).add_columns(
            SMSApp.app_name
        )

    def custom_serializable(self, data):
        """因为做了 join 查询，所有需要自定义序列化返回结果"""

        result_list = []
        for (model, app_name) in data:
            result = {k: v for k, v in model.__dict__.items()}
            result.pop("_sa_instance_state")
            result["app_name"] = app_name
            result_list.append(result)
        return result_list

    def delete(self):
        """如果短信模板中引用了相关应用模板，则禁止删除该短信模板
        """

        pk = self.validate_data.get(self.pk_name)
        if (
            SmsBussinessTemplate.query.filter(
                SmsBussinessTemplate.app_templates.contains('"{}"'.format(pk))
            ).count()
            > 0
        ):
            return Msg.SMS_APP_TEMP_DEPENDENT_DELETE
        return super().delete()
