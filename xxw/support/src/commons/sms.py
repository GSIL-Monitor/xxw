import json

import requests

from src import zk
from src.commons.logger import logger

host = zk.get_os_center_hosts()

def verify_code(phone: str, verify_type: int, verify_code: str):
    """
    短信验证
    phone:验证手机号
    verify_type: 动码类型
    verify_code:验证码
    """
    url = "/msg/verification/run_verify_code"
    try:
        payload = {"phone": phone, "type": verify_type, "verify_code": verify_code}
        headers = {"content-type": "application/json"}
        res = requests.post(host + url, data=json.dumps(payload), headers=headers).json()
        if res["code"] != 0:
            logger.info("verify_code fail: {}".format(res))
            return False
        return True
    except Exception as e:
        import traceback
        logger.error("verify_code error {}".format(traceback.format_exc()))
        return False
