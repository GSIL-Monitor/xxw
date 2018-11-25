from math import ceil

from django.test import TestCase
import requests

# 测试登陆借口

token = "982f7a6430874609b52ff10901288452"
appid = "1"
headers = {
    "jwt": token,
    "appid": appid
}


def user_signin():
    params = {
        "mobile": "13800138000",
        "appid": "123",
        "password": "1234"
    }

    url = "http://127.0.0.1:8000/api/user/sign_in"
    res = requests.post(url, json=params)
    return res.json()


# 测试登出接口
def user_signout():
    url = "http://127.0.0.1:8000/api/user/sign_out"
    res = requests.get(url)
    print(res.json())


# 测试获取用户信息
def get_user_info():
    url = "http://127.0.0.1:8000/api/user/info"
    res = requests.get(url)
    print(res.json())


# 测试更新用户信息
def update_user_info():
    url = "http://127.0.0.1:8000/api/user/info"
    params = {
        "username": "张学友",
        "wechat": "zhangxueyou",
        "qq": "123456789",
        "address": "成都天府新区兴隆湖畔 D 区",
        "avatar": "https://img.qq.com",
        "mail": "123456789@qq.com",
        "sex": "male"
    }
    res = requests.put(url, json=params)
    print(res.json())


# 测试更改密码
def change_password():
    params = {
        "token": token,
        "oldPassword": "1234",
        "verifyPassword": "1234",
        "newPassword": "1234"
    }
    url = "http://127.0.0.1:8000/api/user/password"
    res = requests.put(url, json=params)
    print(res.json())


# 测试用户管理
def get_users():

    page, count = 1, 10
    url = "http://111.230.231.89:8000/api/user"
    data = requests.get(url, headers=headers)
    print(data.json())
    # total = data.json()["data"].get("total")
    # page = ceil(total/count) - page + 1
    # new_data = requests.get(url, params={"page": page, "count": count}, headers=headers)
    # print(len(new_data.json()["data"]["result"]))
    # assert len(new_data.json()["data"]["result"]) > 1


if __name__ == "__main__":
    # print(user_signin())
    # user_signout()
    # get_user_info()
    # update_user_info()
    # change_password()
    get_users()
