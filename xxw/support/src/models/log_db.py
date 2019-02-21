from src import db
from src.commons.date_utils import utc_timestamp


class LogBaseMixin(object):
    __bind_key__ = "log_db"
    __table_args__ = {"mysql_engine": "MyISAM"}
    id = db.Column(db.BigInteger, primary_key=True)
    wx_openid = db.Column(db.String(100), comment="公众号open_id")
    wx_unionid = db.Column(db.String(100), comment="公众号union_id")
    channel = db.Column(db.String(200), comment="渠道")
    sub_channel = db.Column(db.String(200), comment="子渠道")
    merchant_code = db.Column(db.String(100), comment="租户ID", index=True)
    production_code = db.Column(db.String(200), comment="产品ID", index=True)
    manager_id = db.Column(db.String(200), comment="客户经理ID", index=True)
    trx = db.Column(db.String(200), comment="案件号码", index=True)


class LogUserMixin(object):
    uin = db.Column(db.BigInteger, comment="用户唯一id", index=True)
    phone = db.Column(db.String(11), comment="手机号", index=True)


class LogLoading(db.Model, LogBaseMixin):
    """加载表"""
    __tablename__ = "tb_loading"

    location = db.Column(db.String(200), comment="加载地")
    load_time = db.Column(db.BigInteger, comment='加载时间', index=True)
    result = db.Column(db.String(100), comment="加载结果", index=True)


class LogRegister(db.Model, LogBaseMixin, LogUserMixin):
    """注册表"""
    __tablename__ = 'tb_register'

    location = db.Column(db.String(200), comment="认证地")
    reg_time = db.Column(db.BigInteger, comment="注册时间", index=True)
    result = db.Column(db.String(100), comment="注册结果", index=True)


class LogLogin(db.Model, LogBaseMixin, LogUserMixin):
    """登陆表"""
    __tablename__ = "tb_login"

    location = db.Column(db.String(200), comment="登陆地")
    login_time = db.Column(db.BigInteger, comment="登陆时间", index=True)
    result = db.Column(db.String(10), comment="登陆结果", index=True)


class LogRealnameAuth(db.Model, LogBaseMixin, LogUserMixin):
    """实名认证表"""
    __tablename__ = "tb_realnameauth"

    location = db.Column(db.String(200), comment="认证地")
    auth_time = db.Column(db.BigInteger, comment="认证时间", index=True)
    result = db.Column(db.String(10), comment="认证结果", index=True)


class LogCredit(db.Model, LogBaseMixin, LogUserMixin):
    """授信表"""
    __tablename__ = 'tb_credit'

    location = db.Column(db.String(200), comment="授信地")
    credit_amt = db.Column(db.DECIMAL(12, 2), comment="授信额度")
    credit_rate = db.Column(db.DECIMAL(6, 2), comment="授信利率")
    credit_time = db.Column(db.BigInteger, comment="授信时间", index=True)
    result = db.Column(db.String(10), comment="授信结果", index=True)


class LogFaceSign(db.Model, LogBaseMixin, LogUserMixin):
    """面签表"""
    __tablename__ = 'tb_face_sign'

    location = db.Column(db.String(200), comment="面签地")
    face_sign_time = db.Column(db.BigInteger, comment="面签时间", index=True)
    result = db.Column(db.String(10), comment="面签结果", index=True)


class LogBindBankcard(db.Model, LogBaseMixin, LogUserMixin):
    """预绑卡表"""
    __tablename__ = 'tb_pre_bind_bankcard'

    location = db.Column(db.String(200), comment="预绑卡地点")
    bind_time = db.Column(db.BigInteger, comment="预绑卡时间", index=True)
    result = db.Column(db.String(10), comment="预绑卡结果", index=True)


class LogBindBankCard(db.Model, LogBaseMixin, LogUserMixin):
    """绑卡表"""
    __tablename__ = 'tb_bind_bankcard'

    location = db.Column(db.String(200), comment="绑卡地点")
    bind_time = db.Column(db.BigInteger, comment="绑卡时间", index=True)
    result = db.Column(db.String(10), comment="绑卡结果", index=True)


class LogWithdraw(db.Model, LogBaseMixin, LogUserMixin):
    """提现表"""

    __tablename__ = 'tb_withdraw'

    location = db.Column(db.String(200), comment="提现地点")
    name = db.Column(db.String(100), comment="姓名（实名）")

    draw_time = db.Column(db.BigInteger, comment="提现时间", index=True)
    bank_card_no = db.Column(db.String(20), comment="提现卡号")
    load_amt = db.Column(db.DECIMAL(12, 2), comment="提现金额")
    load_terms = db.Column(db.BigInteger, comment="提现期数")
    load_rate = db.Column(db.DECIMAL(10, 5), comment="提现利率")
    load_method = db.Column(db.String(200), comment="还款方式")
    result = db.Column(db.String(10), comment="提现结果")


class LogRepay(db.Model, LogBaseMixin, LogUserMixin):
    """还款表"""

    __tablename__ = "tb_repay"

    name = db.Column(db.String(200), comment="用户实名")
    location = db.Column(db.String(200), comment="还款地点")
    repay_time = db.Column(db.BigInteger, comment="还款时间", index=True)
    bank_no = db.Column(db.String(20), comment="还款卡号", index=True)
    repay_amt = db.Column(db.DECIMAL(12, 2), comment="还款额度")
    repay_method = db.Column(db.String(200), comment="还款方式", index=True)


class LogCase(db.Model):
    """案件查询"""
    __bind_key__ = "log_db"
    __tablename__ = "tb_case"

    id = db.Column(db.BigInteger, primary_key=True)

    wx_unionid = db.Column(db.String(100), comment="公众号union_id")
    uin = db.Column(db.BigInteger, comment="用户唯一id", index=True)
    name = db.Column(db.String(200), comment="客户名称", index=True)
    phone = db.Column(db.String(11), comment="客户手机号", index=True)
    id_card = db.Column(db.String(20), comment='身份证', index=True)
    production_code = db.Column(db.String(200), comment="产品ID", index=True)
    production_name = db.Column(db.String(100), comment="产品名称", index=True)
    merchant_code = db.Column(db.String(100), comment="租户ID", index=True)
    merchant_name = db.Column(db.String(100), comment="租户名字")
    operator_id = db.Column(db.String(100), comment="操作人ID")
    operator = db.Column(db.String(100), comment="操作人姓名")
    gps_address = db.Column(db.String(200), comment="地点")
    case_type = db.Column(db.Integer, \
                          comment='案件类型 0-加载 1-注册 2-实名认证 3-面签 4-授信 5-提现 6-还款', index=True)
    gps_city = db.Column(db.String(100), comment="城市")
    latitude = db.Column(db.String(50), comment='精度')
    longitude = db.Column(db.String(50), comment='纬度')

    result = db.Column(db.String(10), comment="事件结果")
    trx = db.Column(db.String(100), comment="案件号码")

    trigger_time = db.Column(db.BigInteger, comment="触发时间", index=True)

    start_time = db.Column(db.BigInteger, comment="案件开始时间", index=True)
    end_time = db.Column(db.BigInteger, comment="案件结束时间", index=True)

    data = db.Column(db.JSON, comment="数据直接保存")
