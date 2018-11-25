from datetime import datetime

from flask import request

from src.commons.model_resource import BaseResource, MongoModelResource
from src.models import Event, FraudApiConfig


class EventAPI(MongoModelResource):
    model = Event
    allow_query_all = True
    allow_methods = ["get"]
    filter_fields = [
        ["trx", "==", "trx", str],
        ["telephone", "==", "telephone", str],
        ["id_card", "==", "id_card", str],
        ["user_name", "==", "user_name", str],
        ["product", "==", "product", str],
        ["event_type", "==", "event_type", str],
        ["created__lte", "==", "created__lte", lambda x: datetime.fromtimestamp(float(x))],
        ["created__gte", "==", "created__gte", lambda x: datetime.fromtimestamp(float(x))]
    ]


class EventCount(BaseResource):
    def get(self):
        product = request.args.get("product")
        queryset = Event.objects
        if product:
            queryset = queryset.filter(product=product)
        return {
            "total": queryset.count(),
            "review": queryset.filter(decision__FraudResult__resultCode="review").count(),
            "reject": queryset.filter(decision__FraudResult__resultCode="reject").count(),
            "accept": queryset.filter(decision__FraudResult__resultCode="accept").count(),
        }


class EventCountByType(BaseResource):
    def get(self):
        fraud_config = FraudApiConfig.objects.first()
        product = request.args.get("product")
        queryset = Event.objects
        if product:
            queryset = queryset.filter(product=product)
        ret = {}
        for event_type in fraud_config.EVENT_TYPES.keys():
            q = queryset.filter(event_type=event_type)
            ret[event_type] = {
                "total": q.count(),
                "review": q.filter(decision__FraudResult__resultCode="review").count(),
                "reject": q.filter(decision__FraudResult__resultCode="reject").count(),
                "accept": q.filter(decision__FraudResult__resultCode="accept").count(),
            }
        return ret
