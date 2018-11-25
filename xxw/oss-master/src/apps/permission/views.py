from uuid import uuid4, uuid1

from django.db.models import Q
from rest_framework.views import APIView

from src.apps.common.func import make_response, permission_required, superuser_required, appid_required, token_required
from src.apps.model.models import Business, User, Role, Interface, Menu, Merchant, Domain
from src.constant import Msg

from .serializers import (
    BaseSerializer, BizSerializer, AddBizSerializer, BizEditSerializer,
    AcBizSerializer, AuthSerializer, AddAuthSerializer, InquireSreializer,
    AddRoleSerializer, RoleEditSerializer, AddMeIntSerializer, MeInSerializer,
    MeInEditSerializer, AddMerSerializer, EditMerSerializer, AllMerRole,
    QueryMerSerializer, EditMerDomain, MerSysSerializer, AddInterSerializer,
    EditIntSerializer)

from .util import role_insert, query_dict


# 公共接口-查询已启用的业务系统
class BusinessInquire(APIView):
    """
    查询已启用的业务系统
    """

    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        # 返回对应的商户的业务系统, 已启用的业务系统
        user = request.current_user
        factory = {"status": True}
        if not user.is_admin:
            factory.update({
                "merchant__code": user.merchant.code
            }) if user.merchant else {}
        business = Business.objects.filter(**factory).order_by("-create_time")
        data = [{
            "id": str(i.code),
            "name": i.name
        } for i in business if i.status]
        return make_response(data={"result": data})


# 公共接口 - 用户菜单
class UserMenu(APIView):
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        user = request.current_user
        appid = request.META.get("HTTP_APPID", None)
        try:
            biz = Business.objects.get(appid=appid)
            roles = user.roles.all()
            menus = [i.menu.all() for i in roles]
            menus = [j for i in menus for j in i]
            if user.is_admin:
                menus = Menu.objects.all()
            return make_response(
                data={
                    "name": user.name,
                    "merchantId": str(user.merchant.code) if user.merchant else None,
                    "merchantName": user.merchant.name if user.merchant else None,
                    "menu": [{
                        "id": str(i.code),
                        "name": i.name,
                        "path": i.path
                    } for i in menus],
                    "businessName": biz.name,
                    "businessId": str(biz.code)
                })
        except Business.DoesNotExist:
            return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)


# 业务接入管理
class BusinessViewSet(APIView):

    # 业务接入管理 - 查询
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = BizSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            page = data["page"]
            count = data["count"]
            name = data.get("name")
            user = request.current_user
            factory = {}
            if name:
                factory.update({"name__contains": name})
            if not user.is_admin:
                factory.update({"merchant__code": user.merchant.code})
            business = Business.objects.filter(
                **factory).order_by("-create_time")
            total = business.count()
            business = business[(page - 1) * count:page * count]
            return make_response(
                data={
                    "result": [{
                        "id": str(i.code),
                        "name": i.name,
                        "appid": i.appid,
                        "status": i.status
                    } for i in business],
                    "total":
                    total
                })
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 添加业务系统
    @token_required
    @appid_required
    @permission_required
    def post(self, request):
        serializer = AddBizSerializer(data=request.data)
        if serializer.is_valid():
            user = request.current_user
            data = serializer.validated_data
            name = data["name"]
            appid = data["appid"]
            biz = Business.objects.filter(name=name)
            if biz:
                return make_response(
                    code=Msg.BUSINESS_NAME_ALREADY_EXIST, status=400)
            business = Business(
                name=name,
                appid=str(uuid4()).replace("-", "") if appid else None,
                creator=user,
                code=str(uuid1()).replace("-", ""))
            business.save()
            if user.merchant:
                business.merchant.add(user.merchant)
                business.save()
            return make_response()
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 编辑业务系统
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = BizEditSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            id = data["id"]
            name = data.get("name", None)
            appid = data.get("appid", None)
            try:
                business = Business.objects.get(code=id)
                if appid and business.appid:
                    # 如果该业务系统的 appid 已经存在
                    return make_response(
                        code=Msg.APPID_ALREADY_EXIST, status=400)
                # 业务系统不允许重名
                if name:
                    # 查询一下这个 name 存不存在
                    biz = Business.objects.filter(name=name)
                    if biz and biz[0].name != business.name:
                        return make_response(
                            code=Msg.BUSINESS_NAME_ALREADY_EXIST, status=400)
                business.name = name if name else business.name
                business.appid = str(uuid4()).replace(
                    "-", "") if appid else business.appid
                business.save()
                return make_response()
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 业务接入管理 - 激活或禁用业务系统
class ActiveBusiness(APIView):
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = AcBizSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            id = data["id"]
            status = data["status"]
            try:
                business = Business.objects.get(code=id)
                business.status = status
                business.save()
                return make_response()
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 业务接入管理 - 分配 appid
class BusinessAppid(APIView):
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = BaseSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            try:
                business = Business.objects.get(code=id)
                if business.appid:
                    return make_response(
                        code=Msg.APPID_ALREADY_EXIST, status=400)
                business.appid = str(uuid4()).replace("-", "")
                business.save()
                return make_response()
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 授权管理
class AuthPermission(APIView):

    # 查询
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = AuthSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            page = data["page"]
            count = data["count"]
            name = data.get("name")
            user = request.current_user
            # superuser 用户查询所有的用户
            factory = {"active": True, "is_admin": False}
            if name:
                factory.update({"name__contains": name})
            if not user.is_admin:
                # 商户用户只能看到除自己以外的用户
                factory.update({"merchant__code": user.merchant.code})
            users = User.objects.filter(
                ~Q(code=user.code), **factory).order_by("-create_time")
            total = users.count()
            users = users[(page - 1) * count:page * count]
            data = []
            for i in users:
                res = {
                    "id": str(i.code),
                    "name": i.name,
                    "mobile": i.mobile,
                    "merchantName": i.merchant.name if i.merchant else None,
                    "merchantId": str(i.merchant.code) if i.merchant else None
                }
                businesses = {}
                roles = i.roles.all()
                for role in roles:
                    # 获取角色对应的业务 id 和业务名
                    business_id = role.business.code
                    business_name = role.business.name
                    if business_id in businesses:
                        businesses[business_id][1].append({
                            "id":
                            str(role.code),
                            "name":
                            role.name
                        })
                    else:
                        businesses[business_id] = [
                            business_name, [{
                                "id": str(role.code),
                                "name": role.name
                            }]
                        ]
                res.update({
                    "businesses": [{
                        "id": str(k),
                        "name": v[0],
                        "roles": v[1]
                    } for k, v in businesses.items()]
                })
                data.append(res)
            return make_response(data={"result": data, "total": total})
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 授权
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = AddAuthSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user_id = data["id"]
            roles = data["roles"]
            try:
                user = User.objects.get(code=user_id)
                user.roles.clear()
                for i in roles:
                    role = Role.objects.get(code=i)
                    user.roles.add(role)
                user.save()
                return make_response()
            except User.DoesNotExist:
                return make_response(code=Msg.USER_NOT_EXISTS, status=400)
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
            except Role.DoesNotExist:
                return make_response(code=Msg.ROLE_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 授权管理 - 获取所有的业务系统和角色
class BusinessRole(APIView):

    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = AllMerRole(data=request.GET)
        if serializer.is_valid():
            user = request.current_user
            merchant_code = serializer.validated_data["merchantId"]
            business = Business.objects.filter(merchant__code=merchant_code)
            data = {}
            if user.is_admin:
                for i in business:
                    data[(str(i.code), i.name)] = []
                    for j in i.roles.all():
                        data[(str(i.code), i.name)].append({
                            "id": str(j.code),
                            "name": j.name
                        })
            else:
                for i in business:
                    data[(str(i.code), i.name)] = []
                    for j in i.roles.all():
                        if j.merchant:
                            data[(str(i.code), i.name)].append({
                                "id": str(j.code),
                                "name": j.name
                            })
            return make_response(
                data={
                    "business": [{
                        "id": k[0],
                        "name": k[1],
                        "roles": v
                    } for k, v in data.items()]
                })


# 角色管理
class RolePermission(APIView):

    # 查询
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = InquireSreializer(data=request.GET)
        if serializer.is_valid():
            user = request.current_user
            merchant_id = user.merchant.code if user.merchant else None
            data = serializer.validated_data
            page, count, id, name = data["page"], data["count"], data.get(
                "businessId", None), data.get("name", None)
            # 超级用户获取所有的 role， 而其余用户获取当前业务系统的 role
            factory = {}
            if id:
                factory.update({"business__code": id})
            if name:
                factory.update({"name__contains": name})
            if not user.is_admin:
                factory.update({"merchant__code": merchant_id})
            roles = Role.objects.filter(**factory).order_by("-create_time")
            total = roles.count()
            roles = roles[(page - 1) * count:page * count]
            return make_response(
                data={
                    "result": [{
                        "id":
                        str(i.code),
                        "name":
                        i.name,
                        "businessId":
                        str(i.business.code),
                        "businessName":
                        i.business.name,
                        "creator":
                        i.creator.name,
                        "interface": [{
                            "id": str(j.code),
                            "path": j.path
                        } for j in i.interface.all()],
                        "menu": [{
                            "id": str(j.code),
                            "path": j.path
                        } for j in i.menu.all()]
                    } for i in roles],
                    "total":
                    total
                })
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 添加

    @token_required
    @appid_required
    @permission_required
    def post(self, request):
        serializer = AddRoleSerializer(data=request.data)
        if serializer.is_valid():
            user = request.current_user
            data = serializer.validated_data
            name = data["name"]
            business_id = data["businessId"]
            interface = data["interface"]
            menu = data["menu"]
            factor = {"business__code": business_id}
            if user.merchant:
                factor.update({"merchant__code": user.merchant.code})
            factor.update({"name": name})
            if Role.objects.filter(**factor):
                return make_response(
                    code=Msg.ROLE_NAME_ALREADY_EXIST, status=400)
            try:
                biz = Business.objects.get(code=business_id)
                role = Role(
                    name=name,
                    creator=user,
                    merchant=user.merchant,
                    business=biz,
                    code=str(uuid1()).replace("-", ""))
                role.save()
                return role_insert(role, interface, menu)
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(code=Msg.PARAMS_ERROR, status=400)

    # 修改
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = RoleEditSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = request.current_user
            id = data["id"]
            name = data.get("name", None)
            business_id = data.get("businessId", None)
            interface = data.get("interface", None)
            menu = data.get("menu", None)
            try:
                factor = {
                    "merchant__code": user.merchant.code
                } if user.merchant else {}
                factor.update({"name": name})
                role = Role.objects.get(code=id)
                roles = Role.objects.filter(**factor)
                if roles and roles[0].name != name:
                    return make_response(
                        code=Msg.ROLE_NAME_ALREADY_EXIST, status=400)
                biz = Business.objects.get(code=business_id)
                role.name = name if name else role.name
                if business_id is None:
                    return make_response()
                else:
                    if interface is not None:
                        role.interface.clear()
                    if menu is not None:
                        role.menu.clear()
                    interface = [] if interface is None else interface
                    menu = [] if menu is None else menu
                    role.business = biz
                    return role_insert(role, interface, menu)
            except Role.DoesNotExist:
                return make_response(code=Msg.ROLE_NOT_EXIST, status=400)
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 删除
    @token_required
    @appid_required
    @permission_required
    def delete(self, request):
        serializer = BaseSerializer(data=request.GET)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            try:
                role = Role.objects.get(code=id)
                # 删除角色
                # 判断用户是否有此角色
                role.delete()
                return make_response()
            except Role.DoesNotExist:
                return make_response(code=Msg.PARAMS_ERROR)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 角色管理 - 添加角色 - 业务系统 - 接口和菜单
class BusinessInterfaceMenu(APIView):
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = BaseSerializer(data=request.GET)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            user = request.current_user
            try:
                business = Business.objects.get(code=id)
                # 判断用户是否有访问此业务系统的权限
                if not user.is_admin and user.merchant not in business.merchant.all(
                ):
                    return make_response(code=Msg.NO_DATA, status=403)
                return make_response(
                    data={
                        "interface": [{
                            "id": str(i.code),
                            'name': i.name,
                        } for i in Interface.objects.filter(
                            business=business, visible=True)],
                        "menu": [{
                            "id": str(i.code),
                            "name": i.name,
                            "path": i.path
                        } for i in Menu.objects.filter(
                            business=business, visible=True)]
                    })
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 接口管理
class InterfacePermission(APIView):

    # 查询
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = MeInSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            page, count, id, name, path = \
                data["page"], data["count"], data.get(
                    "businessId"), data.get("name"), data.get("path")
            factory = query_dict(id, name, path)
            interface = Interface.objects.filter(**factory)
            total = interface.count()
            interface = interface.order_by("-create_time")[(page - 1) *
                                                           count:page * count]
            return make_response(
                data={
                    "result": [{
                        "name": i.name,
                        "path": i.path,
                        "method": i.method,
                        "id": str(i.code),
                        "businessId": str(i.business.code),
                        "businessName": i.business.name,
                        "visible": i.visible
                    } for i in interface],
                    "total":
                    total
                })

        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 添加
    @token_required
    @appid_required
    @permission_required
    def post(self, request):
        user = request.current_user
        if not user.is_admin:
            # 仅限超级用户添加
            return make_response(code=Msg.NO_DATA, status=403)
        serializer = AddInterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                biz = Business.objects.get(code=data["businessId"])
                interface = Interface(
                    name=data["name"],
                    path=data["path"],
                    method=data["method"],
                    visible=data["visible"],
                    creator=user,
                    business=biz,
                    code=str(uuid1()).replace("-", ""))
                interface.save()
                return make_response()
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 修改
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        user = request.current_user
        if not user.is_admin:
            # 仅限超级用户修改
            return make_response(code=Msg.NO_DATA, status=403)
        serializer = EditIntSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            id = data["id"]
            business_id = data.get("businessId", None)
            try:
                interface = Interface.objects.get(code=id)
                name = data.get("name", interface.name)
                path = data.get("path", interface.path)
                method = data.get("method", interface.method)
                business = None
                if business_id:
                    business = Business.objects.get(code=business_id)
                interface.name = name
                interface.path = path
                interface.method = method
                interface.business = business if business else interface.business
                interface.visible = data.get("visible", interface.visible)
                interface.save()
                return make_response()
            except Interface.DoesNotExist:
                return make_response(code=Msg.INTERFACE_NOT_EXIST, status=400)
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 删除
    @token_required
    @appid_required
    @permission_required
    def delete(self, request):
        user = request.current_user
        if not user.is_admin:
            # 仅限超级用户删除
            return make_response(code=Msg.NO_DATA, status=403)
        serializer = BaseSerializer(data=request.GET)
        if serializer.is_valid():
            try:
                interface = Interface.objects.get(
                    code=serializer.validated_data["id"])
                interface.delete()
                return make_response()
            except Interface.DoesNotExist:
                return make_response(code=Msg.INTERFACE_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 菜单管理
class MenuPermission(APIView):

    # 查询
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = MeInSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            page, count, id, name, path = \
                data["page"], data["count"], data.get(
                    "businessId"), data.get("name"), data.get("path")
            factory = query_dict(id, name, path)
            menu = Menu.objects.filter(**factory)
            total = menu.count()
            menu = menu.order_by("-create_time")[(page - 1) * count:page *
                                                 count]
            return make_response(
                data={
                    "result": [{
                        "name": i.name,
                        "path": i.path,
                        "id": str(i.code),
                        "businessId": str(i.business.code),
                        "businessName": i.business.name,
                        "visible": i.visible
                    } for i in menu],
                    "total":
                    total
                })
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 添加
    @token_required
    @appid_required
    @permission_required
    def post(self, request):
        user = request.current_user
        if not user.is_admin:
            # 仅限超级用户添加
            return make_response(code=Msg.NO_DATA, status=403)
        serializer = AddMeIntSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                biz = Business.objects.get(code=data["businessId"])
                menu = Menu(
                    name=data["name"],
                    path=data["path"],
                    creator=user,
                    business=biz,
                    code=str(uuid1()).replace("-", ""),
                    visible=data["visible"],
                )
                menu.save()
                return make_response()
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 修改
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        user = request.current_user
        if not user.is_admin:
            # 仅限超级用户修改
            return make_response(code=Msg.NO_DATA, status=403)
        serializer = MeInEditSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            id = data["id"]
            business_id = data.get("businessId", None)
            name = data.get("name", None)
            path = data.get("path", None)
            try:
                menu = Menu.objects.get(code=id)
                business = None
                if business_id:
                    business = Business.objects.get(code=business_id)
                menu.name = name if name else menu.name
                menu.path = path if path else menu
                menu.business = business if business else menu.business
                menu.visible = data.get("visible", menu.visible)
                menu.save()
                return make_response()
            except Menu.DoesNotExist:
                return make_response(code=Msg.MENU_NOT_EXIST, status=400)
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 删除
    @token_required
    @appid_required
    @permission_required
    def delete(self, request):
        user = request.current_user
        if not user.is_admin:
            return make_response(code=Msg.NO_DATA, status=403)
        serializer = BaseSerializer(data=request.GET)
        if serializer.is_valid():
            try:
                menu = Menu.objects.get(code=serializer.validated_data["id"])
                menu.delete()
                return make_response()
            except Menu.DoesNotExist:
                return make_response(code=Msg.MENU_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 商户管理
class MerchantManage(APIView):
    @token_required
    @appid_required
    @superuser_required
    def get(self, request):
        serializer = QueryMerSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            page, count, name, production = \
                data["page"], data["count"], data.get(
                    "name", None), data.get("production", None)
            factor = {"name__contains": name} if name else {}
            factor.update({
                "production__contains": production
            } if production else {})
            merchant = Merchant.objects.filter(
                **factor).order_by("-create_time")
            total = merchant.count()
            return make_response(
                data={
                    "result": [{
                        "id":
                        str(i.code),
                        "name":
                        i.name,
                        "production":
                        i.production,
                        "logo":
                        i.logo,
                        "ibaLoanName":
                        i.iba_loan_name,
                        "ibaLoanNo":
                        i.iba_loan_no,
                        "ibaCollectionName":
                        i.iba_collection_name,
                        "ibaCollectionNo":
                        i.iba_collection_no,
                        "ibaPreDepositName":
                        i.iba_pre_deposit_name,
                        "ibaPreDepositNo":
                        i.iba_pre_deposit_no,
                        "orgNo":
                        i.org_no,
                        "domains": [{
                            "businessId": str(j.business.code),
                            "businessName": str(j.business.name),
                            "domain": j.domain,
                            "domainId": str(j.code)
                        } for j in i.domains.all()]
                    } for i in merchant[(page - 1) * count:page * count]],
                    "total":
                    total
                })
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    @token_required
    @appid_required
    @superuser_required
    def post(self, request):
        serializer = AddMerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            name = data["name"]
            if Merchant.objects.filter(name=name):
                return make_response(
                    code=Msg.MERCHANT_NAME_ALREADY_EXIST, status=400)
            # 对同业账户重复性进行检测
            if Merchant.objects.filter(iba_loan_no=data["ibaLoanNo"]):
                return make_response(
                    code=Msg.LOAN_NO_ALREADY_EXIST, status=400)
            if Merchant.objects.filter(
                    iba_collection_no=data["ibaCollectionNo"]):
                return make_response(
                    code=Msg.COLLECTION_NO_ALREADY_EXIST, status=400)
            if Merchant.objects.filter(
                    iba_pre_deposit_no=data["ibaPreDepositNo"]):
                return make_response(
                    code=Msg.PRE_DEPOSIT_NO_ALREADY_EXIST, status=400)
            mer = Merchant(
                name=data["name"],
                logo=data["logo"],
                iba_loan_name=data["ibaLoanName"],
                iba_loan_no=data["ibaLoanNo"],
                iba_collection_name=data["ibaCollectionName"],
                iba_collection_no=data["ibaCollectionNo"],
                iba_pre_deposit_name=data["ibaPreDepositName"],
                iba_pre_deposit_no=data["ibaPreDepositNo"],
                org_no=data["orgNo"],
                production=data["production"],
                code=str(uuid1()).replace("-", ""))
            mer.save()
            return make_response()
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    @token_required
    @appid_required
    @superuser_required
    def put(self, request):
        serializer = EditMerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                mer = Merchant.objects.get(code=data["id"])
                name = serializer.validated_data.get("name", mer.name)
                if Merchant.objects.filter(~Q(code=mer.code), name=name):
                    return make_response(
                        code=Msg.MERCHANT_NAME_ALREADY_EXIST, status=400)
                if Merchant.objects.filter(
                        ~Q(code=mer.code),
                        iba_loan_no=data.get("ibaLoanNo", mer.iba_loan_no)):
                    return make_response(code=Msg.LOAN_NO_ALREADY_EXIST)
                if Merchant.objects.filter(
                        ~Q(code=mer.code),
                        iba_collection_no=data.get("ibaCollectionNo",
                                                   mer.iba_collection_no)):
                    return make_response(code=Msg.COLLECTION_NO_ALREADY_EXIST)
                if Merchant.objects.filter(
                        ~Q(code=mer.code),
                        iba_pre_deposit_no=data.get("ibaPreDepositNo",
                                                    mer.iba_pre_deposit_no)):
                    return make_response(code=Msg.PRE_DEPOSIT_NO_ALREADY_EXIST)
                mer.name = name if name else mer.name
                mer.logo = data.get("logo", mer.logo)
                mer.iba_loan_name = data.get("ibaLoanName", mer.iba_loan_name)
                mer.iba_loan_no = data.get("ibaLoanNo", mer.iba_loan_no)
                mer.iba_collection_name = data.get("ibaCollectionName",
                                                   mer.iba_collection_name)
                mer.iba_collection_no = data.get("ibaCollectionNo",
                                                 mer.iba_collection_no)
                mer.iba_pre_deposit_name = data.get("ibaPreDepositName",
                                                    mer.iba_pre_deposit_name)
                mer.iba_pre_deposit_no = data.get("ibaPreDepositNo",
                                                  mer.iba_pre_deposit_no)
                mer.org_no = data.get("orgNo", mer.org_no)
                mer.production = data.get("production", mer.production)
                mer.save()
                return make_response()
            except Merchant.DoesNotExist:
                return make_response(code=Msg.MERCHANT_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 商户管理 - 修改域名
class MerchantDomain(APIView):
    @token_required
    @appid_required
    @superuser_required
    def put(self, request):
        serializer = EditMerDomain(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if Domain.objects.filter(
                    ~Q(code=data["id"]), domain=data["domain"]):
                return make_response(code=Msg.DOMAIN_ALREADY_EXIST, status=400)
            try:
                do = Domain.objects.get(code=data["id"])
                do.domain = data["domain"]
                do.save()
                return make_response()
            except Domain.DoesNotExist:
                return make_response(code=Msg.DOMAIN_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 商户管理 - 分配系统
class MerchantSystem(APIView):
    @token_required
    @appid_required
    @superuser_required
    def put(self, request):
        serializer = MerSysSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                mer = Merchant.objects.get(code=data["id"])
                # 先清空当前用户的所有分配系统和域名
                mer.business.clear()
                Domain.objects.filter(merchant__code=data["id"]).delete()
                domains = []
                for i in data["system"]:
                    biz = Business.objects.get(code=i["businessId"])
                    mer.business.add(biz)
                    if Domain.objects.filter(domain=i["domain"]):
                        return make_response(
                            code=Msg.DOMAIN_ALREADY_EXIST, status=400)
                    domains.append(
                        Domain(
                            domain=i["domain"],
                            business=biz,
                            merchant=mer,
                            creator=request.current_user,
                            code=str(uuid1()).replace("-", "")))
                for i in domains:
                    i.save()
                mer.save()
                return make_response()
            except Merchant.DoesNotExist:
                return make_response(code=Msg.MERCHANT_NOT_EXIST, status=400)
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
        return make_response(
            code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


class BuzInterMe(APIView):
    """
    获取该业务系统下用户能访问的接口和菜单
    """

    @token_required
    @appid_required
    def get(self, request):
        appid = request.META.get("HTTP_APPID", None)
        try:
            biz = Business.objects.get(appid=appid)
            user = request.current_user
            if user.is_admin:
                return make_response(
                    data={
                        "interface": [{
                            "id": i.code,
                            "name": i.name,
                            "path": i.path
                        } for i in biz.interface.all()],
                        "menu": [{
                            "id": i.code,
                            "name": i.name,
                            "path": i.path
                        } for i in biz.menu.all()]
                    })
            roles = user.roles.all()
            interface = [j for i in roles for j in i.interface.all()]
            menu = [j for i in roles for j in i.menu.all()]
            return make_response(
                data={
                    "interface": [{
                        "id": i.code,
                        "name": i.name,
                        "path": i.path
                    } for i in interface],
                    "menu": [{
                        "id": i.code,
                        "name": i.name,
                        "path": i.path
                    } for i in menu]
                })
        except Business.DoesNotExist:
            return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)
