# coding=utf-8
"""
@author: teddy
@time: 2018/09/26
@desc: 调度引擎运行事务管理
"""
import json
import math

import requests
from schema import And, Optional, Schema, Use

from elasticsearch_dsl import (Document, InnerDoc, Integer, Keyword, Q, Search,
                               Text)
from src import es_client, schedu_redo_url
from src.commons.logger import logger
from src.commons.model_resource import BaseResource


class ScheduRun(Document):
    trx = Text(fields={'keyword': Keyword()})
    cmd_id = Integer()
    rule_id = Integer()
    uin = Integer()
    phone = Text(fields={'keyword': Keyword()})
    merchant_code = Text(fields={'keyword': Keyword()})
    production_code = Text(fields={'keyword': Keyword()})
    exec_way = Integer()
    recover_index = Integer()
    can_recover = Integer()
    message = Text()
    stime = Integer()
    operate_status = Integer()
    operator = Text(fields={'keyword': Keyword()})
    operator_id = Text(fields={'keyword': Keyword()})
    state = Integer()

    class Index:
        name = 'schedurun*'


class ScheduBin(Document):
    trx = Text(fields={'keyword': Keyword()})
    recover_index = Integer()
    rule_id = Integer()
    message = Text()

    class Index:
        name = 'schedubin*'


class ScheduRunAPI(BaseResource):
    validate_schemas = {
        "get": Schema(
            {
                Optional("trx"): str,
                Optional("cmd_id"): Use(int),
                Optional("rule_id"): Use(int),
                Optional("uin"): Use(int),
                Optional("phone"): str,
                Optional("merchant_code"): str,
                Optional("production_code"): str,
                Optional("exec_way"): Use(int),
                Optional("recover_index"): Use(int),
                Optional("can_recover"): Use(int),
                Optional("start_time"): Use(int),
                Optional("end_time"): Use(int),
                Optional("page", default=1): And(Use(int), lambda x: x > 0),
                Optional("page_size", default=10): And(Use(int), lambda x: x > 0),
                Optional("index_suffix", default="*"): str,
                Optional("operate_status"): Use(int),
                Optional("operator"): str,
                Optional("operator_id"): str,
                Optional("state"): Use(int),
            }
        )
    }

    def get(self):
        list_fields = ['trx', 'cmd_id', 'rule_id', 'phone', 'merchant_code', 'production_code', 'exec_way',
                       'recover_index', 'can_recover', 'message', 'operate_status', 'operator', 'operator_id', 'stime', 'state']
        data = self.validate_data
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        page = data.pop('page')
        page_size = data.pop('page_size')
        index_suffix = data.pop('index_suffix')
        index = 'schedurun' + index_suffix
        filters = []
        if start_time:
            filters.append({"range": {"stime": {"gte": start_time}}})
            data.pop('start_time')
        if end_time:
            filters.append({"range": {"stime": {"lte": end_time}}})
            data.pop('end_time')

        # 精确搜索text字段使用keyword（建索引的时候指定了该字段为keyword）
        data = {"%s.keyword" % k if isinstance(v, str) else k: str(v) for k, v in data.items()}

        query = [Q("term", **{k: v}) for k, v in data.items()]
        filters.extend(query)
        search = ScheduRun.search(using=es_client, index=index).query(
            'bool', filter=filters).source(list_fields).sort('-stime.keyword')

        logger.info("ES query: %s" % search.to_dict())

        total = search.count()
        page_search = search[(page - 1) * page_size:page * page_size]
        page_results = page_search.execute(ignore_cache=True)
        results = []
        for ret in page_results:
            tmp = dict()
            ret_dict = ret.to_dict(include_meta=True)
            tmp = ret_dict['_source']
            tmp['id'] = ret_dict['_id']
            tmp['index'] = ret_dict['_index']
            tmp['operate_status'] = ret.operate_status
            tmp['operator'] = ret.operator
            tmp['operator_id'] = ret.operator_id
            results.append(tmp)
        return {
            "total": total,
            "pages": math.ceil(total / page_size),
            "page": page,
            "page_size": page_size,
            "results": results
        }


class ScheduBinRedoAPI(BaseResource):
    validate_schemas = {
        "post": Schema(
            {
                "scheduruns": list,
                "operator": str,
                "operator_id": str
            }
        )
    }

    def get_schedbin_message(self, trx):
        """
        获取事务数据
        """
        filters = [Q("term", **{"trx.keyword": trx}), Q("term", **{"recover_index": 0})]
        search = ScheduBin.search(using=es_client).query('bool', filter=filters).source('message')
        response = search.execute()
        cnt = len(response)
        if cnt == 0:
            logger.warn('trx:{},recover_index=0 from es not found [toby should care]' % trx)
            return ''
        elif cnt > 1:  # 理论上不会出现同一trx，recover_index=0时多条记录
            logger.warn('trx:{},recover_index=0 from es found more than one record[toby should care]' % trx)
            return ''
        schedubin = response[0]
        return json.loads(schedubin.message)

    def trans_task(self, trx, operator, operator_id):
        """
        处理事务重做的具体逻辑
        """
        try:
            trans = self.get_schedbin_message(trx)
            if not trans:
                logger.info("Query failed, trx: {}".format(trx))
                return False
            resp = requests.post(schedu_redo_url, json=trans, timeout=15)
            if not (resp.status_code == 200 and resp.json()["code"] == 0):
                logger.warning("response trx: {} status: {} result {}".format(
                    trx, resp.status_code, resp.text))
                return False
            logger.info("Request success. trx: {}.".format(trx))
            return True
        except Exception as e:
            logger.error("Redo faild.trx: [{}]. error: {}".format(trx, e))
            return False
        return True

    def post(self):
        scheduruns = self.validate_data.get('scheduruns')
        operator = self.validate_data.get('operator')
        operator_id = self.validate_data.get('operator_id')
        logger.info("重做调度引擎运行事务 ids:{},operator:{},operator_id:{}".format(scheduruns, operator, operator_id))
        success = []
        fails = []
        for schedurun in scheduruns:
            schedurun_id = schedurun['id']
            schedurun_index = schedurun['index']
            schedurun = ScheduRun.get(using=es_client, id=schedurun_id, index=schedurun_index)
            trx = schedurun.trx
            if not schedurun.can_recover == 1:
                logger.info("schedurun_id:{} 事务不支持重做".format(schedurun_id))
                schedurun.operate_status = 0
                schedurun.operator = operator
                schedurun.operator_id = operator_id
                schedurun.save(using=es_client, id=schedurun_id, index=schedurun_index)
                return "当前事务不支持重做", 400
            ret = self.trans_task(trx, operator, operator_id)
            if ret:
                logger.info("重做调度引擎运行事务调用接口成功 schedurun_id:{}".format(schedurun_id))
                schedurun.operate_status = 1
                schedurun.operator = operator
                schedurun.operator_id = operator_id
                schedurun.save(using=es_client, id=schedurun_id, index=schedurun_index)
                success.append({"id": schedurun_id, "index": schedurun_index})
            else:
                logger.info("重做调度引擎运行事务调用接口失败 schedurun_id:{}".format(schedurun_id))
                fails.append({"id": schedurun_id, "index": schedurun_index})
        data = {"success": success, "fails": fails}
        logger.info("重做调度引擎运行事务结果 :{}".format(data))
        return data
