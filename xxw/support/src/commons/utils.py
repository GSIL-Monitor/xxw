import datetime
import json

from bson import ObjectId, DBRef
from flask import abort, request
from mongoengine import NotUniqueError
from schema import Schema, SchemaError, SchemaMissingKeyError

from src import Msg


def validate_schema(schema: Schema, data: dict, remove_blank=False):
    """schema验证,验证成功返回数据，验证失败返回错误信息
    Parameters
    ----------
    schema:Schema: 验证规则
    data: 验证数据
    remove_blank : 是否去除空白字段

    Returns (data,errors)
    -------

    """

    if not isinstance(data, dict):
        return Msg.PARAMS_ERROR, 400
    if remove_blank:
        for k, v in data.items():
            if v != "":
                data[k] = v
    try:
        validate_data = schema.validate(data)
        return validate_data, []
    except SchemaError as e:
        return {}, str(e.autos)
    else:
        return validate_data, []


class MongoEncoder(json.JSONEncoder):
    """
    处理mongo中取出来的datatime,data,objectid,dbref
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, DBRef):
            return str(obj.id)
        else:
            return json.JSONEncoder.default(self, obj)

