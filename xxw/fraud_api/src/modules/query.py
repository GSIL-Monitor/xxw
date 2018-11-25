from collections import defaultdict
from datetime import datetime, timedelta

from flask import request

from src.commons.model_resource import MongoModelResource
from src.models import Event


def timestamp_to_datetime(value):
    return datetime.fromtimestamp(float(value))


filter_fields = [
    ["created", "<=", "created__lte", timestamp_to_datetime],
    ["created", ">=", "created__gte", timestamp_to_datetime],
    ["product", "==", "product", str],
    ["event_type", "==", "event_type", str]
]


class Map(MongoModelResource):
    """大屏坐标数据"""

    model = Event
    allow_methods = ["get"]
    filter_fields = filter_fields
    max_page_size = 100000
    list_fields = ["gps_coordinate", "trx", "created", "event_type"]

    def get(self):
        data = super().get()
        start = request.args.get('start')
        if not start:
            return "start必填", 400
        start = timestamp_to_datetime(start)
        product = request.args.get('product')
        data["count"] = self.model.objects.filter(created__gte=start, product=product).count()
        return data


class LatestMap(MongoModelResource):
    """大屏最新N条事件"""

    model = Event
    allow_methods = ["get"]
    default_page_size = 5


class Cycle(MongoModelResource):
    """事件大盘-同周期对比图数据"""
    model = Event
    allow_methods = ["get"]
    filter_fields = filter_fields

    def get(self):
        request_data = request.args.to_dict()
        date = request_data.pop("date")
        try:
            date = timestamp_to_datetime(date)
        except:
            date = datetime.utcnow()

        queryset = self.get_queryset()
        today = date.date()
        tomorrow = (date + timedelta(days=+1)).date()
        yesterday = (date + timedelta(days=-1)).date()
        last_week_today = (date + timedelta(days=-7)).date()  # 上周的今天
        last_week_today_tomorrow = (date + timedelta(days=-6)).date()

        def get_data(start, end):
            return list(queryset.filter(created__gte=start, created__lt=end).aggregate(
                {"$group": {"_id": {"$hour": "$created"}, "count": {"$sum": 1}}}
            ))

        today_data = get_data(today, tomorrow)
        yesterday_data = get_data(yesterday, today)
        last_week_today_data = get_data(last_week_today, last_week_today_tomorrow)

        # 统计最近七天每小时同比平均值
        last_week_avg_data = list(queryset.filter(created__gte=last_week_today, created__lt=tomorrow).aggregate(
            {
                "$group": {
                    "_id": {"hour": {"$hour": "$created"}, "day": {"$dayOfYear": "$created"}},
                    "count": {"$sum": 1},
                }
            }
        ))

        hour_count = defaultdict(int)
        for d in last_week_avg_data:
            hour_count[d["_id"]["hour"]] += d["count"]

        return {
            "today": today_data,
            "yesterday": yesterday_data,
            "last_week_today": last_week_today_data,
            "last_week_avg": [{"_id": _id, "count": int(count / 7)} for _id, count in hour_count.items()],
        }


class RuleTop(MongoModelResource):
    model = Event
    allow_methods = ["get"]
    filter_fields = filter_fields

    def get(self):
        """获取命中规则topN
        """
        top = int(request.args.get("top", 5))
        pipeline = [{"$group": {"_id": "$decision.FraudResult.reAct", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        results = self.get_queryset().aggregate(*pipeline)
        return [e for e in results][:top]
