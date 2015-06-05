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
platform 中 news 正負面的比例
每一篇的正負面都與新聞政見的關聯度相乘
正負面的程度每個全部都有做正規化
正規化的方式是找Upper bound 也就是正面的len取log
求出來的分數 (value + U)/2U

後相加在做正規化
結果為 plat 有議員的 news 的正負面* news的相關度
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

if __name__ == "__main__":
    stopword = parseStopWord()
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