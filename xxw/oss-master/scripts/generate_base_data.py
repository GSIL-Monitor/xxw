"""
此脚本用于生成 oss 系统中的 业务系统 数据和 接口、菜单 数据
creator: roywu
created: 2018-07-26
"""
import random
from uuid import uuid1

from src.apps.model.models import User, Business, Menu, Interface

menu = [
  {
    "name": "仪表盘",
    "path": "/"
  },
  {
    "name": "权限管理-授权管理",
    "path": "/permission/auth"
  },
  {
    "name": "权限管理-角色管理",
    "path": "/permission/role"
  },
  {
    "name": "权限管理-接口管理",
    "path": "/permission/api"
  },
  {
    "name": "权限管理-菜单管理",
    "path": "/permission/menu"
  },
  {
    "name": "系统接入管理",
    "path": "/system"
  },
  {
    "name": "商户管理",
    "path": "/merchant"
  },
  {
    "name": "用户管理",
    "path": "/user"
  }
]

interface = [
  {
    "name": "权限管理-授权管理-列表",
    "path": "/api/v1/permission/auth",
    "method": "GET"
  },
  {
    "name": "权限管理-授权管理-授权",
    "path": "/api/v1/permission/auth",
    "method": "PUT"
  },
  {
    "name": "权限管理-授权管理-系统角色列表",
    "path": "/api/v1/permission/auth/business_role",
    "method": "GET"
  },
  {
    "name": "权限管理-角色管理-列表",
    "path": "/api/v1/permission/role",
    "method": "GET"
  },
  {
    "name": "权限管理-角色管理-编辑",
    "path": "/api/v1/permission/role",
    "method": "PUT"
  },
  {
    "name": "权限管理-角色管理-添加",
    "path": "/api/v1/permission/role",
    "method": "POST"
  },
  {
    "name": "权限管理-角色管理-删除",
    "path": "/api/v1/permission/role",
    "method": "DELETE"
  },
  {
    "name": "权限管理-角色管理-菜单接口列表",
    "path": "/api/v1/permission/role/business/interface_menu",
    "method": "GET"
  },
  {
    "name": "权限管理-接口管理-列表",
    "path": "/api/v1/permission/interface",
    "method": "GET"
  },
  {
    "name": "权限管理-接口管理-编辑",
    "path": "/api/v1/permission/interface",
    "method": "PUT"
  },
  {
    "name": "权限管理-接口管理-删除",
    "path": "/api/v1/permission/interface",
    "method": "DELETE"
  },
  {
    "name": "权限管理-接口管理-添加",
    "path": "/api/v1/permission/interface",
    "method": "POST"
  },
  {
    "name": "权限管理-菜单管理-列表",
    "path": "/api/v1/permission/menu",
    "method": "GET"
  },
  {
    "name": "权限管理-菜单管理-添加",
    "path": "/api/v1/permission/menu",
    "method": "POST"
  },
  {
    "name": "权限管理-菜单管理-编辑",
    "path": "/api/v1/permission/menu",
    "method": "PUT"
  },
  {
    "name": "权限管理-菜单管理-删除",
    "path": "/api/v1/permission/menu",
    "method": "DELETE"
  },
  {
    "name": "系统接入管理-列表",
    "path": "/api/v1/business",
    "method": "GET"
  },
  {
    "name": "系统接入管理-编辑",
    "path": "/api/v1/business",
    "method": "PUT"
  },
  {
    "name": "系统接入管理-添加",
    "path": "/api/v1/business",
    "method": "POST"
  },
  {
    "name": "系统接入管理-激活状态",
    "path": "/api/v1/business/activation",
    "method": "PUT"
  },
  {
    "name": "系统接入管理-分配APPID",
    "path": "/api/v1/business/appid",
    "method": "PUT"
  },
  {
    "name": "商户管理-列表",
    "path": "/api/v1/merchant",
    "method": "GET"
  },
  {
    "name": "商户管理-添加",
    "path": "/api/v1/merchant",
    "method": "POST"
  },
  {
    "name": "商户管理-编辑",
    "path": "/api/v1/merchant",
    "method": "PUT"
  },
  {
    "name": "商户管理-分配系统",
    "path": "/api/v1/merchant/system",
    "method": "PUT"
  },
  {
    "name": "用户管理-列表",
    "path": "/api/v1/user",
    "method": "GET"
  },
  {
    "name": "用户管理-添加",
    "path": "/api/v1/user",
    "method": "POST"
  },
  {
    "name": "用户管理-编辑",
    "path": "/api/v1/user",
    "method": "PUT"
  },
  {
    "name": "用户管理-激活状态",
    "path": "/api/v1/user/activation",
    "method": "PUT"
  },
  {
    "name": "用户管理-商户列表",
    "path": "/api/v1/user/merchant",
    "method": "GET"
  },
  {
    "name": "用户管理-重置密码",
    "path": "/api/v1/user/password/reset",
    "method": "PUT"
  },
  {
    "name": "已激活系统列表",
    "path": "/api/v1/public/business",
    "method": "GET"
  },
  {
    "name": "动态菜单列表",
    "path": "/api/v1/public/user_menu",
    "method": "GET"
  }
]


def operate_data():
    # 生成 superuser
    print("生成超级用户中......")
    user = User(
        name="超级用户",
        mobile="13308086321",
        is_admin=True,
        active=True,
        code=str(uuid1()).replace("-", "")
    )
    password = "".join([str(random.randint(0, 9)) for _ in range(8)])
    user.generate_password(password)
    user.save()
    print("成功超级用户成功，密码：{}, 请务必记住！".format(password))
    print("生成权限系统中......")
    appid = str(uuid1()).replace("-", "")
    biz = Business(
        # 业务系统名
        name="权限系统",
        # 生成的 appid
        appid=appid,
        # 状态，是否启用
        status=True,
        creator=user,
        code=str(uuid1()).replace("-", "")
    )
    biz.save()
    print("权限系统生成成功!")
    print("权限系统 appid 为 {}".format(appid))
    print("生成菜单中......")
    for i in menu:
        m = Menu(
            name=i["name"],
            path=i["path"],
            business=biz,
            creator=user,
            code=str(uuid1()).replace("-", "")
        )
        m.save()
    print("生成菜单成功!")
    print("生成接口中......")
    for i in interface:
        inter = Interface(
            name=i["name"],
            path=i["path"],
            method=i["method"],
            business=biz,
            creator=user,
            code=str(uuid1()).replace("-", "")
        )
        inter.save()
    print("生成接口成功！")


def run():
    try:
        operate_data()
        print("成功!")
    except Exception as e:
        print("失败!")
        print("失败原因: {}".format(str(e)))
