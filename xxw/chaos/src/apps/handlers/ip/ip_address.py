# IP归属地
from schema import Schema

from src import Msg, ma
from src.apps.handlers.ip import get_data_by_ipip, get_data_by_amap, get_data_by_file
from src.apps.models.ip_address import IPAddress
from src.comm.model_resource import BaseResource
from src.comm.sms_utils import verification_ip


class IPAddressSchema(ma.Schema):
    class Meta:
        fields = tuple(IPAddress._fields.keys())[0:-2]


ip_address_schema = IPAddressSchema()
ip_address_schemas = IPAddressSchema(many=True)


class IPAddressAPI(BaseResource):
    """IP归属地"""
    validate_schemas = {"get": Schema({"ip": str})}
    allow_methods = ["get"]

    def get(self):
        ip = self.validate_data["ip"]
        if not verification_ip(ip):
            return Msg.ERRPR_IP_NUMBER
        data = get_data_by_file(ip) or get_data_by_ipip(ip) or get_data_by_amap(ip)
        if data:
            ip_address = IPAddress.objects().filter(ip=ip).first()
            if not ip_address:
                ip_address = IPAddress(**data).save()
            return {"results": ip_address_schema.dump(ip_address)}
        else:
            ip_address = IPAddress.objects().filter(ip=ip).first()
            if ip_address:
                return {"results": ip_address_schema.dump(ip_address)}
            return {"results": "查无此IP地址"}



