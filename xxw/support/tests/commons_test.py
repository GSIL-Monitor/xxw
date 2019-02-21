from flask import url_for
from tests import FlaskSQLTestCase, FlaskMongoEngineTestCase
from copy import deepcopy
from flask_sqlalchemy.model import DefaultMeta


class FlaskMongoCommonsTest(FlaskMongoEngineTestCase):
    test_data = {"post": {},
                 "put": {},
                 "get":{}}
    func = ""
    # model = RiskArgs

    def test_post_commons_success(self):
        """测试成功创建"""
        test_data = deepcopy(self.test_data["post"])
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_post_commons_error_params_type(self):
        """测试发送错误参数"""
        test_data = deepcopy(self.test_data["post"])
        if isinstance(test_data[list(test_data.keys())[0]], list):
            test_data[list(test_data.keys())[0]] = {"error_params_type"}
        else:
            test_data[list(test_data.keys())[0]] = ["error_params_type"]
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def test_post_commons_missing_params(self):
        """测试发送缺失参数"""
        test_data = deepcopy(self.test_data["post"])
        del test_data[list(test_data.keys())[0]]
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def test_post_commons_empty_params(self):
        """测试更新某个字段是空字符串数据"""

        test_data = deepcopy(self.test_data["post"])
        test_data[list(test_data.keys())[0]] = ""
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_post_commons_no_params(self):
        """测试不发送参数"""
        response = self.client.post(url_for(self.func), json={})
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def get_id(self):
        """获取id"""
        response = self.client.post(url_for(self.func), json=self.test_data["post"])
        id = response.json["data"]["id"]
        return id

    def test_put_commons_success(self):
        """测试成功更新"""
        test_data = deepcopy(self.test_data["put"])
        test_data["id"] = self.get_id()
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_put_commons_missing_key_params(self):
        """测试发送缺失关键参数数据"""

        test_data = deepcopy(self.test_data["put"])

        self.test_post_commons_success()
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_put_commons_error_params(self):
        """测试发送错误格式数据更新"""

        test_data = deepcopy(self.test_data["put"])
        test_data["id"] = self.get_id()
        if isinstance(test_data[list(test_data.keys())[0]], list):
            test_data[list(test_data.keys())[0]] = {"error_params_type"}
        else:
            test_data[list(test_data.keys())[0]] = ["error_params_type"]
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def test_put_commons_no_params(self):
        """测试不发送参数更新"""

        self.test_post_commons_success()
        response = self.client.put(url_for(self.func), json={})
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_put_commons_NOEXIST(self):
        """测试更新不存在的数据"""
        test_data = deepcopy(self.test_data["put"])

        test_data["id"] = "5b7a7d8e992e285ca61daf3d"
        self.test_post_commons_success()
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 20000, msg=response.json)

    def test_put_commons_empty(self):
        """测试更新某个字段是空字符串数据"""
        test_data = deepcopy(self.test_data["put"])
        test_data[list(test_data.keys())[0]] = ""
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_get_commons_success_full_params(self):
        """测试发送完整参数获取数据"""
        test_data = deepcopy(self.test_data["get"])

        self.test_post_commons_success()
        response = self.client.get(url_for(self.func, **test_data))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_success_part_params(self):
        """测试发送部分参数获取数据"""
        test_data = deepcopy(self.test_data["get"])
        del test_data[list(test_data.keys())[0]]

        self.test_post_commons_success()
        response = self.client.get(url_for("commoncodeapi", **test_data))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_success_no_params(self):
        """测试不发送参数获取数据"""

        self.test_post_commons_success()
        response = self.client.get(url_for(self.func))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_error_params(self):
        """测试发送错误参数获取数据"""

        data = {"test_error_params": 1}
        self.test_post_commons_success()
        response = self.client.get(url_for(self.func, **data))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_empty_params(self):
        """测试发送错误参数获取数据"""
        test_data = deepcopy(self.test_data["get"])
        test_data[list(test_data.keys())[0]] = ""
        response = self.client.get(url_for(self.func, **test_data))
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_delete_commons_success(self):
        """测试删除数据"""
        id = self.get_id()
        response = self.client.delete(url_for(self.func), json={"id": id})
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertEqual(response.json["data"], {})

    def test_delete_commons_NOTEXIST(self):
        """测试删除不存在的数据"""

        self.client.post(url_for(self.func), json=self.test_data["post"])
        response = self.client.delete(url_for(self.func), json={"id": "5b7a7d8e992e285ca61daf3d"})
        self.assertEqual(response.json["code"], 20000, msg=response.json)

    def test_delete_commons_error_params(self):
        """测试发送错误格式的数据"""

        self.client.post(url_for(self.func), json=self.test_data["post"])
        response = self.client.delete(url_for(self.func), json={"id": 111})
        self.assertEqual(response.json["code"], 10002, msg=response.json)


class FlaskSQLCommonsTest(FlaskSQLTestCase):
    test_data = {"post": {},
                 "put": {},
                 "get":{}}
    func = ""
    model = None

    def test_post_commons_success(self):
        """测试成功创建"""
        test_data = deepcopy(self.test_data["post"])
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_post_commons_error_params_type(self):
        """测试发送错误参数"""
        test_data = deepcopy(self.test_data["post"])
        if isinstance(test_data[list(test_data.keys())[0]], list):
            test_data[list(test_data.keys())[0]] = {"error_params_type"}
        else:
            test_data[list(test_data.keys())[0]] = ["error_params_type"]
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def test_post_commons_missing_params(self):
        """测试发送缺失参数"""
        test_data = deepcopy(self.test_data["post"])
        del test_data[list(test_data.keys())[0]]
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def test_post_commons_empty_params(self):
        """测试更新某个字段是空字符串数据"""

        test_data = deepcopy(self.test_data["post"])
        test_data[list(test_data.keys())[0]] = ""
        response = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_post_commons_no_params(self):
        """测试不发送参数"""
        response = self.client.post(url_for(self.func), json={})
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def get_id(self):
        """获取id"""
        response = self.client.post(url_for(self.func), json=self.test_data["post"])
        id = response.json["data"]["id"]
        return id

    def test_put_commons_success(self):
        """测试成功更新"""
        test_data = deepcopy(self.test_data["put"])
        test_data["id"] = self.get_id()
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_put_commons_missing_key_params(self):
        """测试发送缺失关键参数数据"""

        test_data = deepcopy(self.test_data["put"])

        self.test_post_commons_success()
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_put_commons_error_params(self):
        """测试发送错误格式数据更新"""

        test_data = deepcopy(self.test_data["put"])
        test_data["id"] = self.get_id()
        if isinstance(test_data[list(test_data.keys())[0]], list):
            test_data[list(test_data.keys())[0]] = {"error_params_type"}
        else:
            test_data[list(test_data.keys())[0]] = ["error_params_type"]
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 400, msg=response.json)

    def test_put_commons_no_params(self):
        """测试不发送参数更新"""

        self.test_post_commons_success()
        response = self.client.put(url_for(self.func), json={})
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_put_commons_NOEXIST(self):
        """测试更新不存在的数据"""
        test_data = deepcopy(self.test_data["put"])

        test_data["id"] = "5b7a7d8e992e285ca61daf3d"
        self.test_post_commons_success()
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_put_commons_empty(self):
        """测试更新某个字段是空字符串数据"""
        test_data = deepcopy(self.test_data["put"])
        test_data[list(test_data.keys())[0]] = ""
        response = self.client.put(url_for(self.func), json=test_data)
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_get_commons_success_full_params(self):
        """测试发送完整参数获取数据"""
        test_data = deepcopy(self.test_data["get"])

        self.test_post_commons_success()
        response = self.client.get(url_for(self.func, **test_data))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_success_part_params(self):
        """测试发送部分参数获取数据"""
        test_data = deepcopy(self.test_data["get"])
        del test_data[list(test_data.keys())[0]]

        self.test_post_commons_success()
        response = self.client.get(url_for("commoncodeapi", **test_data))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_success_no_params(self):
        """测试不发送参数获取数据"""

        self.test_post_commons_success()
        response = self.client.get(url_for(self.func))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_error_params(self):
        """测试发送错误参数获取数据"""

        data = {"test_error_params": 1}
        self.test_post_commons_success()
        response = self.client.get(url_for(self.func, **data))
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertIsNotNone(response.json["data"])

    def test_get_commons_empty_params(self):
        """测试发送错误参数获取数据"""
        test_data = deepcopy(self.test_data["get"])
        test_data[list(test_data.keys())[0]] = ""
        response = self.client.get(url_for(self.func, **test_data))
        self.assertEqual(response.json["code"], 0, msg=response.json)

    def test_delete_commons_success(self):
        """测试删除数据"""
        id = self.get_id()
        response = self.client.delete(url_for(self.func), json={"id": id})
        self.assertEqual(response.json["code"], 0, msg=response.json)
        self.assertEqual(response.json["data"], "success!")

    def test_delete_commons_NOTEXIST(self):
        """测试删除不存在的数据"""

        self.client.post(url_for(self.func), json=self.test_data["post"])
        response = self.client.delete(url_for(self.func), json={"id": "5b7a7d8e992e285ca61daf3d"})
        self.assertEqual(response.json["code"], 10012, msg=response.json)

    def test_delete_commons_error_params(self):
        """测试发送错误格式的数据"""

        self.client.post(url_for(self.func), json=self.test_data["post"])
        response = self.client.delete(url_for(self.func), json={"id": 111})
        self.assertEqual(response.json["code"], 10012, msg=response.json)


class ModelTestMeta(type):
    """ModelSchemaResourceMeta"""

    def __new__(cls, name, bases, attrs):
        model = attrs.get("model")
        if model is None:
            return super().__new__(cls, name, bases, attrs)
        if isinstance(model, DefaultMeta):
            return type(name, (FlaskSQLCommonsTest,), attrs)
        else:
            return type(name, (FlaskMongoCommonsTest,), attrs)


class FlaskCommonsTest(metaclass=ModelTestMeta):
    """FlaskCommonsTestCase"""

