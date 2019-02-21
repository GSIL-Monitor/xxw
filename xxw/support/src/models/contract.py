"""合同管理"""
from mongoengine import EmbeddedDocument

from src.commons.date_utils import utc_timestamp
from src.models.base_mongo import db


class SingLocation(db.EmbeddedDocument):
    meta = {"strict": False}
    sign_type = db.IntField(verbose_name="签章类型（2=坐标签章,3=关键字签章）")
    visible = db.BooleanField(verbose_name="签章是否可见")
    page = db.IntField(verbose_name="坐标签章 文件的页码")
    lx = db.IntField(verbose_name="坐标签章 X坐标")
    ly = db.IntField(verbose_name="坐标签章 Y坐标")
    keyword = db.StringField(verbose_name="关键字签章 关键字")
    keyword_location_style = db.StringField(verbose_name="关键字签章 位置风格")
    keyword_offset_x = db.IntField(verbose_name="横轴偏移")
    keyword_offset_y = db.IntField(verbose_name="纵轴偏移")


class ContractTemplate(db.Document):
    """合同/协议管理"""

    meta = {
        "collection": "support_contract_template",
        "indexes": ["template_code", "merchant_code", "contract_type", "create_time"],
        "ordering": ["-create_time"],
        "strict": False,
    }
    template_code = db.StringField(required=True, verbose_name="模版编号")
    merchant_code = db.StringField(required=True, verbose_name="商户（租户） code")
    contract_type = db.StringField(required=True, verbose_name="合同类型")
    user_sign_conf = db.EmbeddedDocumentField(SingLocation, required=True, verbose_name="用户签章配置")
    biz_sign_conf = db.EmbeddedDocumentField(SingLocation, verbose_name="租户签章配置")
    html = db.StringField(verbose_name="模版html")
    create_time = db.IntField(default=utc_timestamp, verbose_name="创建时间")
    update_time = db.IntField(default=utc_timestamp, verbose_name="更新时间")
    operator_id = db.StringField(required=True, verbose_name="操作人")
    operator = db.StringField(required=True, verbose_name="操作人")
    template_name = db.StringField(verbose_name="模版名称")
    template_text_args = db.ListField(db.StringField(), verbose_name="PDF模版文本域参数")


class CFCASealCode(db.Document):
    """签章印章配置"""

    meta = {
        "collection": "support_cfca_seal_code",
        "indexes": ["merchant_code", "code", "create_time"],
        "ordering": ["-create_time"],
        "strict": False,
    }
    merchant_code = db.StringField(required=True, unique=True, verbose_name="商户（租户） code")
    code = db.StringField(required=True, verbose_name="印章编码")  # 印章编码
    password = db.StringField(required=True, verbose_name="印章密码")
    cfca_org_code = db.StringField(required=True, verbose_name="CFCA租户机构代码")
    create_time = db.IntField(default=utc_timestamp, verbose_name="创建时间")
    update_time = db.IntField(default=utc_timestamp, verbose_name="更新时间")
    operator = db.StringField(required=True, verbose_name="操作人")
    operator_id = db.StringField(required=True, verbose_name="操作人")


class UserContract(db.Document):
    """用户合同表"""

    meta = {
        "collection": "support_user_contract",
        "indexes": [
            "merchant_code",
            "uin",
            "name",
            "contract_serial_no",
            "contract_type",
            "create_time",
            "id_card",
            "phone"
        ],
        "ordering": ["-create_time"],
        "strict": False,
    }
    merchant_code = db.StringField(required=True, verbose_name="商户")
    uin = db.IntField(required=True, verbose_name="用户id")
    name = db.StringField(verbose_name="客户名称")
    id_type = db.StringField(verbose_name="证件类型")
    id_card = db.StringField(verbose_name="证件号码")
    phone = db.StringField(verbose_name="手机号码")
    contract_serial_no = db.StringField(verbose_name="合同业务流水号")
    contract_type = db.StringField(verbose_name="合同类型")
    contract_name = db.StringField(verbose_name="合同名称")
    file_type = db.StringField(verbose_name="文件类型")
    file_name = db.StringField(verbose_name="文件名称")
    file_path = db.StringField(verbose_name="文件路径")
    file_remark = db.StringField(verbose_name="文件备注")
    proof_pdf_id = db.StringField(verbose_name="合同存储标识ID")
    create_time = db.IntField(required=True, default=utc_timestamp, verbose_name="存储时间")
    update_time = db.IntField(default=utc_timestamp, verbose_name="更新时间")
