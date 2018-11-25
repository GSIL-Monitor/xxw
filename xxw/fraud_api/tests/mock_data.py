#!/usr/bin/env python

# -*-coding:utf-8-*-
import random
from datetime import timedelta

from faker import Faker

from src.models import *

connect(host="mongodb://localhost/tumblelog")


def mock_event():
    fake = Faker("zh_CN")

    now = int(datetime.now().timestamp() * 1000)
    start = now - 7 * 24 * 60 * 60 * 60 * 1000
    d = datetime.now()
    for i in range(1000):
        a = [
            Event(
                **{
                    "token": "xxxx",
                    "created": d + timedelta(hours=-random.randint(1, 200)),
                    "event_id": fake.sha1(raw_output=False),
                    "product": "xw",
                    "event_type": random.choice(Event.EVENT_TYPES),
                    "wx_openid": fake.sha1(raw_output=False),
                    "wx_unionid": fake.sha1(raw_output=False),
                    "telephone": fake.phone_number(),
                    "id_card": fake.ssn(min_age=18, max_age=90),
                    "telephone_decode": "136****6000",
                    "telephone_city": fake.city(),
                    "telephone_city_code": "028",
                    "user_id": fake.user_name(),
                    "user_name": fake.name(),
                    "login_retry_cnt": 1,
                    "last_auth_result": "通过",
                    "login_result": "成功",
                    "gps_latitude": float(
                        "{}.{}".format(
                            random.randint(10, 40), random.randint(100000, 999999)
                        )
                    ),
                    "gps_longitude": float(
                        "{}.{}".format(
                            random.randint(80, 120), random.randint(100000, 999999)
                        )
                    ),
                    "gps_geohash": fake.sha1(raw_output=False),
                    "gps_address": fake.address(),
                    "address": fake.address(),
                    "address_latitude": float(
                        "{}.{}".format(
                            random.randint(10, 40), random.randint(100000, 999999)
                        )
                    ),
                    "address_longitude": float(
                        "{}.{}".format(
                            random.randint(80, 120), random.randint(100000, 999999)
                        )
                    ),
                    "address_geohash": fake.sha1(raw_output=False),
                    "gps_city": fake.city(),
                    "gps_province": fake.province(),
                    "gps_city_code": fake.numerify(),
                    "gps_country": fake.country(),
                    "ip": fake.ipv4_public(),
                    "device_platform": "h5",
                    "os_type": "IOS",
                    "os_version": "7.0",
                    "resolution": "1280x780",
                    "device_id": fake.sha1(raw_output=False),
                    "device_type": "yyy",
                    "ip_province": fake.province(),
                    "ip_city": fake.city(),
                    "decision": {
                        "rules": ["F_XT_FW0001", "F_XT_FW0002", "F_XT_FW0003"],
                        "return_code": "AF00001",
                        "process_code": "ACK0001",
                        "result": random.choice(["accept", "review", "reject"]),
                    },
                }
            )
            for _ in range(1000)
        ]
        # print(a[0].to_dict())
        Event.objects.insert(a)
        print(i)


class FraudConfig(DynamicDocument):
    """反欺诈系统配置"""

    product = StringField()
    time_window = DictField()
    major_property = ListField()
    minor_property = ListField()
    event_type = ListField()
    mongo_db = DictField()


def mock_fraudconfig():
    config = {
        "product": "xw",
        "time_window": {
            "7d": 7 * 24 * 60 * 60 * 60,
            "5d": 5 * 24 * 60 * 60 * 60,
            "1d": 24 * 60 * 60 * 60,
            "30m": 30 * 60,
            "5m": 5 * 60,
            "1m": 60,
        },
        "major_property": [""],
        "minor_property": [""],
        "event_type": ["动态验证码", "登录", "修改密码", "实名认证", "申请额度", "绑卡", "提现"],
        "mongo_db": {
            "host": "127.0.0.1",
            "port": 27017,
            "user": "",
            "pwd": "",
            "db": "tumblelog",
        },
    }
    mock = FraudApiConfig(**config)
    mock.save()


def datetime_format(date, fmt):
    """格式化时间"""
    return datetime.strptime(datetime.strftime(date, fmt), fmt)


def mock_hour_count():
    from tasks.services import hour_count

    start = datetime.now() + timedelta(days=-10)
    end = datetime.now()
    hour_count(start, end)


def mock_daily_trends_count():
    from tasks.services import daily_trends_count

    for i in range(7):
        date = datetime.now() + timedelta(days=-i)
        daily_trends_count(date)


def mock_weekly_count():
    from tasks.services import week_count

    date = datetime.now() + timedelta(weeks=-1)
    year = date.isocalendar()[0]
    week = date.isocalendar()[1]
    week_count(year, week)


if __name__ == "__main__":
    print("mocking data....")
    # Event.objects().delete()
    # EventCounter.objects().delete()
    # mock_event()
    # mock_hour_count()
    # mock_daily_trends_count()
    # mock_weekly_count()
    # mock_fraudconfig()
