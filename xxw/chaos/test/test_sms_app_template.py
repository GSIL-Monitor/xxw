import pytest
from flask import url_for

from src.apps.models.sms import SMSAppTemplate, SmsBussinessTemplate, db
from src.config.msgconfig import Msg


def test_get_no_data(client):
    result = client.get(url_for("smsapptemplateapi")).json
    assert result["code"] == 0
    assert result["data"]["results"] == []


def test_get_join(client, sms_app, sms_app_template):
    client.post(url_for("smsappapi"), json=sms_app)
    sms_app2 = sms_app.copy()
    sms_app2["app_name"] = "xxxxx"
    client.post(url_for("smsappapi"), json=sms_app2)
    client.post(url_for("smsapptemplateapi"), json=sms_app_template)
    sms_app_template["app_id"] = 2
    sms_app_template["template_title"] = "titleee"
    client.post(url_for("smsapptemplateapi"), json=sms_app_template)
    result = client.get(url_for("smsapptemplateapi")).json
    assert len(result["data"]["results"]) == 2
    assert result["data"]["results"][0]["app_name"] == sms_app["app_name"]
    assert result["data"]["results"][1]["app_name"] == sms_app2["app_name"]


def test_post_success(client, sms_app_template):
    result = client.post(url_for("smsapptemplateapi"), json=sms_app_template).json
    assert result["code"] == 0
    assert SMSAppTemplate.query.count() == 1


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("template_content_code", "564363453231"),
        ("template_title", "这是标题2314234"),
        ("template", "这是内容123213"),
        ("price", "0.341"),
        ("operator_id", "3252"),
        ("operator", "jack1"),
        ("is_valid", 0),
    ],
)
def test_put_success(client, sms_app_template, key, value):
    result = client.post(url_for("smsapptemplateapi"), json=sms_app_template).json

    result = client.put(
        url_for("smsapptemplateapi"), json={"id": result["data"]["id"], key: value}
    ).json
    assert result["code"] == 0
    assert result["data"][key] == value


def test_can_not_delete(client, sms_app_template):

    bus_temp = SmsBussinessTemplate(
        merchant_code="934562",
        production_code="64334",
        template_type_code="1",
        app_templates='["1", "12", "21", "3", "11"]',
        operator_id="8454",
        operator="李四",
    )
    db.session.add(bus_temp)
    db.session.commit()

    post_result = client.post(url_for("smsapptemplateapi"), json=sms_app_template).json
    result = client.delete(
        url_for("smsapptemplateapi"), json={"id": post_result["data"]["id"]}
    ).json
    assert result["code"] == Msg.SMS_APP_TEMP_DEPENDENT_DELETE

    bus_temp.app_templates = '["12", "21", "3", "11"]'
    db.session.add(bus_temp)
    db.session.commit()
    result = client.delete(
        url_for("smsapptemplateapi"), json={"id": post_result["data"]["id"]}
    ).json
    assert result["code"] == Msg.SUCCESS
