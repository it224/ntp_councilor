#encoding=utf-8
'''
FUZZY TOPSIS model
四個attribute
'''
from __future__ import division
import re
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

class mongoConnect(object):
    """docstring for mongoConnect"""
    def __init__(self, arg):
        super(mongoConnect, self).__init__()
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = client['ntp_councilor']
        self.c_plats         = self.db[arg.c_plats_name]                    #所有政見638筆  ntp_crs
        self.c_plat_bill_cor = self.db[arg.c_plat_bill_cor_name]            #政見議案關係   ntp_platform_bill_cor
        self.c_plat_news_cor = self.db[arg.c_plat_news_cor_name]            #政見新聞關係   ntp_news_plat_cor
        self.c_news_pn       = self.db[arg.c_news_position_negative_name]   #政見新聞正負面  ntp_platform_bill_pn_cor
        self.c_join_bills    = self.db[arg.c_join_bills_name]               #政見議案參與數  ntp_news_bill_join_cor
        self.weight_fuzzy_list = [{"VL":[0.0, 0.0, 0.1]}, {"L":[0, 0.1, 0.3]}, {"ML":[0.1, 0.3, 0.5]}, {"M":[0.3, 0.5, 0.7]}, {"MH":[0.5, 0.7, .0.9]}, {"H":[0.7, 0.9, 1.0]}, {"VH":[0.9, 1.0, 1.0]}]
    def make_martix():
        #638個排名
        all_plats        = list(self.c_plats.find({}, {"_id":1, "cr_id":1, "plat_origin":1, "name":1 }))
        #4個屬性
        plat_bill_cor    = list(self.c_plat_bill_cor.find({}, {"_id":1, "cr_id":1, "name":1, "accuracy":1 }))
        plat_news_cor    = list(self.c_plat_news_cor.find({}, {"_id":1, "cr_id":1, "cr":1, "accuracy":1 }))
        news_p_n         = list(self.c_news_pn.find({}, {"_id":1, "cr_id":1, "name":1, "pos_value":1}))
        join_bills        = list(self.c_joy_bills.find({}, {"_id":1, "cr_id":1, "name":1, "join_value":1}))



if __name__ == '__main__':
    