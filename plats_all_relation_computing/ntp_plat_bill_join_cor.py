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
collection_plat_bill = db["ntp_platform_bill_extend_cor"]
collection_plat_bill_join = db['ntp_platform_bill_join_cor']


if __name__ == "__main__":
    plat_list = list(collection_plat_bill.find())
    for plat in plat_list:
        save_dict ={}
        save_dict["_id"]=plat["_id"]
        save_dict["cr_id"]=plat["cr_id"]
        save_dict["name"]=plat["name"]
        all_count = 0
        bills_list = plat["bill_list"]
        for bill in bills_list:
            if bill["cor_value"] > 0:
                all_count = all_count+1
        if all_count != 0:
            join_count = all_count/len(bills_list)
        else:
            join_count = 0
        save_dict["join_count"] = join_count
        print save_dict
        collection_plat_bill_join.save(save_dict)
    print "end all"
    exit(0)