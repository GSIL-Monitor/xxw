from src.commons.model_resource import MongoModelResource
from src.models import Feature


class FeatureAPI(MongoModelResource):
    model = Feature
    allow_query_all = True
    filter_fields = [
        ["product", "==", "product", str],
        ["name", "==", "name__icontains", str],
        ["event_type", "==", "event_type", str]
    ]
