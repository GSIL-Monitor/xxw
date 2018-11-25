"""数据models"""
from datetime import datetime

from flask_mongoengine import BaseQuerySet
from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    DynamicDocument,
    IntField,
    PointField,
    PolygonField,
    StringField,
)


class Event(DynamicDocument):
    """事件

    gps_coordinate:
        {'type' : 'Point' ,
        'coordinates' : [x, y]}
    ip_coordinate:
        {'type' : 'Point' ,
        'coordinates' : [x, y]}
    address_coordinate:
        {'type' : 'Point' ,
        'coordinates' : [x, y]}
    """
    meta = {"collection": "event",
            "indexes": ["trx", "telephone", "product", "id_card", "ip", "device_id", "created", "event_type",
                        "user_name"],
            "ordering": ["-created"],
            "strict": False,
            "queryset_class": BaseQuerySet,
            }

    event_type = StringField(required=True, verbose_name="事件类型")
    trx = StringField(required=True, verbose_name="事务ID")
    product = StringField(required=True, verbose_name="产品编号")
    wx_openid = StringField(required=True, verbose_name="微信openid")
    wx_unionid = StringField(verbose_name="微信unionid")
    user_id = StringField(required=True, verbose_name="用户id")
    user_name = StringField(required=True, verbose_name="用户名称")
    device_id = StringField(required=True, verbose_name="设备指纹ID")
    device_info = DictField(verbose_name="设备信息")
    telephone = StringField(required=True, verbose_name="手机号")
    telephone_city = StringField(required=True, verbose_name="手机号归属城市")
    id_card = StringField(required=True, verbose_name="身份证号")
    id_card_city = StringField(required=True, verbose_name="身份证号归属城市")
    gps_coordinate = PointField(required=True, verbose_name="GPS纬度")
    gps_address = StringField(required=True, verbose_name="GPS地址")
    gps_city = StringField(required=True, verbose_name="GPS城市")
    ip = StringField(required=True, verbose_name="IP地址")
    ip_coordinate = PointField(required=True, verbose_name="IP坐标")
    ip_city = StringField(required=True, verbose_name="IP城市")
    address = StringField(required=True, verbose_name="地址")
    address_coordinate = PointField(required=True, verbose_name="联系地址坐标")
    address_city = StringField(required=True, verbose_name="联系地址城市")
    created = DateTimeField(default=datetime.utcnow, verbose_name="创建时间")
    decision = DictField(verbose_name="决策结果")
    features = DictField(verbose_name="特征结果")


class FraudApiConfig(DynamicDocument):
    meta = {"collection": "feature_config", "queryset_class": BaseQuerySet}
    LIST_TYPES = DictField(required=True)
    BLACK_WHITE_LIST_TYPES = DictField(required=True)
    TIME_WINDOWS = DictField(required=True)
    TIME_WINDOWS_VALUE = DictField(required=True)
    PRODUCTS = DictField(required=True)
    DIMENSIONS = DictField(required=True)
    EVENT_TYPES = DictField(required=True)


class Feature(DynamicDocument):
    """特征集"""

    meta = {"collection": "feature", "ordering": ["-created"], "queryset_class": BaseQuerySet}
    product = StringField(required=True, verbose_name="产品代号")
    code = StringField(verbose_name="特征代号")
    name = StringField(verbose_name="特征标题")
    event_type = StringField(required=True, verbose_name="事件类型代号")
    event_type_name = StringField(verbose_name="事件类型名称")
    major_dimension = StringField(required=True, verbose_name="主维度code")
    major_dimension_name = StringField(verbose_name="主维度名称")
    minor_dimension = StringField(verbose_name="次维度code")
    minor_dimension_name = StringField(verbose_name="次维度名称")
    feature_type = StringField(verbose_name="特征集类型")
    is_active = BooleanField(required=True, verbose_name="状态")  # true-禁用，false-启用
    time_window_name = StringField(verbose_name="时间窗口名称")
    time_window_value = IntField(verbose_name="时间窗口分钟数")
    time_window = StringField(required=True, verbose_name="时间窗口字段")
    created = DateTimeField(default=datetime.utcnow, verbose_name="创建时间")
    update_time = DateTimeField(default=datetime.utcnow, verbose_name="修改时间")

    def update(self, **data):
        fraud_config = FraudApiConfig.objects.first()
        if self.minor_dimension:
            code = "{}__{}__{}".format(
                self.major_dimension, self.minor_dimension, self.time_window
            )
            name = "同一{}{}内不同{}出现次数".format(
                fraud_config.DIMENSIONS[self.major_dimension],
                fraud_config.TIME_WINDOWS[self.time_window],
                fraud_config.DIMENSIONS[self.minor_dimension],
            )
        else:
            code = "{}__{}".format(self.major_dimension, self.time_window)
            name = "同一{}{}内出现次数".format(
                fraud_config.DIMENSIONS[self.major_dimension],
                fraud_config.TIME_WINDOWS[self.time_window]
            )
        data["code"] = code
        data["name"] = name
        data["event_type_name"] = fraud_config.EVENT_TYPES[self.event_type]
        data["major_dimension_name"] = fraud_config.DIMENSIONS[self.major_dimension]

        if self.minor_dimension:
            data["minor_dimension_name"] = fraud_config.DIMENSIONS[self.minor_dimension]
        data["time_window_name"] = fraud_config.TIME_WINDOWS[self.time_window]
        data["time_window_value"] = fraud_config.TIME_WINDOWS_VALUE[self.time_window]
        super().update(**data)

    def save(self, **kwargs):
        fraud_config = FraudApiConfig.objects.first()
        if self.minor_dimension:
            code = "{}__{}__{}".format(
                self.major_dimension, self.minor_dimension, self.time_window
            )
            name = "同一{}{}内不同{}出现次数".format(
                fraud_config.DIMENSIONS[self.major_dimension],
                fraud_config.TIME_WINDOWS[self.time_window],
                fraud_config.DIMENSIONS[self.minor_dimension],
            )
        else:
            code = "{}__{}".format(self.major_dimension, self.time_window)
            name = "同一{}{}内出现次数".format(
                fraud_config.DIMENSIONS[self.major_dimension],
                fraud_config.TIME_WINDOWS[self.time_window]
            )
        self.code = code
        self.name = name
        self.event_type_name = fraud_config.EVENT_TYPES[self.event_type]
        self.major_dimension_name = fraud_config.DIMENSIONS[self.major_dimension]

        if self.minor_dimension:
            self.minor_dimension_name = fraud_config.DIMENSIONS[self.minor_dimension]
        self.time_window_name = fraud_config.TIME_WINDOWS[self.time_window]
        self.time_window_value = fraud_config.TIME_WINDOWS_VALUE[self.time_window]
        super().save(**kwargs)


class Area(DynamicDocument):
    """区域管理"""

    meta = {"collection": "area", "ordering": ["-created"], "strict": False, "queryset_class": BaseQuerySet}

    product = StringField(required=True, verbose_name="产品")
    created = DateTimeField(required=True, default=datetime.utcnow, verbose_name="创建时间")
    update_time = DateTimeField(required=True, default=datetime.utcnow, verbose_name="修改时间")
    status = BooleanField(required=True, verbose_name="黑白名单")
    gps = PolygonField(required=True, verbose_name="坐标集")
    city = StringField(required=True, verbose_name="城市")
    address = StringField(required=True, verbose_name="地址")
    list_type = StringField(verbose_name="名单类型")


class BlackWhiteList(DynamicDocument):
    """黑白名单"""

    meta = {"collection": "black_white_list", "ordering": ["-created"], "indexes": ["title"],
            "queryset_class": BaseQuerySet}

    title = StringField(required=True, verbose_name="名单标题")
    product = StringField(required=True, verbose_name="产品")
    list_type = StringField(required=True, verbose_name="名单类型")
    type = StringField(required=True, verbose_name="是否是白名单")
    data = StringField(required=True, verbose_name="名单值")
    created = DateTimeField(required=True, default=datetime.utcnow, verbose_name="创建时间")
    update_time = DateTimeField(required=True, default=datetime.utcnow, verbose_name="更新时间")
    is_allow = BooleanField(required=True, default=True)


def to_dict(instance):
    result = {}
    for field_name, field_type in instance._fields.items():
        if instance[field_name] is not None:
            if field_name == 'id':
                result[field_name] = str(instance[field_name])
            elif field_type.__class__ == DateTimeField:
                result[field_name] = int(instance[field_name].timestamp())
            else:
                result[field_name] = instance[field_name]
    return result


Document.to_dict = to_dict
