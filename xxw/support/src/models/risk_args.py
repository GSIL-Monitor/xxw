from datetime import datetime

from .base_mongo import db


class RiskArgs(db.Document):
    """风险参数配置"""

    meta = {"collection": "support_risk_args"}  # 集合名

    merchant_code = db.StringField(required=True, verbose_name="银行id")
    production_code = db.StringField(required=True, verbose_name="产品id")
    rule_name = db.StringField(required=True, verbose_name="规则名称")
    rule_id = db.IntField(verbose_name="规则id")
    rule_desc = db.StringField(required=True, verbose_name="规则描述")
    rule_conf = db.DictField(required=True, verbose_name="规则配置")
    status = db.BooleanField(required=True, default=False, verbose_name="操作开关")
    created = db.IntField(required=True, default=lambda: int(datetime.utcnow().timestamp()), verbose_name="创建时间")
