# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from src.apps.model.models import User


class UserSignin(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=100)


class PasswordSerializer(serializers.Serializer):

    oldPassword = serializers.CharField(max_length=100)
    newPassword = serializers.CharField(max_length=100)
    verifyPassword = serializers.CharField(max_length=100)

    def validate(self, data):
        if data["newPassword"] != data["verifyPassword"]:
            raise serializers.ValidationError("two password are not equal.")
        return data


class UserInfoSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=100, required=False, allow_null=True)
    sex = serializers.CharField(max_length=7, required=False, allow_null=True)
    mail = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    wechat = serializers.CharField(max_length=50, required=False, allow_null=True)
    address = serializers.CharField(max_length=200, required=False, allow_null=True)
    qq = serializers.CharField(max_length=20, required=False, allow_null=True)
    avatar = serializers.CharField(max_length=100, required=False, allow_null=True)


class UserSerializer(serializers.Serializer):

    page = serializers.IntegerField(default=1)
    count = serializers.IntegerField(default=10)
    name = serializers.CharField(max_length=100, required=False)
    mobile = serializers.CharField(max_length=100, required=False)


class ResetPasswordSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=32)


class UserEditSerializer(UserInfoSerializer, ResetPasswordSerializer):

    wechat = serializers.CharField(max_length=50, required=False, allow_null=True)


class UserAdditionSerializer(UserInfoSerializer):

    mobile = serializers.CharField(min_length=11, max_length=11)
    merchantId = serializers.CharField(max_length=32)


class UserActivationSerializer(ResetPasswordSerializer):

    status = serializers.BooleanField()


class MerBizNameSerializer(serializers.Serializer):

    domain = serializers.CharField(max_length=128, required=False)
    appid = serializers.CharField(max_length=64)
