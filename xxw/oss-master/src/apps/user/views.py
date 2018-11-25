import logging
from uuid import uuid1

from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from .serializers import (
    UserSignin,
    PasswordSerializer,
    UserInfoSerializer,
    UserSerializer,
    ResetPasswordSerializer,
    UserEditSerializer,
    UserAdditionSerializer,
    UserActivationSerializer,
    MerBizNameSerializer,
)
from src.constant import Msg
from src.apps.common.func import (
    make_response,
    generate_token,
    permission_required,
    appid_required,
    token_required,
)
from src.apps.model.models import User, Merchant, Menu, Interface, Domain, Business
from src.apps.common.conn import redis_conn


class SignIn(APIView):
    """
    用户登陆接口
    """
    @appid_required
    def post(self, request):
        serializer = UserSignin(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data["mobile"]
            password = serializer.validated_data["password"]
            # 检测用户是否存在
            try:
                user = User.objects.get(mobile=mobile)
                # 验证用户的密码和用户是否启用
                if not user.active:
                    return make_response(code=Msg.USER_NOT_ACTIVE, status=403)
                if user.verify_password(password):
                    appid = request.META.get("HTTP_APPID", None)
                    if not user.is_admin:
                        biz = Business.objects.get(appid=appid)
                        if biz not in [i.business for i in user.roles.all()]:
                            return make_response(code=Msg.PERMISSION_DENIED, status=403)
                        permissions = (
                            [i.appid for i in user.merchant.business.all()] if user.merchant else []
                        )
                        if appid not in permissions:
                            return make_response(code=Msg.PERMISSION_DENIED, status=403)
                    token = generate_token(user)
                    # 记录本次登陆时间
                    user.last_login = now()
                    user.save()
                    # 用户的接口和权限，超级用户返回所有的接口和菜单
                    if user.is_admin:
                        menu = [
                            {"id": str(i.code), "name": i.name}
                            for i in Menu.objects.all()
                        ]
                        interface = [
                            {"id": str(i.code), "name": i.name}
                            for i in Interface.objects.all()
                        ]
                    else:
                        roles = user.roles.all()
                        menu = [
                            {"id": str(i.code), "name": i.name}
                            for j in roles
                            for i in j.menu.all()
                        ]
                        interface = [
                            {"id": str(i.code), "name": i.name}
                            for j in roles
                            for i in j.interface.all()
                        ]
                    return make_response(
                        data={
                            "token": token,
                            "name": user.name,
                            "merchantId": str(user.merchant.code)
                            if user.merchant
                            else None,
                            "merchantName": user.merchant.name
                            if user.merchant
                            else None,
                            "menu": menu,
                            "interface": interface,
                        }
                    )
                return make_response(code=Msg.PASSWORD_ERROR, status=400)
            except User.DoesNotExist:
                return make_response(code=Msg.MOBILE_NOT_REGISTER, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


class SignOut(APIView):
    """
    用户登出
    """
    @token_required
    def get(self, request):
        token = request.META.get("HTTP_JWT", None)
        redis_conn.delete(token)
        return make_response()


class UserInfo(APIView):
    """
    用户信息相关
    """
    @token_required
    def get(self, request):
        """
        获取用户信息
        """
        user = request.current_user
        return make_response(
            data={
                "name": user.name,
                "mobile": user.mobile,
                "sex": user.sex,
                "mail": user.mail,
                "wechat": user.wechat,
                "address": user.address,
                "qq": user.qq,
                "avatar": user.avatar,
            }
        )

    @token_required
    def put(self, request):
        """
        修改用户信息
        """
        serializer = UserInfoSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = request.current_user
            user.name = data.get("name", user.name)
            user.sex = data.get("sex", user.sex)
            user.address = data.get("address", user.address)
            user.wechat = data.get("wechat", user.wechat)
            user.qq = data.get("qq", user.qq)
            user.avatar = data.get("avatar", user.avatar)
            user.mail = data.get("mail", user.mail)
            user.update_time = now()
            user.save()
            return make_response()
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


class Password(APIView):
    """
    密码相关
    """
    @token_required
    def put(self, request):
        """
        修改用户密码
        """

        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data["oldPassword"]
            new_password = serializer.validated_data["newPassword"]
            user = request.current_user
            if user.verify_password(old_password):
                user.generate_password(new_password)
                user.save()
                token = request.META.get("HTTP_JWT", None)
                redis_conn.delete(token)
                return make_response()
            return make_response(code=Msg.OLD_PASSWORD_ERROR, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 用户管理
class UserManage(APIView):

    # 获取用户信息

    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        serializer = UserSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            page = data.get("page")
            count = data.get("count")
            name = data.get("name")
            mobile = data.get("mobile")
            user = request.current_user
            factory = {}
            if name:
                factory.update({"name__contains": name})
            if mobile:
                factory.update({"mobile": mobile})
            if not user.is_admin:
                factory.update({"merchant__code": user.merchant.code})
            users = User.objects.filter(**factory).order_by("-create_time")
            total = users.count()
            users = users[(page - 1) * count : page * count]
            res = [
                {
                    "name": i.name,
                    "mobile": i.mobile,
                    "sex": i.sex,
                    "mail": i.mail,
                    "wechat": i.wechat,
                    "address": i.address,
                    "status": i.active,
                    "id": str(i.code),
                    "qq": i.qq,
                    "merchantId": str(i.merchant.code) if i.merchant else None,
                    "merchantName": i.merchant.name if i.merchant else None,
                }
                for i in users
            ]
            return make_response(data={"result": res, "total": total})
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 编辑用户
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = UserEditSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = User.objects.get(code=data["id"])
                user.name = data.get("name", user.name)
                user.sex = data.get("sex", user.sex)
                user.mail = data.get("mail", user.mail)
                user.wechat = data.get("wechat", user.wechat)
                user.qq = data.get("qq", user.qq)
                user.address = data.get("address", user.address)
                user.update_time = now()
                user.save()
                return make_response()
            except User.DoesNotExist:
                return make_response(code=Msg.USER_NOT_EXISTS, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

    # 添加用户
    @token_required
    @appid_required
    @permission_required
    def post(self, request):
        serializer = UserAdditionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                merchant = Merchant.objects.get(code=data["merchantId"])
                mobile = data["mobile"]
                if User.objects.filter(mobile=mobile):
                    return make_response(code=Msg.MOBILE_USED, status=400)
                user = User(
                    mobile=mobile,
                    name=data.get("name"),
                    sex=data.get("sex"),
                    wechat=data.get("wechat"),
                    qq=data.get("qq"),
                    mail=data.get("mail"),
                    address=data.get("address"),
                    merchant=merchant,
                    code=str(uuid1()).replace("-", ""),
                )
                user.generate_password("123456")
                user.save()
                return make_response()
            except Merchant.DoesNotExist:
                return make_response(code=Msg.MERCHANT_NOT_EXIST, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 用户管理 - 重置密码
class ResetPassword(APIView):
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = User.objects.get(code=data["id"])
                user.generate_password("123456")
                user.save()
                return make_response()
            except User.DoesNotExist:
                return make_response(code=Msg.USER_NOT_EXISTS, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 用户管理 - 获取商户信息
class MerchantView(APIView):
    @token_required
    @appid_required
    @permission_required
    def get(self, request):
        merchant = Merchant.objects.filter(active=True).order_by("-create_time")
        data = [{"id": str(i.code), "name": i.name} for i in merchant]
        return make_response(data={"result": data})


# 用户管理 - 启用禁用用户
class UserActivation(APIView):
    @token_required
    @appid_required
    @permission_required
    def put(self, request):
        serializer = UserActivationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = User.objects.get(code=data["id"])
                user.active = data["status"]
                user.save()
                return make_response()
            except User.DoesNotExist:
                return make_response(code=Msg.USER_NOT_EXISTS, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


# 获取商户名和系统名
class MerBizName(APIView):
    def get(self, request):
        serializer = MerBizNameSerializer(data=request.GET)
        if serializer.is_valid():
            domain = serializer.validated_data.get("domain")
            appid = serializer.validated_data["appid"]
            try:
                do = Domain.objects.filter(domain=domain)
                biz = Business.objects.get(appid=appid)
                return make_response(
                    data={
                        "merchantName": do[0].merchant.name if do else None,
                        "businessName": biz.name,
                    }
                )
            except Business.DoesNotExist:
                return make_response(code=Msg.BUSINESS_NOT_EXIST, status=400)

        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


class ObtainUserId(APIView):
    @token_required
    def get(self, request):
        return make_response(data={"userId": request.current_user.id})


@csrf_exempt
def upload_file(request):
    """
    图片上传
    :param request:
    :return:
    """
    if request.method == "POST":
        try:
            image = request.FILES.get("image")
            if not image:
                return make_response(code=Msg.NO_DATA, status=400)
            name = str(uuid1()).replace("-", "")
            filename = "images/{}.jpg".format(name)

            with open(settings.MEDIA_ROOT + "/" + filename, "wb+") as f:
                for chunk in image.chunks():
                    f.write(chunk)
            return make_response(
                data={
                    "url": "//"
                    + request.META["HTTP_HOST"]
                    + settings.MEDIA_URL
                    + filename
                }
            )
        except Exception as e:
            logging.warning(str(e))
            return make_response(code=Msg.UPLOAD_IMG_FAILED)
    return make_response(status=405)
