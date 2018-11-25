"""参数管理"""

from src.commons.model_resource import MongoModelResource
from src.models import BlackWhiteList


class BlackWhiteListAPI(MongoModelResource):
    """通用参数字典"""

    model = BlackWhiteList
    filter_fields = [
        ["product", "==", "product", str],
        ["list_type", "==", "list_type", str],
        ["data", "==", "data", str],
        ["is_allow", "==", "is_allow", bool],
    ]
