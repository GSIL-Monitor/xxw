from src.commons.model_resource import MongoModelResource
from src.models import Area


class AreaAPI(MongoModelResource):
    """区域管控"""
    model = Area
    filter_fields = [['product', '==', 'product', str],
                     ['status', '==', 'status', bool]]
