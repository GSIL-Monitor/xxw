"""
监控项目一些公用的函数

creator: roywu
create_time: 2018-09-11 10:00AM
"""

import json
from schema import Schema, And, Use
from flask import request
from bson.objectid import ObjectId
from src.commons.constant import Msg, ConfigNameMap
from src.commons.utils import validate_schema
from src.models.user import TbUser, TbOperation
from src import db, support_config_db, logger, zk, app, support_config_storage, redis
from src.commons.date_utils import utc_timestamp

universal_schema = Schema({
    "category": And(Use(int), lambda x: x in list(ConfigNameMap.name.keys())),
    "user_code": str
}, ignore_extra_keys=True)


def permission_check(func):
    def decorator(*args, **kwargs):
        method = request.method
        if method == "GET":
            params = request.args.to_dict()
        else:
            params = request.json
        req, error = validate_schema(universal_schema, params)
        if error:
            return error, 400
        user = TbUser.query.filter_by(code=req["user_code"]).first()
        if not user:
            return Msg.USER_NOT_EXISTS, 400
        if not user.is_admin:
            # 获取用户所有的能访问的菜单 path
            menus = [i.path for j in user.roles for i in j.menu]
            category_name = ConfigNameMap.name[req["category"]]
            if ConfigNameMap.menu_path[category_name] not in menus:
                return Msg.PERMISSION_DENIED, 401
        request.current_user = user
        return func(*args, **kwargs)
    return decorator


def judge_version(now_config: dict, wait_to_sync_config: dict) -> bool:
    """
    判断 version
    """
    if not now_config.get("VERSION"):
        # 如果现在配置里面没有 VERSIOIN，初始化为 1.0
        now_config["VERSION"] = 1.0
    using_version = now_config.get("VERSION") or 1.0
    wait_to_sync_config_version = float(wait_to_sync_config["config"]["VERSION"])
    if float(using_version) >= float(wait_to_sync_config_version):
        logger.info("WRONG VERSION | USING CONFIG VERSION: {} | WAIT_TO_SYNC_CONFIG_VERSION: {}".format(
            using_version, wait_to_sync_config_version
        ))
        return False
    return True


def sync_config(category: str, user: TbUser, wait_to_sync_config: dict, _type: str) -> tuple:
    """
    同步配置
    """
    cache_data = CacheData(category)
    if category == "SUPPORT":
        # 现在的配置
        now_config = support_config_db.find_one() or {}
        if not judge_version(now_config, wait_to_sync_config):
            return Msg.WRONG_VERSION, 400
        # 先remove 再 insert
        support_config_db.delete_many({})
        support_config_db.insert_one(wait_to_sync_config.get("config"))
        wait_to_sync_config.get("config").pop("_id")
        app.config.update(wait_to_sync_config.get("config"))
        cache_data.set(wait_to_sync_config.get("config"))
        logger.info("SUPPORT | SYNC {} CONFIG".format(category))
    else:
        now_config = zk.get_config(category)
        if not judge_version(now_config, wait_to_sync_config):
            return Msg.WRONG_VERSION, 400
        status = zk.write_config(category, wait_to_sync_config["config"])
        if status is False:
            return Msg.SYNC_FAILED, 400
        cache_data.set(wait_to_sync_config["config"])
        logger.info("SUPPORT | SYNC {} CONFIG".format(category))
    # 将待更新数据里面的 is_sync 修改为 True
    wait_to_sync_config["is_sync"] = True
    _id = str(wait_to_sync_config.pop("_id"))
    support_config_storage.update({"_id": ObjectId(_id)}, wait_to_sync_config)
    msg = "SUPPORT | MONITOR | {} | SUCCESS | USER: {} {} | CATEGORY: {}".format(
        _type, user.code, user.name, category)
    operation = TbOperation(
            operator_code=user.code,
            content=msg,
            operate_time=utc_timestamp(),
            category=category,
            type=_type
        )
    db.session.add(operation)
    db.session.commit()
    logger.info(msg)
    return {}, 200


def release_lock(req, user):
    key = "edit_{}_config_lock".format(ConfigNameMap.name[req["category"]])
    data = redis.get(key)
    if not data:
        return {}, 200
    elif data and json.loads(data)["user_code"] == user.code:
        redis.delete(key)
        return {}, 200
    else:
        return Msg.RELEASE_LOCK_FAILED, 400


class CacheData:

    """
    缓存数据
    """

    def __init__(self, category: str):
        self.category = category
        self.key = "cache_{}_config_data".format(category)

    def set(self, data):
        redis.set(self.key, json.dumps(data))

    def get(self):
        data = redis.get(self.key)
        return json.loads(data) if data else {}


def get_version(category: str) -> float:

        if category == ConfigNameMap.SUPPORT:
            config = support_config_db.find_one()
        else:
            config = zk.get_config(category)
        version = config.get("VERSION") or 1
        return float(version)
