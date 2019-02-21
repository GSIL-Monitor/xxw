"""
商户信息推送
author: roy wu
create at: 2018-08-20 10:17 AM
"""

import time
import requests
from src.commons.local_host import ip
from src import zk, db
from src.commons.logger import logger


def push_merchant(merchant) -> tuple:
    """
    推送商户信息
    """
    url = zk.loan_mng_hosts
    if not url:
        return False, "未找到信贷核心地址"
    params = {
        "ctrlData": {
            "servcId": "AS_BANK_ACCOUNT_UPDATE",
            "servcScn": "01",
            "sysIndicator": "000001",
            "reqTime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "transMedium": "00000000",
            "bizTrackNo": "{}".format(time.time()*10000000),
            "transSeqNo": "{}".format(time.time()*10000000),
            "hostIp": ip,
        },
        "body": {
            "reqHead": {
                "bankNo": merchant.code,
                "custId": merchant.code
            },
            "bankName": merchant.name,
            "openFlag": "1",
            "acctSelfInd": "1",
            "merchNo": merchant.xw_code,
            "loanAcctNo": merchant.iba_loan_no,
            "loanAcctName": merchant.iba_loan_name,
            "deduAcctNo": merchant.iba_collection_no,
            "deduAcctName": merchant.iba_collection_name,
            "preAcctNo": merchant.iba_pre_deposit_no,
            "preAcctName": merchant.iba_pre_deposit_name,
            "assetsImpairmentNum": "90",
            "orgNo": merchant.org_no
        }
    }
    if merchant.push_flag == 0:
        params["body"].update({"operType": "1"})
    else:
        params["body"].update({"operType": "2"})
    try:
        res = requests.post(url + "/loan_mng/handle", json=params).json()
        code = res["respData"]["code"]
        if code == "00000000":
            merchant.push_flag = 1
            db.session.commit()
            logger.info("PUSH MERCHANT SUCCESS!")
            return True, ""
        else:
            logger.warn("push merchant info failed, failed info {}".format(res))
            return False, res.get("respData", {}).get("message") or str(res)
    except Exception as e:
            logger.warn("push merchant info failed, failed info {}".format(str(e)))
            return False, "网络错误"
