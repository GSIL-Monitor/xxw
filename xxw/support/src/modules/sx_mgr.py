import json


from flask_restful import Resource
from src import mongo_db as support_db, credit_center_db
from src.commons.error_handler import requests_error_handler, RequestsError
from src.commons.logger import logger
from src.commons.reqparse import RequestParser


class CreditDetail(Resource):
    """授信、提现、提额人工审核、历史案件详情管理"""

    def __init__(self):
        self.reqparse = RequestParser()

    @requests_error_handler
    def get(self):
        self.reqparse.add_argument("trx", type=str, required=True, nullable=False, code=1014010001, desc="事务ID")
        self.reqparse.add_argument("type", type=str, required=False, code=1014010001, desc="数据类型")
        rq_args = self.reqparse.parse_args(strict=True)
        trx = rq_args.get("trx", "")
        search_type = rq_args.get("type", "")
        search_list = self.verification_search_type(search_type)

        if not trx:
            raise RequestsError(code=1014010001, message=',事务ID不能为空')
        
        # 查询所有接口配置信息
        self.interface_dict = self.get_interfaces()

        ret_data = dict()
        for tp in search_list:
            ret_data[tp] = eval('self.{0}'.format(tp))(trx)
        logger.info("success queried credit detail information,query parameters are %s" % json.dumps(rq_args))
        return ret_data

    def get_interfaces(self):
        """
        查询所有接口信息
        :return 返回接口对应信息
        """
        support_col = 'credit_conf'
        interface_list = support_db[support_col].find({}).sort([('interface', -1), ('update_time', -1)])
        interface_dict = {}
        for item in interface_list:
            interface_dict.update({
                item.get('interface'): '{supplier}-{product}({interface})'.format(
                    supplier=item.get('supplier'),
                    product=item.get('product'),
                    interface=item.get('interface')
                )
            })
        return interface_dict

    @staticmethod
    def verification_search_type(search_type):
        """
        验证查询类型
        :param search_type:
        :return: 返回查询类型列表
        """
        all_type = ['user_info', 'app_info', 'channel_info', 'anti_fraud_info', 'merch_control_info',
                    'change_manual_info_list', 'credit_result', 'credit_info', 'third_data']
        if search_type:
            search_list = list(set(search_type.split(',')))
            search_list = [tp for tp in search_list if tp]
            unknow_list = list(set(search_list).difference(set(all_type)))
            if unknow_list:
                raise RequestsError(code=1014010003, message='：{0}'.format(','.join(unknow_list)))
        else:
            search_list = all_type
        return search_list

    def credit_info(self, trx):
        """
        获取人行征信中原始信息与etl结果信息
        :param trx: 事务ID
        :return: 人行征信原始信息与etl结果信息 dict
        """
        ret_data = self.third_rh_data(trx, origin_col="tb_credit_rh_zx_origin", etl_col="tb_credit_rh_zx_etl",
                                      interface_dict=self.interface_dict, del_origin=True)
        return ret_data

    def third_data(self, trx):
        """
        获取三方征信中原始信息与etl结果信息
        :param trx: 事务ID
        :return: 三方征信原始信息与etl结果信息 dict
        """
        ret_data = self.third_rh_data(trx, origin_col="tb_credit_third_zx_origin", etl_col="tb_credit_third_zx_etl",
                                      interface_dict=self.interface_dict)
        return ret_data

    @staticmethod
    def credit_result(trx):

        """
        获取ILOG结果信息
        :param trx: 事务ID
        :return: ilog结果信息 list
        """

        try:
            connection = credit_center_db['tb_credit_results']  # ilog信息所存放的mongo集合
            raw_data = connection.find({"trx": trx}, {"step": 1, "credit_result": 1, "control_flow": 1, "_id": 0,
                                                      "event_type": 1}).sort([("step", -1), ('update_time', -1)])
        except Exception as e:
            raise RequestsError(code=1014020001, message=",获取ILOG结果信息失败")
        data_list = list(raw_data)
        return data_list

    @staticmethod
    def anti_fraud_info(trx):

        """
        查询反欺诈结果信息
        :param trx: 事务ID
        :return: 反欺诈结果 dict
        """
        try:
            connection = credit_center_db['tb_credit_results']  # 反欺诈结果所在mongo集合
            raw_data = connection.find_one({"trx": trx, "anti_fraud_info": {"$exists": True}},
                                           {"anti_fraud_info": 1, "_id": 0})
        except Exception as e:
            raise RequestsError(code=1014020001, message=",获取反欺诈结果信息失败")
        return raw_data.get("anti_fraud_info", "") if raw_data else {}

    @staticmethod
    def change_manual_info_list(trx):

        """
        查询人工审核数据
        :param trx: 事务ID
        :return: 人工审核数据
        """

        ret_list = []
        try:
            connection = credit_center_db['tb_credit_results']  # 人工审核数据所在mongo集合
            raw_manual_data = connection.find({"trx": trx, "change_manual_info": {"$exists": True}},
                                              {"change_manual_info": 1, "step": 1, "_id": 0}).sort(
                [("step", -1), ('update_time', -1)])
        except Exception as e:
            raise RequestsError(code=1014020001, message=", 获取人工审核数据失败")

        for manual_data in raw_manual_data:
            try:
                manual_data_dict = manual_data.get("change_manual_info")
                del manual_data["change_manual_info"]
            except Exception as e:
                manual_data_dict = {}
            manual_data.update(manual_data_dict)
            ret_list.append(manual_data)
        return ret_list

    @staticmethod
    def third_rh_data(trx, origin_col, etl_col, interface_dict, del_origin=False):

        """
        获取三方征信/人行征信中原始信息与etl结果信息
        :param trx: 事务ID
        :param support_db: 征信接口配置所存放的mongo数据库
        :param credit_db: 征信结果所存放的mongo数据库
        :param origin_col: 原始结果所存放的mongo集合
        :param etl_col: etl数据所存放的mongo集合
        :param support_col: 征信接口配置所存放的mongo集合
        :param del_origin: 是否删除etl原始特征
        :return: 三方征信/人行征信原始信息与etl结果信息 dict
        """
        ret_data_dict = {}
        try:
            raw_etl_data = credit_center_db[etl_col].find({"trx": trx}).sort([("step", -1)])
        except Exception as e:
            raise RequestsError(code=1014020001, message=",查询etl数据失败")
        
        if not raw_etl_data.count():
            return {}
        
        update_dict = {}
        serial_no_list = []
        for _etl_data in raw_etl_data:
            for key in _etl_data:
                if "ZX" in key:
                    interface_info_str = interface_dict.get(key)
                    if not interface_info_str:
                        interface_info_str = key
                    
                    if interface_info_str in update_dict:
                        continue

                    etl_data = _etl_data.get(key) or {}
                    _etl_result = etl_data.get('etl_result') or {}
                    try:
                        if del_origin:
                            del _etl_result['origin']
                    except Exception as e:
                        pass
                    
                    serial_no = etl_data.get('serial_no')
                    serial_no_list.append(serial_no)
                    update_dict.update({
                        interface_info_str: {
                            'etl': _etl_result,
                            'serial_no': serial_no,
                        }
                    })

        # 一次性查询所有原始数据
        origin_data_dict = {origin_data.get('serial_no'):origin_data.get('data')
            for origin_data in credit_center_db[origin_col].find({'serial_no': {'$in': serial_no_list}})}
        
        for k,v in update_dict.items():
            etl = v.get('etl') or {}
            serial_no = v.get('serial_no')
            origin = origin_data_dict.get(serial_no) or {}
            ret_data_dict.update({
                k: {
                    'origin': origin,
                    'etl': etl
                }
            })
        
        return ret_data_dict

    @staticmethod
    def channel_info(trx):

        """
        查询渠道信息
        :param trx: 事务ID
        :return:渠道信息 dict
        """

        ret_dict = {}
        try:
            connection = credit_center_db['tb_credit_merchant']  # 渠道信息所在mongo集合
            raw_channel_dict = connection.find_one({"trx": trx, "step": 1,
                                                    "channel_info": {"$exists": True}},
                                                   {"channel_info": 1, "_id": 0})
        except Exception as e:
            raise RequestsError(code=1014020001, message=",查询渠道信息失败")
        if not raw_channel_dict:
            return {}
        ret_dict.update(raw_channel_dict.get("channel_info", "")) if raw_channel_dict else {}
        return ret_dict

    @staticmethod
    def merch_control_info(trx):

        """
        查询风险驾驶舱风险参数(只有授信才有)
        :param trx: 事务ID
        :return: 风险驾驶舱风险参数 dict
        """

        try:
            connection = credit_center_db['tb_credit_merchant']  # 风险参数所在mongo集合
            raw_merch_dict = connection.find_one({"trx": trx, "step": 1,
                                                  "merch_control_info": {"$exists": True}},
                                                 {"merch_control_info": 1, "_id": 0})
        except Exception as e:
            raise RequestsError(code=1014020001, message=",查询风险驾驶舱风险参数失败")
        if not raw_merch_dict:
            return {}
        merch_control_info = raw_merch_dict.get("merch_control_info", "")
        return merch_control_info if merch_control_info else {}

    @staticmethod
    def product_list_info(trx):

        """
        查询产品信息（只有授信才有）
        :param trx: 事务ID
        :param credit_db: 产品信息所在mongo数据库
        :param product_col: 产品信息所在mongo集合
        :return: 产品信息 list
        """

        try:
            connection = credit_center_db['tb_credit_merchant']
            raw_product_dict = connection.find_one(
                {"trx": trx, "step": 1, "product_list_info": {"$exists": True}}, {"product_list_info": 1, "_id": 0})
        except Exception as e:
            raise RequestsError(code=1014020001, message=",查询产品信息失败")
        if not raw_product_dict:
            return []
        product_dict = raw_product_dict.get("product_list_info", "")
        if not product_dict:
            return []
        product_list = product_dict.get("productlist", "")
        return product_list if product_list else []

    def user_info(self, trx):

        """
        查询用户基本信息
        :param trx: 事务ID
        :return: 用户基本信息 dict
        """
        ret_data = self.get_info_from_user(trx, 'user_info')
        return ret_data

    def app_info(self, trx):

        """
        银行宝衍生信息
        :param trx: 事务ID
        :return: 银行宝衍生信息 dict
        """
        ret_data = self.get_info_from_user(trx, 'app_info')
        return ret_data

    @staticmethod
    def get_info_from_user(trx, info_type):
        """
        查询用户信息
        :param trx: 事务ID
        :param info_type: 查询信息类型
        :return: 用户对应信息 dict
        """

        try:
            collection = credit_center_db['tb_credit_user']  # 用户信息所在mongo集合
            raw_user_dict = collection.find_one({"trx": trx}, {info_type: 1, "_id": 0})
            if raw_user_dict:
                raw_user_dict = raw_user_dict.get(info_type, dict())
            else:
                raw_user_dict = dict()
        except Exception as e:
            raise RequestsError(code=1014020001, message=",查询用户信息失败")
        return raw_user_dict
