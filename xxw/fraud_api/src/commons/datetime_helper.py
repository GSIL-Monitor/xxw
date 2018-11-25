import time
from datetime import datetime, timedelta

def utc_timestamp():
    return int(datetime.utcnow().timestamp())

def first_day_of_week(year: int, week: int):
    """获取给定年份,周数所对应那周的第一天日期"""
    year_start_str = str(year) + "0101"  # 当年第一天
    year_start = datetime.strptime(year_start_str, "%Y%m%d")  # 格式化为日期格式
    year_start_calendar_msg = year_start.isocalendar()  # 当年第一天的周信息
    year_start_weekday = year_start_calendar_msg[2]
    year_start_year = year_start_calendar_msg[0]
    if year_start_year < int(year):
        day_delat = (8 - int(year_start_weekday)) + (int(week) - 1) * 7
    else:
        day_delat = (8 - int(year_start_weekday)) + (int(week) - 2) * 7

    a = year_start + timedelta(days=day_delat)
    return a


def datetime_format(date, fmt):
    """时间格式化"""
    return datetime.strptime(datetime.strftime(date, fmt), fmt)


def utc2local(utc_dtm):
    # UTC 时间转本地时间（ +8:00 ）
    local_tm = datetime.fromtimestamp(0)
    utc_tm = datetime.utcfromtimestamp(0)
    offset = local_tm - utc_tm
    return utc_dtm + offset


def local2utc(local_dtm):
    # 本地时间转 UTC 时间（ -8:00 ）
    return datetime.utcfromtimestamp(local_dtm.timestamp())


def func_time(func):
    """计时器"""

    def _wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        print(func.__name__, "run:", time.time() - start)

    return _wrapper
