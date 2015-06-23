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
    words_use = pseg.cut(test_sent)
    for word_use in words_use:
        result_arr.append({"pos":word_use.flag, "term":word_use.word})
    print("no ckip")
    return result_arr


segmenter = CKIPSegmenter('gcsn', 'rb303147258')
parser = CKIPParser('gcsn', 'rb303147258')

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection = db['ntp_crs']
collection_save = db['ntp_platform_example']
crs = list(collection.find().limit(5))

for cr in crs:
    for plat in cr["platform"]:
        platforms_term = []
        plat_save = {}
        plat_save["cr_id"] = cr["_id"]
        plat_save["cr_name"] = cr["name"]
        plat_save["plat_origin"] = plat
        try:
            result = segmenter.process(plat)
            if result['status_code'] != '0':
                print('Process Failure: ' + result['status'])
                platforms_term = cuttest(plat)
            else:
                for sentence in list(result['result']):
                    for term in sentence:
                        if term['pos'] != u"PERIODCATEGORY" and term['pos'] != u"COMMACATEGORY" and term['pos'] != u"PAUSECATEGORY" and term['pos'] != u"PARENTHESISCATEGORY":
                            print(term['term'].encode('utf-8'), term['pos'])
                            platforms_term.append({"pos":term['pos'], "term":term['term']})
            sleep(2)
        except Exception, e:
            print("error")
            print(e)
            platforms_term = cuttest(plat)
        finally:
            plat_save["platforms_term"] = platforms_term
            print(plat_save)
            collection_save.save(plat_save)
   