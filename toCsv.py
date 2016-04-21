# -*- coding: utf-8 -*-
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import csv
from pymongo import MongoClient
import time

client=MongoClient()
db=client['my_zhihu_data']
con=db['zhihu__user__profile']

@profile
def f():
    with open('zhihu_user_data_30k.csv',"wb") as f:
        start_time=time.time()
        csv_writer=csv.writer(f)
        csv_writer.writerow([
                    '用户名',
                    '被赞同数',
                    '被感谢数',
                    '关注了',
                    '关注者',
                    '学校',
                    '专业',
                    '公司',
                    '职位',
                    '所在地',
                    '性别',
                    '相关说明',
                    '个性签名',
                    'url'])
        for user in con.find():
            csv_writer.writerow([
                user['user_name'],
                user['user_be_agreed'],
                user['user_be_thanked'],
                user['user_followees'],
                user['user_followers'],
                user['user_education_school'],
                user['user_education_subject'],
                user['user_employment'],
                user['user_employment_extra'],
                user['user_location'],
                user['user_gender'],
                user['user_info'],
                user['user_intro'],
                user['user_url']
            ])
        print "to csv,it cost:",time.time()-start_time

if __name__=="__main__":
    f()
