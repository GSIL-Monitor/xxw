#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import datetime

def get_page_no(page_no):
    try:
        page_no = page_no if page_no > 1 else 1
    except Exception as e:
        page_no = 1
    return page_no


def dt_to_ts(now_date):
    """
    时间转换为时间戳
    """
    try:
        tt = now_date.timetuple()
        return int(time.mktime(tt))
    except Exception as e:
        return


def ts_to_dt(ts, formatter='%Y/%m/%d %H:%M:%S'):
    """
    时间戳转换为时间
    """
    try:
        return datetime.datetime.utcfromtimestamp(
            ts).strftime(formatter)
    except Exception as e:
        return