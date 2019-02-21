"""参数管理"""
from schema import Schema, Optional
from src.commons.model_resource import ModelSchemaResource
from src.models.args_mgr import CommonCode, IndustryPosition


class CommonCodeAPI(ModelSchemaResource):
    """通用参数字典"""

    model = CommonCode
    allow_query_all = True
    filter_fields = [
        ["type", "==", "type", str],
        ["code", "==", "code", str],
        ["name", "==", "name", str],
        ["desc", "==", "desc", str],
        ["operator", "==", "operator", str],
        ["operator_id", "==", "operator_id", str]
    ]
    validate_schemas = {
        "post": Schema(
            {"type": str,
             "code": str,
             "name": str,
             "desc": str,
             "operator_id": str,
             "operator": str}
        ),
        "put": Schema(
            {"id": str,
             Optional("code"): str,
             Optional("type"): str,
             Optional("name"): str,
             Optional("desc"): str,
             "operator_id": str,
             "operator": str
             }
        ),
        "delete": Schema(
            {"id": str}
        )
    }


class IndustryPositionAPI(ModelSchemaResource):
    """行业信息表"""
    model = IndustryPosition
    allow_query_all = True
    filter_fields = [
        ["industry_code", "==", "industry_code", str],
        ["industry_name", "==", "industry_name", str],
        ["position_name", "==", "position_name", str],
        ["position_code", "==", "position_code", str],
        ["rank", "==", "rank", str],
        ["operator", "==", "operator", str],
        ["operator_id", "==", "operator_id", str]
    ]
    validate_schemas = {
        "post": Schema(
            {"industry_code": str,
             "industry_name": str,
             "position_code": str,
             "position_name": str,
             Optional("rank"): str,
             "operator_id": str,
             "operator": str,
             }
        ),
        "put": Schema(
            {"id": str,
             Optional("industry_name"): str,
             Optional("position_name"): str,
             Optional("rank"): str,
             "operator_id": str,
             "operator": str,
             }
        ),
        "delete": Schema(
            {"id": str}
        )
    }


class IndustryCodeAPI(ModelSchemaResource):
    """行业代码表"""
    model = IndustryPosition

    def get(self):
        pipline = [
            {"$group": {"_id": {"industry_code": "$industry_code", "industry_name": "$industry_name"}}

             }
        ]
        queryset = IndustryPosition.objects().only("industry_code", "industry_name").aggregate(*pipline)
        return {"results": [_["_id"] for _ in queryset]}
