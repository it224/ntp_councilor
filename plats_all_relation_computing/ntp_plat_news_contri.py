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
議員對 platform 的貢獻比之全議會對 platform 的貢獻在百分之幾，建立在news之上
'''

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection_news = db["ntp_platform_news_cor"]
collection_all_news = db["ntp_news_url_list_ckip"]
collection_plat_news_pn = db['ntp_platform_news_pn_cor']
collection_same_word = db['same_word_my_country']
all_news_parse_dict = {}

def returnFile(path):
    content_use = list()
    with open("./ntusd/ntusd-"+path+".txt") as f:
        content = f.readlines()
    for word in content:
        content_use.append(word.decode('utf-8').split('\n')[0])
    return content_use

positive_lists = returnFile("positive")
negative_lists = returnFile("negative")

def parseStopWord():
    json_data=open('stopword.json')
    data = json.load(json_data)
    json_data.close()
    return data

stopword = parseStopWord()

def extendWord(plat_terms):
    plat_all_words = plat_terms
    for term in plat_terms:
        termFind = collection_same_word.find({"word":term})
        try:
            if termFind.count() > 0:
                plat_all_words = list(set(plat_all_words) | set(termFind[0]["same_word"]))
        except Exception, e:
            print e
            raise
    return plat_all_words

def removeOneTerm(array):
    array_return = []
    for term in array:
        if len(term) > 1:
            array_return.append(term)
    return array_return

def getNews_withID(news_id):
    if str(news_id) not in all_news_parse_dict.keys():
        news_dict = collection_all_news.find_one({"_id":news_id})
        #刪除stopword
        news_term_ckip_all = list(set(news_dict["story_term_ckip_all"]).difference(set(stopword)))
        #刪除一個字的(第一次)
        news_term_ckip_all = removeOneTerm(news_term_ckip_all)
        #擴張詞彙
        news_term_ckip_all = extendWord(news_term_ckip_all)
        #刪除stopword(第二次)
        news_term_ckip_all = list(set(news_term_ckip_all).difference(set(stopword)))
        #刪除一個字的(第二次)
        news_term_ckip_all = removeOneTerm(news_term_ckip_all)
        news_dict["news_term_ckip_all"] = news_term_ckip_all
        all_news_parse_dict[str(news_dict["_id"])] = news_dict
        return news_dict
    else:
        return all_news_parse_dict[str(news_id)]

def compute(cr_id, cr_name, plat_news_list_cor, news_list):
    #plat_bill_list全部是同一個cr的
    # cr_dict = {}
    # cr_dict["_id"] = str(cr_id)
    # cr_dict["name"] = cr_name
    plat_news_list_use = []

    for index, plat in enumerate(plat_news_list_cor):
        all_news_dict = plat["all_news_dict"]
        save_dict ={}
        save_dict["plat_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["name"]
        all_count = 0
        news_arr = []

        for news in news_list:
            news_dict = {}
            news_use = getNews_withID(news["_id"])
            news_term_ckip_all = news_use["news_term_ckip_all"]

            #算正負面的比例
            pso_positive = len(list(set(news_term_ckip_all).intersection(set(positive_lists))))+1 #避免為0
            nso_negative = len(list(set(news_term_ckip_all).intersection(set(negative_lists))))+1 #避免為0

            #算比例
            so = math.log(pso_positive/nso_negative)
            so = so *all_news_dict[str(news["_id"])]["cor_value"]

            news_dict["news_id"] = news["_id"]
            news_dict["np_cor_value"] = so
            news_arr.append(news_dict)

            all_count = all_count+so
        if all_count != 0:
            join_count = all_count/len(news_list)
        else:
            join_count = 0
        save_dict["join_count"] = join_count
        # save_dict["news_list"]  = news_arr
        plat_news_list_use.append(save_dict)
    # cr_dict["plat_news_list_use"] = plat_news_list_use
    return plat_news_list_use

if __name__ == "__main__":
    
    plat_news_list = list(collection_news.find())
    for plat_news in plat_news_list:
        save_dict ={}
        save_dict["_id"]=plat_news["_id"]
        save_dict["cr_id"]=plat_news["cr_id"]
        save_dict["name"]=plat_news["name"]
        news_arr = []
        all_news_dict = {}
        all_count = 0
        news_list = list(plat_news["news_list"])
        for news in news_list:
            news_dict = {}
            news_cor_value = news["cor_value"]
            news_id = news["news_id"]
            news_use = getNews_withID(news_id)
            news_term_ckip_all = news_use["news_term_ckip_all"]
            
            #算正負面的比例
            pso_positive = len(list(set(news_term_ckip_all).intersection(set(positive_lists))))+1 #避免為0
            nso_negative = len(list(set(news_term_ckip_all).intersection(set(negative_lists))))+1 #避免為0
            
            #算比例
            so = math.log(pso_positive/nso_negative)
            so = so *news_cor_value
            
            news_dict["news_id"] = news["news_id"]
            news_dict["np_cor_value"] = so
            news_arr.append(news_dict)
            all_news_dict[str(news["news_id"])] = news_dict
            all_count = all_count+so
                    
        if len(news_arr) != 0:
            ac = all_count/len(news_arr)
        else:
            ac = 0
        save_dict["all_so_normalize"] = ac
        save_dict["all_so"] = all_count
        save_dict["news_list"] = news_arr
        save_dict["all_news_dict"] = all_news_dict
        collection_plat_news_pn.save(save_dict)
    print "end all"
    exit(0)