# 业务模版管理
import json
from datetime import datetime

from schema import And, Optional, Schema, Use

from src import db
from src.apps.models.sms import SMSAppTemplate, SmsBussinessTemplate
from src.comm.logger import logger
from src.comm.model_resource import SQLModelSchemaResource
from src.config.msgconfig import Msg


def template_id_int_to_str(app_templates):
    new_app_templates = []
    for t_id in json.loads(app_templates):
        if not SMSAppTemplate.query.filter_by(id=t_id).first():
            return Msg.SMS_BUSSINESS_APP_TEMPLATE_IS_NOT_EXIST
        new_app_templates.append(str(t_id))
    return json.dumps(new_app_templates)


class SmsBussinessTemplateAPI(SQLModelSchemaResource):
    """短信业务模板"""

    model = SmsBussinessTemplate
    allow_query_all = True
    filter_fields = [
        ["merchant_code", "==", "merchant_code", str],
        ["production_code", "==", "production_code", str],
        ["template_type_code", "==", "template_type_code", int],
        ["production_name", "contains", "production_name", str],
        ["is_valid", "==", "is_valid", int],
    ]
    update_exclude_fields = [
        "production_code",
        "merchant_code",
        "create_time",
        "production_name",
        "template_type_code",
    ]
    can_not_be_empty = And(Use(lambda s: str(s).strip()), len, error="Can not be empty")
    is_json_str = And(lambda c: json.loads(c), error="Not JSON string")
    is_bool = And(Use(int), lambda n: n in (0, 1))
    validate_schemas = {
        "post": Schema(
            {
                "merchant_code": can_not_be_empty,
                Optional("production_code"): can_not_be_empty,
                Optional("production_name"): can_not_be_empty,
                "template_type_code": can_not_be_empty,
                "app_templates": is_json_str,
                "operator_id": can_not_be_empty,
                "operator": can_not_be_empty,
                Optional("is_auto"): is_bool,
                Optional("is_valid"): is_bool,
            }
        ),
        "put": Schema(
            {
                "id": can_not_be_empty,
                Optional("app_templates"): is_json_str,
                Optional("is_auto"): is_bool,
                "operator_id": can_not_be_empty,
                "operator": can_not_be_empty,
                Optional("is_valid"): is_bool,
            }
        ),
    }

    def get(self):
        return_results = super().get()
        if not isinstance(return_results, dict):
            return return_results
        results = return_results["results"]
        detail_results = []
        for item in results:
            item["detail_template"] = []
            new_app_templates = []
            for app_template_id in json.loads(item["app_templates"]):
                app_template = SMSAppTemplate.query.get(int(app_template_id))
                if app_template:
                    data = dict()
                    data["app_template_id"] = int(app_template_id)
                    data["channel_name"] = app_template.channel_name
                    data["template_title"] = app_template.template_title
                    data["template"] = app_template.template
                else:
                    logger.warning("Bussiness Template: tb_sms_app_template is error")
                    return Msg.SMS_BUSSINESS_APP_TEMPLATE_IS_NOT_EXIST

                new_app_templates.append(int(app_template_id))
                item["detail_template"].append(data)
            item["app_templates"] = json.dumps(new_app_templates)
            detail_results.append(item)

        return_results["results"] = detail_results

        return return_results

    def post(self):
        production_code = self.validate_data.get("production_code", "")
        is_valid = self.validate_data.get("is_valid")
        instance, errors = self.detail_schema.load(self.validate_data)
        if is_valid:
            sms_bussiness_template = SmsBussinessTemplate.query.filter_by(
                production_code=production_code,
                merchant_code=instance.merchant_code,
                template_type_code=instance.template_type_code,
                is_valid=1,
            ).first()

            if sms_bussiness_template:
                logger.info("Bussiness Template: template is exist")
                return Msg.SMS_BUSSINESS_TEMPLATE_IS_EXIST
        if errors:
            logger.info(errors)
            return Msg.FIELD_TYPE_ERROR

        if isinstance(template_id_int_to_str(instance.app_templates), str):
            instance.app_templates = template_id_int_to_str(instance.app_templates)
        else:
            return template_id_int_to_str(instance.app_templates)

        try:
            db.session.add(instance)
            db.session.commit()
        except Exception as e:
            logger.info(str(e))
            return Msg.DB_COMMIT_ERROR
        return self.detail_schema.dump(instance).data

    def put(self):
        instance = self.model.query.get(self.validate_data.get(self.pk_name))
        if not instance:
            return Msg.INSTANCE_IS_NOT_EXIST
        is_valid = self.validate_data.get("is_valid")
        if is_valid:
            sms_bussiness_template = SmsBussinessTemplate.query.filter_by(production_code=instance.production_code,
                                                                          merchant_code=instance.merchant_code,
                                                                          template_type_code=instance.template_type_code,
                                                                          is_valid=1).first()
            if sms_bussiness_template:
                logger.info("Bussiness Template: template is exist")
                return Msg.SMS_BUSSINESS_TEMPLATE_IS_EXIST

        instance, errors = self.detail_schema.load(self.validate_data, partial=True)
        exclude_fields = set(self.validate_data.keys()) & set(
            self.update_exclude_fields
        )
        include_fields = set(self.validate_data.keys()) - set(
            self.update_include_fields
        )
        if self.update_include_fields and include_fields:
            logger.info("Not allowed to update " + str(include_fields))
            return Msg.NOT_ALLOW_UPDATE_FIELD_IS_EXIST
        if exclude_fields:
            logger.info("Not allowed to update " + str(exclude_fields))
            return Msg.NOT_ALLOW_UPDATE_FIELD_IS_EXIST
        if errors:
            logger.info(errors)
            return Msg.FIELD_TYPE_ERROR

        if hasattr(instance, "update_time"):
            instance.update_time = int(datetime.utcnow().timestamp())

        app_templates = self.validate_data.get("app_templates")
        if app_templates:
            if isinstance(template_id_int_to_str(app_templates), str):
                instance.app_templates = template_id_int_to_str(app_templates)
            else:
                return template_id_int_to_str(app_templates)
        db.session.commit()
        return self.detail_schema.dump(instance).data
