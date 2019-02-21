from datetime import datetime, date, timedelta

from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import func, literal_column, text, cast, DATE

from src.models.log_db import (LogRegister, LogCredit, LogWithdraw, LogRepay, LogFaceSign, LogLoading)
from src.models.manager import TbManager
from src import db


def get_static_data(manager_id, start, end):
    # 授信核准量
    credit_success_query = db.session.query(func.count(LogCredit.id)). \
        filter(LogCredit.manager_id == manager_id)
    if start and start.strip():
        credit_success_query = credit_success_query.filter(LogCredit.credit_time >= start)
    if end and end.strip():
        credit_success_query = credit_success_query.filter(LogCredit.credit_time <= end)
    credit_success_query = credit_success_query.label('credit_success_count')

    # 授信拒接量
    credit_fail_query = db.session.query(func.count(LogCredit.id)). \
        filter(LogCredit.manager_id == manager_id)
    if start and start.strip():
        credit_fail_query = credit_fail_query.filter(LogCredit.credit_time >= start)
    if end and end.strip():
        credit_fail_query = credit_fail_query.filter(LogCredit.credit_time <= end)
    credit_fail_query = credit_fail_query.label("credit_fail_count")

    # 授信中的量
    credit_audit_query = db.session.query(func.count(LogCredit.id)). \
        filter(LogCredit.manager_id == manager_id)
    if start and start.strip():
        credit_audit_query = credit_audit_query.filter(LogCredit.credit_time >= start)
    if end and end.strip():
        credit_audit_query = credit_audit_query.filter(LogCredit.credit_time <= end)
    credit_audit_query = credit_audit_query.label("credit_audit_count")

    # 面签量
    face_sign_query = db.session.query(func.count(LogFaceSign.id)). \
        filter(LogFaceSign.manager_id == manager_id)
    if start and start.strip():
        face_sign_query = face_sign_query.filter(LogFaceSign.face_sign_time >= start)
    if end and end.strip():
        face_sign_query = face_sign_query.filter(LogFaceSign.face_sign_time <= end)
    face_sign_query = face_sign_query.label("face_sign_count")

    # 扫码量
    loading_qr_query = db.session.query(func.count(LogLoading.id)). \
        filter(LogLoading.manager_id == manager_id)
    if start and start.strip():
        loading_qr_query = loading_qr_query.filter(LogLoading.load_time >= start)
    if end and end.strip():
        loading_qr_query = loading_qr_query.filter(LogLoading.load_time <= end)
    loading_qr_query = loading_qr_query.label("loading_qr_count")

    # 注册量
    register_query = db.session.query(func.count(LogRegister.id)). \
        filter(LogRegister.manager_id == manager_id)
    if start and start.strip():
        register_query = register_query.filter(LogRegister.reg_time >= start)
    if end and end.strip():
        register_query = register_query.filter(LogRegister.reg_time <= end)
    register_query = register_query.label("register_count")

    # 申请量
    credit_total_query = db.session.query(func.count(LogCredit.id)). \
        filter(LogCredit.manager_id == manager_id)
    if start and start.strip():
        credit_total_query = credit_total_query.filter(LogCredit.credit_time >= start)
    if end and end.strip():
        credit_total_query = credit_total_query.filter(LogCredit.credit_time <= end)
    credit_total_query = credit_total_query.label("credit_total_count")

    # 提现量
    withdraw_num_query = db.session.query(func.count(LogWithdraw.id)). \
        filter(LogWithdraw.manager_id == manager_id)
    if start and start.strip():
        withdraw_num_query = withdraw_num_query.filter(LogWithdraw.draw_time >= start)
    if end and end.strip():
        withdraw_num_query = withdraw_num_query.filter(LogWithdraw.draw_time <= end)
    withdraw_num_query = withdraw_num_query.label("withdraw_num_count")

    # 提现金额
    withdraw_money_query = db.session.query(func.sum(LogWithdraw.load_amt)). \
        filter(LogWithdraw.manager_id == manager_id)
    if start and start.strip():
        withdraw_money_query = withdraw_money_query.filter(LogWithdraw.draw_time >= start)
    if end and end.strip():
        withdraw_money_query = withdraw_money_query.filter(LogWithdraw.draw_time <= end)
    withdraw_money_query = withdraw_money_query.label("withdraw_money_count")

    base_query = db.session.query("1").add_columns(credit_success_query). \
        add_columns(credit_fail_query). \
        add_columns(credit_audit_query). \
        add_columns(face_sign_query). \
        add_columns(loading_qr_query). \
        add_columns(register_query). \
        add_columns(credit_total_query). \
        add_columns(withdraw_num_query). \
        add_columns(withdraw_money_query).one()

    return [
        base_query.credit_success_count,
        base_query.credit_fail_count,
        base_query.credit_audit_count,
        base_query.face_sign_count,
        base_query.loading_qr_count,
        base_query.register_count,
        base_query.credit_total_count,
        base_query.withdraw_num_count,
        base_query.withdraw_money_count]


class ManagerSaleStatus(Resource):
    """ 获取客户经理的统计数据"""

    def get(self):
        # 时间控制，注意的UTC时间。

        start = request.args.get('start')
        end = request.args.get('end')

        base_query = db.session.query(TbManager.id, TbManager.phone, TbManager.name, TbManager.code)

        # 查询
        query_fields = ['merchant_code', 'name', 'phone']
        for query_field in query_fields:
            field = request.args.get(query_field)
            if field and field.strip():
                base_query = base_query.filter(getattr(TbManager, query_field) == field).filter(
                    TbManager.is_delete == False)

        # 分页
        page = int(request.args.get('page') or 1)
        page_size = int(request.args.get('page_size') or 10)

        if page_size == -1:
            all = base_query.count()
            pagination = base_query.paginate(page=page, per_page=all)
        else:
            pagination = base_query.paginate(page=page, per_page=page_size)

        # 序列化返回
        dict_result = []
        v = lambda amount: 0 if not amount else str(amount)
        for row in pagination.items:
            ext_data = get_static_data(row.code, start, end)
            tp = {
                'id': row.id,
                'name': row.name,
                'phone': row.phone,
                'credit_success': ext_data[0],
                'credit_fail': ext_data[1],
                'credit_audit': ext_data[2],
                'face_sign_count': ext_data[3],
                'loading_qr_count': ext_data[4],
                'register': ext_data[5],
                'credit_total': ext_data[6],
                'withdraw_num': ext_data[7],
                'withdraw_money': v(ext_data[8])
            }
            dict_result.append(tp)

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": dict_result
        }


class ManagerSaleChart(Resource):
    """ 客户经理统计图 """

    def get(self):
        start = request.args.get("start")
        end = request.args.get('end')
        name = request.args.get('name')

        def get_manager_id_by_name(manager_name):
            manager_id = db.session.query(TbManager.id).filter(TbManager.name == manager_name).first()
            return manager_id.id

        if name and name.strip():
            manager_exist = db.session.query(TbManager.id).filter(TbManager.name == name).scalar()
            if not manager_exist:
                return "查无此人", 400

        loading_qr_query, register_query, credit_query, withdraw_query = None, None, None, None
        print(request)

        query_lists = [

            {
                "label": "扫码量",
                "name": loading_qr_query,
                "model": LogLoading,
                "fields": [LogLoading.id, LogLoading.load_time.label('c_time')],
                "columns": [
                    {
                        "req_args": "merchant_code",
                        "model_args": "merchant_code",
                        "type": 0
                    },
                    {
                        "req_args": "name",
                        "model_args": "manager_id",
                        "type": 1,
                        "trans": get_manager_id_by_name
                    }
                ],
                "time_control": 'load_time',
            },

            {
                "label": "注册量",
                "name": register_query,
                "model": LogRegister,
                "fields": [LogRegister.id, LogRegister.reg_time.label('c_time')],
                "columns": [
                    {
                        "req_args": "merchant_code",
                        "model_args": "merchant_code",
                        "type": 0
                    },
                    {
                        "req_args": "name",
                        "model_args": "manager_id",
                        "type": 1,
                        "trans": get_manager_id_by_name
                    }
                ],
                "time_control": "reg_time"
            },
            {
                "label": "申请量",
                "name": credit_query,
                "model": LogCredit,
                "fields": [LogCredit.id, LogCredit.credit_time.label('c_time')],
                "columns": [
                    {
                        "req_args": "merchant_code",
                        "model_args": "merchant_code",
                        "type": 0
                    },
                    {
                        "req_args": "name",
                        "model_args": "manager_id",
                        "type": 1,
                        "trans": get_manager_id_by_name
                    }
                ],
                "time_control": "credit_time"
            },

            {
                "label": "提现量",
                "name": withdraw_query,
                "model": LogWithdraw,
                "fields": [LogWithdraw.id, LogWithdraw.draw_time.label('c_time'), LogWithdraw.load_amt],
                "columns": [
                    {
                        "req_args": "merchant_code",
                        "model_args": "merchant_code",
                        "type": 0
                    },
                    {
                        "req_args": "name",
                        "model_args": "manager_id",
                        "type": 1,
                        "trans": get_manager_id_by_name
                    }
                ],
                "time_control": "draw_time"
            }

        ]

        for query in query_lists:
            query['name'] = db.session.query(*query['fields'])
            for column in query['columns']:
                t = request.args.get(column['req_args'])
                if t and t.strip():
                    if column['type'] == 0:
                        query['name'] = query['name'].filter(getattr(query['model'], column['model_args']) == t)
                    if column['type'] == 1:
                        query['name'] = query['name'].filter(
                            getattr(query['model'], column['model_args']) == column['trans'](t))
            if start and start.strip():
                query['name'] = query['name'].filter(getattr(query['model'], query['time_control']) >= start)
            if end and end.strip():
                query['name'] = query['name'].filter(getattr(query['model'], query['time_control']) <= end)
            query['name'] = query['name'].order_by(getattr(query['model'], query['time_control']))

        # 查询完成， 统计数量
        # 时间的规范每天的零点到23：59：59为一天的数据。比如9-13 00:00:00 - 9-13 23;59:59为1天的数据。
        # 如果时间到9-14 00:00:00 为第二天。。。时间为UTC时间搓。注意。
        start_timestamp = int(start)
        end_timestamp = int(end)

        h = []
        while start_timestamp <= end_timestamp + 1:
            h.append(start_timestamp)
            start_timestamp += 24 * 60 * 60

        def get_sale_statis(q_list):
            for query in q_list:
                tmp = [0] * len(h)
                result_list = query['name'].all()

                cur_h, cur_result = 0, 0
                while (cur_h < len(h)) and (cur_result < len(result_list)):
                    if result_list[cur_result].c_time < h[cur_h]:
                        tmp[cur_h] += 1  # 次数， 下面是金额
                        cur_result += 1
                    else:
                        cur_h += 1
                yield tmp[1:]
            raise StopIteration

        sale_static = [i for i in get_sale_statis(query_lists)]

        # 完成统计，显示结果
        build_result = []
        for i in range(4):
            t = {
                "name": query_lists[i]['label'],
                "data": sale_static[i],
                "time": [b for b in h[:-1]]
            }
            build_result.append(t)

        return {
            "results": build_result
        }
