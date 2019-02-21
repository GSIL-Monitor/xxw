import copy
import json
from src import db
from src.commons.logger import logger
from src.commons.error_handler import requests_error_handler, RequestsError
from src.commons.reqparse import RequestParser
from src.models.task_models import CreditConf
from src.models.user import TbMerchantCredit, TbOperation
from flask_restful import Resource, request


class MerchantCredit(Resource):

    def __init__(self):
        self.reqparse = RequestParser()

    @requests_error_handler
    def get(self):
        """
        获取租户对应产品所拥有征信源
        :return: 租户对应产品所拥有征信源详情
        """
        # 里面更新征信源的可用状态将自动更新interface_status
        self.reqparse.add_argument("merchant_code", type=str, required=True, location=["json", "args"],
                                   code=1014010001, desc="租户id")
        self.reqparse.add_argument("production_code", type=str, required=True, location=["json", "args"],
                                   code=1014010001, desc="产品id")
        self.reqparse.add_argument("interface_status", type=int, location=["json", "args"], code=1014010002,
                                   desc="三方接口可用状态")
        rq_args = self.reqparse.parse_args(strict=True)
        query_dict = {
            "merchant_code": rq_args.get("merchant_code", ""),
            "production_code": rq_args.get("production_code", ""),
            "interface_status": rq_args.get("interface_status", ""),
        }
        type_orm = {"third_zx": "三方征信", "rh_zx": "人行征信"}
        query_dict = {k: v for k, v in query_dict.items() if v is not None}
        query_dict["is_delete"] = 0
        full_merchant_list = self.get_interface_mysql(query_dict)
        full_interface_dict = self.mongo_full_interface()
        interface_merchant_list, wait_update_list = self.format_data(full_interface_dict, full_merchant_list,
                                                                     query_dict)
        if wait_update_list:
            self.to_post_put(TbMerchantCredit, wait_update_list)
        ret_dict = {}
        for data in interface_merchant_list.values():
            for k, v in data.items():
                if v != 0 and not v:  # 此处value可能为0
                    data.update({k: ""})
            type_zx = type_orm.get(data["type"], data["type"])
            if type_zx in ret_dict:
                ret_dict[type_zx].append(data)
            else:
                ret_dict[type_zx] = [data]
        log_data = "SUPPORT | MARCHANT_CREDIT | GET_MARCHANT_CREDIIT | SUCCESS | MERCHANT:{} | PRODUCT: {}".\
            format(query_dict["merchant_code"], query_dict["production_code"])
        logger.info(log_data)
        return {"total": len(ret_dict), "results": json.loads(json.dumps(ret_dict))}

    @requests_error_handler
    def post(self):
        """
        修改租户对应产品使用的征信源
        :return: 成功：code=0
        """
        # 里面将判断插入、更新，更新时更改字段为status，插入时默认status=1
        raw_args_dict = request.json  # 只能是application/json格式的数据传入
        if not raw_args_dict:
            raise RequestsError(code=1014010001)
        raw_args_list = raw_args_dict.get("data", "")
        operator_id = raw_args_dict.get("operator_id", "")
        if not raw_args_list or not operator_id:
            raise RequestsError(code=1014010001)
        if not self.check_params(raw_args_list, ["merchant_code", "production_code", "interface", "status"]):
            raise RequestsError(code=1014010001)
        merchant_code = raw_args_list[0]["merchant_code"]
        production_code = raw_args_list[0]["production_code"]
        # 现在传入的（启用/关闭）数据
        open_interface = set([data["interface"] for data in raw_args_list if data["status"] == 1])
        close_interface = set([data["interface"] for data in raw_args_list if data["status"] == 0])

        query_dict = {"merchant_code": merchant_code, "production_code": production_code, "is_delete": 0}
        all_data_list = self.get_interface_mysql(query_dict)
        all_opened_data_list = []
        all_closed_data_list = []
        for data in all_data_list:
            for k, v in data.items():
                if k == "status" and v == 1:
                    all_opened_data_list.append(data)
                elif k == "status" and v == 0:
                    all_closed_data_list.append(data)

        # 原来启动的数据源
        all_opened_data_interface = set([data["interface"] for data in all_opened_data_list])
        # 原来关闭的数据源
        all_closed_data_interface = set([data["interface"] for data in all_closed_data_list])
        # 没变的  现在启用的&数据库中启用的 | 现在关闭&数据库中关闭的
        origin_interface_set = (open_interface & all_opened_data_interface) | \
                               (close_interface & all_closed_data_interface)
        # 需要更新status=0  现在需要关闭的-没变的
        put_interface_set = close_interface - origin_interface_set
        # 需要更新/新增status=1  现在需要启用的-没变的
        put_post_interface_set = open_interface - origin_interface_set
        # 需要新增的  (现在启用的-没变的)- 数据库中关闭的
        post_interface_list = (open_interface - origin_interface_set) - all_closed_data_interface
        # 需要将status=0变为status=1的数据
        opening_data_list = [data for data in raw_args_list if data["interface"] in list(put_post_interface_set)]
        # 需要将status=1变为status=0的数据
        closing_data_list = [data for data in raw_args_list if data["interface"] in list(put_interface_set)]
        # 所有需要改变的数据
        change_data_list = opening_data_list + closing_data_list
        if not change_data_list:
            return {}
        db_status = self.to_post_put(TbMerchantCredit, change_data_list)
        if db_status:
            # 记录日志
            log_data = self.create_log_msg(operator_id, merchant_code, production_code, list(put_interface_set),
                                           list(put_post_interface_set), list(post_interface_list))
            logger.info(log_data)
            self.operator_log(operator_id, log_data)
        return {}

    @staticmethod
    def to_post_put(model, data_list):
        """
        在模型中插入/更新数据
        :param model: 模型,对应model需要定义__init__方法，联合主键
        :param data_list: 多个更新数据字典组成的列表:[{},{}]
        :return: True|Error
        """
        merchant_credit_list = []
        for post_data in data_list:
            merchant_credit = db.session.merge(model(**post_data))
            merchant_credit_list.append(merchant_credit)
        try:
            db.session.add_all(merchant_credit_list)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RequestsError(code=1014020001, message="post")  # 数据库操作失败

    @staticmethod
    def mongo_full_interface():
        """
        从mongo获取全量的征信源信息
        :return: 征信源信息字典:{interface:{}}
        """
        set_find_dict = {"is_delete": 0}
        try:
            result = CreditConf.objects.filter(**set_find_dict).order_by("interface")
        except Exception as e:
            raise RequestsError(code=1014020001)  # 数据库操作失败
        if not result.count():
            return None
        # 方便后面更具接口编号获取接口信息
        interface_data = {interface.to_simple_json()["interface"]: interface.to_simple_json() for interface in result}
        return interface_data

    @staticmethod
    def format_data(interface_data_dict, merchant_data_list, query_dict):
        """
        整理GET方法返回字段，同时过滤需要更新interface_status字段的征信源接口
        :param interface_data_dict: 全量的征信源信息字典:{interface:{}}
        :param merchant_data_list: 租户产品在数据库中存在的所有征信源信息列表，status=0|1都包含
        :param query_dict: GET方法传入的参数，用于获取merchant_code， production_code
        :return: 整理字段后的数据+需要更新interface_status字段的征信源接口:{}+[{}]
        """
        wait_update = []
        product_info = {"merchant_code": query_dict["merchant_code"], "production_code": query_dict["production_code"]}
        interface_format_dict = copy.deepcopy(interface_data_dict)
        merchant_data_interface_list = [data["interface"] for data in merchant_data_list]
        for data in interface_format_dict.values():
            data.update(product_info)
            if not data["interface_status"] and data["interface"] in merchant_data_interface_list:
                # 发现租户拥有的征信源不可用，及时更新数据库
                wait_update.append(data)
        for merchant_data in merchant_data_list:
            interface = merchant_data.get("interface", "")  # 从租户这边获取
            interface_data = interface_format_dict.get(interface, "")
            if not interface_data:
                # 发现租户拥有的征信源删除，及时更新数据库
                update_dict = {"interface_status": 0}
                merchant_data.update(update_dict)
                wait_update.append(merchant_data)
            else:
                interface_data.update({"status": merchant_data["status"], "is_own": 1})
        return interface_format_dict, wait_update

    @staticmethod
    def get_interface_mysql(query_dict):
        """
        在数据库中获取数据
        :param query_dict: 查询条件
        :return: 查询到的数据字典组成的列表:[{}]
        """
        try:
            all_data = TbMerchantCredit.query.filter_by(**query_dict)
        except Exception as e:
            raise RequestsError(code=1014020001)  # 数据库操作失败
        if not all_data:
            return []
        all_data_list = [data.to_json() for data in all_data]
        return all_data_list

    @staticmethod
    def check_params(params_list, check_items_list):
        """
        检查数据字典中的键是否正确
        :param params_list: 数据字典列表:[{}]
        :param check_items_list: 需要校验的字段列表:[]
        :return: 通过:True, 不通过:False
        """
        param_list = [params_dict.keys() for params_dict in params_list]
        for data in param_list:
            if set(data) & set(check_items_list) != set(check_items_list):
                return False
        return True

    @staticmethod
    def create_log_msg(operator_id, merchant, product, closing_interface, opening_interface, insert_interface):
        """
        生成记录日志需要的数据
        """
        msg = "SUPPORT | MARCHANT_CREDIT | EDIT_MARCHANT_CREDIIT | SUCCESS | USER: {} | MERCHANT_CODE:{} | " \
              "PRODUCTION_CODE: {} | CLOSE_INTERFACES: {} | OPEN_INTERFACES: {} | INSERT_INTERFACE: {}".\
            format(operator_id, merchant, product, closing_interface, opening_interface, insert_interface)
        return msg

    @staticmethod
    def operator_log(operator_id, log_data):
        """
        记录用户敏感操作
        :param operator_id: 用户ID
        :param log_data: 记录信息
        :return: None
        """
        operation = TbOperation(operator_code=operator_id, content=log_data, type="EDIT", category="MARCHANT_CREDIT")
        try:
            db.session.add(operation)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RequestsError(code=1014020001)  # 数据库操作失败

