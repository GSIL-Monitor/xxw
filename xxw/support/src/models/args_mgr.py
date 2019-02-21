from src.commons.date_utils import utc_timestamp

from .base_mongo import db


# 通用参数字典
class CommonCode(db.Document):
    """通用参数字典"""
    meta = {"collection": "support_commoncode","strict": False}  # 集合名
    type = db.StringField(required=True, verbose_name="字典类型")
    code = db.StringField(required=True, unique_with="type", verbose_name="字典编号")
    name = db.StringField(required=True, verbose_name="名称")
    desc = db.StringField(required=True, verbose_name="描述")
    operator = db.StringField(required=True, verbose_name="操作人姓名")
    operator_id = db.StringField(required=True, verbose_name="操作人ID")
    create_time = db.IntField(required=True, default=utc_timestamp, verbose_name="存储时间")
    update_time = db.IntField(default=utc_timestamp, verbose_name="更新时间")


class IndustryPosition(db.Document):
    """行业职位表"""
    meta = {"collection": "support_industry_position","strict": False}
    industry_code = db.StringField(required=True, verbose_name="行业代码")
    industry_name = db.StringField(verbose_name="行业名称")
    position_code = db.StringField(required=True, unique_with="industry_code", verbose_name="职业代码")
    position_name = db.StringField(verbose_name="职业名称")
    rank = db.StringField(verbose_name="风险等级")
    create_time = db.IntField(required=True, default=utc_timestamp, verbose_name="存储时间")
    update_time = db.IntField(default=utc_timestamp, verbose_name="更新时间")
    operator = db.StringField(required=True, verbose_name="操作人")
    operator_id = db.StringField(required=True, verbose_name="操作人ID")


