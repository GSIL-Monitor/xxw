from django.test import TestCase
import requests



#管理-分配
def post_Manager():
    params = {
    "phone": "18206708980",
      
    }
    url = "http://127.0.0.1:8000/api/v1/manager/manage"
    res = requests.post(url, json=params)
    print (res)
    print(res.json())

#管理-获取客户经理信息
def get_Manager():

    url = "http://127.0.0.1:8000/api/v1/manager/manage"
    res = requests.get(url, )
    print (res)
    print(res.json())
#管理-编辑
def put_manager():
    params = {
        
        "manager_code": "1",
        "sex":"male"
        
    }
    url = "http://127.0.0.1:8000/api/v1/manager/manage"
    res = requests.put(url, json=params)
    print (res)
    print(res.json())

#管理-重置密码
def reset_password():
    params = {
        "manager_code": "1",
    }
    url = "http://127.0.0.1:8000/api/v1/manager/manage/resetpassword"
    res = requests.put(url, json=params)
    print(res.json())

#经理登录
def post_sign():
    params = {
    "phone":"18206708942",
    "union_id": "1111",
    "open_id":"2222",
    "pwd":"123456", 
    "kind":"1",
    }
    url = "http://127.0.0.1:8000/api/v1/manager/sign_in"
    res = requests.post(url, json=params)
    print (res)
    print(res.json())
    t =(res.json()).get("data").get("token")
    return t

#修改当前客户经理密码
def change_password():
    params = {
        "oldPassword": "000000",
        "verifyPassword": "123456",
        "newPassword": "123456"
    }
    url = "http://127.0.0.1:8000/api/v1/manager/info/password"
    res = requests.put(url, json=params,headers=headers)
    print(res.json())

#获取当前客户经理信息
def get_manager_info():    
    headers = {
    "jwt": token,
    }
    url = "http://127.0.0.1:8000/api/v1/manager/info"
    res = requests.get(url,headers=headers)
    print(res.json())

#修改当前客户经理信息
def put_manager_info():
    params = {
        "address":"45678"               
    }
    headers = {
    "jwt": token,
    }    
    url = "http://127.0.0.1:8000/api/v1/manager/info"
    res = requests.put(url, json=params,headers=headers)
    print (res)
    print(res.json())

#获取当前客户经理签约表信息
def get_contract():
    headers = {
    "jwt": token,
    }      
    url = "http://127.0.0.1:8000/api/v1/manager/info/contract"
    res = requests.get(url,headers=headers)
    print(res.json())

#获取当前客户经理总提成
def get_Commission():
    headers = {
    "jwt": token,
    }  
    url = "http://127.0.0.1:8000/api/v1/manager/info/contract/commission"
    res = requests.get(url,headers=headers)
    print(res.json())


# post_Manager()
# #get_Manager()
# put_manager()s
# reset_password()

#信息类测试
token=post_sign()
# get_manager_info()
# put_manager_info()
# #change_password()
# get_contract()
# get_Commission()


    

