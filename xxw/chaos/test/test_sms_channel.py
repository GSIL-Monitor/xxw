from flask import url_for


def test_get_success(client):
    result = client.get(url_for("smschannelapi")).json
    assert result["code"] == 0
    from src.comm.sms_utils import SMSSender

    assert SMSSender.channel_list == result["data"]["results"]
