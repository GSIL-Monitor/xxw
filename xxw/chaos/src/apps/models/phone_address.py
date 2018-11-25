from src import db


class PhoneAddress(db.Model):
    """
    手机号码归属地
    """

    __tablename__ = "tb_phone"

    id = db.Column(db.Integer, primary_key=True)
    pref = db.Column(db.String(8), comment="前三位")
    phone = db.Column(db.String(8), index=True, unique=True, comment="前七位")
    province = db.Column(db.String(32), comment="省份")
    city = db.Column(db.String(32), comment="城市")
    isp = db.Column(db.String(8), comment="运营商")
    post_code = db.Column(db.String(32), comment="邮编")
    city_code = db.Column(db.String(32), comment="城市编码")
    area_code = db.Column(db.String(32), comment="区域编码")

    def __repr__(self):
        return " {}".format(self.name)
