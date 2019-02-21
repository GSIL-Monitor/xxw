from flask import url_for
from src.models.sms import SmsTemplate, SmsTemplateType
from tests.commons_test import FlaskCommonsTest
from copy import deepcopy
from tests.data import sms_template_get, sms_template_post, sms_template_put, \
    sms_template_type_get, sms_template_type_post, sms_template_type_put


class SmsTemplateTest(FlaskCommonsTest):
    test_data = {"post": sms_template_post,
                 "put": sms_template_put,
                 "get": sms_template_get}
    func = "smstemplateapi"
    model = SmsTemplate
    models = [SmsTemplate, ]

    def test_post_smstemplate_twice(self):
        test_data = deepcopy(self.test_data["post"])
        response1 = self.client.post(url_for(self.func), json=test_data)
        response2 = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response2.json["code"], 400)


class SmsTemplateTypeTest(FlaskCommonsTest):
    test_data = {"post": sms_template_type_post,
                 "put": sms_template_type_put,
                 "get": sms_template_type_get}
    func = "smstemplatetypeapi"
    model = SmsTemplateType
    models = [SmsTemplateType, ]

    def test_post_smstemplate_twice(self):
        test_data = deepcopy(self.test_data["post"])
        response1 = self.client.post(url_for(self.func), json=test_data)
        response2 = self.client.post(url_for(self.func), json=test_data)
        self.assertEqual(response2.json["code"], 400)