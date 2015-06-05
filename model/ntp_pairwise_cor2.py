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


collection_cr_plat = db['ntp_platform']
collection_plat_bill_cor      = db["ntp_platform_bill_cor"]
collection_plat_news_cor      = db['ntp_platform_news_cor']
collection_plat_bill_join_cor = db['ntp_platform_bill_join_cor']
collection_plat_news_pn_cor   = db['ntp_platform_news_pn_cor']


client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']




if __name__ == "__main__":
    plat_list = list(collection_cr_plat.find())
    plat_dic = {}
    for i, plat in enumerate(plat_list):
        plat = plat_list[i]
        if str(plat["_id"]) not in plat_dic.keys():
            plat_dic[str(plat["_id"])] = 0
#         # plat_bill_cor      = collection_plat_bill_cor.find_one({"_id":plat["_id"]})["accuracy"]
#         # plat_news_cor      = collection_plat_news_cor.find_one({"_id":plat["_id"]})["accuracy"]
#         # plat_bill_join_cor = collection_plat_bill_join_cor.find_one({"_id":plat["_id"]})["join_count"]
#         # plat_news_pn_cor   = collection_plat_news_pn_cor.find_one({"_id":plat["_id"]})["all_so_normalize"]
#         if i < len(plat_list)-1:
#             for j, plat_other in enumerate(plat_list):
#                 if i < j:
#                     major = 0
#                     compare = 0
#                     print "j :" + str(j)
#                     plat_other               = plat_list[j]
#                     plat_bill_cor_other      = collection_plat_bill_cor.find_one({"_id":plat_other["_id"]})["accuracy"]
#                     plat_news_cor_other      = collection_plat_news_cor.find_one({"_id":plat_other["_id"]})["accuracy"]
#                     plat_bill_join_cor_other = collection_plat_bill_join_cor.find_one({"_id":plat_other["_id"]})["join_count"]
#                     plat_news_pn_cor_other   = collection_plat_news_pn_cor.find_one({"_id":plat_other["_id"]})["all_so_normalize"]

#                     major = plat_bill_cor + plat_news_cor + plat_bill_join_cor + plat_news_pn_cor
#                     compare = plat_bill_cor_other + plat_news_cor_other + plat_bill_join_cor_other + plat_news_pn_cor_other
                    
#                     '''
#                     major = 0
#                     compare = 0

#                     if plat_bill_cor > plat_bill_cor_other:
#                         major = major+1
#                     else:
#                         compare = compare+1

#                     if plat_news_cor > plat_news_cor_other:
#                         major = major+1
#                     else:
#                         compare = compare+1

#                     if plat_bill_join_cor > plat_bill_join_cor_other:
#                         major = major+1
#                     else:
#                         compare = compare+1

#                     if plat_news_pn_cor > plat_news_pn_cor_other:
#                         major = major+1
#                     else:
#                         compare = compare+1
#                     '''
#                     if major > compare:
#                         dic[str(plat["_id"])] = dic[str(plat["_id"])] +1
#                     else:
#                         if str(plat_other["_id"]) not in dic.keys():
#                             dic[str(plat_other["_id"])] = 1
#                         else:
#                             dic[str(plat_other["_id"])] = dic[str(plat_other["_id"])] + 1
#     with open('data_compare_same.json', 'w') as outfile:
#         json.dump(dic, outfile)