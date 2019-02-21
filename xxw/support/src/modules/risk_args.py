
import time
import random
from datetime import datetime
from schema import Schema

from flask import request

from src.commons.logger import logger
from src.commons.rule_conf import Degrees
from src.commons.model_resource import ModelSchemaResource
from src.models.risk_args import RiskArgs
from src import Msg
from src.models.user import TbProduction, TbMerchant
from src.models.args_mgr import IndustryPosition


class RiskArgsAPI(ModelSchemaResource):

    model = RiskArgs
    filter_fields = [
        ["merchant_code", "==", "merchant_code", str],
        ["production_code", "==", "production_code", str],
        ["rule_id", "==", "rule_id", str],
        ["rule_name", "==", "rule_name", str],
    ]
    update_exclude_fields = ["production_code", "merchant_code", "created", "rule_id"]

    validate_schemas = {
        "post": Schema(
            {
                "rule_name": str,
                "rule_desc": str,
                "status": bool,
                "merchant_code": str,
                "production_code": str,
                "rule_conf": dict
            }
        )}

    def post(self):
        instance, errors = self.detail_schema.load(request.json)
        merchant_code = instance.merchant_code.strip()
        production_code = instance.production_code.strip()
        status = request.json.get("status")
        if status:
            r_args = self.model.objects.filter(merchant_code=merchant_code, production_code=production_code, status=True).first()
            if r_args:
                logger.info("Risk args: living rule is exist")
                return "living rule is exist", 400
        if not all([merchant_code, production_code]):
            logger.info("Risk args: fields can not empty")
            return "fields can not empty", 400
        if not TbMerchant.query.filter_by(code=merchant_code).first():
            logger.info("Risk args: Merchant is not exist")
            return "Merchant is not exist", 400
        if not TbProduction.query.filter_by(code=production_code, merchant_code=merchant_code).first():
            logger.info("Risk args: Production is not exist")
            return "Production is not exist", 400
        if errors:
            logger.info("Risk args: {}".format(str(errors)))
            return str(errors), 400
        errors = validate_rule_conf(instance)
        if errors:
            logger.info("Risk args: {}".format(errors[0]))
            return errors
        instance.rule_id = int(str(int(time.time())) + str(random.randint(0, 9)))
        instance.save()
        return self.detail_schema.dump(instance).data

    def put(self):

        _id = request.json.pop("id")
        instance = self.model.objects(id=_id).filter(id=_id).first()
        if not instance:
            return Msg.NO_DATA, 400
        exclude_fields = set(request.json.keys()) & set(self.update_exclude_fields)
        include_fields = set(request.json.keys()) - set(self.update_include_fields)
        if self.update_include_fields and include_fields:
            logger.info("Risk args: Not Allowed To Update " + str(include_fields))
            return "Not allowed to update " + str(include_fields), 400
        if exclude_fields:
            logger.info("Risk args: Not Allowed To Update " + str(exclude_fields))
            return "Not allowed to update " + str(exclude_fields), 400
        status = request.json.get("status")

        instance, errors = self.detail_schema.update(instance, request.json)

        if errors:
            logger.info("Risk args: {}".format(str(errors)) )
            return str(errors), 400

        errors = validate_rule_conf(instance)

        if errors:
            logger.info("Risk args: {}".format(errors[0]))
            return errors

        merchant_code = instance.merchant_code.strip()
        production_code = instance.production_code.strip()
        if status:
            r_args = self.model.objects.filter(merchant_code=merchant_code, production_code=production_code,
                                               status=True).first()
            if r_args:
                logger.info("Risk args: living rule is exist")
                return "living rule is exist", 400

        if getattr(instance, "update_time", None):
            instance.update_time = int(datetime.utcnow().timestamp())
        instance.save()
        return self.detail_schema.dump(instance).data


def validate_rule_conf(instance):
    validate_fields = {"age_range", "degrees", "selected_industries_and_professions", "lend_range"}
    not_allow_fields = set(instance.rule_conf.keys()) - validate_fields
    include_fields = validate_fields - set(instance.rule_conf.keys())
    ind_pos_all = IndustryPosition.objects.all()
    industry_position_code = dict()
    for ind_pos in ind_pos_all:
        industry_position_code.setdefault(ind_pos.industry_code, set()).add(ind_pos.position_code)
    if not_allow_fields:
        return f"Not allowed to create {not_allow_fields}", 400
    if include_fields:
        return f"{include_fields} can not empty", 400
    for item in instance.rule_conf["degrees"]:
        if item not in Degrees.__members__.keys():
            return f"{item} is not exist", 400
    for ind in instance.rule_conf["selected_industries_and_professions"]:
        if ind["industry_code"] not in industry_position_code.keys():
            return "{} is not exist".format(ind["industry_code"]), 400
        for prof in ind["professions"]:
            if prof["position_code"] not in industry_position_code[ind["industry_code"]]:
                return "{} is not exist".format(prof["position_code"]), 400


