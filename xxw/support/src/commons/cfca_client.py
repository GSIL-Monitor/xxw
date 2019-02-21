import os

import requests
import xmltodict
from lxml import etree
from src import cfca_url

class CFCAClient:
    """CFCA请求客户端"""

    def __init__(self, url):
        self.url = cfca_url + url  # CFCA接口地址

    @staticmethod
    def parse_xml_response(response):
        """解析CFCA接口返回XML"""
        parser = etree.XMLParser(encoding="UTF-8", recover=True)
        tree = etree.fromstring(response, parser)
        xml_str = etree.tostring(tree)
        response_dict = xmltodict.parse(xml_str)
        return response_dict

    def post(self, payload):
        response = requests.request(
            "POST", self.url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return self.parse_xml_response(response.text)

    def get_template(self,template_code: str, operatorCode: str):
        """获取CFCA模版信息"""
        payload = (
            f"functionType=getTemplate"
            f"&templateCode={template_code}"
            f"&operatorCode={operatorCode}"
        )
        result = self.post(payload)
        if result.get("Result") and result.get("Result")["Code"] == "200":
            return result.get("Result")["Template"], {}
        else:
            return None, result.get("Result")["Message"]
