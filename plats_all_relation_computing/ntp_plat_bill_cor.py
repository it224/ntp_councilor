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
collection_plat_bill = db['ntp_platform_bill_cor']
all_bill_parse_dict = {} #切好詞的bill就放裡面

    
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

def getBill(bill):
    if str(bill["_id"]) not in all_bill_parse_dict.keys():
        bill_dict = bill
        #刪除stopword
        bill_term_ckip_all = list(set(bill["description_term"]).difference(set(stopword)))
        #刪除一個字的(第一次)
        bill_term_ckip_all = removeOneTerm(bill_term_ckip_all)
        #擴張詞彙
        bill_term_ckip_all = extendWord(bill_term_ckip_all)
        #刪除stopword(第二次)
        bill_term_ckip_all = list(set(bill_term_ckip_all).difference(set(stopword)))
        #刪除一個字的(第二次)
        bill_term_ckip_all = removeOneTerm(bill_term_ckip_all)
        bill_dict["bill_term_ckip_all"] = bill_term_ckip_all
        all_bill_parse_dict[str(bill["_id"])] = bill_dict
        return bill_dict
    else:
        return all_bill_parse_dict[str(bill["_id"])]
        
def compute(plat_list, bill_list):
    # cr_dict = {}
    # cr_dict["_id"] = bill_list[0]["cr_id"]
    # cr_dict["name"] = bill_list[0]["cr_name"]
    plat_bill_list_use = []

    for plat in plat_list:
        save_dict ={}
        save_dict["plat_id"]= plat["_id"]
        save_dict["cr_id"]= plat["cr_id"]
        save_dict["name"]= plat["cr_name"]
        # all_bill_dict = {}
        bill_arr = []
        all_count = 0

        plat_terms = list(set(plat["platforms_term"]).difference(set(stopword)))
        plat_terms = removeOneTerm(plat_terms)
        plat_terms = extendWord(plat_terms)
        plat_terms = list(set(plat_terms).difference(set(stopword)))
        plat_terms = removeOneTerm(plat_terms)
        for bill in bill_list:
            bill_dict = {}
            bill_use = getBill(bill)
            bill_term_ckip_all = bill_use["bill_term_ckip_all"]

            #取交集
            interArr = list(set(bill_term_ckip_all).intersection(set(plat_terms)))
            cor_value = 0
            if(len(interArr)!=0):
                cor_value = len(interArr)/len(plat_terms)
            bill_dict["bill_id"] = bill["_id"]
            bill_dict["interWord"] = interArr
            bill_dict["cor_value"] = cor_value
            # all_bill_dict[str(bill["_id"])] = bill_dict
            bill_arr.append(bill_dict)
            all_count = all_count+cor_value
        if len(bill_arr) != 0:
            ac = all_count/len(bill_arr)
        else:
            ac = 0
        save_dict["accuracy"] = ac
        # save_dict["bill_list"]  = bill_arr
        # save_dict["all_bill_dict"] = all_bill_dict
        plat_bill_list_use.append(save_dict)
    # cr_dict["all_plat_bill_cor"] = plat_bill_list_use
    # return cr_dict
    return plat_bill_list_use

if __name__ == "__main__":
    plat_list = list(collection_cr_plat.find())
    #舊版本，只抓與該議員有關的議案 bills_list = list(collection_bills.find({"$or":[{"proposed_id" : plat["cr_id"]}, { "petitioned_id" : plat["cr_id"]}]}))
    bills_list = list(collection_bills.find())
    for plat in plat_list:
        save_dict ={}
        save_dict["_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["cr_name"]
        all_bill_dict = {}
        bill_arr = []
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

        for bill in bills_list:
            bill_dict = {}
            bill_use = getBill(bill)
            bill_term_ckip_all = bill_use["bill_term_ckip_all"]

            #取交集
            interArr = list(set(bill_term_ckip_all).intersection(set(plat_terms)))
            cor_value = 0
            if(len(interArr)!=0):
                cor_value = len(interArr)/len(plat_terms)
            bill_dict["bill_id"] = bill["_id"]
            bill_dict["interWord"] = interArr
            bill_dict["cor_value"] = cor_value
            all_bill_dict[str(bill["_id"])] = bill_dict
            bill_arr.append(bill_dict)
            all_count = all_count+cor_value
        if len(bill_arr) != 0:
            ac = all_count/len(bill_arr)
        else:
            ac = 0
        save_dict["accuracy"] = ac
        save_dict["bill_list"]  = bill_arr
        save_dict["all_bill_dict"] = all_bill_dict
        print "save_dict"
        print save_dict
        print ""
        collection_plat_bill.save(save_dict)
    print "end all"
    exit(0)