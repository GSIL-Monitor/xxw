"""租户合同管理"""
from flask import abort, request
from flask_restful import Resource
from schema import Optional, Schema

from marshmallow_mongoengine import ModelSchema
from src.commons.cfca_client import CFCAClient
from src.commons.logger import logger
from src.commons.model_resource import ModelSchemaResource
from src.commons.utils import validate_schema
from src.models.contract import CFCASealCode, ContractTemplate, UserContract

CONTRACT_TYPE = {
    "CONTRACT_REGISTER": "用户注册协议",
    "CONTRACT_PERSON_INFO": "个人信息查询及使用授权书",
    "CONTRACT_PERSON_CREDIT": "个人征信授权书",
    "CONTRACT_CREDIT_CEILING": "授信额度合同",
    "CONTRACT_LOAN": "个人借款合同",
    "CONTRACT_DELEGATE_DEBIT": "委托扣款授权书",
    "CONTRACT_BIND_CARD": "绑卡合同",
}

CONTRACT_TEXT_ARGS = {
    "title": "标题",
    "bank": "银行名字",
    "name": "用户姓名/借款人/本人姓名/收款人/收款人",
    "id_card": "身份证号码",
    "contract_date": "合同签订日期/日期（年   月   日）",
    "loan_amount": "贷款金额",
    "loan_amount_upper": "贷款金额大写",
    "loan_limit":"贷款期限",
    "loan_start_date":"自贷款发放之日起至（年   月   日）",
    "loan_rate_name":"贷款利率名称",
    "loan_rate":"贷款利率",
    "payment_account":"收款账户",
    "payback_method":"还款方式",
    "due_date":"还款日",
}


class ContractTemplateAPI(ModelSchemaResource):
    """合同模版管理"""

    model = ContractTemplate
    allow_query_all = True
    filter_fields = [
        ["merchant_code", "==", "merchant_code", str],
        ["contract_type", "==", "contract_type", str],
    ]
    update_exclude_fields = [
        "template_code",
        "merchant_code",
        "template_name",
        "create_time",
        "update_time",
    ]

    def post(self):
        """新增合同模版"""
        instance, errors = self.detail_schema.load(request.json)
        if errors:
            return str(errors), 400
        # 先获取租户配置的CFCA组织代码用于调用CFCA接口获取模版信息（模版名称）
        seal_code = CFCASealCode.objects(
            merchant_code=request.json["merchant_code"]
        ).first()
        if not seal_code:
            return "CFCA租户机构代码未配置", 400
        client = CFCAClient(url="PaperlessAssistServlet")
        res, errors = client.get_template(
            instance.template_code, seal_code.cfca_org_code
        )
        if errors:
            return str(errors), 400
        instance.template_name = res.get("TemplateName")
        instance.save()
        return {}


class HtmlTemplateAPI(ModelSchemaResource):
    """HTML模板"""

    model = ContractTemplate
    allow_methods = ["get"]

    def get(self):
        logger.info("获取HTML模板 参数: %s" % request.args)
        if request.args.get("merchant_code") and request.args.get("contract_type"):
            instance = (
                self.model.objects(
                    merchant_code=request.args.get("merchant_code"),
                    contract_type=request.args.get("contract_type"),
                )
                .only("html")
                .first()
            )
            if instance:
                logger.info("获取HTML模板 id: %s" % instance.id)
                return {"html": instance.html}
            logger.info("未获取HTML模板")
        return "未获取到HTML模版", 400


class CFCASealCodeAPI(ModelSchemaResource):
    """租户签章管理"""

    model = CFCASealCode
    allow_methods = ["get", "put"]
    update_exclude_fields = ["create_time", "update_time", "merchant_code"]

    def get(self):
        """根据bid查询租户签章信息"""
        if request.args.get("merchant_code"):
            instance = self.model.objects(
                merchant_code=request.args.get("merchant_code")
            ).first()
            if instance:
                return self.detail_schema.dump(instance).data
        return {}

    def put(self):
        """更新租户签章配置"""
        if not request.json.get("id"):  # 不存在id则新建
            return super().post()
        return super().put()


class ContractTypeAPI(Resource):
    """合同类型"""

    def get(self):
        return CONTRACT_TYPE


class ContractTextArgsAPI(Resource):
    """合同模版文本参数"""

    def get(self):
        return CONTRACT_TEXT_ARGS


class ContractConfigAPI(Resource):
    """合同类型和合同模板文本参数"""

    def get(self):
        return {
            "CONTRACT_TYPE": CONTRACT_TYPE,
            "CONTRACT_TEXT_ARGS": CONTRACT_TEXT_ARGS,
        }


class CFCATemplateAPI(Resource):
    """获取CFCA模版数据接口"""

    def get(self):
        """根据模版编号从CFCA获取模版数据"""
        schema = Schema({"template_code": str, "merchant_code": str})
        data, errors = validate_schema(schema, request.args.to_dict(), remove_blank=True)
        if errors:
            return str(errors), 400
        # 先获取租户配置的CFCA组织代码用于调用CFCA接口获取模版信息（模版名称）
        seal_code = CFCASealCode.objects(merchant_code=data["merchant_code"]).first()
        if not seal_code:
            return "CFCA租户机构代码未配置", 400
        client = CFCAClient(url="PaperlessAssistServlet")
        res, errors = client.get_template(
            data.get("template_code"), seal_code.cfca_org_code
        )
        if errors:
            return str(errors), 400
        ret = {
            "template_code": res.get("TemplateCode"),
            "version": res.get("Version"),
            "template_name": res.get("TemplateName"),
            "template_format": res.get("TemplateFormat"),
            "template_data": res.get("TemplateData"),
        }
        return ret


class UserContractAPI(ModelSchemaResource):
    """查询用户合同"""

    model = UserContract
    allow_methods = ["get"]
    filter_fields = [
        ["merchant_code", "==", "merchant_code", str],
        ["uin", "==", "uin", int],
        ["name", "==", "name", str],
        ["id_card", "==", "name", str],
        ["phone", "==", "name", str],
        ["contract_serial_no", "==", "contract_serial_no", str],
        ["contract_type", "==", "contract_type", str],
        ["create_time", "<=", "start_time", str],
        ["create_time", ">=", "end_time", str],
    ]
