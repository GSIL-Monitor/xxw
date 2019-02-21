from flask_restful import Resource, reqparse
from flask import request

from src import db
from src.models.log_db import LogCredit, LogRegister

import importlib
import inspect


class UserHistoryWorkOrder(Resource):
    """获取用户历史工单"""

    def get(self):
        uin = request.args.get('uin')
        # 注册时间
        register_time = db.session.query(LogRegister.reg_time).filter(LogRegister.uin == uin).first()
        # 授信时间
        credit_time = db.session.query(LogCredit.credit_time).filter(LogCredit.uin == uin).first()

        v = lambda x: None if not x else x[0]

        return {
            "register": v(register_time),
            "credit": v(credit_time)
        }
