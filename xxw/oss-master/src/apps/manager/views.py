import logging
import requests
from uuid import uuid1
from datetime import timedelta, datetime
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.timezone import now
import datetime 
from django.utils.timezone import utc
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from .serializers import ManagerAdditionSerializer, ResetPasswordSerializer, ManagerSigninSerializer,\
    ModifyPasswordSerializer, ManagerEditSerializer, GetManagerInfoSerializer, ForgetPasswordSerializer,\
    ContractinfoSerializer, CommissionInfoSerializer, ContractInfoManageSerializer, ManagerInfoSerializer
from src.constant import Msg
from src.apps.common.func import make_response, generate_token, permission_required, token_required
from src.apps.model.models import User, Merchant, Menu, Interface, Domain, Business, Manager, ChannelPhone, Contract
from src.apps.common.conn import redis_conn
from .util import (generate_manager_token, manager_token_required, user_test_token_required)


# 商户经理管理
class ManagerManage(APIView):
    # 分配经理   
    @token_required
    def post(self, request):
        serializer = ManagerAdditionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data                                       
            user = request.current_user           
            phone = data["phone"]                           
            if Manager.objects.filter(phone=phone):
                return make_response(code=Msg.MOBILE_USED, status=400)                                                     
            manager = Manager(                     
                merchant_code = user.merchant.code,
                phone = phone,
                creator = user,
                code = str(uuid1()).replace("-","")
            )
            manager.generate_password("123456")
            manager.save()
            return make_response()
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)   
    # 获取经理信息
    @token_required
    def get(self, request):
        serializer = GetManagerInfoSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            manager = Manager.objects.all()
            data=[{
                "id":str(i.id),
                "name":i.name,
                "phone":i.phone,
                "sex":i.sex,
                "address":i.address,
                "code":i.code,
                "create_time":i.create_time,
                "update_time":i.update_time,
                "creator":i.creator.name,
                "status":i.status,
                "id_code":i.id_code,
                "id_img":i.id_img,
                "head_img":i.head_img,                              
            }for i in manager]
            return make_response(data={"result":data})
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)
    #　编辑信息
    @token_required
    def put(self, request):
        serializer = ManagerEditSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                manager = Manager.objects.get(code=data["manager_code"])
                manager.name=data.get("name",manager.name)
                manager.sex=data.get("sex",manager.sex)
                manager.address=data.get("address",manager.address)
                manager.id_img=data.get("id_img",manager.id_img)
                manager.head_img=data.get("head_img",manager.head_img)
                manager.save()
                return make_response()
            except Manager.DoesNotExist:    
                return make_response(code=Msg.MANAGER_NOT_EXISTS, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

# 商户经理　-　重置密码
class ResetManagerPassword(APIView):
   @token_required 
   def put(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                manager = Manager.objects.get(code=data["manager_code"])
                manager.generate_password("123456")
                manager.save()
                return make_response()
            except Manager.DoesNotExist:
                return make_response(code=Msg.MANAGER_NOT_EXISTS, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)


class ManagerSignIn(APIView):
    """
    客户经理登录接口
    """
    def post(self, request):
        serializer = ManagerSigninSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            kind = data["kind"]
            if kind =="1":
                #电话+密码登录
                try:
                    phone = data["phone"]
                    password = data["pwd"]
                except KeyError:
                    return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)
                if not Manager.objects.filter(phone=phone):
                    return make_response( code=Msg.MANAGER_NOT_EXISTS, status=400) 
                manager = Manager.objects.get(phone=phone)  
                
                now = datetime.datetime.utcnow().replace(tzinfo=utc)   
                if manager.pwd_frozen_time and manager.pwd_frozen_time > now:
                    #冻结
                    msg = "密码错误多次，账号已被冻结，请于 {} 之后再试。".format(
                    manager.pwd_frozen_time.strftime("%y-%m-%d %H:%M:%S"))
                    return make_response( msg=msg)
                elif manager.pwd_frozen_time and manager.pwd_frozen_time <= now:                    
                    #已出冻结
                    manager.pwd_frozen_time = None
                    manager.pwd_err_count = 0
                    manager.save()
                    if not manager.verify_password(password):
                        manager.pwd_err_count +=1
                        manager.save()
                        if manager.pwd_err_count >=3:
                            #错误大于３冻结２４小时 
                            manager.pwd_frozen_time = now + timedelta(1)
                            manager.pwd_err_count = 0                            
                            manager.save()
                            return make_response(code=Msg.ACCOUNT_FREEZING, status=400)               
                        return make_response( code=Msg.PASSWORD_ERROR, status=400)
                    else:
                        manager.pwd_err_count = 0
                        manager.save()
                        token = generate_manager_token(manager)
                        return make_response(
                            data={
                                "token":token,
                                "name":manager.name,

                                }
                        )
                else:
                    #print("未判断出是否冻结")
                    if not manager.verify_password(password):
                        manager.pwd_err_count +=1
                        manager.save()
                        if manager.pwd_err_count >=3:
                            #print("错误大于３冻结２４小时") 
                            manager.pwd_frozen_time = now + timedelta(1)
                            manager.pwd_err_count = 0
                            manager.save()
                            return make_response( code=Msg.ACCOUNT_FREEZING, status=400)               
                        return make_response( code=Msg.PASSWORD_ERROR, status=400)
                    else:
                        manager.pwd_err_count = 0
                        manager.save()
                        token = generate_manager_token(manager)                      
                        return make_response(
                            data={
                                "token":token,
                                "name":manager.name,

                                }                            
                    )        
            elif kind =="2":
                #联合id获取phone　+密码登录 
                try:
                    password = data["pwd"]
                    union_id = data["union_id"]
                    open_id = data["open_id"]
                except KeyError:
                    return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)
                combine_id = union_id + open_id
                if not ChannelPhone.objects.filter(combine_id=combine_id):                    
                    return make_response( code=Msg.COMBINE_ID_NOT_EXISTS, status=400)
                channelPhone = ChannelPhone.objects.get(combine_id=combine_id)
                if  channelPhone.phone == None:
                    return make_response( code=Msg.COMBINE_ID_NOT_BINGDING, status=400)
                phone = channelPhone.phone
                manager = Manager.objects.get(phone=phone)
                #print("判断是否冻结")
                now = datetime.datetime.utcnow().replace(tzinfo=utc)   
                if manager.pwd_frozen_time and manager.pwd_frozen_time > now:
                    #冻结
                    msg = "密码错误多次，账号已被冻结，请于 {} 之后再试。".format(
                    manager.pwd_frozen_time.strftime("%y-%m-%d %H:%M:%S"))
                    return make_response( msg=msg)
                elif manager.pwd_frozen_time and manager.pwd_frozen_time <= now:                    
                    #已出冻结
                    manager.pwd_frozen_time = None
                    manager.pwd_err_count = 0
                    manager.save()
                    if not manager.verify_password(password):
                        manager.pwd_err_count +=1
                        manager.save()
                        if manager.pwd_err_count >=3:
                            #错误大于３冻结２４小时 
                            manager.pwd_frozen_time = now + timedelta(1)
                            manager.pwd_err_count = 0                            
                            manager.save()
                            return make_response( code=Msg.ACCOUNT_FREEZING, status=400)               
                        return make_response( code=Msg.PASSWORD_ERROR, status=400)
                    else:
                        manager.pwd_err_count = 0
                        manager.save()
                        token = generate_manager_token(manager)
                        return make_response(
                            data={
                                "token":token,
                                "name":manager.name,

                                }                            
                        )
                else:
                    #print("未判断出是否冻结")
                    if not manager.verify_password(password):
                        manager.pwd_err_count +=1
                        manager.save()
                        if manager.pwd_err_count >=3:
                            #print("错误大于３冻结２４小时") 
                            manager.pwd_frozen_time = now + timedelta(1)
                            manager.pwd_err_count = 0
                            manager.save()
                            return make_response( code=Msg.ACCOUNT_FREEZING, status=400)               
                        return make_response( code=Msg.PASSWORD_ERROR, status=400)
                    else:
                        manager.pwd_err_count = 0
                        manager.save()
                        token = generate_manager_token(manager)                        
                        return make_response(
                            data={
                                "token":token,
                                "name":manager.name,

                                }                            
                        )
            else:
                #短信验证登录               
                phone = data["phone"]
                if not Manager.objects.filter(phone=phone):
                    return make_response( code=Msg.MANAGER_NOT_EXISTS, status=400) 
                manager = Manager.objects.get(phone=phone)
                #调取短信验证 返回成功码为０
                code="0"
                if code =="0":
                    token = generate_manager_token(manager)                   
                    return make_response(
                            data={
                                "token":token,
                                "name":manager.name,
                                }                        
                    )
                elif code =="-1":
                    return make_response() 
                return make_response(msg="系统错误")
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

class ForgetPassword(APIView): 
   """
   客户经理忘记密码（验证码验证）
   """
   def put(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            verify_code = data["verify_code"]
            phone = data["phone"]
            try:
                manager = Manager.objects.get(phone=phone)
                #调短信验证               
                if verify_code =="0":
                    return make_response()
            except Manager.DoesNotExist:
                return make_response(code=Msg.MANAGER_NOT_EXISTS, status=400)
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)




class ModifyPassword(APIView):
    """
    修改商户经理密码
    """
    @manager_token_required
    def put(self, request):
        serializer = ModifyPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            old_password = data["oldPassword"]
            new_password = data["newPassword"]
            manager = request.current_user            
            if manager.verify_password(old_password):
                manager.generate_password(new_password)
                manager.save()
                token = request.META.get("HTTP_JWT", None)
                redis_conn.delete(token)                    
                return make_response()
            return make_response(code=Msg.OLD_PASSWORD_ERROR, status=400)
                
        return make_response(code=Msg.PARAMS_ERROR, msg=serializer.errors, status=400)

class ManagerInfo(APIView):
    """
    客户经理信息相关
    """
    @manager_token_required
    def get(self, request):
        """
        获取信息
        """
        manager = request.current_user
        return make_response(
            data={
                "name":manager.name,
                "phone":manager.phone,
                "merchant_code":manager.merchant_code,
                "union_id":manager.union_id,
                "open_id":manager.open_id,
                "address":manager.address,
                "id_img":manager.id_img,
                "head_img":manager.head_img,
            }
        )

    @manager_token_required
    def put (self, request):
        """
        修改信息
        """
        print(request.data)
        serializer = ManagerInfoSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            print(data.get("address"))
            manager =request.current_user
            manager.address = data.get("address", manager.address)
            manager.id_img = data.get("id_img", manager.id_img)
            manager.head_img = data.get("head_img", manager.head_img)
            manager.save()
            return make_response()
        return make_response(code=Msg.PARAMS_ERROR, msg = serializer.errors ,status=400 )
        

class ContractInfo(APIView):
    """
    获取签约信息
    """
    @manager_token_required
    def get(self, request):
        manager = request.current_user  
        contractlist = Contract.objects.filter(manager=manager)           
        data = [{
            "id":str(i.id),
            "singn_code":i.singn_code,
            "manager":str(i.manager.id),
            "user":str(i.user.id),
            "create_time":i.create_time,
            "commission":i.commission,
            "singn_longityde":i.singn_longityde,
            "singn_latitude":i.singn_latitude,
            "img":i.img,
            "status":i.status,
        }for i in contractlist]                                
        return make_response(data={"result" :data})
            
class CommissionInfo(APIView):
    """
    获取总提成
    """
    @manager_token_required
    def get(self, request):
        manager = request.current_user             
        contractlist = Contract.objects.filter(manager=manager)
        sum =0
        for i in contractlist:
            sum+=i.commission
        return make_response(data={"result" : sum })



       



        








