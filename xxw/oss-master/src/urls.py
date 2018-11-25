"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from src.apps.user.views import (SignIn, Password, SignOut, UserInfo, MerchantView, ResetPassword, UserManage,
                                 UserActivation, MerBizName, ObtainUserId, upload_file)
from src.apps.permission.views import (BusinessInquire, UserMenu, BusinessViewSet, ActiveBusiness, BusinessAppid,
                                       AuthPermission, BusinessRole, RolePermission, BusinessInterfaceMenu,
                                       InterfacePermission, MenuPermission, MerchantManage, MerchantSystem, BuzInterMe)
from src.apps.manager.views import (ManagerManage, ManagerSignIn, ModifyPassword, ResetManagerPassword, ContractInfo, CommissionInfo,
                                     ForgetPassword, ManagerInfo )


urlpatterns = [
    # 用户
    path("api/v1/", include({
        path("user/sign_in", SignIn.as_view()),
        path("user/password", Password.as_view()),
        path("user/sign_out", SignOut.as_view()),
        path("user/info", UserInfo.as_view()),
        path("user/merchant", MerchantView.as_view()),
        # 用户管理
        path("user", UserManage.as_view()),
        path("user/password/reset", ResetPassword.as_view()),
        path("user/activation", UserActivation.as_view()),
        # 获取商户名和系统名
        path("user/name", MerBizName.as_view()),
        # 图片上传
        path("img/upload", upload_file),
        # 获取用户 id
        path("user/id", ObtainUserId.as_view()),
        # 公共接口
        path("public/business", BusinessInquire.as_view()),
        path("public/user_menu", UserMenu.as_view()),
        # 业务接入管理
        path("business", BusinessViewSet.as_view()),
        path("business/activation", ActiveBusiness.as_view()),
        path("business/appid", BusinessAppid.as_view()),
        # 权限管理 - 授权管理
        path("permission/auth", AuthPermission.as_view()),
        path("permission/auth/business_role", BusinessRole.as_view()),
        # 权限管理 - 角色管理
        path("permission/role", RolePermission.as_view()),
        path("permission/role/business/interface_menu", BusinessInterfaceMenu.as_view()),
        # 权限管理 - 接口管理
        path("permission/interface", InterfacePermission.as_view()),
        # 权限管理 - 菜单管理
        path("permission/menu", MenuPermission.as_view()),
        # 商户管理
        path("merchant", MerchantManage.as_view()),
        path("merchant/system", MerchantSystem.as_view()),
        # 获取该业务系统下用户能访问的接口和菜单
        path("business/inter_menu", BuzInterMe.as_view())
    })),
    #客户经理
    path("api/v1/", include({

        #管理-分配经理-获取信息-编辑信息
        path("manager/manage", ManagerManage.as_view()),
        #管理-重置密码
        path("manager/manage/resetpassword", ResetManagerPassword.as_view()),
        #登录-忘记密码
        path("manager/sign_in", ManagerSignIn.as_view()),
        path("manager/sign_in/forgetpassword", ForgetPassword.as_view()),        
        #信息-获取-修改
        path("manager/info",ManagerInfo.as_view()),
        #信息-修改密码
        path("manager/info/password", ModifyPassword.as_view()),
        #信息-获取签约信息
        path("manager/info/contract", ContractInfo.as_view()), 
        #信息-获取总提成
        path("manager/info/contract/commission", CommissionInfo.as_view()),
          
    })),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
