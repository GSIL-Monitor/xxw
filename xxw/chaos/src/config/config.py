#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc: 需要手动配置的配置文件
"""
import os

from src.comm.logger import logger
from src.comm.zkCli import ZKClient

service_name = "chaos"
zk_servers = os.environ.get("ZK_SERVERS")
host = os.environ.get("HOST")

zk = ZKClient(zk_servers, service_name, host)
zk.read_config()


def _get_conf(name):
    """环境变量没有就从 zk 读取
    """
    return os.environ.get(name) or zk.config.get(name)


cur_env = _get_conf("CUR_ENV")  # local 本地开发环境，dev 联调环境 test 测试环境  prod 生产环境
chaos_db = _get_conf("CHAOS_DB")
sentry_dsn = _get_conf("SENTRY_DNS")
redis_url = _get_conf("REDIS_URL")
log_db = _get_conf("LOG_DB")
sqlalchemy_track_modifications = _get_conf("SQLALCHEMY_TRACK_MODIFICATIONS")
sqlalchemy_pool_size = _get_conf("SQLALCHEMY_POOL_SIZE")
bussiness_alert_sentry_dsn = _get_conf("ALERT_SENTRY_DNS")
mongo_uri = os.environ.get("MONGO_URI")
# 验证码短信过期时间 (分钟)
VERIFY_CODE_EXPIRE = int(_get_conf("VERIFY_CODE_EXPIRE"))

# 环境 log
logger.info("zk config: {}".format((zk.config)))
logger.info("service_name: {}".format(service_name))
logger.info("sentry_dsn: {}".format(sentry_dsn))
logger.info("bussiness_alert_sentry_dsn: {}".format(bussiness_alert_sentry_dsn))
logger.info("chaos_db: {}".format(chaos_db))
logger.info("zk_servers: {}".format(zk_servers))
logger.info("host: {}".format(host))
logger.info("redis_url: {}".format(redis_url))
logger.info("server_env: {}".format(cur_env))
logger.info("log_db: {}".format(log_db))
