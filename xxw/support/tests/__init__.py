import os
import unittest

from src.main import app
from src.models import base_mongo
from sqlalchemy import create_engine, MetaData


# @unittest.skip("demonstrating skipping")
class FlaskMongoEngineTestCase(unittest.TestCase):

    mongodb_url = app.config["MONGODB_SETTINGS"]["host"] + "_test"

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["SERVER_NAME"] = "127.0.0.1:5000"
        # mongodb_url = self.app.config["MONGODB_SETTINGS"]["host"] + "_test"
        app.config.update({"MONGODB_SETTINGS": {"host": self.mongodb_url}})
        self.db_name = os.path.basename(self.mongodb_url)
        self.assertIn("test", self.db_name)  # 数据库名字不包含 test 则认为使用的非测试数据库
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.db = base_mongo.db

    def tearDown(self):
        try:
            self.db.connection.drop_database(self.db_name)
        except Exception:
            self.db.connection.client.drop_database(self.db_name)
        self.ctx.pop()


# @unittest.skip("demonstrating skipping")
class FlaskSQLTestCase(unittest.TestCase):
    models = []

    def setUp(self):
        self.engine = create_engine('sqlite:///test.db')
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config["SERVER_NAME"] = "127.0.0.1:5000"
        self.metadata = MetaData(self.engine)
        self.test_tables = []
        for model in self.models:
            self.test_tables.append(model.metadata.tables[model.__tablename__])
        self.metadata.create_all(tables=self.test_tables)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()








