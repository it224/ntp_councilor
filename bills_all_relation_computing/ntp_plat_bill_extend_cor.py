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
bill 與 platform 的分數 但是擴張詞彙
'''

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection_bills = db["ntp_bills"]
collection_cr_plat = db['ntp_platform']
collection_same_word = db['same_word_my_country']
collection_plat_bill = db['ntp_platform_bill_extend_cor']
    
def parseStopWord():
    json_data=open('stopword.json')
    data = json.load(json_data)
    json_data.close()
    return data

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

if __name__ == "__main__":
    stopword = parseStopWord()
    plat_list = collection_cr_plat.find()
    for plat in plat_list:
        save_dict ={}
        save_dict["_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["cr_name"]
        bill_arr = []
        all_count = 0
        bills_list = list(collection_bills.find({"$or":[{"proposed_id" : plat["cr_id"]}, { "petitioned_id" : plat["cr_id"]}]}))
        for bill in bills_list:
            bill_dict = {}
            
            #刪除stopword            
            plat_terms = list(set(plat["platforms_term"]).difference(set(stopword)))
            bill_term_ckip_all = list(set(bill["description_term"]).difference(set(stopword)))

            #刪除一個字的(第一次)
            plat_terms = removeOneTerm(plat_terms)
            news_term_ckip_all = removeOneTerm(news_term_ckip_all)

            #擴張詞彙
            plat_terms = extendWord(plat_terms)
            bill_term_ckip_all = extendWord(bill_term_ckip_all)

            #刪除一個字的(第二次)
            plat_terms = removeOneTerm(plat_terms)
            bill_term_ckip_all = removeOneTerm(bill_term_ckip_all)

            #取交集
            interArr = list(set(bill_term_ckip_all).intersection(set(plat_terms)))
            cor_value = 0
            if(len(interArr)!=0):
                cor_value = len(interArr)/len(plat_terms)
            bill_dict["bill"] = bill
            bill_dict["cor_value"] = cor_value
            bill_arr.append(bill_dict)
            all_count = all_count+cor_value
        if len(bill_arr) != 0:
            ac = all_count/len(bill_arr)
        else:
            ac = 0
        save_dict["accuracy"] = ac
        save_dict["bill_list"] = bill_arr
        print "save_dict"
        print save_dict
        print ""
        collection_plat_bill.save(save_dict)
    print "end all"
    exit(0)