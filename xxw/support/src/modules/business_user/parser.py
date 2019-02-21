"""
b 端用户接口参数控制
author: roywu
date: 2018-08-24 10:35
"""

from flask_restful import reqparse

sign_in = reqparse.RequestParser()
sign_in.add_argument("mobile", location="json", type=str, required=True)
sign_in.add_argument("password", location="json", type=str, required=True)

user_info = reqparse.RequestParser()
user_info.add_argument("name", location="json", type=str, required=True)
user_info.add_argument("sex", location="json", type=str)
user_info.add_argument("address", location="json", type=str)
user_info.add_argument("wechat", location="json", type=str)
user_info.add_argument("qq", location="json", type=str)
user_info.add_argument("avatar", location="json", type=str)
user_info.add_argument("mail", location="json", type=str)

modify_password = reqparse.RequestParser()
modify_password.add_argument("oldPassword", location="json", type=str, required=True)
modify_password.add_argument("newPassword", location="json", type=str, required=True)
modify_password.add_argument("verifyPassword", location="json", type=str, required=True)

query_user = reqparse.RequestParser()
query_user.add_argument("page", location="args", type=int, default=1)
query_user.add_argument("count", location="args", type=int, default=10)
query_user.add_argument("name", location="args", type=str)
query_user.add_argument("mobile", location="args", type=str)

edit_user = reqparse.RequestParser()
edit_user.add_argument("name", location="json", type=str, required=True)
edit_user.add_argument("sex", location="json", type=str)
edit_user.add_argument("address", location="json", type=str)
edit_user.add_argument("wechat", location="json", type=str)
edit_user.add_argument("qq", location="json", type=str)
edit_user.add_argument("id", location="json", type=str, required=True)
edit_user.add_argument("mail", location="json", type=str)
edit_user.add_argument("mobile", location="json", type=str, required=True)

add_user = reqparse.RequestParser()
add_user.add_argument("name", location="json", type=str, required=True)
add_user.add_argument("sex", location="json", type=str)
add_user.add_argument("address", location="json", type=str)
add_user.add_argument("wechat", location="json", type=str)
add_user.add_argument("qq", location="json", type=str)
add_user.add_argument("merchantId", location="json", type=str, required=True)
add_user.add_argument("mail", location="json", type=str)
add_user.add_argument("mobile", location="json", type=str, required=True)

reset_pwd = reqparse.RequestParser()
reset_pwd.add_argument("id", location="json", type=str, required=True)

active_user = reqparse.RequestParser()
active_user.add_argument("id", location="json", type=str, required=True)
active_user.add_argument("status", location="json", type=bool, required=True)

obtain_mer_biz = reqparse.RequestParser()
obtain_mer_biz.add_argument("appid", location="args", type=str, required=True)
obtain_mer_biz.add_argument("domain", location="args", type=str)

biz_query = reqparse.RequestParser()
biz_query.add_argument("page", location="args", type=int, default=1)
biz_query.add_argument("count", location="args", type=int, default=10)
biz_query.add_argument("name", location="args", type=str)

add_biz = reqparse.RequestParser()
add_biz.add_argument("name", location="json", type=str, required=True)
add_biz.add_argument("appid", location="json", type=bool, default=False)

edit_biz = reqparse.RequestParser()
edit_biz.add_argument("name", location="json", type=str, required=True)
edit_biz.add_argument("id", location="json", type=str, required=True)
edit_biz.add_argument("appid", location="json", type=bool)

active_biz = reqparse.RequestParser()
active_biz.add_argument("status", location="json", type=bool, required=True)
active_biz.add_argument("id", location="json", type=str, required=True)

asign_appid = reqparse.RequestParser()
asign_appid.add_argument("id", location="json", type=str, required=True)

auth_query = reqparse.RequestParser()
auth_query.add_argument("page", location="args", type=int, default=1)
auth_query.add_argument("count", location="args", type=int, default=10)
auth_query.add_argument("name", location="args", type=str)

auth = reqparse.RequestParser()
auth.add_argument("id", location="json", type=str, required=True)
auth.add_argument("roles", location="json", type=list, required=True)

auth_manage = reqparse.RequestParser()
auth_manage.add_argument("merchantId", location="args", type=str, required=True)

role_query = reqparse.RequestParser()
role_query.add_argument("page", location="args", type=int, default=1)
role_query.add_argument("count", location="args", type=int, default=10)
role_query.add_argument("name", location="args", type=str)
role_query.add_argument("businessId", location="args", type=str)

delete_role = reqparse.RequestParser()
delete_role.add_argument("id", location="args", type=str, required=True)

role_mer_in = reqparse.RequestParser()
role_mer_in.add_argument("id", location="args", type=str, required=True)

inter_query = reqparse.RequestParser()
inter_query.add_argument("page", location="args", type=int, default=1)
inter_query.add_argument("count", location="args", type=int, default=10)
inter_query.add_argument("businessId", location="args", type=str)
inter_query.add_argument("name", location="args", type=str)
inter_query.add_argument("path", location="args", type=str)

delete_inter = reqparse.RequestParser()
delete_inter.add_argument("id", location="args", type=str, required=True)

menu_query = reqparse.RequestParser()
menu_query.add_argument("page", location="args", type=int, default=1)
menu_query.add_argument("count", location="args", type=int, default=10)
menu_query.add_argument("businessId", location="args", type=str)
menu_query.add_argument("name", location="args", type=str)
menu_query.add_argument("path", location="args", type=str)

delete_menu = reqparse.RequestParser()
delete_menu.add_argument("id", location="args", type=str, required=True)

mer_query = reqparse.RequestParser()
mer_query.add_argument("page", location="args", type=int, default=1)
mer_query.add_argument("count", location="args", type=int, default=10)
mer_query.add_argument("name", location="args", type=str)
mer_query.add_argument("production", location="args", type=str)

verify_interface = reqparse.RequestParser()
verify_interface.add_argument("interface", location="json", type=str, required=True)
verify_interface.add_argument("method", location="json", type=str, required=True)

query_production = reqparse.RequestParser()
query_production.add_argument("merchant_code", location="args", type=str)
query_production.add_argument("page", location="args", type=int, default=1)
query_production.add_argument("page_size", location="args", type=int, default=10)
