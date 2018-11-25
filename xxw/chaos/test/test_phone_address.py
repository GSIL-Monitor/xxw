from flask import url_for

phone = {"phone": "18030446730"}
err_phone = {"phone": "123456"}


def test_get_phone_address_success(client):
    response = client.get(url_for("phoneaddressapi", **phone)).json
    assert response["code"] == 0


def test_get_phone_address_error_phone(client):
    response = client.get(url_for("phoneaddressapi", **err_phone)).json
    assert response["code"] == 1016100101
