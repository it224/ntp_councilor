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
collection_crs       = db["ntp_crs"]
collection_plat_bill = db["ntp_platform_bill_cor"]
collection_bills =  db["ntp_bills"]
# collection_plat_bill_join = db['ntp_platform_bill_join_cor']
# collection_same_word = db['same_word_my_country']
# all_bill_parse_dict = {} #切好詞的bill就放裡面


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

def compute(cr_id, cr_name, plat_bill_list_cor, bill_list): #所有政見, plat_bill_list_cor 中的 all_bill_dict 中有 cr 對該政見的相關分數, bill_list 為 cr 參與的所有議案
    '''
        所有政見，計算每個議員對其政見的貢獻（不是只有提出政見的議員）
    '''
    # cr_dict = {}
    # cr_dict["_id"] = cr_id
    # cr_dict["name"] = cr_name
    plat_bill_list_use = []

    for index, plat in enumerate(plat_bill_list_cor):
        cr_all_bill_dict = plat["all_bill_dict"]
        save_dict ={}
        save_dict["plat_id"]= plat["_id"]
        save_dict["cr_id"]= plat["cr_id"]
        save_dict["name"]=plat["name"]
        all_count = 0
        bill_arr = []

        for bill in bill_list:
            bill_dict = {}
            bill_use = getBill_withID(bill["_id"])
            bill_term_ckip_all = bill_use["bill_term_ckip_all"]

            #算正負面的比例
            pso_positive = len(list(set(bill_term_ckip_all).intersection(set(positive_lists))))+1 #避免為0
            nso_negative = len(list(set(bill_term_ckip_all).intersection(set(negative_lists))))+1 #避免為0

            #算比例
            so = math.log(pso_positive/nso_negative)
            so = so *cr_all_bill_dict[str(bill["_id"])]["cor_value"]

            bill_dict["bill_id"] = bill["_id"]
            bill_dict["np_cor_value"] = so
            bill_arr.append(bill_dict)

            all_count = all_count+so
        if all_count != 0:
            join_count = all_count/len(bill_list)
        else:
            join_count = 0
        save_dict["join_count"] = join_count
        # save_dict["bill_list"]  = bill_arr
        plat_bill_list_use.append(save_dict)
    # cr_dict["plat_bill_list_use"] = plat_bill_list_use
    # return cr_dict
    return plat_bill_list_use
        

if __name__ == "__main__":
    
    plat_list = list(collection_plat_bill.find())
    crs  = list(collection_crs.find({}, {"_id":1}))

    for plat in plat_list:
        array_all_cr_value = []
        cr_main = {}
        for cr in crs:
            save_dict ={}
            save_dict["cr_id"] = cr["_id"]
            bills_list = list(collection_bills.find({"$or":[{"proposed_id" : cr["_id"]}, { "petitioned_id" : cr["_id"]}]}, {"_id":1}))
            for bill in bills_list:
                bills_dict = plat["all_bill_dict"]
                all_bill = []
                bill_value = 0
                for bill in bills_list:
                    bill_use = bills_dict[bill["_id"]]
                    cor_value = bill_use["cor_value"]
                    bill_value = bill_value + cor_value
                    all_bill.append(bill_use)
                bill_value = bill_value/len(all_bill)
            
            if cr["_id"] == plat["cr_id"]:
                cr_main["cr_id"] =  cr["_id"]
                cr_main["bill_value"] = bill_value
                array_all_cr_value.append(cr_main)
            else:
                save_dict["cr_id"] = cr["_id"]
                save_dict["bill_value"] = bill_value
                array_all_cr_value.append(save_dict)
        # cr_main 是該政見的主事者，array_all_cr_value 是剩餘的64個人，比較cr_main在65人中的分數排名第幾
        newlist = sorted(list_to_be_sorted, key=lambda k: k['bill_value'])
        





            # for bill in bills_list:
            #     bill_dict = {}
            #     bill_use = getBill_withID(bill["bill_id"])
            #     bill_term_ckip_all = bill_use["bill_term_ckip_all"]
                
            #     #算正負面的比例
            #     pso_positive = len(list(set(bill_term_ckip_all).intersection(set(positive_lists))))+1 #避免為0
            #     nso_negative = len(list(set(bill_term_ckip_all).intersection(set(negative_lists))))+1 #避免為0

            #     #算比例
            #     so = math.log(pso_positive/nso_negative)
            #     so = so *bill["cor_value"]

            #     bill_dict["bill_id"] = bill["bill_id"]
            #     bill_dict["np_cor_value"] = so
            #     all_bill_dict[str(bill["bill_id"])] = bill_dict
            #     bill_arr.append(bill_dict)

            #     all_count = all_count+so
            #     print all_count
            # if all_count != 0:
            #     join_count = all_count/len(bills_list)
            # else:
            #     join_count = 0
            # save_dict["join_count"] = join_count
            # save_dict["bill_list"]  = bill_arr
            # save_dict["all_bill_dict"]  = all_bill_dict
            # print save_dict
            # collection_plat_bill_join.save(save_dict)
        print "end all"
        exit(0)