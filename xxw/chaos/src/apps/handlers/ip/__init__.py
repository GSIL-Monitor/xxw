import json
from _md5 import md5

import datx
import requests

from src.apps.models.ip_address import IPAddress

key = "61e71b0f62445676583637cc709707de"  # 高德的个人账号key
Token = ""  # ipip购买服务后的Token
sid = ""  # ipip购买服务后的sid
uid = ""  # ipip购买服务后的uid
timeout = 1  # 设置访问超时


def get_all_fields(x, y):  # 返回数据库所有字段
    new_dict = {}
    if isinstance(x, dict):
        for i in y:
            new_dict[i] = x.get(i, "")
    elif isinstance(x, list):
        new_dict = {k: v for k in y for v in x}
    return new_dict


# 通过高德API获取ip地址
def get_data_by_amap(ip):
    url = "https://restapi.amap.com/v3/ip?ip={}&output=json&key={}".format(ip, key)
    try:
        res = requests.get(url, timeout=timeout)
        get_data = json.loads(res.content)
        get_data["ip"] = ip  # 拿到的是一个字典
        return get_all_fields(get_data, tuple(IPAddress._fields.keys())[0:-2])
    except Exception:
        return


# 调用ipip接口获取ip地址
def get_data_by_ipip(ip):
    sign = md5(("addr=" + ip + "&token=" + Token).encode('utf-8'))
    headers = {'token': Token}
    url = "http://ipapi.ipip.net/find?addr={}&sig={}".format(ip, sign)
    try:
        res = requests.get(url, headers=headers, timeout=timeout)
        get_data = json.loads(res.content)
        get_data["data"].insert(0, ip)  # 拿到的是一个列表
        return get_all_fields(get_data["data"], tuple(IPAddress._fields.keys())[0:-2])
    except Exception:
        return


# 调用datx文件获取ip地址
def get_data_by_file(ip):
    data_source = datx.City("./17monipdb.datx")
    try:
        result = data_source.find(ip)
        result.insert(0, ip)
        return get_all_fields(result, tuple(IPAddress._fields.keys())[0:-2])
    except Exception:
        return
