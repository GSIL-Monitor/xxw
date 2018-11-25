import pytest
from flask import url_for

from src.apps.models.sms import SMSApp
from src.config.msgconfig import Msg


def test_get_no_data(client):
    result = client.get(url_for("smsappapi")).json
    assert result["code"] == 0
    assert result["data"]["results"] == []


def test_get_filter(client, sms_app):
    client.post(url_for("smsappapi"), json=sms_app)
    for k, v in sms_app.items():
        result = client.get(url_for("smsappapi"), query_string={k: v}).json
        assert len(result["data"]["results"]) == 1


def test_get_page(client, sms_app):
    from src import db

    for i in range(100):
        sms_app_temp = sms_app.copy()
        sms_app_temp["app_name"] = sms_app_temp["app_name"] + str(i)
        app = SMSApp(**sms_app_temp)
        db.session.add(app)
    db.session.commit()
    result = client.get(
        url_for("smsappapi"), query_string={"page_size": 5, "page": 10}
    ).json
    assert result["data"]["page"] == 10
    assert result["data"]["page_size"] == 5
    assert result["data"]["pages"] == 20
    assert len(result["data"]["results"]) == 5


def test_post_success(client, sms_app):
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert result["code"] == 0
    assert SMSApp.query.count() == 1

    for i in range(10):
        sms_app_temp = sms_app.copy()
        sms_app_temp["app_name"] = sms_app_temp["app_name"] + str(i)
        client.post(url_for("smsappapi"), json=sms_app_temp)

    assert SMSApp.query.count() == 11


def test_post_unique(client, sms_app):
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert result["code"] == 0
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert result["code"] == Msg.INSTANCE_IS_EXIST
    client.delete(url_for("smsappapi"), json={"id": 1})
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert result["code"] == 0


@pytest.mark.parametrize(
    "field",
    (
        "sign_name",
        "app_name",
        "channel_code",
        "channel_name",
        "config",
        "operator_id",
        "operator",
    ),
)
def test_post_field_empty(client, sms_app, field):
    sms_app[field] = ""
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert result["code"] == Msg.VALIDATE_ERROR

    sms_app.pop(field)
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert result["code"] == Msg.VALIDATE_ERROR


def test_post_instance_is_exist(client, sms_app):
    client.post(url_for("smsappapi"), json=sms_app)
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert SMSApp.query.count() == 1
    assert result["code"] == Msg.INSTANCE_IS_EXIST


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("app_name", "阳泉银行21323"),
        ("channel_name", "阳泉银行21323"),
        ("config", '{"appid": "t34t3g3g3", "appkey": "f34fg34g"}'),
        ("operator_id", "阳泉银行21323"),
        ("operator", "阳泉银行21323"),
        ("is_valid", 0),
    ],
)
def test_put_success(client, sms_app, key, value):
    result = client.post(url_for("smsappapi"), json=sms_app).json
    result = client.put(
        url_for("smsappapi"), json={"id": result["data"]["id"], key: value}
    ).json
    assert result["code"] == 0
    assert result["data"][key] == value


def test_delete_success(client, sms_app):
    result = client.post(url_for("smsappapi"), json=sms_app).json
    assert SMSApp.query.count() == 1
    result = client.delete(url_for("smsappapi"), json={"id": result["data"]["id"]}).json
    assert result["code"] == 0
    assert SMSApp.query.count() == 1
    result = client.get(url_for("smsappapi")).json
    assert len(result["data"]["results"]) == 0


def test_delete_illegal_id(client, sms_app):
    result = client.delete(url_for("smsappapi"), json={"id": 123}).json
    assert result["code"] == Msg.INSTANCE_IS_NOT_EXIST
    result = client.delete(url_for("smsappapi"), json={"id1": "asd"}).json
    assert result["code"] == Msg.VALIDATE_ERROR


def test_can_not_delete(client, sms_app, sms_app_template):
    app_result = client.post(url_for("smsappapi"), json=sms_app).json
    template_result = client.post(
        url_for("smsapptemplateapi"), json=sms_app_template
    ).json

    result = client.delete(
        url_for("smsappapi"), json={"id": app_result["data"]["id"]}
    ).json
    assert result["code"] == Msg.SMS_APP_DEPENDENT_DELETE

    result = client.delete(
        url_for("smsapptemplateapi"), json={"id": template_result["data"]["id"]}
    ).json
    assert result["code"] == 0

    result = client.delete(
        url_for("smsappapi"), json={"id": app_result["data"]["id"]}
    ).json
    assert result["code"] == 0
