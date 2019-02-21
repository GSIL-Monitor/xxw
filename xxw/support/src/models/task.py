from .base_mongo import db
from src.commons.date_utils import utc_timestamp


class AutoUpdateTimeDocument(db.Document):
    meta = {"abstract": True}

    def clean(self):
        if hasattr(self, "update_time"):
            self.update_time = utc_timestamp()

    def update(self, **kwargs):
        if hasattr(self, "update_time"):
            kwargs["update_time"] = utc_timestamp()
        return super().update(**kwargs)


SIZE = (0, 1, 2, 3, 4)


class Evt(AutoUpdateTimeDocument):
    meta = {
        "collection": "audit_task_evts",
        "indexes": [
            "merchant_code",
            "production_code",
            "uin",
            "evt_type",
            "time",
            "status",
            "create_time",
            "update_time",
            "operator_id",
            "operator"
        ],
        "ordering": ["-time"],
        "strict": False,
    }
    serial_no = db.StringField(required=True, verbose_name="流水号")
    merchant_code = db.StringField(required=True, verbose_name="商户 code")
    production_code = db.StringField(required=True, verbose_name="产品 code")
    uin = db.IntField(required=True, verbose_name="用户ID")
    evt_type = db.StringField(required=True,
                              verbose_name="审核事件类型 cash-提现，apply_credit-授信，trans-事务，face_sign 面签，antifraud-反欺诈)")
    data = db.DictField(verbose_name="审核相关数据对象")
    materials = db.ListField(db.StringField(), verbose_name="审核材料")
    time = db.IntField(required=True, verbose_name="时间，UNIX时间戳")
    status = db.IntField(required=True, default=0, verbose_name="审核事件状态，添加时会自动创建 0-待审核，1-执行中，2-通过,3-驳回，4-挂起 ，默认 0", choices=SIZE)
    operator_id = db.StringField(required=True, verbose_name="操作人")
    operator = db.StringField(required=True, verbose_name="操作人")
    create_time = db.IntField(required=True, default=utc_timestamp, verbose_name="存储时间")
    update_time = db.IntField(verbose_name="更新时间")
    audit_extend_fileds = db.DictField(verbose_name="审核扩展字段")
    audite_desc = db.StringField(verbose_name="审核备注")
    username = db.StringField(verbose_name="用户姓名")
    phone = db.StringField(verbose_name="用户手机号")
    id_card = db.StringField(verbose_name="身份证号")
    manager_code = db.StringField(verbose_name="客户经理编号")
