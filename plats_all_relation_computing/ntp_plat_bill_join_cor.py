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
platform 中 bills 的參與個數
相關分數不是0就+1
最後做一次正規化    
'''

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection_plat_bill = db["ntp_platform_bill_cor"]
collection_all_bill = db["ntp_bills"]
collection_plat_bill_join = db['ntp_platform_bill_join_cor']
collection_same_word = db['same_word_my_country']
all_bill_parse_dict = {} #切好詞的bill就放裡面


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

def getBill_withID(bill_id):
    if str(bill_id) not in all_bill_parse_dict.keys():
        bill_dict = collection_all_bill.find_one({"_id":bill_id})
        #刪除stopword
        bill_term_ckip_all = list(set(bill_dict["description_term"]).difference(set(stopword)))
        #刪除一個字的(第一次)
        bill_term_ckip_all = removeOneTerm(bill_term_ckip_all)
        #擴張詞彙
        bill_term_ckip_all = extendWord(bill_term_ckip_all)
        #刪除stopword(第二次)
        bill_term_ckip_all = list(set(bill_term_ckip_all).difference(set(stopword)))
        #刪除一個字的(第二次)
        bill_term_ckip_all = removeOneTerm(bill_term_ckip_all)
        bill_dict["bill_term_ckip_all"] = bill_term_ckip_all
        all_bill_parse_dict[str(bill_id)] = bill_dict
        return bill_dict
    else:
        return all_bill_parse_dict[str(bill_id)]


if __name__ == "__main__":
    stopword = parseStopWord()
    plat_list = list(collection_plat_bill.find())
    for plat in plat_list:
        save_dict ={}
        save_dict["_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["name"]
        all_count = 0
        bill_arr = []
        all_bill_dict = {}
        bills_list = plat["bill_list"]
        for bill in bills_list:
            bill_dict = {}
            bill_use = getBill_withID(bill["bill_id"])
            bill_term_ckip_all = bill_use["bill_term_ckip_all"]
            
            #算正負面的比例
            pso_positive = len(list(set(bill_term_ckip_all).intersection(set(positive_lists))))+1 #避免為0
            nso_negative = len(list(set(bill_term_ckip_all).intersection(set(negative_lists))))+1 #避免為0

            #算比例
            so = math.log(pso_positive/nso_negative)
            so = so *bill["cor_value"]

            bill_dict["bill_id"] = bill["_id"]
            bill_dict["np_cor_value"] = so
            all_bill_dict[str(bill["_id"])] = bill_dict
            bill_arr.append(bill_dict)

            all_count = all_count+so

        if all_count != 0:
            join_count = all_count/len(bills_list)
        else:
            join_count = 0
        save_dict["join_count"] = join_count
        save_dict["bill_list"]  = bill_arr
        save_dict["all_bill_dict"]  = all_bill_dict
        print save_dict
        collection_plat_bill_join.save(save_dict)
    print "end all"
    exit(0)