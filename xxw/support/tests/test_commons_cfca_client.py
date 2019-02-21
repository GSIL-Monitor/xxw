import logging

from src.commons.cfca_client import CFCAClient


def test_cfcaclient():
    url = "PaperlessAssistServlet"
    payload = ""
    client = CFCAClient(url)
    x = client.post(payload=payload)
    assert x is not None
