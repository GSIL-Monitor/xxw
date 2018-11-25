from rest_framework import serializers
from rest_framework.authtoken.models import Token
from src.apps.model.models import Manager

class ManagerAdditionSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)



class ManagerSigninSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=100,required = False)
    union_id = serializers.CharField(max_length=100,required = False)
    open_id = serializers.CharField(max_length=100,required = False)
    pwd = serializers.CharField(max_length=50,required = False)
    kind = serializers.CharField(max_length=50)


class ResetPasswordSerializer(serializers.Serializer):
    manager_code = serializers.CharField(max_length=100)
    

class ManagerEditSerializer(serializers.Serializer):
    manager_code = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100,required = False)
    sex = serializers.CharField(max_length=100,required = False)
    address = serializers.CharField(max_length=100,required = False)
    id_img = serializers.CharField(max_length=100,required = False)
    head_img = serializers.CharField(max_length=100,required = False) 


class ManagerInfoSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=100,required = False,allow_null=True)
    id_img =  serializers.CharField(max_length=100,required = False,allow_null=True)
    head_img = serializers.CharField(max_length=100,required = False,allow_null=True)


class GetManagerInfoSerializer(serializers.Serializer):
   # something = serializers.CharField(max_length=11)
   pass

class ModifyPasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(max_length=100)
    newPassword = serializers.CharField(max_length=100)
    verifyPassword = serializers.CharField(max_length=100)

    
    def validate(self, data):
        if data["newPassword"] != data["verifyPassword"]:
            raise serializers.ValidationError("two password are not equal.")
        return data    

class ForgetPasswordSerializer(serializers.Serializer): 
    phone = serializers.CharField(max_length=11) 
    verify_code = serializers.CharField(max_length=50) 

class ContractinfoSerializer(serializers.Serializer):
    
    #manager_id = serializers.CharField(max_length=100)
    pass 
   
class CommissionInfoSerializer(serializers.Serializer):
    #manager = serializers.CharField(max_length=100)
    manager_code = serializers.CharField(max_length=11) 

class  ContractInfoManageSerializer(serializers.Serializer):
    manager_code = serializers.CharField(max_length=11)
    user_code = serializers.CharField(max_length=11)
    

