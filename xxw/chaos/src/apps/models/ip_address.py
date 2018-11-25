from src import mongo_db as db


class IPAddress(db.Document):
    """
    IP归属地
    """
    meta = {"collection": "ip_address","strict": False, "indexes": ["ip"]}

    ip = db.StringField(required=True, verbose_name="IP")
    country = db.StringField(default="中国", verbose_name="国家")
    province = db.StringField(verbose_name="省份")
    city = db.StringField(verbose_name="城市")
    unit = db.StringField(verbose_name="单位或学校")
    latitude = db.StringField(verbose_name="纬度")
    longitude = db.StringField(verbose_name="经度")
    time_zone = db.StringField(verbose_name="时区")
    area_code = db.StringField(verbose_name="中国行政区划代码")
    itc = db.StringField(verbose_name="国际电话区号")
    wcc = db.StringField(verbose_name="国际大洲代码")

