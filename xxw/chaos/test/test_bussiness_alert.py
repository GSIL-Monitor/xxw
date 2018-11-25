from flask import url_for


def test_alert(client):
    data = {
        "service_name": "chaos",
        "type": "inter",
        "message": "测试",
        "host": "10.0.0.1",
        "timestamp": 1537252076,
        "level": "error",
        "stack_info": "Error",
        "extra": {},
    }
    result = client.post(url_for("alertapi"), json=data).json
    assert result["code"] == 0
