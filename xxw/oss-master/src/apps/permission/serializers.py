from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=32)


class PageCount(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    count = serializers.IntegerField(default=10)
    

class BizSerializer(PageCount):
    name = serializers.CharField(max_length=100, required=False)


class AddBizSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    appid = serializers.BooleanField(default=False, required=False)


class BizEditSerializer(AddBizSerializer, BaseSerializer):
    pass


class AcBizSerializer(BaseSerializer):

    status = serializers.BooleanField()   


class AuthSerializer(PageCount):

    name = serializers.CharField(max_length=100, required=False)


class AddAuthSerializer(BaseSerializer):
    roles = serializers.ListField()


class InquireSreializer(PageCount):

    name = serializers.CharField(max_length=100, required=False) 
    businessId = serializers.CharField(max_length=32, required=False)


class AddRoleSerializer(serializers.Serializer):
    
    name = serializers.CharField(max_length=100)
    businessId = serializers.CharField()
    interface = serializers.ListField()
    menu = serializers.ListField()


class RoleEditSerializer(serializers.Serializer):

    id = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=100, required=False)
    businessId = serializers.CharField(required=False)
    interface = serializers.ListField(required=False)
    menu = serializers.ListField(required=False)

    def validate(self, data):
        biz_id = data.get("businessId", None)
        interface = data.get("interface", None)
        menu = data.get("menu", None)
        if interface is not None and biz_id is None:
            raise serializers.ValidationError("must need business id")
        elif menu is not None and biz_id is None:
            raise serializers.ValidationError("must need business id")
        elif biz_id and interface is None and menu is None:
            raise serializers.ValidationError("must need interface or menu")
        return data


class AddMeIntSerializer(serializers.Serializer):
    """
    菜单、接口 添加
    """

    businessId = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=100)
    path = serializers.CharField(max_length=100)
    visible = serializers.BooleanField()


class AddInterSerializer(AddMeIntSerializer):
    method = serializers.CharField(max_length=10)


class MeInSerializer(PageCount):
    """
    查询 接口 菜单
    """

    businessId = serializers.CharField(max_length=32, required=False)
    name = serializers.CharField(max_length=100, required=False)
    path = serializers.CharField(max_length=100, required=False)


class MeInEditSerializer(BaseSerializer):
    businessId = serializers.CharField(max_length=32, required=False)
    name = serializers.CharField(max_length=100, required=False)
    path = serializers.CharField(max_length=100, required=False)
    visible = serializers.BooleanField()


class EditIntSerializer(MeInEditSerializer):
    method = serializers.CharField(max_length=10, required=False)


class QueryMerSerializer(BizSerializer):
    production = serializers.CharField(max_length=64, required=False)


class AddMerSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=100)
    logo = serializers.CharField(max_length=256)
    ibaLoanName = serializers.CharField(max_length=32)
    ibaLoanNo = serializers.CharField(max_length=128)
    ibaCollectionName = serializers.CharField(max_length=32)
    ibaCollectionNo = serializers.CharField(max_length=128)
    ibaPreDepositName = serializers.CharField(max_length=32)
    ibaPreDepositNo = serializers.CharField(max_length=128)
    orgNo = serializers.CharField(max_length=32)
    production = serializers.CharField(max_length=64)


class EditMerSerializer(BaseSerializer):

    name = serializers.CharField(max_length=100, required=False)
    logo = serializers.CharField(max_length=256, required=False)
    ibaLoanName = serializers.CharField(max_length=32, required=False)
    ibaLoanNo = serializers.CharField(max_length=128, required=False)
    ibaCollectionName = serializers.CharField(max_length=32, required=False)
    ibaCollectionNo = serializers.CharField(max_length=128, required=False)
    ibaPreDepositName = serializers.CharField(max_length=32, required=False)
    ibaPreDepositNo = serializers.CharField(max_length=128, required=False)
    orgNo = serializers.CharField(max_length=32, required=False)
    production = serializers.CharField(max_length=64, required=False)


class AllMerRole(serializers.Serializer):

    merchantId = serializers.CharField(max_length=32)


class EditMerDomain(BaseSerializer):

    domain = serializers.CharField(max_length=128)


class MerSysSerializer(BaseSerializer):

    system = serializers.ListField()

    def validate(self, data):
        for i in data["system"]:
            if len(i) != 2 and sorted(i.keys()) != ["businessId", "domain"]:
                raise serializers.ValidationError("wrong type of system")
        return data
