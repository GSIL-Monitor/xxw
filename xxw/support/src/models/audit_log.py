#!/usr/bin/env python
from src import db


class TbCreditLog(db.Model):
    """
    征信日志，调用流水
    """
    __bind_key__ = "log_db"
    __tablename__ = 'tb_credit_log'

    id = db.Column(db.Integer, primary_key=True, comment="自增ID")
    seq_no = db.Column(db.String(50), nullable=False, comment="调用流水ID")
    index_key = db.Column(db.String(100), nullable=False, comment="查询索引")
    interface = db.Column(db.String(20), nullable=False, comment="接口编码")
    supplier = db.Column(db.String(100), nullable=False, comment="供应商")
    product = db.Column(db.String(100), nullable=False, comment="供应商产品名称")
    type = db.Column(db.String(20), nullable=False, comment="接口类型")
    merchant_code = db.Column(db.String(32), nullable=True, comment="租户ID")
    production_code = db.Column(db.String(32), nullable=True, comment="产品ID")
    uin = db.Column(db.BigInteger, nullable=False, comment="用户ID")
    name = db.Column(db.String(100), nullable=False, comment="用户姓名")
    id_type = db.Column(db.String(10), nullable=False, comment="证件类型")
    id_card = db.Column(db.String(50), nullable=False, comment="证件号码")
    phone = db.Column(db.String(30), nullable=False, comment="手机号码")
    url = db.Column(db.String(200), comment="请求地址")
    price = db.Column(db.Numeric, nullable=True, comment="调用价格")
    start_time = db.Column(db.BigInteger, nullable=False, comment="调用开始时间")
    end_time = db.Column(db.BigInteger, nullable=True, comment="调用结束时间")
    status = db.Column(db.String(10), nullable=True, comment="调用结果")
    update_time = db.Column(db.BigInteger, nullable=False, comment="更新时间")

    def to_json(self):
        return {
            'id': self.id,
            'merchant_code': self.merchant_code or "",
            'production_code': self.production_code or "",
            'seq_no': self.seq_no,
            'interface': self.interface,
            'supplier': self.supplier,
            'product': self.product,
            'type': self.type,
            'uin': self.uin,
            'name': self.name,
            'id_type': self.id_type,
            'id_card': self.id_card,
            'phone': self.phone,
            'url': self.url or '',
            'start_time': self.start_time or '',
            'status': self.status or '',
            'price': str(self.price or 0),
            'end_time': self.end_time or '',

            'update_time': self.update_time or ''
        }
    
    def to_pretty(self):
        return {
            'id': self.id,
            'merchant_code': self.merchant_code or "",
            'production_code': self.production_code or "",
            'supplier': self.supplier,
            'product': self.product,
            'type': self.type,
            'name': self.name,
            'id_card': self.id_card,
            'id_type': self.id_type,
            'phone': self.phone,
            'start_time': self.start_time or '',
            'price': str(self.price or ''),
            'update_time': self.update_time or ''
        }
