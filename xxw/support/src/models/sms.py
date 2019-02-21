from datetime import datetime

from src import db
from src.commons.logger import logger


class SmsTemplate(db.Model):
    """短信模板"""

    __tablename__ = "tb_sms_template"

    id = db.Column(db.Integer, primary_key=True)
    merchant_code = db.Column(db.String(128), nullable=False, comment="商户")
    production_code = db.Column(db.String(128), nullable=False, comment="产品id")
    production_name = db.Column(db.String(128), nullable=False, comment="产品名称")
    template_content_code = db.Column(db.String(128), nullable=False, comment="内容模板编号")
    template_type_code = db.Column(db.Integer, nullable=False, comment="模板类型id")
    template_title = db.Column(db.String(128), nullable=False, comment="模板名称")
    template = db.Column(db.String(512), nullable=False, comment="内容模板")
    create_time = db.Column(db.BigInteger, default=lambda: int(datetime.utcnow().timestamp()), comment="创建时间")
    update_time = db.Column(db.BigInteger, default=lambda: int(datetime.utcnow().timestamp()), comment="修改时间")
    is_valid = db.Column(db.Boolean, comment="是否有效", default=True)
    price = db.Column(db.String(128), nullable=False, comment="价格")
    is_delete = db.Column(db.Boolean, comment="是否删除", default=False)


class SmsTemplateType(db.Model):
    """短信模板类型"""

    __tablename__ = "tb_sms_tempate_type"
    id = db.Column(db.Integer, primary_key=True)
    template_type = db.Column(db.String(128), nullable=False, comment="类型标题")
    code = db.Column(db.Integer, nullable=False, unique=True, comment="模板类型id")


class SmsLog(db.Model):
    """短信记录"""
    __bind_key__ = "log_db"
    __tablename__ = "tb_sms_log"
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(128), nullable=False, comment="短信流水号")
    template_code = db.Column(db.Integer, nullable=False, comment="模板id")
    template_content_code = db.Column(db.String(128), nullable=False, comment="内容模板编号")
    production_code = db.Column(db.String(128), nullable=False, comment="产品id")
    production_name = db.Column(db.String(128), nullable=False, comment="产品名称")
    params = db.Column(db.String(128), comment="模板参数")
    template_type = db.Column(db.String(128), nullable=False, comment="模板类型")
    merchant_code = db.Column(db.String(128), nullable=False, comment="发送方")
    receiver = db.Column(db.String(128), nullable=False, comment="接受方")
    status = db.Column(db.Integer, nullable=False, comment="发送状态（0:失败 1:成功)")
    create_time = db.Column(db.BigInteger, default=lambda: int(datetime.utcnow().timestamp()), comment="创建时间")
    remarks = db.Column(db.String(128), comment="备注")

    def to_dict(self):

        temp = SmsTemplate.query.get_or_404(self.template_code)
        if temp is None:
            logger.warn("tb_sms_template exceptions")
            return {}
        return {
            "id": self.id,
            "serial_number": self.serial_number,
            "template_content_code": self.template_content_code,
            "production_code": self.production_code,
            "template_title": temp.template_title,
            "template_type": self.template_type,
            "template": temp.template,
            "template_code": self.template_code,
            "production_name": self.production_name,
            "params": self.params,
            "merchant_code": self.merchant_code,
            "receiver": self.receiver,
            "status": self.status,
            "create_time": self.create_time,
            "remarks": self.remarks
        }



