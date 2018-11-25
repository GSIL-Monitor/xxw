import json
from datetime import datetime

from bson import ObjectId

from src.commons.datetime_helper import utc2local


class MongoEncoder(json.JSONEncoder):
    """
    JSON Encoder，序列化对象为JSON字符串
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return utc2local(obj).strftime("%Y-%m-%d %H:%M:%s")
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
