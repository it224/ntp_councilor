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
from import_file import import_file



'''
platform 中 pairwise 的比較
   :1
:2  2 :2
:3  1  2 :3
:4  1  2  3 :4
:5  5  5  5  5 :5

每個對比 最後算
altern 1 2 3 4 5
value  2 3 1 0 4 次



比法一樣是四個attribute比
但是算法不同
情況有兩種
1. 議員甲的
    政見AB對比時
    只抓取議員甲的新聞與議案
    計算四個attribute的值總和來對打
2. 議員甲乙的
    政見AB對比時
    抓取議員甲乙的新聞與議案作為subset
    只用這個subset來計算四個attribute的值總和來對打
'''

client = MongoClient('mongodb://localhost:27017/')
db                            = client['ntp_councilor']
collection_crs                = db['ntp_crs']
collection_cr_plat            = db['ntp_platform']
collection_bill               = db['ntp_bills']
collection_news               = db['ntp_news_url_list_ckip']
collection_plat_bill_cor      = db["ntp_platform_bill_cor"]
collection_plat_news_cor      = db["ntp_platform_news_cor"]

collection_cr_for_all_plats   = db['ntp_crs_compare']

plat_bill_cor                 = import_file("../plats_all_relation_computing/ntp_plat_bill_cor.py")
plat_news_cor                 = import_file("../plats_all_relation_computing/ntp_plat_news_cor.py")
plat_bill_join_cor            = import_file("../plats_all_relation_computing/ntp_plat_bill_join_cor.py")
plat_news_pn_cor              = import_file("../plats_all_relation_computing/ntp_plat_news_pn_cor.py") 

crs = list(collection_crs.find())
plat_list = list(collection_cr_plat.find())
cr_plat_bill_list_cor = list(collection_plat_bill_cor.find())
cr_plat_news_list_cor = list(collection_plat_news_cor.find())
count = 0
for cr in crs:    
    cr_dict = {}
    cr_id = cr["_id"]
    cr_name = cr["name"]
    cr_dict["cr_id"] = cr_id
    cr_dict["cr_name"] = cr_name

    bill_list = list(collection_bill.find({"$or":[{"proposed_id" : cr_id}, { "petitioned_id" : cr_id}]}))
    news_list = list(collection_news.find({"cr_id": cr_id}))

    cr_plat_bill_cor_list        = plat_bill_cor.compute(plat_list, bill_list) 
    cr_plat_news_cor_list        = plat_news_cor.compute(plat_list, news_list)
    cr_plat_bill_join_cor_list   = plat_bill_join_cor.compute(cr_id, cr_name, cr_plat_bill_list_cor, bill_list)
    cr_plat_news_pn_cor_list     = plat_news_pn_cor.compute(cr_id, cr_name, cr_plat_news_list_cor, news_list)

    cr_dict["cr_plat_bill_cor_list"] = cr_plat_bill_cor_list
    cr_dict["cr_plat_news_cor_list"] = cr_plat_news_cor_list
    cr_dict["cr_plat_bill_join_cor_list"] = cr_plat_bill_join_cor_list
    cr_dict["cr_plat_news_pn_cor_list"] = cr_plat_news_pn_cor_list

    print collection_cr_for_all_plats.save(cr_dict)