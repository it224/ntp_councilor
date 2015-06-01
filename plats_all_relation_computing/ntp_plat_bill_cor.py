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
bill 與 platform 的分數
'''

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection_bills = db["ntp_bills"]
collection_cr_plat = db['ntp_platform']
collection_plat_bill = db['ntp_platform_bill_cor']

def parseStopWord():
    json_data=open('stopword.json')
    data = json.load(json_data)
    json_data.close()
    return data

def removeOneTerm(array):
    array_return = []
    for term in array:
        if len(term) > 1:
            array_return.append(term)
    return array_return

if __name__ == "__main__":
    stopword = parseStopWord()
    plat_list = list(collection_cr_plat.find())
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

            #刪除一個字的
            plat_terms = removeOneTerm(plat_terms)
            bill_term_ckip_all = removeOneTerm(bill_term_ckip_all)

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
        print save_dict
        collection_plat_bill.save(save_dict)
    print "end all"
    exit(0)