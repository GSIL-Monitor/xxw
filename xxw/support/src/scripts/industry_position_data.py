# coding=utf-8
from datetime import datetime

import pymongo
import xlrd

client = pymongo.MongoClient('mongodb://115.159.112.97:27017')
db_name = 'support'
db = client[db_name]
collection_set01 = db['support_industry_position']

# 文件中的中文转码
data = xlrd.open_workbook('../../industry_position.xlsx')
# 获取数据
table = data.sheet_by_name('Sheet1')
# 获取sheet
nrows = table.nrows
# 获取总行数
ncols = table.ncols
# 获取总列数


sheet1 = data.sheet_by_index(0)
idx = sheet1.row_values(0)
datas = []
for i in range(1, nrows):
    row_data = table.row_values(i)
    row_data_dict = {}
    # 遍历行数据的每一项，赋值进行数据字典
    for j in range(len(row_data)):
        item = row_data[j]
        row_data_dict[idx[j]] = item
    # 将行数据字典加入到datas列表中
    row_data_dict["rank"] = str(row_data_dict["rank"])
    row_data_dict["position_code"] = str(row_data_dict["position_code"]).split('.')[0]
    row_data_dict["create_time"] = int(datetime.utcnow().timestamp())
    row_data_dict['update_time'] = int(datetime.utcnow().timestamp())
    datas.append(row_data_dict)

try:
    for data in datas:
        collection_set01.save(data)
except Exception as e:
    print(e)
