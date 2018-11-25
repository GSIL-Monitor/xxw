import json
import os

from flask import Flask, make_response
from flask_mongoengine import MongoEngine
from mongoengine import connect

from flask_restful import Api
from src.commons.constant import Msg
from src.commons.get_host_ip import ip
from src.commons.logger import logger
from src.commons.utils import ZKClient

app = Flask(__name__)
port = os.environ.get("PORT", 10120)
ip = os.environ.get("IP", ip)
host = os.environ.get("HOST", "{ip}:{host}".format(ip=ip, host=port))
mongo_url = os.environ.get("MONGO_URL")
mongo_username = os.environ.get("MONGO_USER", "")
mongo_password = os.environ.get("MONGO_PASS", "")

logger.info(f"host {host}")
logger.info(f"mongo_url {mongo_url}")

app.config.update({"MONGODB_SETTINGS": {"host": mongo_url}})

connect(host=mongo_url, username=mongo_username, password=mongo_password)
api = Api(app)
db = MongoEngine(app)


@api.representation("application/json")
def output_json(data, code, headers=None):
    if isinstance(data, dict) and data.get("is_simple"):
        data = {
            "code": data.get("code", 0),
            "msg": data.get("msg", ""),
            "data": data.get("data") or {},
        }
    else:
        if code == 200:
            data = {"code": Msg.SUCCESS, "msg": Msg.msg[Msg.SUCCESS], "data": data}
        else:
            if isinstance(data, int) and int(data) in Msg.msg:
                data = {"code": data, "msg": Msg.msg[data], "data": None}
            else:
                data = {"code": code, "msg": data, "data": None}
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp
