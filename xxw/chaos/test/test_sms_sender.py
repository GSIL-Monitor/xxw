import pytest
from flask import url_for

from src.comm.sms_utils import single_sms_sender
from src.config.msgconfig import Msg


@pytest.mark.skip(reason="skip")
def test_liantong_sender():
    """ 联通发送短信测试
    """
    result, error = single_sms_sender(
        channel_code="liantong",
        receiver="18582554687",
        template_content="你好,你的订单：{1}，请及时查收",
        params=["88888888"],
        template_content_code="",
        conf_params={"CorpID": "CDJS006669", "Pwd": "xxxxx"},
        sign_name="涌泉贷",
    )
    assert result is True


@pytest.mark.skip(reason="skip")
def test_check_app_temp(client, sms_app, sms_app_template):
    """测试应用模板是否有效
    """
    sms_app["channel_code"] = "tx"
    client.post(url_for("smsappapi"), json=sms_app)
    client.post(url_for("smsapptemplateapi"), json=sms_app_template)
    result = client.post(
        url_for("smsapptemplatecheckapi"),
        json={"phone": "18582554687", "app_template_id": 1, "params": [1, 2]},
    ).json

    assert result["code"] == Msg.ERROR
