from datetime import datetime
from schema import Schema, Optional

from flask import request

from src import Msg
from src.commons.logger import logger
from src.commons.mongo_resource import MongoModelResource
from src.models.regional_control import RegionalControl
from src.models.user import TbProduction


class RegionalControlAPI(MongoModelResource):
    """区域管控"""
    model = RegionalControl

    regional_total = 10

    filter_fields = [['production_code', '==', 'production_code', str],
                     ['status', '==', 'status', bool]]

    update_exclude_fields = ["production_code", "created", "update_time"]

    validate_schemas = {
        "post": Schema(
            {
                "city": str,
                "address": str,
                Optional("status"): bool,
                "regional_type": str,
                "production_code": str,
                "gps": dict
            }
        ),
        "put": Schema(
            {
                "id": str,
                Optional("city"): str,
                Optional("address"): str,
                Optional("status"): bool,
                Optional("regional_type"): str,
                Optional("gps"): dict
            }
        )
    }

    def post(self):

        instance = self.model(**request.json)

        production_code = instance.production_code.strip()
        if not TbProduction.query.filter_by(code=production_code).first():
            logger.info("Regional control: Production is not exist")
            return "Production is not exist", 400
        regional_total = RegionalControl.objects.filter(production_code=production_code, status=True).count()
        if regional_total >= self.regional_total:
            logger.info(f"living regional_control can not more than {self.regional_total}")
            return f"living regional_control can not more than {self.regional_total}", 400
        try:
            instance.save()
        except Exception as e:
            logger.info(str(e))
            return str(e), 400
        return instance.to_dict()

    def put(self):
        _id = request.json.pop("id")
        instance = self.model.objects().filter(id=_id).first()

        if not instance:
            return Msg.NO_DATA, 400
        exclude_fields = set(request.json.keys()) & set(self.update_exclude_fields)
        include_fields = set(request.json.keys()) - set(self.update_include_fields)
        if self.update_include_fields and include_fields:
            logger.info("Not Allowed To Update " + str(include_fields))
            return "Not allowed to update " + str(include_fields), 400
        if exclude_fields:
            logger.info("Not Allowed To Update " + str(exclude_fields))
            return "Not allowed to update " + str(exclude_fields), 400

        status = request.json.get("status")
        if status:
            regional_total = RegionalControl.objects.filter(production_code=instance.production_code, status=True).count()
            if regional_total >= self.regional_total:
                logger.info(f"living regional_control can not more than {self.regional_total}")
                return f"living regional_control can not more than {self.regional_total}", 400
        instance.update_time = int(datetime.utcnow().timestamp())
        try:
            instance.update(**request.json)
            instance.save()
        except Exception as e:
            logger.info(str(e))
            return str(e), 400
        return instance.to_dict()