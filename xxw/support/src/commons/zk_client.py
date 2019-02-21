import json
from src.commons.logger import logger
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

from src.commons.constant import ConfigNameMap


class ZkClient:

    def __init__(self, zk_servers, app):
        self.app = app
        self.zk = KazooClient(hosts=zk_servers)
        self.zk.start()
        self.server_node_path = "/entry/service"
        self.node = "/entry/serviceinfo/node/loan_mng"
        self.os_center_node = "/entry/service/os_center/node"
        self.loan_mng_hosts = ""

        self.zk.DataWatch(self.node, self.get_loan_mng_hosts)
        self.zk.DataWatch(self.os_center_node, self.get_os_center_hosts)
        self.zk.DataWatch(self.server_node_path, self.get_servers_node)
        
    def get_loan_mng_hosts(self, *args):
        try:
            data = json.loads(self.zk.get(self.node)[0])
            ip = data["node_list"][0]["ip"]
            port = data["node_list"][0]["port"]
            host = "http://{}:{}".format(ip, port)
            logger.info("ZK | GET LOAN_MNG HOSTS | SUCCESS | HOST: {}".format(host))
            self.loan_mng_hosts = host
            return host
        except Exception as e:
            logger.info("ZK | GET LOAN_MNG HOSTS | FAILED | ERROR: {}".format(str(e)))
            self.loan_mng_hosts = ""

    def get_os_center_hosts(self, *args):
        try:
            children = self.zk.get_children(self.os_center_node)
            node = children[0]
            data = self.zk.get(self.os_center_node+"/"+node)[0].decode()
            host = "http://{}".format(data)
            logger.info("ZK | GET OS_CENTER HOSTS | SUCCESS | HOST: {}".format(host))
            return host
        except Exception as e:
            logger.info("ZK | GET OS_CENTER HOSTS | FAILED | ERROR: {}".format(str(e)))
            return ""

    def get_config(self, category):
        path = ConfigNameMap.zk_path[category]
        if not self.zk.exists(path):
            self.zk.create(path, json.dumps({}).encode())
        try:
            data = json.loads(self.zk.get(path)[0].decode())
            return data
        except Exception as e:
            logger.info("ZK | GET CONFIG | FAILED | CATEGORY: {}| ERROR: {}".format(category, str(e)))
            return {}

    def write_config(self, category, config):
        path = ConfigNameMap.zk_path[category]
        try:
            self.zk.ensure_path(path)
            if not self.zk.exists(path):
                self.zk.create(path, json.dumps({}).encode())
            self.zk.set(path, json.dumps(config).encode())
            return True
        except Exception as e:
            logger.info("ZK | SYNC CONFIG | FAILED | CATEGORY: {}| ERROR: {}".format(category, str(e)))
            return False

    def get_servers_node(self, *args):
        """
        获取所有服务的注册节点
        """
        servers_node = []

        def _get_childern(path):
            try:
                reg = self.zk.get_children(path)
                return reg
            except Exception as e:
                return []

        def _get_data(path):
            try:
                data = self.zk.get(path)[0].decode()
                return data
            except Exception as e:
                return None

        try:
            all_server = self.zk.get_children(self.server_node_path)
            for server_name in all_server:
                path = "{}/{}/node".format(self.server_node_path, server_name)
                registration = _get_childern(path)
                data = []
                for i in registration:
                    node_data = _get_data(path+"/"+i)
                    data.append(node_data)
                servers_node.append({
                    "name": server_name,
                    "node": list(set(data))
                })
            return servers_node
        except NoNodeError as e:
            logger.warn("NO NODE ERROR | NODE PATH {}".format(self.server_node_path))
            return []
