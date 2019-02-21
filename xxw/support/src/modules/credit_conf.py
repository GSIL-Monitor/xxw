import json

from src import db
from bson import ObjectId
from flask_restful import Resource
from src.commons.logger import logger
from src.commons.date_utils import utc_timestamp
from src.commons.error_handler import requests_error_handler, RequestsError
from src.commons.reqparse import RequestParser
from src.commons.utils import MongoEncoder
from src.models.task_models import CreditConf
from src.models.user import TbOperation


class CreditConfigManageViews(Resource):
    """
    征信数据源接口配置
    """
    def __init__(self):
        self.reqparse = RequestParser()

    @staticmethod
    def data_format(class_data_list):
        """
        格式化输出QuerySrt对象中所有数据
        :param class_data_list: QuerySet列表
        :return:正确格式化数据返回数据，否则返回错误码
        """

        if not class_data_list.count():
            return []  # 没有数据

        ret_data = []
        for data in class_data_list:
            d_data = json.dumps(data._data, cls=MongoEncoder)  # 自定义方法解析mongo中取出的对象
            l_data = json.loads(d_data)
            for k, v in l_data.items():
                if v != 0 and not v:
                    l_data.update({k: ""})
            one_data = {"id": l_data["_id"], "interface": l_data["interface"], "supplier": l_data["supplier"],
                        "product": l_data["product"], "type": l_data["type"], "desc": l_data["desc"]}
            l_data.pop("_id")
            l_data.pop("interface")
            one_data["data"] = json.dumps(l_data)
            ret_data.append(one_data)
        return ret_data

    @requests_error_handler
    def get(self):
        """
        根据传入参数获取相应征信配置
        :return:
        """
        self.reqparse.add_argument("id", type=str, location=['json', 'args'], code=1014010002, desc="数据ID")
        self.reqparse.add_argument("interface", type=str, location=['json', 'args'], code=1014010002, desc="接口编码")
        self.reqparse.add_argument("type", type=str, location=['json', 'args'], code=1014010002, desc="接口类型")
        self.reqparse.add_argument("supplier", type=str, location=['json', 'args'], code=1014010002, desc="供应商")
        self.reqparse.add_argument("status", type=int, location=['json', 'args'], code=1014010002, desc="接口状态")
        self.reqparse.add_argument("product", type=str, location=['json', 'args'], code=1014010002, desc="接口名称")
        self.reqparse.add_argument("page", type=int, location=['json', 'args'], default=1, code=1014010002, desc="页码")
        self.reqparse.add_argument("page_size", type=int, location=['json', 'args'], default=10, code=1014010002, desc="页量")

        rq_args = self.reqparse.parse_args(strict=True)
        page = rq_args.get("page")
        page_size = rq_args.get("page_size")
        if page <= 0 or page_size <= 0:
            return 1014010004  # 页码传入不正确
        query_dict = {
            "_id": ObjectId(rq_args.get("id")) if rq_args.get("id", "") else None,
            "interface": rq_args.get("interface", ""),
            "type": rq_args.get("type", ""),
            "supplier": rq_args.get("supplier", ""),
            "product": rq_args.get("product", ""),
            "status": rq_args.get("status", ""),
        }
        ret_data = {"total": 0, "page": 0, "page_size": 0, "results": {}}
        query_dict = {k: v for k, v in query_dict.items() if v is not None}
        set_find_dict = {'%s__contains' % k: v for k, v in query_dict.items()}
        set_find_dict["is_delete"] = 0
        result = CreditConf.objects.filter(**set_find_dict).order_by("interface")
        if page_size >= 100:
            page_size = result.count()
            page = 1
        if result.count() > 0 and page_size * page >= result.count() + page_size:
            return 1014010004  # "页码过大"
        ret_data["total"] = result.count()
        ret_data["page_size"] = page_size
        ret_data["page"] = page
        start = (page - 1) * page_size
        in_data = self.data_format(result.limit(page_size).skip(start))
        ret_data["results"] = in_data
        msg = "SUPPORT | INTERFACE_CONF | GET_INTERFACE_CONF | SUCCESS | DATA: {}".\
            format(json.dumps(query_dict, ensure_ascii=False))
        logger.info(msg)
        return ret_data

    @requests_error_handler
    def post(self):
        """
        新增征信配置
        """
        self.reqparse.add_argument("interface", type=str, required=True, location=['json', 'args'],
                                   code=1014010001, desc="接口编号")
        self.reqparse.add_argument("operator_id", type=str, location=['json', 'args'], required=True,
                                   code=1014010001, desc="操作人ID")
        self.reqparse.add_argument("supplier", type=str, location=['json', 'args'], code=1014010002, desc="接口供应商")
        self.reqparse.add_argument("product", type=str, location=['json', 'args'], code=1014010002, desc="产品名称")
        self.reqparse.add_argument("type", type=str, location=['json', 'args'], code=1014010002, desc="接口类型")
        self.reqparse.add_argument("desc", type=str, location=['json', 'args'], code=1014010002, desc="接口描述")
        self.reqparse.add_argument("secret_key", type=str, location=['json', 'args'], code=1014010002, desc="安全码")
        self.reqparse.add_argument("url", type=str, location=['json', 'args'], code=1014010002, desc="接口api")
        self.reqparse.add_argument("retry", type=int, location=['json', 'args'], code=1014010002, desc="重试次数")
        self.reqparse.add_argument("method", type=str, location=['json', 'args'], code=1014010002, desc="请求方式")
        self.reqparse.add_argument("headers", type=dict, location=['json', 'args'], code=1014010002, desc="请求头参数字典")
        self.reqparse.add_argument("auth_info", type=dict, location=['json', 'args'], code=1014010002, desc="接口认证信息")
        self.reqparse.add_argument("account_config", type=dict, location=['json', 'args'], code=1014010002, desc="人行账号配置")
        self.reqparse.add_argument("rate_limit", type=dict, location=['json', 'args'], code=1014010002, desc="限速配置字典")
        self.reqparse.add_argument("timeout", type=int, location=['json', 'args'], code=1014010002, desc="超时时间")
        self.reqparse.add_argument("expire", type=int, location=['json', 'args'], code=1014010002, desc="缓存过期时间")
        self.reqparse.add_argument("status", type=int, location=['json', 'args'], code=1014010002, desc="接口状态")
        self.reqparse.add_argument("sys_params", type=dict, location=['json', 'args'], code=1014010002, desc="系统参数字典")
        self.reqparse.add_argument("user_params", type=dict, location=['json', 'args'], code=1014010002, desc="用户参数字典")
        self.reqparse.add_argument("input_params", type=dict, location=['json', 'args'], code=1014010002, desc="请求参数字典")
        self.reqparse.add_argument("success_code_dict", type=dict, location=['json', 'args'], code=1014010002,
                                   desc="成功状态码字典")
        self.reqparse.add_argument("retry_code_dict", type=dict, location=['json', 'args'], code=1014010002,
                                   desc="失败重试状态码字典")
        self.reqparse.add_argument("failed_code_dict", type=dict, location=['json', 'args'], code=1014010002,
                                   desc="失败状态码字典")

        raw_args_dict = self.reqparse.parse_args(strict=True)
        if not CreditConf.objects(interface=raw_args_dict["interface"], is_delete=0).count() == 0:
            return 1014010004  # 接口已经存在
        raw_args_dict["create_time"] = raw_args_dict["update_time"] = utc_timestamp()
        create_data = CreditConf()
        try:
            for k, v in raw_args_dict.items():
                if k not in ["operator_id"]:
                    setattr(create_data, k, v or None)
            create_data.save()
            # 记录日志
            msg = self.create_log_msg(operator_id=raw_args_dict["operator_id"], interface=raw_args_dict["interface"],
                                      data=json.dumps(raw_args_dict, ensure_ascii=False), status="SUCCESS")
            self.operator_log(operator_id=raw_args_dict["operator_id"], log_data=msg, method="POST")
            logger.info(msg)
            return 0
        except Exception as e:
            msg = self.create_log_msg(operator_id=raw_args_dict["operator_id"], interface=raw_args_dict["interface"],
                                      data=json.dumps(raw_args_dict, ensure_ascii=False), status="FAILED")
            self.operator_log(operator_id=raw_args_dict["operator_id"], log_data=msg, method="POST")
            logger.error(msg)
            return 1014020001  # 数据格式错误

    @requests_error_handler
    def put(self):
        """
        更新征信配置
        """
        self.reqparse.add_argument("interface", type=str, required=True, location=['json', 'args'],
                                   code=1014010001, desc="接口编号")
        self.reqparse.add_argument("operator_id", type=str, location=['json', 'args'], required=True,
                                   code=1014010001, desc="操作人ID")
        self.reqparse.add_argument("supplier", type=str, location=['json', 'args'], code=1014010002, desc="接口供应商")
        self.reqparse.add_argument("product", type=str, location=['json', 'args'], code=1014010002, desc="产品名称")
        self.reqparse.add_argument("type", type=str, location=['json', 'args'], code=1014010002, desc="接口类型")
        self.reqparse.add_argument("desc", type=str, location=['json', 'args'], code=1014010002, desc="接口描述")
        self.reqparse.add_argument("secret_key", type=str, location=['json', 'args'], code=1014010002, desc="安全码")
        self.reqparse.add_argument("url", type=str, location=['json', 'args'], code=1014010002, desc="接口api")
        self.reqparse.add_argument("retry", type=int, location=['json', 'args'], code=1014010002, desc="重试次数")
        self.reqparse.add_argument("method", type=str, location=['json', 'args'], code=1014010002, desc="请求方式")
        self.reqparse.add_argument("headers", type=dict, location=['json', 'args'], code=1014010002, desc="请求头参数字典")
        self.reqparse.add_argument("auth_info", type=dict, location=['json', 'args'], code=1014010002, desc="接口认证信息")
        self.reqparse.add_argument("account_config", type=dict, location=['json', 'args'], code=1014010002, desc="人行账号配置")
        self.reqparse.add_argument("rate_limit", type=dict, location=['json', 'args'], code=1014010002, desc="限速配置字典")
        self.reqparse.add_argument("timeout", type=int, location=['json', 'args'], code=1014010002, desc="超时时间")
        self.reqparse.add_argument("expire", type=int, location=['json', 'args'], code=1014010002, desc="缓存过期时间")
        self.reqparse.add_argument("status", type=int, location=['json', 'args'], code=1014010002, desc="接口状态")
        self.reqparse.add_argument("sys_params", type=dict, location=['json', 'args'], code=1014010002, desc="系统参数字典")
        self.reqparse.add_argument("user_params", type=dict, location=['json', 'args'], code=1014010002, desc="用户参数字典")
        self.reqparse.add_argument("input_params", type=dict, location=['json', 'args'], code=1014010002, desc="请求参数字典")
        self.reqparse.add_argument("success_code_dict", type=dict, location=['json', 'args'], code=1014010002,
                                   desc="成功状态码字典")
        self.reqparse.add_argument("retry_code_dict", type=dict, location=['json', 'args'], code=1014010002,
                                   desc="失败重试状态码字典")
        self.reqparse.add_argument("failed_code_dict", type=dict, location=['json', 'args'], code=1014010002,
                                   desc="失败状态码字典")
        raw_args_dict = self.reqparse.parse_args(strict=True)
        if not CreditConf.objects(interface=raw_args_dict["interface"], is_delete=0).count() == 1:
            return 1014010004  # 接口编码错误
        up_data = CreditConf.objects.filter(interface=raw_args_dict["interface"])[0]
        raw_args_dict["update_time"] = utc_timestamp()
        try:
            for k, v in raw_args_dict.items():
                if k not in ["operator_id"]:
                    setattr(up_data, k, v or None)
            up_data.save()
            msg = self.create_log_msg(operator_id=raw_args_dict["operator_id"], interface=raw_args_dict["interface"],
                                      data=json.dumps(raw_args_dict, ensure_ascii=False), status="SUCCESS")
            self.operator_log(operator_id=raw_args_dict["operator_id"], log_data=msg, method="PUT")
            logger.info(msg)
            return 0
        except Exception as e:
            msg = self.create_log_msg(operator_id=raw_args_dict["operator_id"], interface=raw_args_dict["interface"],
                                      data=json.dumps(raw_args_dict, ensure_ascii=False), status="FAILED")
            self.operator_log(operator_id=raw_args_dict["operator_id"], log_data=msg, method="PUT")
            logger.error(msg)
            return 1014020001  # 数据格式错误

    @requests_error_handler
    def delete(self):
        """
        删除征信配置
        """
        self.reqparse.add_argument("interface", type=str, required=True, location=['json', 'args'],
                                   code=1014010001, desc="接口编号")
        self.reqparse.add_argument("operator_id", type=str, location=['json', 'args'], required=True,
                                   code=1014010001, desc="操作人ID")
        raw_args_dict = self.reqparse.parse_args(strict=True)
        if not CreditConf.objects(interface=raw_args_dict["interface"], is_delete=0).count() == 1:
            return 1014010004  # 接口编码错误
        try:
            de_data = CreditConf.objects(interface=raw_args_dict["interface"], is_delete=0)
            de_data.update(set__is_delete=int(1))
            msg = self.create_log_msg(operator_id=raw_args_dict["operator_id"], interface=raw_args_dict["interface"],
                                      data=json.dumps(raw_args_dict, ensure_ascii=False), status="SUCCESS")
            self.operator_log(operator_id=raw_args_dict["operator_id"], log_data=msg, method="DELETE")
            logger.info(msg)
            return 0
        except Exception as e:
            msg = self.create_log_msg(operator_id=raw_args_dict["operator_id"], interface=raw_args_dict["interface"],
                                      data=json.dumps(raw_args_dict, ensure_ascii=False), status="FAILED")
            self.operator_log(operator_id=raw_args_dict["operator_id"], log_data=msg, method="DELETE")
            logger.error(msg)
            return 1014020001  # 数据格式错误

    @staticmethod
    def create_log_msg(operator_id, interface, data, status="SUCCESS"):
        """
        生成记录日志需要的数据
        """
        msg = "SUPPORT | INTERFACE_CONF | EDIT_INTERFACE_CONF | {} | USER: {} | INTERFACE: {} | DATA: {}". \
            format(status, operator_id, interface, data)
        return msg

    @staticmethod
    def operator_log(operator_id, log_data, method):
        """
        记录用户敏感操作
        :param method: 方法
        :param operator_id: 用户ID
        :param log_data: 记录信息
        :return: None
        """
        operation = TbOperation(operator_code=operator_id, content=log_data, type=str(method), category="INTERFACE_CONF")
        try:
            db.session.add(operation)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RequestsError(code=1014020001)  # 数据库操作失败