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
'''
news 與 platform 的分數 但是是擴張
'''

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection_news = db["ntp_news_url_list_ckip"]
collection_same_word = db['same_word_my_country']
collection_cr_plat = db['ntp_platform']
collection_plat_news = db['ntp_platform_news_cor']
all_news_parse_dict = {}


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
        if termFind.count() > 0:
            plat_all_words = list(set(plat_all_words) | set(termFind[0]["same_word"]))
    return plat_all_words

def removeOneTerm(array):
    array_return = []
    for term in array:
        if len(term) > 1:
            array_return.append(term)
    return array_return

def getNews(news):
    if str(news["_id"]) not in all_news_parse_dict.keys():
        news_dict = news
        #刪除stopword
        news_term_ckip_all = list(set(news["story_term_ckip_all"]).difference(set(stopword)))
        #刪除一個字的(第一次)
        news_term_ckip_all = removeOneTerm(news_term_ckip_all)
        #擴張詞彙
        news_term_ckip_all = extendWord(news_term_ckip_all)
        #刪除stopword(第二次)
        news_term_ckip_all = list(set(news_term_ckip_all).difference(set(stopword)))
        #刪除一個字的(第二次)
        news_term_ckip_all = removeOneTerm(news_term_ckip_all)
        news_dict["news_term_ckip_all"] = news_term_ckip_all
        all_news_parse_dict[str(news["_id"])] = news_dict
        return news_dict
    else:
        return all_news_parse_dict[str(news["_id"])]

def compute(plat_list, news_list): 
    cr_dict = {}
    cr_dict["_id"] = news_list[0]["cr_id"]
    # cr_dict["name"] = news_list[0]["cr_name"]
    plat_news_list_use = []

    for plat in plat_list:        
        save_dict ={}
        save_dict["plat_id"]= plat["_id"]
        save_dict["cr_id"]= plat["cr_id"]
        save_dict["name"]= plat["cr_name"]
        news_arr = []
        all_news_dict = {}
        all_count = 0

        plat_terms = list(set(plat["platforms_term"]).difference(set(stopword)))
        plat_terms = removeOneTerm(plat_terms)
        plat_terms = extendWord(plat_terms)
        plat_terms = list(set(plat_terms).difference(set(stopword)))
        plat_terms = removeOneTerm(plat_terms)

        for news in news_list:
            news_dict = {}
            news_use = getNews(news)
            news_term_ckip_all = news_use["news_term_ckip_all"]

            interArr = list(set(news_term_ckip_all).intersection(set(plat_terms)))
            cor_value = 0
            if(len(interArr)!=0):
                cor_value = len(interArr)/len(plat_terms)
            news_dict["news_id"] = news["_id"]
            news_dict["interWord"] = interArr
            news_dict["cor_value"] = cor_value
            news_arr.append(news_dict)
            # all_news_dict[str(news["_id"])] = news_dict
            all_count = all_count+cor_value
        if len(news_arr) != 0:
            ac = all_count/len(news_arr)
        else:
            ac = 0
        save_dict["accuracy"] = ac
        # save_dict["news_list"] = news_arr
        # save_dict["all_news_dict"] = all_news_dict
        plat_news_list_use.append(save_dict)
    # cr_dict["plat_news_list_use"] = plat_news_list_use
    # return cr_dict
    return plat_news_list_use

if __name__ == "__main__":
    plat_list = list(collection_cr_plat.find())
    #舊版方法，只找與議員有關的新聞 news_list = list(collection_news.find({"cr_id":plat["cr_id"]}))
    news_list = list(collection_news.find())
    for plat in plat_list:
        save_dict ={}
        save_dict["_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["cr_name"]
        news_arr = []
        all_news_dict = {}
        all_count = 0

        #刪除stopword          
        plat_terms = list(set(plat["platforms_term"]).difference(set(stopword)))
        #刪除一個字的(第一次)
        plat_terms = removeOneTerm(plat_terms)
        #擴張詞彙
        plat_terms = extendWord(plat_terms)
        #刪除stopword(第二次)
        plat_terms = list(set(plat_terms).difference(set(stopword)))
        #刪除一個字的(第二次)
        plat_terms = removeOneTerm(plat_terms)

        
        for news in news_list:
            news_dict = {}
            news_use = getNews(news)
            news_term_ckip_all = news_use["news_term_ckip_all"]

            interArr = list(set(news_term_ckip_all).intersection(set(plat_terms)))
            cor_value = 0
            if(len(interArr)!=0):
                cor_value = len(interArr)/len(plat_terms)
            news_dict["news_id"] = news["_id"]
            news_dict["interWord"] = interArr
            news_dict["cor_value"] = cor_value
            news_arr.append(news_dict)
            all_news_dict[str(news["_id"])] = news_dict
            all_count = all_count+cor_value
        if len(news_arr) != 0:
            ac = all_count/len(news_arr)
        else:
            ac = 0
        save_dict["accuracy"] = ac
        save_dict["news_list"] = news_arr
        save_dict["all_news_dict"] = all_news_dict
        print save_dict
        collection_plat_news.save(save_dict)
    print "end all"
    exit(0)