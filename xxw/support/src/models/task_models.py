"""数据models"""
from .base_mongo import db


class CreditConf(db.DynamicDocument):
    """
    三方征信源配置
    """
    meta = {'collection': 'credit_conf'}
    _id = db.ObjectIdField()
    interface = db.StringField(max_length=1024, required=True, verbose_name="接口编码")
    supplier = db.StringField(max_length=1024, verbose_name="供应商")
    product = db.StringField(max_length=1024, verbose_name="接口名称")
    type = db.StringField(max_length=1024, verbose_name="接口类别")
    desc = db.StringField(max_length=1024, verbose_name="接口描述")
    secret_key = db.StringField(max_length=1024, verbose_name="安全码")
    url = db.StringField(max_length=1024, verbose_name="接口请求地址")
    retry = db.IntField(verbose_name="失败重试次数")
    method = db.StringField(max_length=1024, verbose_name="接口请求方式")
    headers = db.DictField(verbose_name="接口请求头")
    auth_info = db.DictField(verbose_name="接口认证信息")
    account_config = db.DictField(verbose_name="人行账号配置")
    rate_limit = db.DictField(verbose_name="限速配置")
    timeout = db.IntField(verbose_name="接口连接超时时间")
    expire = db.IntField(verbose_name="接口数据缓存过期时间")
    status = db.IntField(verbose_name="接口状态")
    sys_params = db.DictField(verbose_name="系统参数")
    user_params = db.DictField(verbose_name="用户参数")
    input_params = db.DictField(verbose_name="接口参数")
    success_code_dict = db.DictField(verbose_name="成功状态码字典")
    retry_code_dict = db.DictField(verbose_name="失败重试状态码字典")
    failed_code_dict = db.DictField(verbose_name="失败状态码字典")
    create_time = db.IntField(verbose_name="创建时间")
    update_time = db.IntField(verbose_name="更新时间")
    is_delete = db.IntField(default=0, verbose_name="是否删除")

    def to_simple_json(self):
        return {
            "interface": self.interface or "",
            "supplier": self.supplier or "",
            "product": self.product or "",
            "type": self.type or "",
            "desc": self.desc or "",
            "interface_status": self.status or 0,
            "status": 0,
            "is_own": 0,
        }
