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
collection_plat_bill_cor      = db["ntp_platform_bill_extend_cor"]
collection_plat_news_cor      = db['ntp_platform_news_extend_cor']
collection_plat_bill_join_cor = db['ntp_platform_bill_join_extend_cor']
collection_plat_news_pn_cor   = db['ntp_platform_news_pn_extend_cor']

collection_plat_pairwise_sort   = db['ntp_platform_PAIRWISE_extend_sort']




def compaire(idOne, idTwo):
    plat_bill_cor      = collection_plat_bill_cor.find_one({"_id":ObjectId(idOne)})["accuracy"]
    plat_news_cor      = collection_plat_news_cor.find_one({"_id":ObjectId(idOne)})["accuracy"]
    plat_bill_join_cor = collection_plat_bill_join_cor.find_one({"_id":ObjectId(idOne)})["join_count"]
    plat_news_pn_cor   = collection_plat_news_pn_cor.find_one({"_id":ObjectId(idOne)})["all_so_normalize"]


    plat_bill_cor_other      = collection_plat_bill_cor.find_one({"_id":ObjectId(idTwo)})["accuracy"]
    plat_news_cor_other      = collection_plat_news_cor.find_one({"_id":ObjectId(idTwo)})["accuracy"]
    plat_bill_join_cor_other = collection_plat_bill_join_cor.find_one({"_id":ObjectId(idTwo)})["join_count"]
    plat_news_pn_cor_other   = collection_plat_news_pn_cor.find_one({"_id":ObjectId(idTwo)})["all_so_normalize"]

    major = 0
    compare = 0

    major = plat_bill_cor + plat_news_cor + plat_bill_join_cor + plat_news_pn_cor
    compare = plat_bill_cor_other + plat_news_cor_other + plat_bill_join_cor_other + plat_news_pn_cor_other

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
            
                    


        