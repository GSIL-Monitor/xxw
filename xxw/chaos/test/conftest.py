import os
from test.mock_data import sms_app_data, sms_app_template_data

import pytest

os.environ.update(
    {
        "HOST": "127.0.0.1:10160",
        "REDIS_URL": "redis://127.0.0.1:6379",
        # "CHAOS_DB": "mysql+pymysql://root:123456@127.0.0.1:3306/chaos_db",
        "CHAOS_DB": "sqlite:///test.db",
        # "LOG_DB": "mysql+pymysql://root:123456@127.0.0.1:3306/log_db",
        "LOG_DB": "sqlite:///test_log_db.db",
        "ZK_SERVERS": "111.230.231.89:2181,111.230.231.89:2182,111.230.231.89:2183",
    }
)


@pytest.fixture
def sms_app():
    return sms_app_data.copy()


@pytest.fixture
def sms_app_template():
    return sms_app_template_data.copy()


@pytest.fixture
def client():
    """
    返回 flask client
    """
    from src.config.config import chaos_db, redis_url, log_db

    if (
        "sqlite" not in chaos_db
        or "127.0.0.1" not in redis_url
        or "sqlite" not in log_db
    ):
        raise Exception("单元测试请配置环境变量")

    from src.main import app

    app.config.update({"SQLALCHEMY_POOL_SIZE": None, "SQLALCHEMY_POOL_TIMEOUT": None})
    from src import db

    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "127.0.0.1:5000"
    ctx = app.app_context()
    ctx.push()
    db.create_all()

    yield app.test_client()

    db.session.remove()
    db.drop_all()
    ctx.pop()
