"""
{
    "code": 0,
    "msg": "成功",
    "data": {
        "LIST_TYPES": {
            "ip": "IP地址",
            "mail": "邮箱",
            "telephone": "手机号"
        },
        "BLACK_WHITE_LIST_TYPES": {
            "black": "黑名单",
            "white": "白名单",
            "gray": "灰名单",
            "audit": "审批白名单"
        },
        "TIME_WINDOWS": {
            "7d": "7天",
            "5d": "5天",
            "1d": "1天",
            "1h": "1小时",
            "30m": "30分钟",
            "10m": "10分钟",
            "5m": "5分钟",
            "1m": "1分钟"
        },
        "TIME_WINDOWS_VALUE": {
            "7d": 604800,
            "5d": 432000,
            "1d": 86400,
            "1h": 60,
            "30m": 30,
            "10m": 10,
            "5m": 5,
            "1m": 1
        },
        "PRODUCTS": {
            "xw": "新希望金科",
            "cdns": "成都农商行"
        },
        "DIMENSIONS": {
            "telephone": "电话号码",
            "id_card": "身份证号",
            "ip": "ip地址",
            "gps_coordinate": "GPS定位",
            "address_coordinate": "联系地址",
            "device_id": "设备指纹"
        },
        "EVENT_TYPES": {
            "loading": "首次加载",
            "verify_code": "动态验证码",
            "change_pwd": "修改密码",
            "rst_pwd": "重置密码",
            "change_pay_pwd": "修改交易密码",
            "set_pay_pwd": "设置交易密码",
            "rst_pay_pwd": "重置交易密码",
            "login": "登录",
            "register": "注册",
            "certification": "实名认证",
            "apply": "申请额度",
            "binding": "绑卡",
            "cash": "提现"
        }
    }
}
"""

from src.commons.model_resource import BaseResource
from src.models import FraudApiConfig


class FraudConfigAPI(BaseResource):
    def get(self):
        fraud_config = FraudApiConfig.objects.first()
        return fraud_config.to_dict()
