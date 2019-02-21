"""
对各个服务的监控
1. 服务注册监控

creator: roywu
create_time: 2018-09-12 13:47
"""

from flask_restful import Resource

from src import zk


class ServerRegistration(Resource):

    def get(self):
        """
        所有服务注册情况
        """

        return {"results": zk.get_servers_node()}, 200
