import os
import json
import traceback
from pymongo import MongoClient
from flask import Flask, make_response, request, jsonify

from flask_sqlalchemy import SQLAlchemy as SA
from flask_restful import Api
from flask_marshmallow import Marshmallow
from raven.contrib.flask import Sentry
from redis import StrictRedis
from flask_migrate import Migrate
from src.commons.constant import Msg
from src.commons.zk_client import ZkClient
from src.models import base_mongo
from src.commons.logger import logger
from elasticsearch import Elasticsearch

app = Flask(__name__)

# 读取环境变量（环境变量大写，变量小写）
mongo_uri = os.environ.get("MONGO_URI")
credit_mongo_uri = os.environ.get("CREDIT_MONGO_URL")
credit_mongo_db = os.environ.get('CREDIT_MONGO_DB')
config_table = os.environ.get("CONFIG_TABLE")
zk_servers = os.environ.get("ZK_SERVERS")
support_table = os.environ.get("SUPPORT_TABLE")
mysql_url = os.environ.get("SQLALCHEMY_DATABASE_URI")
redis_host = os.environ.get("REDIS_HOST")
redis_port = int(os.environ.get("REDIS_PORT"))
redis_pwd = os.environ.get("REDIS_PWD")
cfca_url = os.environ.get("CFCA_URL")
schedu_redo_url = os.environ.get("SCHEDU_TRANS_REDO_URL")
es_host = os.environ.get("ES_HOST")

logger.info("mongo_uri %s" % mongo_uri)
logger.info("credit_mongo_uri %s" % credit_mongo_uri)
logger.info("credit_mongo_db %s" % credit_mongo_db)
logger.info("config_table %s" % config_table)
logger.info("zk_servers %s" % zk_servers)
logger.info("support_table %s" % support_table)
logger.info("mysql_url %s" % mysql_url)
logger.info("redis_host %s" % redis_host)
logger.info("redis_port %s" % redis_port)
logger.info("redis_pwd %s" % redis_pwd)
logger.info("cfca_url %s" % cfca_url)
logger.info("schedu_redo_url %s" % schedu_redo_url)
logger.info("es_host %s" % es_host)

# mongo client 建立
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[support_table]
support_config_db = mongo_db[config_table]
support_config_storage = mongo_db["support_config_storage"]

credit_mongo_client = MongoClient(credit_mongo_uri)
credit_center_db = credit_mongo_client[credit_mongo_db]


def read_config_from_mongo(app):
    # 读取 mongodb 里面的配置
    config = support_config_db.find_one()
    if not config:
        logger.info("NO CONFIG IN MONGODB")
    else:
        logger.info("READING CONFIG FROM MONGODB | CONFIG: {}".format(config))
        app.config.update(config if config else {})


read_config_from_mongo(app)

# 更新配置
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
app.config["SQLALCHEMY_POOL_SIZE"] = 10
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.update({"MONGODB_SETTINGS": {"host": mongo_uri}})
app.config["SECRET_KEY"] = "83717cf6a2ba11e8be7c787b8ad1ae43"

class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        super().apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True

# 初始化
redis = StrictRedis(host=redis_host, port=redis_port, password=redis_pwd)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
sentry = Sentry(app, dsn=app.config.get("SENTRY_DSN"))
api = Api(app)
base_mongo.db.init_app(app)
zk = ZkClient(zk_servers=zk_servers, app=app)
es_client = Elasticsearch([es_host])

# 封装全局返回格式
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
        elif code == -200:
            if not isinstance(data, int):
                error_name = data.get("error_name")
                data = {"code": getattr(Msg,error_name) , "msg": Msg.msg[getattr(Msg,error_name)], "data": data.get("data")}
            else:
                data = {"code": data, "msg": Msg.msg[data], "data": {}}
            code = 200
        else:
            if isinstance(data, int) and int(data) in Msg.msg:
                data = {"code": data, "msg": Msg.msg[data], "data": {}}
            else:
                data = {"code": code, "msg": data, "data": {}}
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


@app.errorhandler(500)
def catch_error(error):
    traceback.print_exc()
    logger.error(request.data)
    return jsonify({"code": -1, "msg": "服务器内部错误", "data": {}}), 200
