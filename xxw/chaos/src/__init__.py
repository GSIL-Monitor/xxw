#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc:
"""

import redis
import traceback

from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from raven.contrib.flask import Sentry
from raven import Client
import json

from src.config.config import (
    chaos_db,
    sentry_dsn,
    redis_url,
    cur_env,
    log_db,
    sqlalchemy_track_modifications,
    sqlalchemy_pool_size,
    bussiness_alert_sentry_dsn,
    mongo_uri)
from src.config.msgconfig import Msg
from src.comm.logger import logger

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = chaos_db
app.config["SQLALCHEMY_BINDS"] = {"log_db": log_db}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = sqlalchemy_track_modifications
app.config["SQLALCHEMY_POOL_SIZE"] = sqlalchemy_pool_size
app.config.update({"MONGODB_SETTINGS": {"host": mongo_uri}})

sentry = Sentry(app, dsn=sentry_dsn)
alert_sentry_client = Client(bussiness_alert_sentry_dsn)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)

mongo_db = MongoEngine(app)

redis_conn = redis.StrictRedis(
    connection_pool=redis.ConnectionPool.from_url(
        redis_url, charset="utf-8", decode_responses=True
    )
)


@api.representation("application/json")
def output_json(data, code, headers):
    msg_code = Msg.SUCCESS
    msg = ""
    if isinstance(data, int) and data in Msg.msg:
        msg = Msg.msg[data]
        msg_code = data
        data = None
    elif isinstance(data, str):
        msg_code = Msg.ERROR
        msg = data
        data = None
    if code == 500:
        msg_code = Msg.ERROR
        msg = "服务器内部错误"
        data = None
    elif code != 200:
        msg_code = Msg.ERROR
        data = None

    ret = {"code": msg_code, "msg": msg, "data": data}
    resp = make_response(json.dumps(ret), code)
    resp.headers.extend(headers or {})
    return resp


@app.after_request
def call_after_request_callbacks(response):
    response.headers["Seq"] = request.headers.get("Seq", "")
    return response
