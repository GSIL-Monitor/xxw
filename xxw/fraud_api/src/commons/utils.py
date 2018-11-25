import json
from datetime import datetime

from kazoo.client import KazooClient
from marshmallow import Schema
from schema import SchemaError

from src.commons.constant import Msg


class ZKClient:
    def __init__(self, zk_servers, service_name, host):
        self.zk = KazooClient(zk_servers)
        self.zk.start()

        self.service_name = service_name
        self.serve_path = "/entry/service/{}/node".format(service_name)
        self.zk.ensure_path(self.serve_path)
        self.zk.create(
            self.serve_path + "/server", host.encode(), ephemeral=True, sequence=True
        )
        self.config_path = "/entry/config/service/{}".format(self.service_name)
        self.zk.DataWatch(self.config_path, self.read_config)

    def read_config(self, *args):
        self.zk.ensure_path("/entry/config/service")
        if not self.zk.exists(self.config_path):
            self.zk.create(self.config_path, json.dumps({}).encode())
        self.config = json.loads(self.zk.get(self.config_path)[0].decode())

    def update_config(self, config):
        self.zk.set(self.config_path, json.dumps(config).encode())


def utc_timestamp():
    """返回utc时间戳（秒）"""
    return int(datetime.utcnow().timestamp())


def validate_schema(schema: Schema, data: dict, remove_blank=False):
    """schema验证,验证成功返回数据，验证失败返回错误信息
    Parameters
    ----------
    schema:Schema: 验证规则
    data: 验证数据
    remove_blank : 是否去除空白字段

    Returns (data,errors)
    -------

    """
    if not data:
        return {}, []
    if not isinstance(data, dict):
        return Msg.PARAMS_ERROR, 400
    if remove_blank:
        for k, v in data.items():
            if v != "":
                data[k] = v
    try:
        validate_data = schema.validate(data)
        return validate_data, []
    except SchemaError as e:
        return {}, str(e.autos)
    else:
        return validate_data, []


