# 手机号归属地
from schema import Schema

from src import Msg
from src.apps.models.phone_address import PhoneAddress
from src.comm.model_resource import SQLModelSchemaResource
from src.comm.sms_utils import verification_phone


class PhoneAddressAPI(SQLModelSchemaResource):
    """手机号码归属地"""

    model = PhoneAddress
    allow_methods = ["get"]
    validate_schemas = {"get": Schema({"phone": str})}

    def get(self):
        phone = self.validate_data["phone"]
        if not verification_phone(phone):
            return Msg.ERROR_PHONE_NUMBER
        instance = PhoneAddress.query.filter_by(phone=phone[:7]).first()
        return {"results": self.detail_schema.dump(instance).data}
