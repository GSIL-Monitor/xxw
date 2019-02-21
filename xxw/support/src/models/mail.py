from datetime import datetime

from src import db


class MailTemplate(db.Model):
    """邮件模板"""

    __tablename__ = "tb_mail_template"

    id = db.Column(db.Integer, primary_key=True)
    merchant = db.Column(db.String(128), nullable=False, comment="商户")
    template_type = db.Column(db.String(128), nullable=False, comment="邮件类型")
    template_id = db.Column(db.String(128), nullable=False, comment="邮件模板id")
    template_title = db.Column(db.String(128), nullable=False, comment="邮件模版标题")
    template = db.Column(db.String(512), nullable=False, comment="内容模板")
    create_time = db.Column(db.BigInteger, default=lambda: int(datetime.utcnow().timestamp()), comment="创建时间")
    update_time = db.Column(db.BigInteger, comment="更新时间")
    is_valid = db.Column(db.Boolean, comment="是否有效")


class MailLog(db.Model):
    """邮件日志"""
    __bind_key__ = "log_db"
    __tablename__ = "tb_mail_log"

    id = db.Column(db.Integer, primary_key=True)
    merchant = db.Column(db.String(128), nullable=False, comment="发送方")
    receiver = db.Column(db.String(128), nullable=False, comment="接受方")
    template_title = db.Column(db.String(128), nullable=False, comment="邮件模版标题")
    template_type = db.Column(db.String(128), nullable=False, comment="邮件类型")
    content = db.Column(db.String(512), nullable=False, comment="发送内容")
    status = db.Column(db.Integer, nullable=False, comment="发送状态（0:失败 1:成功 2:发送中)")
    create_time = db.Column(db.BigInteger, default=lambda: int(datetime.utcnow().timestamp()), comment="创建时间")
