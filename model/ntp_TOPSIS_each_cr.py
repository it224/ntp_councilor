#encoding=utf-8
from __future__ import division
import re
import os
import sys
import jieba
import jieba.posseg as pseg
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import math
'''
cr 對所有plat的影響 其topsis的分數
'''

client = MongoClient('mongodb://localhost:27017/')

db = client['ntp_councilor']
collection_crs     = db['ntp_crs']

collection_bill_cor = db['ntp_platform_bill_cor']
collection_news_cor = db['ntp_platform_news_cor']
collection_bill_join_cor = db['ntp_platform_bill_join_cor']
collection_news_pn_cor = db['ntp_platform_news_pn_cor']

if __name__ == "__main__":
    crs = list(collection_crs.find())
    plats_bill_cor = list(collection_bill_cor.find())
    plats_news_cor = list(collection_news_cor.find())
    plats_bill_join_cor = list(collection_bill_join_cor.find())
    plats_news_pn_cor = list(collection_news_pn_cor.find())

    for cr in crs:
        cr_dict = {}
        cr_id = cr["_id"]
        cr_name = cr["name"]
        cr_dict["cr_id"] = cr_id
        cr_dict["cr_name"] = cr_name

        bill_list = list(collection_bill.find({"$or":[{"proposed_id" : cr_id}, { "petitioned_id" : cr_id}]}, {"_id":1}))
        news_list = list(collection_news.find({"cr_id": cr_id}, {"_id":1}))

        for i in range(0, 638, 1): #0~637
            all_bill_dict = plats_bill_cor[i]["all_bill_dict"]
            all_news_dict = plats_news_cor[i]["all_news_dict"]
            all_bill_cor_dict = plats_bill_join_cor[i]["all_bill_dict"]
            all_news_cor_dict = plats_news_pn_cor[i]["all_news_dict"]

            bill_value = 0
            bill_join_value = 0
            for bill_id in bill_list:
                bill_value      = bill_value + all_bill_dict[str(bill_id)]["cor_value"]
                bill_join_value = bill_join_value + all_bill_cor_dict[str(bill_id)]["np_cor_value"]
            
            news_value = 0
            news_pn_value = 0
            for news_id in news_list:
                news_value    = news_value + all_news_dict[str(news_id)]["cor_value"]
                news_pn_value = news_pn_value + all_news_cor_dict[str(news_id)]["np_cor_value"]
