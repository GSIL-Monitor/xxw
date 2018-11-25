#!usr/bin/env python
# coding=utf-8
"""
@author: 
@time: 
@desc:
"""
from schema import And, Optional, Schema

from src import alert_sentry_client
from src.comm.model_resource import BaseResource


class AlertAPI(BaseResource):
    """业务告警API：透传数据上报到sentry"""

    allow_methods = ["post"]
    validate_schemas = {
        "post": Schema(
            {
                "service_name": str,
                "type": And(str, lambda x: x in ["inter", "external"]),
                "message": str,
                "host": str,
                "timestamp": int,
                "level": And(
                    str,
                    lambda x: x
                    in ["fatal", "error", "warning", "info", "debug", "sample"],
                ),
                "stack_info": str,
                Optional("extra", default={}): dict,
            }
        )
    }

    def post(self):
        data = data = self.validate_data

        message = data.pop("message")
        extra = data.pop("extra")
        extra["stack_info"] = data.pop("stack_info")
        alert_sentry_client.send(**{"tags": data, "extra": extra, "message": message})
