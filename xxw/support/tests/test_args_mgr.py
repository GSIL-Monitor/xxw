from flask import url_for
from tests import FlaskMongoEngineTestCase


class CommonCodeTest(FlaskMongoEngineTestCase):
    def test_post_common_code_success(self):
        """测试成功创建"""

        from tests.data import common_code_post
        response = self.client.post(url_for("commoncodeapi"), json=common_code_post)
        self.assertEqual(response.json["data"]["type"], common_code_post["type"])
        self.assertEqual(response.json["data"]["code"], common_code_post["code"])

    def test_post_common_code_error_params(self):
        """测试发送错误参数"""

        from tests.data import common_code_post

        common_code_post = common_code_post.copy()
        common_code_post["type"] = 11111
        response = self.client.post(url_for("commoncodeapi"), json=common_code_post)
        self.assertEqual(response.json["code"], 400)

    def test_post_common_code_missing_params(self):
        """测试发送缺失参数"""

        from tests.data import common_code_post

        common_code_post = common_code_post.copy()
        del common_code_post["code"]
        response = self.client.post(url_for("commoncodeapi"), json=common_code_post)
        self.assertEqual(response.json["code"], 400)

    def test_post_common_code_no_params(self):
        """测试不发送数据"""

        response = self.client.post(url_for("commoncodeapi"))
        self.assertEqual(response.json["code"], 10012)

    def test_post_common_code_repeat(self):
        """测试发送重复的unique字段"""

        from tests.data import common_code_post

        self.client.post(url_for("commoncodeapi"), json=common_code_post)
        response = self.client.post(url_for("commoncodeapi"), json=common_code_post)
        self.assertEqual(response.json["code"], 10011)

    def get_id(self):
        from tests.data import common_code_put
        from tests.data import common_code_post

        common_code_put = common_code_put.copy()
        response = self.client.post(url_for("commoncodeapi"), json=common_code_post)
        id = response.json["data"]["id"]
        common_code_put["id"] = id
        return common_code_put

    def test_put_common_code_success(self):
        """测试成功更新"""

        from tests.data import common_code_put

        common_code_put_by_id = self.get_id()
        response1 = self.client.put(url_for("commoncodeapi"), json=common_code_put_by_id)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.json["data"]["code"], common_code_put["code"])
        self.assertEqual(response1.json["data"]["name"], common_code_put["name"])

    def test_put_common_code_missing_key_params(self):
        """测试发送缺失关键参数数据"""

        from tests.data import common_code_put

        self.test_post_common_code_success()
        response = self.client.put(url_for("commoncodeapi"), json=common_code_put)
        self.assertEqual(response.json["code"], 10002)

    def test_put_common_code_error_params(self):
        """测试发送错误格式数据更新"""

        common_code_put = self.get_id()
        common_code_put["code"] = 111
        response1 = self.client.put(url_for("commoncodeapi"), json=common_code_put)
        self.assertEqual(response1.status_code, 400)

    def test_put_common_code_no_params(self):
        """测试不发送参数更新"""

        self.test_post_common_code_success()
        response = self.client.put(url_for("commoncodeapi"))
        self.assertEqual(response.json["code"], 10002)

    def test_put_common_code_NOEXIST(self):
        """测试更新不存在的数据"""
        from tests.data import common_code_put

        common_code_put["id"] = "111"
        self.test_post_common_code_success()
        response = self.client.put(url_for("commoncodeapi"), json=common_code_put)
        self.assertEqual(response.status_code, 400)

    def test_get_common_code_success_full_params(self):
        """测试发送完整参数获取数据"""
        from tests.data import common_code_get

        self.test_post_common_code_success()
        response = self.client.get(url_for("commoncodeapi", **common_code_get))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_get_common_code_success_part_params(self):
        """测试发送部分参数获取数据"""
        from tests.data import common_code_get

        common_code_get = common_code_get.copy()
        del common_code_get["type"]
        del common_code_get["name"]
        self.test_post_common_code_success()
        response = self.client.get(url_for("commoncodeapi", **common_code_get))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_get_common_code_success_no_params(self):
        """测试不发送参数获取数据"""

        self.test_post_common_code_success()
        response = self.client.get(url_for("commoncodeapi"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_get_common_code_error_params(self):
        """测试发送错误参数获取数据"""

        data = {"xxx": 1}
        self.test_post_common_code_success()
        response = self.client.get(url_for("commoncodeapi", **data))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_delete_common_code_success(self):
        """测试删除数据"""

        from tests.data import common_code_post

        common_code_post = common_code_post.copy()
        response = self.client.post(url_for("commoncodeapi"), json=common_code_post)
        id = response.json["data"]["id"]
        response = self.client.delete(url_for("commoncodeapi"), json={"id": id})
        self.assertEqual(response.json["code"], 0)
        self.assertEqual(response.json["data"], {})

    def test_delete_common_code_NOTEXIST(self):
        """测试删除不存在的数据"""

        from tests.data import common_code_post

        self.client.post(url_for("commoncodeapi"), json=common_code_post)
        response = self.client.delete(url_for("commoncodeapi"), json={"id": "111"})
        self.assertEqual(response.status_code, 400)

    def test_delete_common_code_err_params(self):
        """测试发送错误格式的数据"""

        from tests.data import common_code_post

        self.client.post(url_for("commoncodeapi"), json=common_code_post)
        response = self.client.delete(url_for("commoncodeapi"), json={"id": 111})
        self.assertEqual(response.status_code, 400)


class IndustryPositionTest(FlaskMongoEngineTestCase):
    def test_post_industry_position_success(self):
        """测试成功创建行业职位表"""
        from tests.data import industry_position_post

        response = self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        self.assertEqual(response.json["data"]["industry_code"], industry_position_post["industry_code"])
        self.assertEqual(response.json["data"]["position_code"], industry_position_post["position_code"])

    def test_post_industry_position_error_params(self):
        """测试发送错误数据"""
        from tests.data import industry_position_post

        industry_position_post = industry_position_post.copy()
        industry_position_post["industry_code"] = 200
        response = self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        self.assertEqual(response.status_code, 400)

    def test_post_industry_position_no_params(self):
        """测试不发送数据"""
        response = self.client.post(url_for("industrypositionapi"))
        self.assertEqual(response.json["code"], 10012)

    def test_post_industry_position_missing_params(self):
        """测试发送缺失数据"""

        from tests.data import industry_position_post

        industry_position_post = industry_position_post.copy()
        del industry_position_post["industry_code"]
        response = self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        self.assertEqual(response.json["code"], 400)

    def get_id(self):
        from tests.data import industry_position_post
        from tests.data import industry_position_put

        industry_position_put = industry_position_put.copy()
        response = self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        id = response.json["data"]["id"]
        industry_position_put["id"] = id
        return industry_position_put

    def test_put_industry_position_success(self):
        """测试成功更新数据"""

        from tests.data import industry_position_put

        industry_position_put_id = self.get_id()
        response1 = self.client.put(url_for("industrypositionapi"), json=industry_position_put_id)
        self.assertEqual(response1.json["data"]["industry_name"], industry_position_put["industry_name"])
        self.assertEqual(response1.json["data"]["position_name"], industry_position_put["position_name"])

    def test_put_industry_position_missing_key_params(self):
        """测试缺失关键参数"""

        from tests.data import industry_position_put

        self.test_post_industry_position_success()
        response = self.client.put(url_for("industrypositionapi"), json=industry_position_put)
        self.assertEqual(response.json["code"], 10012)

    def test_put_industry_position_error_params(self):
        """测试发送错误格式参数"""

        industry_position_put_id = self.get_id()
        industry_position_put_id["industry_name"] = 111
        response1 = self.client.put(url_for("industrypositionapi"), json=industry_position_put_id)
        self.assertEqual(response1.json["code"], 400)

    def test_put_industry_position_no_params(self):
        """测试不发送参数更新"""

        self.test_post_industry_position_success()
        response = self.client.put(url_for("industrypositionapi"))
        self.assertEqual(response.json["code"], 10002)

    def test_put_industry_position_NOEXIST(self):
        """测试更新不存在的数据"""
        from tests.data import industry_position_put

        industry_position_put = industry_position_put.copy()
        industry_position_put["id"] = "111"
        self.test_post_industry_position_success()
        response = self.client.put(url_for("industrypositionapi"), json=industry_position_put)
        self.assertEqual(response.status_code, 400)

    def test_get_industry_position_success_full_params(self):
        """测试发送完整参数获取数据"""
        from tests.data import industry_position_get

        self.test_post_industry_position_success()
        response = self.client.get(url_for("industrypositionapi", **industry_position_get))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_get_industry_position_success_part_params(self):
        """测试发送部分参数获取数据"""
        from tests.data import industry_position_get

        del industry_position_get["position_code"]
        self.test_post_industry_position_success()
        response = self.client.get(url_for("industrypositionapi", **industry_position_get))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_industry_position_code_success_no_params(self):
        """测试不发送参数获取数据"""

        self.test_post_industry_position_success()
        response = self.client.get(url_for("industrypositionapi"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_industry_position_code_error_params(self):
        """测试发送错误参数获取数据"""

        data = {"xxx": []}
        self.test_post_industry_position_success()
        response = self.client.get(url_for("industrypositionapi", **data))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["data"])

    def test_delete_industry_position_success(self):
        """测试删除数据"""

        from tests.data import industry_position_post

        industry_position_post = industry_position_post.copy()
        response = self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        id = response.json["data"]["id"]
        response = self.client.delete(url_for("industrypositionapi"), json={"id": id})
        self.assertEqual(response.json["code"], 0)

    def test_delete_industry_position_NOTEXIST(self):
        """测试删除不存在的数据"""

        from tests.data import industry_position_post

        self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        response = self.client.delete(url_for("industrypositionapi"), json={"id": "111"})
        self.assertEqual(response.status_code, 400)

    def test_delete_industry_position_err_params(self):
        """测试发送错误格式的数据"""

        from tests.data import industry_position_post

        self.client.post(url_for("industrypositionapi"), json=industry_position_post)
        response = self.client.delete(url_for("industrypositionapi"), json={"id": 111})
        self.assertEqual(response.status_code, 400)
