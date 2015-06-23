# -*- coding: utf-8 -*-

#################################################
# example.py
# ckip.py
#
# Copyright (c) 2012-2014, Chi-En Wu
# Distributed under The BSD 3-Clause License
#################################################

from __future__ import unicode_literals, print_function, division
import re
import os
import sys
import jieba
import jieba.posseg as pseg
from pymongo import MongoClient
from bson.objectid import ObjectId
from ckip import CKIPSegmenter, CKIPParser
from time import sleep



def cuttest(sent):
    result_arr = []
    words_use = pseg.cut(sent)
    for word_use in words_use:
        result_arr.append({"pos":word_use.flag, "term":word_use.word})
    print("no ckip")
    return result_arr


segmenter = CKIPSegmenter('gcsn', 'rb303147258')
parser = CKIPParser('gcsn', 'rb303147258')

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection = db['ntp_bills']
collection_save = db['ntp_bills_example']
bills = list(collection.find().limit(50))

for bill in bills:
    description_term = []
    try:
        result = segmenter.process(bill["description"])
        if result['status_code'] != '0':
            print('Process Failure: ' + result['status'])
            description_term = cuttest(bill["description"])
        else:
            for sentence in list(result['result']):
                for term in sentence:
                    print(term['term'].encode('utf-8'), term['pos'])
                    if term['pos'] != u"PERIODCATEGORY" and term['pos'] != u"COMMACATEGORY" and term['pos'] != u"PAUSECATEGORY" and term['pos'] != u"PARENTHESISCATEGORY":
                        description_term.append({"pos":term['pos'], "term":term['term']})
        sleep(2)
    except Exception, e:
        print("error")
        print(e)
        description_term = cuttest(bill["description"])
    finally:
        bill["description_all_term"] = description_term
        print(bill)
        collection_save.save(bill)
   