"""日期工具类"""
from datetime import datetime


def utc_timestamp():
    """返回utc时间戳（秒）"""
    return int(datetime.utcnow().timestamp())
