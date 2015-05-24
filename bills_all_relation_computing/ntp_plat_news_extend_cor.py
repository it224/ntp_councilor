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
collection_same_word = db['same_word']
collection_cr_plat = db['ntp_platform']
collection_plat_news = db['ntp_platform_news_cor']

def parseStopWord():
    json_data=open('stopword.json')
    data = json.load(json_data)
    json_data.close()
    return data

def extendWord(plat_terms):
    plat_all_words = list()
    return plat_all_words

def extendWord(terms):
    plat_all_words = list()
    for term in terms:
        term_search_results = list(collection_same_word.find({"word": term}))
        if(len(term_search_results)>0):
            for term_s_r in term_search_results[0]["sameIds"]:
                if term_s_r[1] not in plat_all_words:
                    plat_all_words.append(term_s_r[1])
                else:
                    pass
        else:
            pass
    #結束array的擴張
    print "end extend"
    return plat_all_words

def removeOneTerm(array):
    array_return = []
    for term in array:
        if len(term) > 1:
            array_return.append(term)
    return array_return

if __name__ == "__main__":
    stopword = parseStopWord()
    plat_list = collection_cr_plat.find()
    for plat in plat_list:
        save_dict ={}
        save_dict["_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["cr_name"]
        news_arr = []
        all_count = 0
        news_list = list(collection_news.find({"cr_id":plat["cr_id"]}))
        print plat["cr_name"].encode('utf-8')
        print "的新聞"
        print "news_list"
        print len(news_list)
        print ""        
        for news in news_list:
            news_dict = {}
            
            #刪除stopword            
            plat_terms = list(set(plat["platforms_term"]).difference(set(stopword)))
            news_term_ckip_all = list(set(news["story_term_ckip_all"]).difference(set(stopword)))

            #刪除一個字的(第一次)
            plat_terms = removeOneTerm(plat_terms)
            news_term_ckip_all = removeOneTerm(news_term_ckip_all)

            #擴張詞彙
            plat_terms = extendWord(plat_terms)
            bill_term_ckip_all = extendWord(bill_term_ckip_all)

            #刪除一個字的(第二次)
            plat_terms = removeOneTerm(plat_terms)
            news_term_ckip_all = removeOneTerm(news_term_ckip_all)

            interArr = list(set(news_term_ckip_all).intersection(set(plat_terms)))
            cor_value = 0
            if(len(interArr)!=0):
                cor_value = len(interArr)/len(plat_terms)
            news_dict["news"] = news
            news_dict["cor_value"] = cor_value
            news_arr.append(news_dict)
            all_count = all_count+cor_value
        if len(news_arr) != 0:
            ac = all_count/len(news_arr)
        else:
            ac = 0
        save_dict["accuracy"] = ac
        save_dict["news_list"] = news_arr
        # print save_dict
        collection_plat_news.save(save_dict)
        break
    print "end all"
    exit(0)