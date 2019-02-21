from flask import url_for
from tests.commons_test import FlaskCommonsTest
from copy import deepcopy
from src.models.risk_args import RiskArgs
from tests.data import risk_args_post, risk_args_put, risk_args_get


class RiskArgsTest(FlaskCommonsTest):
    test_data = {"post": risk_args_post,
                 "put": risk_args_put,
                 "get": risk_args_get}
    func = "riskargsapi"
    model = RiskArgs


    def test_post_risk_args_error_params_content(self):
        risk_args_post = deepcopy(self.test_data["post"])
        risk_args_post["rule_conf"]["degrees"].append("error_content")
        response = self.client.post(url_for("riskargsapi"), json=risk_args_post)
        self.assertEqual(response.json["code"], 400)











