"""
配置监控平台
- 修改
- 审批
- 查看
- 定时修改
......
流程：
更新配置 - 校验规则 - 储存配置(mongo 里面的 support_config_storage) - 同步到 support_config 和 zk

同时编辑导致先提交的配置被冲掉问题解决:
1、每次编辑的时候加一个编辑请求，这个时候往 redis 写一个数据
2、用户编辑完成提交的时候，redis 释放数据，然后配置版本 +1
3、同步这个数据，判断当前版本是否比线上版本号大
4、用户长时间不编辑，有超时时间

author: roywu
create_time: 2018-09-06 19:50
"""

import re
import json
from datetime import datetime
from bson.objectid import ObjectId
from schema import Schema, And, Optional, Use
from flask_restful import Resource
from flask import request
from pymongo import DESCENDING

from src import support_config_db, support_config_storage, logger, db, zk, app, redis
from src.commons.utils import validate_schema
from src.models.user import TbUser, TbOperation
from src.commons.constant import Msg, ConfigNameMap
from src.commons.date_utils import utc_timestamp
from src.modules.monitor.util import (permission_check, sync_config, universal_schema, release_lock, CacheData, 
                                      get_version)


class Config(Resource):

    @permission_check
    def get(self):
        req, error = validate_schema(universal_schema, request.args.to_dict())
        if error:
            return error, 400
        category = ConfigNameMap.name[req["category"]]
        cache_data = CacheData(category)
        wait_to_sync_config = support_config_storage.find_one({"category": category},
                                                              sort=[('_id', DESCENDING)])
        wait_to_sync_config = wait_to_sync_config or {}
        if wait_to_sync_config.get("is_sync") is True:
            wait_to_sync_config = {}
        using_config = cache_data.get()
        if not using_config:
            if category == ConfigNameMap.SUPPORT:
                using_config = support_config_db.find_one({}, {"_id": 0})
            else:
                using_config = zk.get_config(category)
            cache_data.set(using_config)
        else:
            logger.info("SUPPORT | CONFIG | GET {} CONFIG | USING CACHE".format(category))
        return {"using_config": using_config, "wait_to_sync_config": wait_to_sync_config.get("config", {})}, 200

    @permission_check
    def put(self):
        """
        """
        schema = Schema({
            "user_code": And(str),
            "category": And(Use(int), lambda x: x in list(ConfigNameMap.name.keys())),
        }, ignore_extra_keys=True)
        req, error = validate_schema(schema, request.json)
        if error:
            return error, 400
        user = TbUser.query.filter_by(code=request.json.pop("user_code")).first()
        # 解锁
        release_lock(req, user)
        request.json.pop("category")
        category = ConfigNameMap.name[req["category"]]
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        # 处理 VERSION
        version = get_version(category)
        # 处理 python 精度问题
        request.json["VERSION"] = round(version + 0.1, 2)
        # support 的配置里面需要隔离掉 SQLALCHEMY_DATABASE_URI
        if category == ConfigNameMap.SUPPORT and request.json.get("SQLALCHEMY_DATABASE_URI"):
            request.json.pop("SQLALCHEMY_DATABASE_URI")
        data = {
            "config": request.json,
            "creator_name": user.name,
            "creator_code": user.code,
            "create_time": utc_timestamp(),
            "category": category,
            "is_sync": False
        }
        msg = "SUPPORT | MONITOR | EDIT_CONFIG | SUCCESS | USER: {} {} | CATEGORY: {}".format(
            user.code, user.name, category)
        try:
            support_config_storage.insert_one(data)
            operation = TbOperation(
                operator_code=user.code,
                content=msg,
                operate_time=utc_timestamp(),
                category=category,
                type="EDIT"
            )
            db.session.add(operation)
            db.session.commit()
            logger.info(msg)
            return {}, 200
        except Exception as e:
            logger.warn("SUPPORT | MONITOR | EDIT_CONFIG | FAILED | CATEGORY: {}| ERROR: {}".format(category, str(e)))
            return Msg.UPDATE_CONFIG_FAILED, 400


class RuleConfig(Resource):
    """
    规则配置
    """

    def get(self):
        return {}, 200

    def put(self):
        return {}, 200

    def post(self):
        return {}, 200


class RuleVerify(Resource):

    def post(self):
        """
        验证规则
        """
        schema = Schema({
            "rule": str,
            "filed": str
        })
        req, error = validate_schema(schema, request.json, remove_blank=True)
        if error:
            return error, 400
        if re.fullmatch(req["rule"], req["filed"]):
            return {"verify": True}, 200
        return {"verify": False}


class ConfigHistory(Resource):
    """
    配置更新历史
    """

    @permission_check
    def get(self):
        """
        获取历史配置更新信息
        """
        schema = Schema({
            Optional("page", default=1): Use(int),
            Optional("page_size", default=10): Use(int),
            "category": And(Use(int), lambda x: x in list(ConfigNameMap.name.keys())),
            "user_code": str
        })
        req, error = validate_schema(schema, request.args.to_dict())
        if error:
            return error, 400
        page, page_size = req["page"], req["page_size"]
        config = list(support_config_storage.find({"category": ConfigNameMap.name[req["category"]], "is_sync": True},
                                                  sort=[('_id', DESCENDING)]))
        return {
            "results": [{
                "creator_code": i["creator_code"],
                "creator_name": i["creator_name"],
                "id": str(i["_id"]),
                "create_time": i["create_time"],
                "config": i["config"],
                "is_sync": i["is_sync"],
                "version": i["config"]["VERSION"]
            } for i in config[(page-1)*page_size: page*page_size]],
            "total": len(config),
            "page": page,
            "page_size": page_size
        }


class SyncConfig(Resource):
    """
    同步配置
    将配置写入 app.config
    将配置同步到 zk
    """
    @permission_check
    def post(self):
        req, error = validate_schema(universal_schema, request.json)
        if error:
            return error, 400
        user = TbUser.query.filter_by(code=req["user_code"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        # 同步配置的时间
        sync_time_range = app.config.get("SYNC_TIME", "1-6")
        sync_time_start = int(sync_time_range.split("-")[0])
        sync_time_end = int(sync_time_range.split("-")[1])
        sync_time = [i for i in range(sync_time_start, sync_time_end+1)]
        # 获取当前时间的小时数， 使用 utc 时间 + 8
        current_time_hour = datetime.utcnow().hour + 8
        if current_time_hour not in sync_time:
            return "当前时间不支持同步，请于 {} 点到 {} 点（24 小时制）进行同步！".format(sync_time_start, sync_time_end), 400
        # 需要更新的配置信息
        wait_to_sync_config = support_config_storage.find_one({}, sort=[('_id', DESCENDING)])
        if not wait_to_sync_config or wait_to_sync_config["is_sync"]:
            return Msg.NO_CONFIG, 400
        category = ConfigNameMap.name[req["category"]]
        return sync_config(category, user, wait_to_sync_config, "SYNC")


class SyncEmergency(Resource):
    """
    紧急同步
    """

    def post(self):
        req, error = validate_schema(universal_schema, request.json)
        if error:
            return error, 400
        user = TbUser.query.filter_by(code=req["user_code"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        category = ConfigNameMap.name[req["category"]]
        # 需要更新的配置信息
        wait_to_sync_config = support_config_storage.find_one({}, sort=[('_id', DESCENDING)])
        if not wait_to_sync_config or wait_to_sync_config["is_sync"]:
            return Msg.NO_CONFIG, 400
        return sync_config(category, user, wait_to_sync_config, "SYNC_EMERGENCY")


class ConfigRollBack(Resource):
    """
    配置回滚
    """

    @permission_check
    def post(self):
        req, error = validate_schema(universal_schema, request.json)
        if error:
            return error, 400
        category = ConfigNameMap.name[req["category"]]
        config_info = support_config_storage.find_one({
            "_id": ObjectId(req["id"]),
            "category": category
            })
        user = TbUser.query.filter_by(code=req["user_code"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        # 把获取到的配置信息插入库中
        version = get_version(category) + 0.1
        config_info["config"]["VERSION"] = version + 0.1
        support_config_storage.insert_one({
            "config": config_info["config"],
            "creator_name": user.name,
            "creator_code": user.code,
            "create_time": utc_timestamp(),
            "category": category,
            "is_sync": False
        })
        msg = "SUPPORT | MONITOR | CONFIG_ROLL_BACK | SUCCESS | USER: {} {} | CATEGORY: {} | CONFIG: {}".format(
            user.code, user.name, category, config_info["config"])
        operation = TbOperation(
                operator_code=user.code,
                content=msg,
                operate_time=utc_timestamp(),
                category=category,
                type="CONFIG_ROLL_BACK"
            )
        db.session.add(operation)
        db.session.commit()
        logger.info(msg)
        return {}, 200


class EditRequest(Resource):

    @permission_check
    def post(self):
        """
        编辑请求
        """
        req, error = validate_schema(universal_schema, request.json)
        if error:
            return error, 400
        user = request.current_user
        # 执行锁住操作
        key = "edit_{}_config_lock".format(ConfigNameMap.name[req["category"]])
        res = redis.get(key)
        if res and json.loads(res)["user_code"] != user.code:
            return Msg.EDIT_LOCKED, 400
        else:
            data = json.dumps({"user_code": user.code})
            exp = app.config.get("EDIT_EXPIRATION")
            exp = int(exp) if exp else 3600
            redis.set(key, data, ex=exp)
            return {"exp_time": exp}, 200


class ReleaseEditLock(Resource):

    @permission_check
    def post(self):
        """
        释放编辑锁
        """
        req, error = validate_schema(universal_schema, request.json)
        if error:
            return error, 400
        user = request.current_user
        return release_lock(req, user)
