#!/usr/bin/env python

# from src.main import db
import time
import datetime
from src.main import db
from src.models.audit_log import TbCreditLog
from src.models.user import (
    TbMerchantCredit, TbMerchant, TbProduction,
)


if __name__ == '__main__':
    db.create_all()
    merchant = TbMerchant()
    merchant.name = "阳泉商行"
    merchant.create_time = datetime.datetime.now()
    merchant.is_active = True
    merchant.org_no = '1111'
    merchant.code = '2222'
    db.session.add(merchant)
    db.session.commit()

    # merchant.save()
    production = TbProduction()
    production.merchant_id = merchant.id
    production.name = '泉涌贷'
    production.code = '111'
    production.status = True
    db.session.add(production)
    db.session.commit()

    merchant_credit = TbMerchantCredit()
    merchant_credit.interface = 'ZX00090001'
    merchant_credit.merchant_code = merchant.code
    merchant_credit.production_code = production.code
    merchant_credit.supplier = '阳泉商行'
    merchant_credit.product = '人行征信'
    merchant_credit.type = '人行征信'
    merchant_credit.price = 0.0
    merchant_credit.desc = '阳泉人行征信'
    merchant_credit.status = True
    merchant_credit.update_time = int(time.time())
    db.session.add(merchant_credit)
    db.session.commit()



