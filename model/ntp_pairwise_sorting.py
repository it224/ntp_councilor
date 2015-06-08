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
platform 中 pairwise 的排序
分數一樣的比排名
'''

client = MongoClient('mongodb://localhost:27017/')

db = client['ntp_councilor']

collection_cr_plat = db['ntp_platform']
collection_cr_for_all_plats   = db['ntp_crs_compare']
collection_plat_pairwise_sort   = db['ntp_platform_PAIRWISE_sort']




def compaire(idOne, idTwo):
    major = 0
    compare = 0

    plat = collection_cr_plat.find_one({"_id":ObjectId(idOne)})
    plat_other = collection_cr_plat.find_one({"_id":ObjectId(idTwo)})

    plat_cr = str(plat["cr_id"])
    plat_other_cr = str(plat_other["cr_id"])

    if plat_cr == plat_other_cr:
        cr_compare = collection_cr_for_all_plats.find_one({"cr_id":plat["cr_id"]})
        
        major_bill_cor =        cr_compare["cr_plat_bill_cor_list"][i]["accuracy"]
        major_news_cor =        cr_compare["cr_plat_news_cor_list"][i]["accuracy"]
        major_bill_join_cor =   cr_compare["cr_plat_bill_join_cor_list"][i]["join_cor"]
        major_news_pn_cor =     cr_compare["cr_plat_news_pn_list"][i]["join_cor"]

        compare_bill_cor =      cr_compare["cr_plat_bill_cor_list"][j]["accuracy"]
        compare_news_cor =      cr_compare["cr_plat_news_cor_list"][j]["accuracy"]
        compare_bill_join_cor = cr_compare["cr_plat_bill_join_cor_list"][j]["join_cor"]
        compare_news_pn_cor =   cr_compare["cr_plat_news_pn_list"][j]["join_cor"]                        
    else:
        cr_compare_major = collection_cr_for_all_plats.find_one({"cr_id":plat["cr_id"]})
        cr_compare_compare = collection_cr_for_all_plats.find_one({"cr_id":plat_other["cr_id"]})
        
        major_bill_cor =        cr_compare_major["cr_plat_bill_cor_list"][i]["accuracy"]     +cr_compare_compare["cr_plat_bill_cor_list"][i]["accuracy"]     
        major_news_cor =        cr_compare_major["cr_plat_news_cor_list"][i]["accuracy"]     +cr_compare_compare["cr_plat_news_cor_list"][i]["accuracy"]     
        major_bill_join_cor =   cr_compare_major["cr_plat_bill_join_cor_list"][i]["join_cor"]+cr_compare_compare["cr_plat_bill_join_cor_list"][i]["join_cor"]
        major_news_pn_cor =     cr_compare_major["cr_plat_news_pn_list"][i]["join_cor"]      +cr_compare_compare["cr_plat_news_pn_list"][i]["join_cor"]      

        compare_bill_cor =      cr_compare_major["cr_plat_bill_cor_list"][j]["accuracy"]     +cr_compare_compare["cr_plat_bill_cor_list"][j]["accuracy"]     
        compare_news_cor =      cr_compare_major["cr_plat_news_cor_list"][j]["accuracy"]     +cr_compare_compare["cr_plat_news_cor_list"][j]["accuracy"]     
        compare_bill_join_cor = cr_compare_major["cr_plat_bill_join_cor_list"][j]["join_cor"]+cr_compare_compare["cr_plat_bill_join_cor_list"][j]["join_cor"]
        compare_news_pn_cor =   cr_compare_major["cr_plat_news_pn_list"][j]["join_cor"]      +cr_compare_compare["cr_plat_news_pn_list"][j]["join_cor"]      

    major = major_bill_cor + major_news_cor + major_bill_join_cor + major_news_pn_cor
    compare = compare_bill_cor + compare_news_cor + compare_bill_join_cor + compare_news_pn_cor

    if major > compare:
        return "idOneBig"
    else:
        return "idTwoBig"


if __name__ == "__main__":

    with open("data_compare_same.json") as json_file:
        json_data = json.load(json_file)
        dic = json_data
        dic = sorted(dic.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        sort_list = []
        for i in range(0, len(dic), 1):
            onekey = dic[i][0]
            onevalue = dic[i][1]
            dic_use = {"_id":ObjectId(onekey), "value": onevalue}
            if dic_use not in sort_list:
                sort_list.append(dic_use)
            if i < len(dic)-1 :
                twokey = dic[i+1][0]
                twovalue = dic[i+1][1]
                if onevalue == twovalue:
                    result = compaire(onekey, twokey)
                    if result is "idTwoBig":
                        dic_other = {"_id":ObjectId(twokey), "value": dic[i+1][1]}
                        sort_list.insert(i, dic_other)
        

        for i, dic in enumerate(sort_list):
            dic["sort"] = i+1
        for dic in sort_list:
            print dic
            print collection_plat_pairwise_sort.save(dic)
            print ""
            
                    


        