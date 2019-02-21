from src.main import db
from src.models.log_db import *
from src.models.manager import *
import time

import decimal
import random
from random import randint


def mock_some_data():
    """创建一些测试数据"""
    from faker import Faker
    fake = Faker('zh-CN')
    print('开始生成数据')

    for i in range(1000):
        log_withdraw = LogWithdraw()
        log_withdraw.wx_openid = 'wx_openid'
        log_withdraw.wx_unionid = '06_jfiefjiejfiejfiejfie_ve'
        log_withdraw.channel = '渠道1'
        log_withdraw.sub_channel = '子渠道1'
        log_withdraw.merchant_code = "0000000" + str(random.randint(1, 9))
        log_withdraw.production_code = randint(1, 9)
        log_withdraw.manager_id = randint(1, 100)
        log_withdraw.uin = randint(1, 1000)
        log_withdraw.phone = fake.phone_number()
        log_withdraw.location = fake.address()
        log_withdraw.name = fake.name()

        d = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        ts = int(d.timestamp())

        log_withdraw.draw_time = ts
        log_withdraw.bank_card_no = fake.credit_card_number(card_type=None)
        log_withdraw.load_amt = float(decimal.Decimal(random.randrange(1000000, 9999999) / 100))
        log_withdraw.load_terms = random.randint(1, 12)
        log_withdraw.load_rate = 0.00005
        log_withdraw.load_method = random.randint(1, 3)
        log_withdraw.result = random.randint(0, 1)
        db.session.add(log_withdraw)
    db.session.commit()

    for i in range(1000):
        log_repay = LogRepay()
        log_repay.wx_openid = 'wx_openid'
        log_repay.wx_unionid = '06_jfiefjiejfiejfiejfie_ve'
        log_repay.channel = '渠道1'
        log_repay.sub_channel = '子渠道1'
        log_repay.merchant_code = "0000000" + str(random.randint(1, 9))
        log_repay.production_code = randint(1, 9)
        log_repay.manager_id = randint(1, 100)
        log_repay.name = fake.name()
        log_repay.uin = randint(1, 1000)
        log_repay.phone = fake.phone_number()
        log_repay.location = fake.address()

        d = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        ts = int(d.timestamp())

        log_repay.repay_time = ts
        log_repay.bank_card_no = fake.credit_card_number(card_type=None)
        log_repay.repay_amt = float(decimal.Decimal(random.randrange(1000000, 9999999) / 100))
        log_repay.repay_method = random.randint(0, 5)
        db.session.add(log_repay)
    db.session.commit()

    for i in range(1000):
        log_credit = LogCredit()
        log_credit.wx_openid = 'wx_openid'
        log_credit.wx_unionid = '06_jfiefjiejfiejfiejfie_ve'
        log_credit.channel = '渠道1'
        log_credit.sub_channel = '子渠道1'
        log_credit.merchant_code = "0000000" + str(random.randint(1, 9))
        log_credit.production_code = randint(1, 9)
        log_credit.manager_id = randint(1, 100)
        log_credit.uin = randint(1, 1000)
        log_credit.phone = fake.phone_number()
        log_credit.location = fake.address()

        d = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        ts = int(d.timestamp())

        log_credit.credit_time = ts
        log_credit.credit_amt = float(decimal.Decimal(random.randrange(1000000, 9999999) / 100))
        log_credit.result = random.randint(0, 5)
        db.session.add(log_credit)
    db.session.commit()

    for i in range(1000):
        if i % 100 == 0:
            print("processing " + str(i / 10) + "%")
        log_register = LogRegister()
        log_register.wx_openid = 'wx_openid'
        log_register.wx_unionid = '06_jfiefjiejfiejfiejfie_ve'
        log_register.channel = '渠道1'
        log_register.sub_channel = '子渠道1'
        log_register.merchant_code = "0000000" + str(random.randint(1, 9))
        log_register.production_code = randint(1, 9)
        log_register.manager_id = randint(1, 100)
        log_register.uin = randint(1, 1000)
        log_register.phone = fake.phone_number()
        log_register.location = fake.address()

        d = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        ts = int(d.timestamp())

        log_register.reg_time = ts
        log_register.result = random.randint(0, 5)
        db.session.add(log_register)
    db.session.commit()

    for i in range(1000):
        if i % 100 == 0:
            print("processing " + str(i / 10) + "%")
        log_loading = LogLoading()
        log_loading.wx_openid = 'wx_openid'
        log_loading.wx_unionid = '06_jfiefjiejfiejfiejfie_ve'
        log_loading.channel = '渠道1'
        log_loading.sub_channel = '子渠道1'
        log_loading.merchant_code = "0000000" + str(random.randint(1, 9))
        log_loading.production_code = randint(1, 9)
        log_loading.manager_id = randint(1, 100)
        log_loading.location = fake.address()

        d = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        ts = int(d.timestamp())

        log_loading.load_time = ts
        log_loading.result = random.randint(0, 5)
        db.session.add(log_loading)
    db.session.commit()

    print("生成数据结束")


def mock_manager_data():
    for i in range(1000):
        from faker import Faker
        fake = Faker('zh-CN')

        manager = TbManager()
        manager.name = fake.name()
        manager.merchant_code = "0000000" + str(random.randint(1, 9))
        manager.head_img = "https://www.google.com.hk/images/branding/googlelogo/2x/googlelogo_color_120x44dp.png"
        manager.id_img = "https://www.google.com.hk/images/branding/googlelogo/2x/googlelogo_color_120x44dp.png"
        manager.id_img_back = "https://www.google.com.hk/images/branding/googlelogo/2x/googlelogo_color_120x44dp.png"
        manager.user_code = 1
        manager.phone = fake.phone_number()
        manager.id_card = fake.ssn(min_age=18, max_age=90)

        d = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        ts = int(d.timestamp())

        manager.create_time = ts
        manager.update_time = ts
        db.session.add(manager)
    db.session.commit()
