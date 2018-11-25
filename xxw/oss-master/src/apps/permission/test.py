"""
针对 permission 的测试
"""

import requests


token = "4a40119763c24cae964509829f9389e9"
appid = "1"
base_url = "http://127.0.0.1:8000/api/v1/"


headers = {
    "jwt": token,
    "appid": appid
}


def merchants():
    url = "user/merchant"

    data = requests.get(base_url+url, headers=headers).json()
    print(data)


def roles():
    url = "permission/role"

    data = requests.get(base_url+url, headers=headers).json()
    print(data)
    # add role
    params = {
        "name": "user_manage",
        "businessId": 1,
        "interface": [1],
        "menu": [2]
    }
    print(requests.post(base_url+url, headers=headers, json=params).json())
    #  update
    params = {
        "id": 1,
        "name": "user_aggre"
    }
    print(requests.post(base_url + url, headers=headers, json=params).json())


def interface():

    url = "permission/interface"

    data = requests.get(base_url+url, headers=headers).json()
    print(data)


def menu():

    url = "permission/menu"

    data = requests.get(base_url+url, headers=headers).json()
    print(data)


def merchant():

    url = "merchant"

    # add a new one
    params = {
        "name": "渤海银行",
        "active": True
    }
    data = requests.post(base_url+url, headers=headers, json=params).json()
    print(data)
    # update info
    params = {
        "name": "渤海商业银行",
        "id": 6
        }
    print(requests.put(base_url+url, headers=headers, json=params).json())
    data = requests.get(base_url+url, headers=headers).json()
    print(data)


if __name__ == "__main__":
    # merchants()
    roles()
    # interface()
    # menu()
    # merchant()
