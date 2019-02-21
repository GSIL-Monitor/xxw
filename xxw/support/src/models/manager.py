"""
商户经理端
"""
from src import db
from src.commons.date_utils import utc_timestamp

from .user import TbMerchant


class TbManager(db.Model):
    """
    商户经理
    """

    __tablename__ = "tb_manager"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=True, index=True, comment="经理名")
    merchant_code = db.Column(db.String(32), index=True, comment="所属商户号")
    phone = db.Column(db.String(11), unique=True, nullable=True, index=True, comment="电话")
    wx_openid = db.Column(db.String(32), nullable=True, comment="# 用户与每个小程序绑定以后产生/绑定几个产生几个")
    sex = db.Column(db.String(32), nullable=True, comment="性别")
    address = db.Column(db.String(32), nullable=True, comment="地址")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    update_time = db.Column(db.BigInteger, default=utc_timestamp, comment="更新时间")
    creator = db.Column(db.String(32), comment="创建者")
    status = db.Column(db.Integer, default=0, comment="状态 0-不在工作  1-在工作 ")
    password = db.Column(db.String(264), comment="密码")
    id_card = db.Column(db.String(18), comment="身份证号码")
    id_img = db.Column(db.String(264), nullable=True, comment="身份证照片-正")
    id_img_back = db.Column(db.String(264), nullable=True, comment="身份证照片-反")
    head_img = db.Column(db.String(264), nullable=True, comment="大头照")
    code = db.Column(db.String(32), nullable=True, comment="客户经理编码")
    is_delete = db.Column(db.Boolean, default=False, comment="是否被删除")
    pwd_err_count = db.Column(db.Integer, default=0, nullable=True, comment="错误密码输出次数")
    pwd_frozen_time = db.Column(db.BigInteger, nullable=True, comment="密码错误冻结时间")


    def __repr__(self):
        return " {}".format(self.name)


class TbBeServedMerchant(db.Model):
    """
    被金科经理所服务的商户关系表
    """
    __tablename__ = "tb_manager_served_merchant"

    id = db.Column(db.Integer, primary_key=True)
    manager_code = db.Column(db.String(32), nullable=True, comment="客户经理编码")
    merchant_code = db.Column(db.String(32), nullable=True, comment="所服务商户")


class TbManagerWorkingAddress(db.Model):
    """
    工作地址表
    """
    __tablename__ = "tb_manager_working_address"

    id = db.Column(db.Integer, primary_key=True)
    manager_code = db.Column(db.String(32), comment="客户经理编码")
    province_code = db.Column(db.String(16), nullable=True, comment="省代码")
    province_name = db.Column(db.String(32), nullable=True, comment="省")
    city_code = db.Column(db.String(32), nullable=True, comment="市代码")
    city_name = db.Column(db.String(16), nullable=True, comment="市")
    area_code = db.Column(db.String(16), nullable=True, comment="工作地址代码")
    area_name = db.Column(db.String(32), nullable=True, comment="工作地址")





class TbFaceSignUser(db.Model):
    """
    面签表
    """
    __tablename__ = "tb_manager_face_sign_user"

    id = db.Column(db.Integer, primary_key=True)
    uin = db.Column(db.Integer, comment="面签用户 id")
    username = db.Column(db.String(16),nullable=True,comment="面签用户名")
    manager_name = db.Column(db.String(16), comment="商户经理名")
    phone = db.Column(db.String(11), comment="面签用户手机号")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    manager_code = db.Column(db.String(200), nullable=True, comment="客户经理编码")
    img = db.Column(db.String(30), nullable=True, comment="经理和用户合照")
    status = db.Column(db.Integer, default=0, comment="签约状态0-待签约,1-已抢单,2-签约审核中,3-审核通过,4-审核未通过")
    code = db.Column(db.String(30), comment="签约表单号(yyyyMMddHHmmss+uin)")
    update_time = db.Column(db.BigInteger, default=utc_timestamp, comment="更新时间")
    id_card = db.Column(db.String(30), comment="面签用户身份证号")
    order_time = db.Column(db.BigInteger, default=utc_timestamp, comment="预约时间")
    order_address = db.Column(db.String(255), comment="预约地点")
    order_address_code = db.Column(db.String(6), comment="预约地点编码(高德6位地区编码)")
    order_address_longitude = db.Column(db.String(80), nullable=True, comment="预约地点gps经度")
    order_address_latiude = db.Column(db.String(80), nullable=True, comment="预约地点gps纬度")
    order_remark = db.Column(db.String(255), nullable=True, comment="备注")
    extend = db.Column(db.String(255), nullable=True, comment="扩展字段")
    merchant_code = db.Column(db.String(80), comment="商户编码")
