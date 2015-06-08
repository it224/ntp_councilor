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
'''

client = MongoClient('mongodb://localhost:27017/')

db = client['ntp_councilor']

collection_cr_plat = db['ntp_platform']
collection_cr_for_all_plats   = db['ntp_crs_compare']


if __name__ == "__main__":
    plat_list = list(collection_cr_plat.find())
    dic = {}
    for i, plat in enumerate(plat_list):
        print "i :"+str(i)
        plat = plat_list[i]
        if str(plat["_id"]) not in dic.keys():
            dic[str(plat["_id"])] = 0
        if i < len(plat_list)-1:
            for j, plat_other in enumerate(plat_list):
                if i < j:
                    major = 0
                    compare = 0
                    print "j :" + str(j)
                    plat_other = plat_list[j]
                    
                    plat_cr = str(plat["cr_id"])
                    plat_other_cr = str(plat_other["cr_id"])

                    if plat_cr == plat_other_cr:
                        cr_compare = collection_cr_for_all_plats.find_one({"cr_id":plat["cr_id"]})
                        
                        major_bill_cor =        cr_compare["cr_plat_bill_cor_list"][i]["accuracy"]
                        major_news_cor =        cr_compare["cr_plat_news_cor_list"][i]["accuracy"]
                        major_bill_join_cor =   cr_compare["cr_plat_bill_join_cor_list"][i]["join_count"]
                        major_news_pn_cor =     cr_compare["cr_plat_news_pn_cor_list"][i]["join_count"]

                        compare_bill_cor =      cr_compare["cr_plat_bill_cor_list"][j]["accuracy"]
                        compare_news_cor =      cr_compare["cr_plat_news_cor_list"][j]["accuracy"]
                        compare_bill_join_cor = cr_compare["cr_plat_bill_join_cor_list"][j]["join_count"]
                        compare_news_pn_cor =   cr_compare["cr_plat_news_pn_cor_list"][j]["join_count"]                        
                    else:
                        cr_compare_major = collection_cr_for_all_plats.find_one({"cr_id":plat["cr_id"]})
                        cr_compare_compare = collection_cr_for_all_plats.find_one({"cr_id":plat_other["cr_id"]})
                        
                        major_bill_cor =        cr_compare_major["cr_plat_bill_cor_list"][i]["accuracy"]     +cr_compare_compare["cr_plat_bill_cor_list"][i]["accuracy"]     
                        major_news_cor =        cr_compare_major["cr_plat_news_cor_list"][i]["accuracy"]     +cr_compare_compare["cr_plat_news_cor_list"][i]["accuracy"]     
                        major_bill_join_cor =   cr_compare_major["cr_plat_bill_join_cor_list"][i]["join_count"]+cr_compare_compare["cr_plat_bill_join_cor_list"][i]["join_count"]
                        major_news_pn_cor =     cr_compare_major["cr_plat_news_pn_cor_list"][i]["join_count"]      +cr_compare_compare["cr_plat_news_pn_cor_list"][i]["join_count"]      

                        compare_bill_cor =      cr_compare_major["cr_plat_bill_cor_list"][j]["accuracy"]     +cr_compare_compare["cr_plat_bill_cor_list"][j]["accuracy"]     
                        compare_news_cor =      cr_compare_major["cr_plat_news_cor_list"][j]["accuracy"]     +cr_compare_compare["cr_plat_news_cor_list"][j]["accuracy"]     
                        compare_bill_join_cor = cr_compare_major["cr_plat_bill_join_cor_list"][j]["join_count"]+cr_compare_compare["cr_plat_bill_join_cor_list"][j]["join_count"]
                        compare_news_pn_cor =   cr_compare_major["cr_plat_news_pn_cor_list"][j]["join_count"]      +cr_compare_compare["cr_plat_news_pn_cor_list"][j]["join_count"]      

                    major = major_bill_cor + major_news_cor + major_bill_join_cor + major_news_pn_cor
                    compare = compare_bill_cor + compare_news_cor + compare_bill_join_cor + compare_news_pn_cor


                    if major > compare:
                        dic[str(plat["_id"])] = dic[str(plat["_id"])] +1
                    else:
                        if str(plat_other["_id"]) not in dic.keys():
                            dic[str(plat_other["_id"])] = 1
                        else:
                            dic[str(plat_other["_id"])] = dic[str(plat_other["_id"])] + 1
    with open('data_compare_same.json', 'w') as outfile:
        json.dump(dic, outfile)