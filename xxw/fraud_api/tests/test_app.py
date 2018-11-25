from src.main import app

client = app.test_client()


def test_api():
    assert client.get("/query/configs?product=xw").status_code == 200
    assert client.get("/query/events_count?product=xw").status_code == 200
    assert client.get("/query/events?&product=xw").status_code == 200
    assert client.get("/query/features?page=1&page_size=10&event_type=").status_code == 200
    assert client.get("/query/map").status_code == 200
    assert client.get("/query/latest_map").status_code == 200
    assert client.get("/query/cycle?date=&product&event_type").status_code == 200
