"""权限管理"""

from flask import request
from schema import Schema, And
from sqlalchemy import or_, and_
from flask_restful import Resource
from src.commons.logger import logger
from collections import defaultdict
from src import db, app
from src.commons.constant import Msg
from src.commons.utils import validate_schema
from src.commons.func import token_appid_permission_required
from src.modules.business_user.util import query_result, role_insert, get_business_code
from src.models.user import TbBusiness, TbInterface, TbMenu, TbRole, TbUser, TbMerchantBusiness, TbOperation
from src.modules.business_user.parser import (auth_query, auth, auth_manage, role_query, delete_role, role_mer_in, 
                                              inter_query, delete_inter, menu_query, delete_menu)


# 授权管理
class AuthPermission(Resource):

    # 查询
    @token_appid_permission_required
    def get(self):
        req = auth_query.parse_args(strict=True)
        page = req["page"]
        count = req["count"]
        name = req.get("name")
        user = request.current_user
        condition = [TbUser.code != user.code,
                     TbUser.active == 1,
                     TbUser.is_admin == 0,
                     TbUser.name.contains("%{}%".format(name if name else ""))]
        if not user.is_admin:
            # 非 admin 用户需要进行 merchant 筛选
            condition.append(TbUser.merchant_code == user.merchant.code)
        users = TbUser.query.filter(*condition).order_by(TbUser.id.desc()).paginate(page=page, per_page=count)
        data = []
        for i in users.items:
            res = {
                "id": str(i.code),
                "name": i.name,
                "mobile": i.phone,
                "merchantName": i.merchant.name if i.merchant else None,
                "merchantId": str(i.merchant.code) if i.merchant else None,
            }
            businesses = {}
            for role in i.roles:
                # 获取角色对应的业务 id 和业务名
                business_code = role.business.code
                business_name = role.business.name
                if business_code in businesses:
                    businesses[business_code][1].append({"id": str(role.code), "name": role.name})
                else:
                    businesses[business_code] = [business_name, [{"id": str(role.code), "name": role.name}]]
            res.update({"businesses": [{"id": str(k), "name": v[0], "roles": v[1]} for k, v in businesses.items()]})
            data.append(res)
        return {"result": data, "total": users.total}, 200

    # 授权
    @token_appid_permission_required
    def put(self):
        req = auth.parse_args(strict=True)
        current_user = request.current_user
        user = TbUser.query.filter_by(code=req["id"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        user.roles.clear()
        for i in req["roles"]:
            role = TbRole.query.filter_by(code=i).first()
            if not role:
                return Msg.ROLE_NOT_EXIST, 400
            elif not current_user.is_admin and role.business.appid == app.config["USER_CENTER"]:
                return Msg.PARAMS_ERROR, 400
            else:
                user.roles.append(role)
        msg = "SUPPORT | B_USER | AUTH | SUCCESS | EDITOR: {} {} | USER: {} {}".format(
            request.current_user.code, request.current_user.name, user.code, user.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="AUTH", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200


# 授权管理 - 获取所有的业务系统和角色
class BusinessRole(Resource):
    @token_appid_permission_required
    def get(self):
        req = auth_manage.parse_args(strict=True)
        user = request.current_user
        data = defaultdict(lambda: [])
        if user.is_admin:
            # 先获取用户所在商户分配的所有系统
            mer_biz = TbMerchantBusiness.query.filter_by(merchant_code=req["merchantId"]).all()
            biz_codes = [i.business_code for i in mer_biz]
            # 超级用户： 查看用户所在商户的角色和超级用户自己创建的角色
            roles = TbRole.query.filter(or_(TbRole.merchant_code == req["merchantId"],
                                            and_(TbRole.merchant_code == None,
                                                 TbRole.business_code.in_(biz_codes)))).all()
        else:
            # 普通管理员： 除用户中心以外商户其他系统的角色
            roles = TbRole.query.filter(TbRole.merchant_code == user.merchant_code,
                                        TbRole.business_code != get_business_code()).all()
        for i in roles:
            res = {"id": i.code, "name": i.name}
            key = (i.business.code, i.business.name)
            data[key].append(res)
        return {"business": [{"id": k[0], "name": k[1], "roles": v} for k, v in data.items()]}, 200


# 角色管理
class RolePermission(Resource):

    # 查询
    @token_appid_permission_required
    def get(self):
        req = role_query.parse_args(strict=True)
        user = request.current_user
        page, count, code, name = req["page"], req["count"], req.get("businessId"), req.get("name")
        condition = []
        if name:
            condition.append(TbRole.name.contains("%{}%".format(name)))
        if code:
            condition.append(TbRole.business_code == code)
        # 超级用户获取所有的 role， 而其余用户获取当前商户的除用户中心以外的其他业务系统的 role
        if not user.is_admin:
            condition.extend([TbRole.merchant_code == user.merchant_code,
                              TbRole.business_code != get_business_code()])
        roles = TbRole.query.filter(*condition).order_by(TbRole.id.desc()).paginate(page=page, per_page=count)
        return {
            "result": [{
                "id": str(i.code),
                "name": i.name,
                "businessId": str(i.business.code),
                "businessName": i.business.name,
                "creator": i.creator.name,
                # 角色创建者所属的商户
                "merchantName": i.creator.merchant.name if i.creator.merchant else "",
                "interface": [{"id": str(j.code), "path": j.path} for j in i.interface],
                "menu": [{"id": str(j.code), "path": j.path} for j in i.menu],
                } for i in roles.items
            ],
            "total": roles.total,
        }, 200

    # 添加
    @token_appid_permission_required
    def post(self):
        schema = Schema({"name": And(str, len), "businessId": And(str), "interface": [str], "menu": [str]})
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        user = request.current_user
        name = req["name"]
        business_code = req["businessId"]
        # 只允许 admin 用户添加用户中心角色
        if not user.is_admin and business_code == get_business_code():
            logger.info("SUPPORT | B_USER | ADD_ROLE | FAILED | USER: {} {} | REASON | {}".format(
                    user.code, user.name, "user has not permission to add a role"))
            return Msg.PARAMS_ERROR, 400
        # 检测角色名是否重复
        """
        逻辑如下:
        超级管理员: 检测 name + merchant + business == None 唯一
        普通用户: 检测 name + merchant + business 是否唯一
        """
        condition = [TbRole.name == name, TbRole.business_code == business_code]
        if user.merchant:
            condition.append(TbRole.merchant_code == user.merchant_code)
        else:
            condition.append(TbRole.merchant_code == None)
        role = TbRole.query.filter(*condition).first()
        if role:
            return Msg.ROLE_NAME_ALREADY_EXIST, 400
        biz = TbBusiness.query.filter_by(code=business_code).first()
        if not biz:
            return Msg.BUSINESS_NOT_EXIST, 400
        role = TbRole(name=name, creator_code=user.code, business_code=biz.code)
        try:
            db.session.add(role)
            user.create_roles.append(role)
            biz.roles.append(role)
            if user.merchant:
                user.merchant.roles.append(role)
                role.merchant_code = user.merchant.code
            data = role_insert(role, req["interface"], req["menu"])
            if data == {}:
                role.code = str(1300000000 + role.id)
                msg = "SUPPORT | B_USER | ADD_ROLE | SUCCESS | USER: {} {} | ROLE: {} {}".format(
                    user.code, user.name, role.code, role.name)
                operation = TbOperation(operator_code=user.code, content=msg, category="ROLE", type="ADD")
                db.session.add(operation)
                db.session.commit()
                logger.info(msg)
                return data, 200
            else:
                db.session.rollback()
                return data, 400
        except Exception as e:
            logger.info("add role failed, error: {}".format(str(e)))
            db.session.rollback()
            return Msg.ADD_ROLE_FAILED, 400

    # 修改
    @token_appid_permission_required
    def put(self):
        schema = Schema({
            "id": And(str),
            "name": And(str, len),
            "businessId": And(str),
            "interface": [str],
            "menu": [str]})
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        user = request.current_user
        code = req["id"]
        name = req.get("name")
        business_code = req.get("businessId")
        interface = req.get("interface")
        menu = req.get("menu")
        condition = [TbRole.name == name, TbRole.code != code, TbRole.business_code == business_code]
        if user.merchant:
            condition.append(TbRole.merchant_code == user.merchant_code)
        else:
            condition.append(TbRole.merchant_code == None)
        dup_role = TbRole.query.filter(*condition).first()
        if dup_role:
            return Msg.ROLE_NAME_ALREADY_EXIST, 400

        biz = TbBusiness.query.filter_by(code=business_code).first()
        if not biz:
            return Msg.BUSINESS_NOT_EXIST, 400
        role = TbRole.query.filter_by(code=code).first()
        # 只允许 admin 用户修改用户中心角色
        if not user.is_admin and role.business.appid == app.config["USER_CENTER"]:
            msg = "SUPPORT | B_USER | EDIT_ROLE | FAILED | USER: {} {} | ROLE: {} {} | REASON | {}".format(
                    user.code, user.name, role.code, role.name, "user has not permission to edit role")
            logger.info(msg)
            return Msg.PARAMS_ERROR, 400
        if not role:
            return Msg.ROLE_NOT_EXIST, 400
        role.name = name
        role.interface.clear()
        role.menu.clear()
        role.business = biz
        data = role_insert(role, interface, menu)
        if data == {}:
            msg = "SUPPORT | B_USER | EDIT_ROLE | SUCCESS | USER: {} {} | ROLE: {} {}".format(
                user.code, user.name, role.code, role.name)
            operation = TbOperation(operator_code=user.code, content=msg, category="ROLE", type="ADD")
            db.session.add(operation)
            db.session.commit()
            logger.info(msg)
            return data, 200
        else:
            db.session.rollback()
            return data, 400

    # 删除
    @token_appid_permission_required
    def delete(self):
        req = delete_role.parse_args(strict=True)
        role = TbRole.query.filter_by(code=req["id"]).first()
        user = request.current_user
        if role:
            # 只允许 admin 用户删除用户中心角色
            if not user.is_admin and role.business.appid == app.config["USER_CENTER"]:
                logger.info("SUPPORT | B_USER | DELTE_ROLE | FAILD | USER: {} {} | ROLE: {} {} | REASON | {}".format(
                    user.code, user.name, role.code, role.name, "user has not permission to delete role"))
                return Msg.PARAMS_ERROR, 400
        # 删除角色
        # 判断用户是否有此角色
        msg = "SUPPORT | B_USER | DELTE_ROLE | SUCCESS | USER: {} {} | ROLE: {} {}".format(
            user.code, user.name, role.code, role.name)
        operation = TbOperation(operator_code=user.code, content=msg, category="ROLE", type="DELETE")
        db.session.add(operation)
        logger.info(msg)
        try:
            db.session.delete(role)
            db.session.commit()
        except Exception as e:
            pass
        finally:
            return {}, 200


# 角色管理 - 添加角色 - 业务系统 - 接口和菜单
class BusinessInterfaceMenu(Resource):
    @token_appid_permission_required
    def get(self):
        """
        添加角色的时候，根据系统 code 获取对应的菜单列表
        超级管理员获取所有
        商户管理可以分配商户下面所有的系统，除用户中心以外
        """
        req = role_mer_in.parse_args(strict=True)
        user = request.current_user
        biz = TbBusiness.query.filter_by(code=req["id"]).first()
        if not biz:
            return Msg.BUSINESS_NOT_EXIST, 400
        if not user.is_admin and not TbMerchantBusiness.query.filter_by(merchant_code=user.merchant.code).first():
            # 判断用户是否有访问此业务系统的权限
            return Msg.NO_DATA, 403
        elif not user.is_admin:
            # 商户管理可以分配商户下面所有的系统，除用户中心以外
            if req["id"] == get_business_code():
                return Msg.USER_FORBIDDEN, 403
        # 超级管理员查看所有
        interface = TbInterface.query.filter_by(business_code=biz.code, visible=True).all()
        menu = TbMenu.query.filter_by(business_code=biz.code, visible=True).all()
        return {
            "interface": [{"id": str(i.code), "name": i.name} for i in interface],
            "menu": [{"id": str(i.code), "name": i.name} for i in menu]
        }, 200


# 接口管理
class InterfacePermission(Resource):

    # 查询
    @token_appid_permission_required
    def get(self):
        req = inter_query.parse_args(strict=True)
        page, count, id, name, path = (
            req["page"],
            req["count"],
            req.get("businessId"),
            req.get("name"),
            req.get("path"),
        )
        interface = query_result(TbInterface, id, name, path, page, count)
        return {
            "result": [{
                "name": i.name,
                "path": i.path,
                "method": i.method,
                "id": str(i.code),
                "businessId": str(i.business.code),
                "businessName": i.business.name,
                "visible": i.visible,
                } for i in interface.items
            ],
            "total": interface.total,
        }, 200

    # 添加
    @token_appid_permission_required
    def post(self):
        schema = Schema({
            "businessId": And(str),
            "interface": [{
                "path": And(str, len),
                "method": And(str, len),
                "name": And(str, len),
                "visible": And(bool)
            }]
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        user = request.current_user
        biz = TbBusiness.query.filter_by(code=req["businessId"]).first()
        if not biz:
            return Msg.BUSINESS_NOT_EXIST, 400
        inters = []
        for i in req["interface"]:
            inter = TbInterface.query.filter_by(business_code=biz.code,
                                                path=i["path"],
                                                method=i["method"]).first()
            if inter:
                # 通过 path 和 method 来确定一个接口，用户就是对这个接口进行修改
                inter.name = i["name"]
                inter.visible = i["visible"]
            else:
                interface = TbInterface(
                    name=i["name"],
                    path=i["path"],
                    method=i["method"],
                    visible=i["visible"],
                    creator_code=user.code,
                    business_code=biz.code,
                )
                biz.interface.append(interface)
                db.session.add(interface)
                inters.append(interface)
        db.session.commit()
        for i in inters:
            i.code = str(1400000000 + i.id)
        msg = "SUPPORT | B_USER | ADD_INTERFACE | SUCCESS | USER: {} {} | INTERFACE: {}".format(
            user.code, user.name, [i.name for i in inters])
        operation = TbOperation(operator_code=user.code, content=msg, category="INTERFACE", type="ADD")
        db.session.add(operation)
        db.session.commit()
        logger.info(Msg)
        return {}, 200

    # 修改
    @token_appid_permission_required
    def put(self):
        schema = Schema({
            "id": And(str),
            "businessId": And(str),
            "path": And(str, len),
            "method": And(str, len),
            "name": And(str, len),
            "visible": And(bool)
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        interface = TbInterface.query.filter_by(code=req["id"]).first()
        if not interface:
            return Msg.INTERFACE_NOT_EXIST, 400
        business = TbBusiness.query.filter_by(code=req["businessId"]).first()
        if not business:
            return Msg.BUSINESS_NOT_EXIST, 400
        interface.name = req["name"]
        interface.path = req["path"]
        interface.method = req["method"]
        interface.business_code = business.code
        interface.visible = req["visible"]
        msg = "SUPPORT | B_USER | EDIT_INTERFACE | SUCCESS | USER: {} {} | INTERFACE: {} {} {}".format(
            request.current_user.code, request.current_user.name, interface.code, interface.name, interface.path)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="INTERFACE", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200

    # 删除
    @token_appid_permission_required
    def delete(self):
        req = delete_inter.parse_args(strict=True)
        interface = TbInterface.query.filter_by(code=req["id"]).first()
        msg = "SUPPORT | B_USER | DELETE_INTERFACE | SUCCESS | USER: {} {} | INTERFACE: {} {} {} {}".format(
            request.current_user.code, request.current_user.name, interface.code, interface.name, interface.path, 
            interface.method)
        operation = TbOperation(operator_code=request.current_user.code,
                                content=msg,
                                category="INTERFACE",
                                type="DELETE")
        db.session.add(operation)
        logger.info(msg)
        try:
            db.session.delete(interface)
            db.session.commit()
        except Exception as e:
            pass
        finally:
            return {}, 200


# 菜单管理
class MenuPermission(Resource):

    # 查询
    @token_appid_permission_required
    def get(self):
        req = menu_query.parse_args(strict=True)
        page, count, id, name, path = (
            req["page"],
            req["count"],
            req.get("businessId"),
            req.get("name"),
            req.get("path"),
        )
        menu = query_result(TbMenu, id, name, path, page, count)
        return {
            "result": [{
                "name": i.name,
                "path": i.path,
                "id": str(i.code),
                "businessId": str(i.business.code),
                "businessName": i.business.name,
                "visible": i.visible,
                } for i in menu.items
            ],
            "total": menu.total,
        }, 200

    # 添加
    @token_appid_permission_required
    def post(self):
        schema = Schema({
            "businessId": And(str),
            "menu": [{
                "path": And(str, len),
                "name": And(str, len),
                "visible": And(bool)
            }]
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        biz = TbBusiness.query.filter_by(code=req["businessId"]).first()
        if not biz:
            return Msg.BUSINESS_NOT_EXIST, 400
        menus = []
        for i in req["menu"]:
            menu = TbMenu.query.filter_by(business_code=biz.code, path=i["path"]).first()
            if menu:
                # 通过 path 来确定一个菜单，用户就是对这个接口进行修改
                menu.name = i["name"]
                menu.visible = i["visible"]
            else:
                menu = TbMenu(
                    name=i["name"],
                    path=i["path"],
                    creator_code=request.current_user.code,
                    business_code=biz.code,
                    visible=i["visible"],
                )
                biz.menu.append(menu)
                menus.append(menu)
        db.session.add_all(menus)
        db.session.commit()
        for menu in menus:
            menu.code = str(1500000000 + menu.id)
        msg = "SUPPORT | B_USER | ADD_MENU | SUCCESS | USER: {} {} | MENU: {}".format(
            request.current_user.code, request.current_user.name, [i.name for i in menus])
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="MENU", type="ADD")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200

    # 修改
    @token_appid_permission_required
    def put(self):
        schema = Schema({
            "id": And(str),
            "businessId": And(str),
            "path": And(str, len),
            "name": And(str, len),
            "visible": And(bool)
        })
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        menu = TbMenu.query.filter_by(code=req["id"]).first()
        if not menu:
            return Msg.MENU_NOT_EXIST, 400
        business = TbBusiness.query.filter_by(code=req["businessId"]).first()
        if not business:
            return Msg.BUSINESS_NOT_EXIST, 400
        menu.name = req["name"]
        menu.path = req["path"]
        menu.business_code = business.code
        menu.visible = req.get("visible")
        msg = "SUPPORT | B_USER | EDIT_MENU | SUCCESS | USER: {} {} | MENU: {} {} {}".format(
            request.current_user.code, request.current_user.name, menu.code, menu.name, menu.path)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="MENU", type="EDIT")
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200

    # 删除
    @token_appid_permission_required
    def delete(self):
        req = delete_menu.parse_args(strict=True)
        menu = TbMenu.query.filter_by(code=req["id"]).first()
        msg = "SUPPORT | B_USER | DELETE_MENU | SUCCESS | USER: {} {} | MENU: {} {} {}".format(
            request.current_user.code, request.current_user.name, menu.code, menu.name, menu.path)
        operation = TbOperation(operator_code=request.current_user.code, content=msg, category="MENU", type="DELETE")
        db.session.add(operation)
        logger.info(msg)
        try:
            db.session.delete(menu)
            db.session.commit()
        except Exception as e:
            pass
        finally:
            return {}, 200
