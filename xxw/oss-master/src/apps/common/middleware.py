from src.apps.model.models import Business
from src.constant import Msg
from .func import token_verify, make_response


class CheckToken:
    """
    自定义中间件
    对用户传递过来的 token 进行验证
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith("/media/images/"):
            response = self.get_response(request)
            return response
        # 登陆系统里面的选项不需要 appid, 上传图片也不需要
        no_need_appid_url = ["/api/v1/user/info", "/api/v1/user/info", "/api/v1/user/password",
                             "/api/v1/user/sign_out", "/api/v1/user/avatar_upload", "/api/v1/user/name",
                             "/api/v1/user/id", "/api/v1/img/upload"]
        # 每一步的请求 headers 里面必须传递 appid
        if path in no_need_appid_url:
            # 随意取一个 appid 给允许不传 appid 的请求
            appid = Business.objects.all()[0].appid
        else:
            appid = request.META.get("HTTP_APPID", None)
            if appid is None:
                return make_response(code=Msg.NO_DATA, status=403)

        business = Business.objects.filter(appid=appid)
        if not business:
            return make_response(code=Msg.NO_DATA, status=403)

        # 登陆允许不传递 token, 上传图片也不需要
        if path not in ["/api/v1/user/sign_in", "/api/v1/user/name", "/api/v1/img/upload"]:
            token = request.META.get("HTTP_JWT", None)
            if token is None:
                return make_response(code=Msg.NO_DATA, status=401)
            user = token_verify(token)
            if user == "EXPIRED":
                return make_response(code=Msg.TOKEN_EXPIRATION, status=401)
            elif user == "INVALID":
                return make_response(code=Msg.INVALID_TOKEN, status=401)
            elif user == "NOTEXIST":
                return make_response(code=Msg.USER_NOT_EXISTS, status=401)
            # 判断用户能不能访问这个 appid 对应的业务系统
            if not user.is_admin and not user.merchant:
                return make_response(code=Msg.NO_DATA, status=403)
            elif not user.is_admin and business[0] not in user.merchant.business.all():
                return make_response(code=Msg.NO_DATA, status=403)
            # 为 request 修改默认 user 属性
            request.current_user = user
        response = self.get_response(request)
        return response



