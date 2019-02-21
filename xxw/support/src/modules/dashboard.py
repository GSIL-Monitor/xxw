from datetime import datetime, date, timedelta, timezone

from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import func, literal_column, text, cast, DATE

from src.models.log_db import (LogRegister, LogCredit, LogWithdraw, LogRepay)
from src import db


class BasicInfo(Resource):
    """基本放款还款信息"""

    def get(self):
        merchant_code = request.args.get('merchant_code')
        # 修改为当天的数据
        today = datetime.now(timezone.utc)
        today_0 = datetime(today.year, today.month, today.day)
        print("sys_Time" + str(today) + "###" + str(today_0))
        week_before = today_0 - timedelta(days=7)

        today_0_timestamp = int(today_0.timestamp())
        week_before_timestamp = int(week_before.timestamp())

        # 最近7天放款
        lend_week_amount = db.session.query(func.sum(LogWithdraw.load_amt)).filter(
            LogWithdraw.merchant_code == merchant_code). \
            filter(LogWithdraw.draw_time > week_before_timestamp).scalar()
        # 最近7天放款次数
        lend_week_count = db.session.query(func.count(LogWithdraw.id)).filter(
            LogWithdraw.merchant_code == merchant_code). \
            filter(LogWithdraw.draw_time > week_before_timestamp).scalar()
        # 今日放贷总数
        lend_today_amount = db.session.query(func.sum(LogWithdraw.load_amt)).filter(
            LogWithdraw.merchant_code == merchant_code). \
            filter(LogWithdraw.draw_time > today_0_timestamp).scalar()
        # 今日放贷次数
        lend_today_count = db.session.query(func.count(LogWithdraw.id)).filter(
            LogWithdraw.merchant_code == merchant_code). \
            filter(LogWithdraw.draw_time > today_0_timestamp).scalar()

        # 今日还款
        repay_today_amount = db.session.query(func.sum(LogRepay.repay_amt)).filter(
            LogRepay.merchant_code == merchant_code). \
            filter(LogRepay.repay_time > today_0_timestamp).scalar()
        # 累计7天还款
        repay_week_amount = db.session.query(func.sum(LogRepay.repay_amt)).filter(
            LogRepay.merchant_code == merchant_code). \
            filter(LogRepay.repay_time > week_before_timestamp).scalar()

        # 总投放额度
        total_credit_amount = db.session.query(func.sum(LogCredit.credit_amt)).filter(
            LogCredit.merchant_code == merchant_code). \
            scalar()

        # 平均利率
        average_interest_rate = db.session.query(func.avg(LogCredit.credit_rate)).filter(
            LogCredit.merchant_code == merchant_code). \
            scalar()

        v = lambda amount: 0 if not amount else str(amount)

        return {
            "load_balance": "2000000",
            "lend_number": {
                'today': lend_today_count,
                'week': lend_week_count
            },
            "lend_money": {
                "today": v(lend_today_amount),
                "week": v(lend_week_amount)
            },
            "repay_number": {
                "today": v(repay_today_amount),
                "week": v(repay_week_amount)
            },
            "total_credit": v(total_credit_amount),
            "average_interest_rate": v(average_interest_rate)
        }


class EventCount(Resource):
    """事件类别占比"""

    def get(self):
        merchant_code = request.args.get('merchant_code')
        try:
            start = int(request.args.get('start'))
            end = int(request.args.get('end'))
        except ValueError:
            return "start, end  必填", 400

        # 查询次数
        register_count = db.session.query(func.count(LogRegister.id)).filter(
            LogRegister.merchant_code == merchant_code). \
            filter(LogRegister.reg_time.between(start, end)).scalar()

        grant_credit_count = db.session.query(func.count(LogCredit.id)).filter(
            LogCredit.merchant_code == merchant_code). \
            filter(LogCredit.credit_time.between(start, end)).scalar()

        lend_count = db.session.query(func.count(LogWithdraw.id)).filter(LogWithdraw.merchant_code == merchant_code). \
            filter(LogWithdraw.draw_time.between(start, end)).scalar()

        repay_count = db.session.query(func.count(LogRepay.id)).filter(LogRepay.merchant_code == merchant_code). \
            filter(LogRepay.repay_time.between(start, end)).scalar()

        total = sum([register_count, grant_credit_count, lend_count, repay_count])

        return {
            "register": register_count,
            "grant_credit": grant_credit_count,
            "lend": lend_count,
            "repay": repay_count,
            "total": total
        }


class RealTimeDetail(Resource):
    """实时明细接口"""

    def get(self):
        merchant_code = request.args.get('merchant_code')
        size = request.args.get('size') or 10

        lend_list = db.session.query(LogWithdraw.name, LogWithdraw.phone, LogWithdraw.draw_time.label('c_time'),
                                     LogWithdraw.load_amt).filter(LogWithdraw.merchant_code == merchant_code). \
            order_by(LogWithdraw.draw_time.desc(), LogWithdraw.id.desc()).limit(size).all()

        repay_list = db.session.query(LogRepay.name, LogRepay.phone, LogRepay.repay_time.label('c_time'),
                                      LogRepay.repay_amt).filter(LogRepay.merchant_code == merchant_code). \
            order_by(LogRepay.repay_time.desc(), LogRepay.id.desc()).limit(size).all()

        # 排序
        len_lend_list = len(lend_list)
        len_repay_list = len(repay_list)
        cur_a, cur_b = 0, 0
        result = []

        while (cur_a < len_lend_list) or (cur_b < len_repay_list):
            if len_lend_list == 0:
                result = repay_list
                break
            if len_repay_list == 0:
                result = lend_list
                break
            if cur_a == len_lend_list:
                result.extend(repay_list[cur_b:])
                break
            if cur_b == len_repay_list:
                result.extend(lend_list[cur_a:])
                break
            if lend_list[cur_a].c_time >= repay_list[cur_b].c_time:
                result.append(lend_list[cur_a])
                cur_a += 1
            else:
                result.append(repay_list[cur_b])
                cur_b += 1

        # 序列化返回
        dict_result = []
        for row in result[:int(size)]:
            tp = {
                'name': row.name,
                'phone': row.phone,
                'datetime': row.c_time,
                'amount': str(row.load_amt) if hasattr(row, 'load_amt') else str(row.repay_amt),
                'type': 0 if hasattr(row, 'load_amt') else 1
            }
            dict_result.append(tp)

        return {
            "results": dict_result
        }


class CompareChart(Resource):
    """放款还款对比图"""

    def get(self):
        merchant_code = request.args.get('merchant_code')
        span = request.args.get('span')

        if span == '0':
            # 获取当天24小时的数据
            today = datetime.now(timezone.utc)
            today_0 = datetime(today.year, today.month, today.day)

            lend_list = db.session.query(LogWithdraw.id, LogWithdraw.draw_time.label('c_time'), LogWithdraw.load_amt). \
                filter(LogWithdraw.merchant_code == merchant_code). \
                filter(LogWithdraw.draw_time > int(today_0.timestamp())). \
                order_by(LogWithdraw.draw_time, LogWithdraw.id.desc()). \
                all()
            repay_list = db.session.query(LogRepay.id, LogRepay.repay_time.label('c_time'), LogRepay.repay_amt). \
                filter(LogRepay.merchant_code == merchant_code). \
                filter(LogRepay.repay_time > int(today_0.timestamp())). \
                order_by(LogRepay.repay_time, LogRepay.id.desc()). \
                all()

            # 统计次数
            h = list(map(lambda x: today_0 + timedelta(hours=x), range(1, 25)))
            result_list1, result_list2 = [0] * 24, [0] * 24

            cur_h, cur_lend = 0, 0
            while (cur_h < 24) and (cur_lend < len(lend_list)):
                if lend_list[cur_lend].c_time <= h[cur_h].timestamp():
                    # result_list1[cur_h] += 1  次数， 下面是金额
                    result_list1[cur_h] += lend_list[cur_lend].load_amt
                    cur_lend += 1
                else:
                    cur_h += 1

            cur_h, cur_repay = 0, 0
            while (cur_h < 24) and (cur_repay < len(repay_list)):
                if repay_list[cur_repay].c_time <= h[cur_h].timestamp():
                    # result_list2[cur_h] += 1  次数， 下面是金额
                    result_list2[cur_h] += repay_list[cur_repay].repay_amt
                    cur_repay += 1
                else:
                    cur_h += 1

            # 返回内容
            return {
                "results": [
                    {
                        "name": "放款",
                        "data": [str(i) for i in result_list1]
                    },
                    {
                        "name": "还款",
                        "data": [str(i) for i in result_list2]
                    }
                ]
            }

        if span == '1':
            # 获取最近7天的数据
            today = datetime.now(timezone.utc)
            today_0 = datetime(today.year, today.month, today.day)
            today_before = today_0 - timedelta(days=7)

            lend_list = db.session.query(LogWithdraw.id, LogWithdraw.draw_time.label('c_time'), LogWithdraw.load_amt). \
                filter(LogWithdraw.merchant_code == merchant_code). \
                filter(LogWithdraw.draw_time.between(today_before.timestamp(), today_0.timestamp())). \
                order_by(LogWithdraw.draw_time.desc(), LogWithdraw.id.desc()). \
                all()
            repay_list = db.session.query(LogRepay.id, LogRepay.repay_time.label('c_time'), LogRepay.repay_amt). \
                filter(LogRepay.merchant_code == merchant_code). \
                filter(LogRepay.repay_time.between(today_before.timestamp(), today_0.timestamp())). \
                order_by(LogRepay.repay_time.desc(), LogRepay.id.desc()). \
                all()

            # 统计次数, result是逆序的。所以需要reverse调整为时间顺序
            h = list(map(lambda x: today_0 - timedelta(days=x), range(1, 8)))
            result_list1, result_list2 = [0] * 7, [0] * 7

            cur_h, cur_lend = 0, 0
            while (cur_h < 7) and (cur_lend < len(lend_list)):
                if lend_list[cur_lend].c_time >= h[cur_h].timestamp():
                    # result_list1[cur_h] += 1  次数， 下面是金额
                    result_list1[cur_h] += lend_list[cur_lend].load_amt
                    cur_lend += 1
                else:
                    cur_h += 1

            cur_h, cur_repay = 0, 0
            while (cur_h < 7) and (cur_repay < len(repay_list)):
                if repay_list[cur_repay].c_time >= h[cur_h].timestamp():
                    # result_list2[cur_h] += 1  次数， 下面是金额
                    result_list2[cur_h] += repay_list[cur_repay].repay_amt
                    cur_repay += 1
                else:
                    cur_h += 1

            # 返回内容
            return {
                "results": [
                    {
                        "name": "放款",
                        "data": [str(i) for i in result_list1][::-1]
                    },
                    {
                        "name": "还款",
                        "data": [str(i) for i in result_list2][::-1]
                    }
                ]
            }
