#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc: 短信相关
"""

from src import db
from src.comm.utils import utc_timestamp


class SMSApp(db.Model):
    """应用表"""

    __tablename__ = "tb_sms_app"

    id = db.Column(db.Integer, primary_key=True, comment="主键")
    app_name = db.Column(db.String(128), nullable=False, comment="应用名称")
    sign_name = db.Column(db.String(128), nullable=False, comment="签名名称")
    channel_code = db.Column(db.String(10), comment="通道商编号")
    channel_name = db.Column(db.String(128), nullable=False, comment="通道商名称")
    config = db.Column(db.Text, nullable=False, comment="应用配置")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    update_time = db.Column(db.BigInteger, default=utc_timestamp, comment="更新时间")
    operator_id = db.Column(db.String(128), nullable=False, comment="操作人")
    operator = db.Column(db.String(128), nullable=False, comment="操作人")
    is_valid = db.Column(db.Integer, default=1, comment="是否有效")
    is_delete = db.Column(db.Integer, default=0, comment="是否删除")


class SMSAppTemplate(db.Model):
    """应用模版表"""

    __tablename__ = "tb_sms_app_template"

    id = db.Column(db.Integer, primary_key=True, comment="主键")
    app_id = db.Column(db.Integer, nullable=False, comment="应用 id")
    template_content_code = db.Column(
        db.String(128), default="", comment="模版编号(从通道商处申请的模版编号)"
    )
    channel_name = db.Column(db.String(128), nullable=False, comment="通道商名称")
    template_title = db.Column(db.String(128), nullable=False, comment="模版名称")
    template = db.Column(db.String(512), nullable=False, comment="模版内容")
    price = db.Column(db.String(128), nullable=False, comment="模版单价")
    is_delete = db.Column(db.Integer, default=0, comment="是否删除")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    update_time = db.Column(db.BigInteger, default=utc_timestamp, comment="更新时间")
    operator_id = db.Column(db.String(128), nullable=False, comment="操作人")
    operator = db.Column(db.String(128), nullable=False, comment="操作人")
    is_valid = db.Column(db.Integer, default=1, comment="是否有效")
    last_check_time = db.Column(db.BigInteger, nullable=True, comment="最后检测时间")
    is_check = db.Column(db.Integer, default=0, comment="是否检测过")


class SmsBussinessTemplate(db.Model):
    """短信模板"""

    __tablename__ = "tb_sms_bussiness_template"

    id = db.Column(db.Integer, primary_key=True, comment="主键")
    merchant_code = db.Column(db.String(128), nullable=False, comment="商户编号")
    production_code = db.Column(db.String(128), default="", comment="产品编号")
    production_name = db.Column(db.String(128), default="", comment="产品名称")
    template_type_code = db.Column(db.Integer, nullable=False, comment="业务短信类型")
    app_templates = db.Column(db.Text, nullable=False, comment="应用模版列表")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    update_time = db.Column(db.BigInteger, default=utc_timestamp, comment="修改时间")
    operator_id = db.Column(db.String(128), nullable=False, comment="操作人")
    operator = db.Column(db.String(128), nullable=False, comment="操作人")
    is_auto = db.Column(db.Integer, comment="是否自动", default=0)
    is_valid = db.Column(db.Integer, default=0, comment="是否有效")


class SmsTemplateType(db.Model):
    """短信模板类型"""

    __tablename__ = "tb_sms_template_type"

    code = db.Column(db.Integer, primary_key=True, comment="类型编码")
    template_type = db.Column(db.String(128), nullable=False, comment="类型标题")


class SmsLog(db.Model):
    """短信记录"""

    __bind_key__ = "log_db"
    __tablename__ = "tb_chaos_sms_log"

    id = db.Column(db.Integer, primary_key=True, comment="主键")
    serial_number = db.Column(db.String(128), nullable=False, comment="短信流水号")
    merchant_code = db.Column(db.String(128), nullable=False, comment="商户编号")
    production_code = db.Column(db.String(128), nullable=False, comment="产品编号")
    production_name = db.Column(db.String(128), nullable=False, comment="产品名称")
    app_template_id = db.Column(db.String(128), nullable=False, comment="应用模板id")
    app_name = db.Column(db.String(128), nullable=False, comment="应用编号")
    channel_name = db.Column(db.String(128), nullable=False, comment="通道商名称")
    template_title = db.Column(db.String(128), nullable=False, comment="模版名称")
    template_content_code = db.Column(db.String(128), default="", comment="通道模板编号")
    template_type_code = db.Column(db.Integer, nullable=False, comment="模板类型编码")
    receiver = db.Column(db.String(128), nullable=False, comment="接受方")
    params = db.Column(db.String(128), nullable=False, comment="模板参数")
    status = db.Column(db.Integer, nullable=False, comment="发送状态（0:失败 1:成功)")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    remarks = db.Column(db.String(512), default="", comment="备注")
    price = db.Column(db.String(128), nullable=False, comment="价格")
    is_auto = db.Column(db.Integer, comment="是否自动", default=0)
