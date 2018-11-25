#!usr/bin/env python
# coding=utf-8
"""
@author: teddy
@time: 2018/09/06
@desc: 短信服务工具类
"""
import hashlib
import json
import re
from urllib.parse import urlencode

import requests
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

from src.comm.logger import logger
from src.comm.utils import print_run_time

PHONE = "^(13[0-9]|14[0-9]|15[0-9]|166|17[0-9]|18[0-9]|19[8|9])\d{8}$"
IP = "^((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))"

XUANWU_ERROR_CODE = {
    "-2": "发送参数填定不正确",
    "-3": "用户载入延迟",
    "-6": "密码错误",
    "-7": "用户不存在",
    "-11": "发送号码数理大于最大发送数量",
    "-12": "余额不足",
    "-99": "内部处理错误",
}

BAIWU_ERROR_CODE = {
    "100": "余额不足",
    "101": "账号关闭",
    "102": "短信内容超过1000字（包括1000字）或为空",
    "103": "手机号码超过200个或合法手机号码为空或者与通道类型不匹配",
    "104": "corp_msg_id超过50个字符或没有传corp_msg_id字段",
    "106": "用户名不存在",
    "107": "密码错误",
    "108": "指定访问ip错误",
    "109": "业务代码不存在或者通道关闭",
    "110": "扩展号不合法",
    "9": "访问地址不存在",
}

LIANTONG_ERROR_CODE = {
    # 大于 0 表示成功，但成功不代表能收到短信
    "–1": "账号未注册",
    "–2": "其他错误",
    "–3": "帐号或密码错误",
    "–5": "余额不足，请充值",
    "–6": "定时发送时间不是有效的时间格式",
    "–7": "提交信息末尾未加签名，请添加中文的企业签名【 】",
    "–8": "发送内容需在1到300字之间",
    "–9": "发送号码为空",
    "–10": "定时时间不能小于系统当前时间",
    "–11": "屏蔽手机号码",
    "–100": "IP 黑名单",
    "–102": "账号黑名单",
    "–103": "IP 未导白",
}


# 正则匹配电话号码
def verification_phone(phone_num):
    ret = re.match(PHONE, phone_num)
    return ret


# 正则匹配ip地址
def verification_ip(ip):
    ret = re.match(IP, ip)
    return ret


def single_sms_sender(
        channel_code,
        receiver,
        template_content,
        params,
        template_content_code,
        conf_params,
        sign_name,
):
    try:
        return SMSSender.send(
            channel_code=channel_code,
            receiver=receiver,
            template_content=template_content,
            params=params,
            template_content_code=template_content_code,
            conf_params=conf_params,
            sign_name=sign_name,
        )
    except NotFoundChannelException:
        return False, "不支持的短信通道"


class NotFoundChannelException(Exception):
    """找不到对应的通道商
    """

    pass


class SMSSender:
    """短信通道商管理，短信发送
    """

    _sender_dict = {}
    channel_list = []

    @classmethod
    def register(cls, code, name):
        def decorator(f):
            cls._sender_dict[code] = f
            cls.channel_list.append({"channel_code": code, "channel_name": name})
            return f

        return decorator

    @classmethod
    def send(cls, **kwargs):
        f = cls._sender_dict.get(kwargs.get("channel_code"))
        if not f:
            raise NotFoundChannelException()
        return f(**kwargs)


@print_run_time
@SMSSender.register("tx", "腾讯")
def tencent_single_sms_sender(
        receiver: str,
        params: list,
        template_content_code: str,
        conf_params: dict,
        sign_name: str,
        **kwargs,
):
    sms_appid = conf_params.get("sms_appid")
    sms_appkey = conf_params.get("sms_appkey")
    sms_sign = conf_params.get("sms_sign") or sign_name
    if not (sms_appid and sms_appkey and sms_sign):
        return False, "请检查appid,appkey,sms_sign配置"
    ssender = SmsSingleSender(sms_appid, sms_appkey)
    try:
        result = ssender.send_with_param(
            "86", receiver, int(template_content_code), params, sign=sms_sign
        )
        logger.info("tx sms result %s" % result)
    except HTTPError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
    status = True if result.get("result") == 0 else False
    return status, result["errmsg"]


@print_run_time
@SMSSender.register("xuanwu", "玄武")
def xuanwu_single_sms_sender(
        receiver: str, template_content: str, params: list, conf_params: dict, **kwargs
):
    text = template_content
    if params:
        params.insert(0, "")  # 模版索引从1开始
        text = template_content.format(*params)
    payload = {
        "username": conf_params["username"],
        "password": hashlib.md5(str(conf_params["password"]).encode()).hexdigest(),
        "to": receiver,
        "text": text,
        "subID": "",
        "msgType": conf_params["msgType"],
        "encode": 1,
        "version": "1.0",
    }
    headers = {"content-type": "application/json"}
    res = requests.post(
        "http://211.147.239.62:9050/cgi-bin/sendsms",
        data=json.dumps(payload),
        headers=headers,
    )
    if res.status_code != 200:
        return False, "HTTP请求失败 status_code %s" % res.status_code
    ret_code = str(res.text)
    if ret_code == "0":
        return True, ""
    elif ret_code in XUANWU_ERROR_CODE:
        return False, "result %s ,msg %s" % (ret_code, XUANWU_ERROR_CODE[ret_code])
    else:
        return False, "result %s ,msg 未知错误" % (ret_code)


@print_run_time
@SMSSender.register("baiwu", "百悟")
def baiwu_single_sms_sender(
        receiver: str,
        template_content: str,
        params: list,
        conf_params: dict,
        sign_name: str,
        **kwargs,
):
    text = template_content
    if params:
        params.insert(0, "")  # 模版索引从1开始
        text = template_content.format(*params)
    text = "【%s】%s" % (sign_name, text)  # 百悟通道模版
    payload = {
        "corp_id": conf_params["corp_id"],
        "corp_pwd": conf_params["corp_pwd"],
        "corp_service": conf_params["corp_service"],
        "mobile": receiver,
        "msg_content": text,
    }
    payload = urlencode(payload, encoding="gbk")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.request(
        "POST",
        "https://sms.cloud.hbsmservice.com:8443/sms_send2.do",
        data=payload,
        headers=headers,
        verify=False,
    )
    if res.status_code != 200:
        return False, "HTTP请求失败 status_code %s" % res.status_code
    ret_code = str(res.text)
    if ret_code.startswith("0#"):
        return True, ""
    elif ret_code in BAIWU_ERROR_CODE:
        return False, "result %s ,msg %s" % (ret_code, BAIWU_ERROR_CODE[ret_code])
    else:
        return False, "result %s ,msg 未知错误" % (ret_code)


@print_run_time
@SMSSender.register("liantong", "联通")
def liantong_single_sms_sender(
        receiver: str,
        template_content: str,
        params: list,
        conf_params: dict,
        sign_name: str,
        **kwargs,
):
    """联通短信发送接口
    """
    text = template_content
    if params:
        params.insert(0, "")  # 模版索引从1开始
        text = template_content.format(*params)
    text = "%s【%s】" % (text, sign_name)  # 联通签名必须在最后

    payload = {
        "CorpID": conf_params["CorpID"],
        "Pwd": conf_params["Pwd"],
        "Mobile": receiver,
        "Content": text,
    }
    data = urlencode(payload, encoding="gbk")

    res = requests.request(
        "POST",
        "https://sdk2.028lk.com/sdk2/BatchSend2.aspx",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if res.status_code != 200:
        return False, "HTTP请求失败 status_code %s" % res.status_code
    ret_code = str(res.text).strip()
    if int(ret_code) > 0:
        return True, ""
    elif ret_code in LIANTONG_ERROR_CODE:
        return False, "result %s ,msg %s" % (ret_code, LIANTONG_ERROR_CODE[ret_code])
    else:
        return False, "result %s ,msg 未知错误" % (ret_code)
