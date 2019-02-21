from schema import Optional, Schema, Use

from src.commons.utils import validate_schema

schema = Schema(
    {
        Optional("type"): str,
        Optional("code"): str,
        Optional("name"): str,
        Optional("desc"): str,
        Optional("operator_id"): str,
        Optional("page_size", default=15): Use(int),
        Optional("page", default=1): Use(int),
    }
)
data, e = validate_schema(schema, {"xx": 1})

print(data, e)
