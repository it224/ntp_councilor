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



def cuttest(test_sent):
    result_arr = []
    noun_terms_arr = []
    verb_terms_arr = []
    words_use = pseg.cut(test_sent)
    for word_use in words_use:
        if re.match("n", word_use.flag) != None:
            noun_terms_arr.append(word_use.word)
        if re.match("v", word_use.flag) != None:
            verb_terms_arr.append(word_use.word)
    result_arr.extend(noun_terms_arr)
    result_arr.extend(verb_terms_arr)
    print("no ckip")
    print(result_arr)
    return (result_arr, noun_terms_arr, verb_terms_arr)


segmenter = CKIPSegmenter('gcsn', 'rb303147258')
parser = CKIPParser('gcsn', 'rb303147258')

client = MongoClient('mongodb://localhost:27017/')
db = client['councilor']
collection = db['ntp_crs']
collection_save = db['ntp_platform']
crs = list(collection.find())

for cr in crs:
    for plat in cr["platform"]:
        platforms_verb = []
        platforms_nonu = []
        platforms_term = []
        plat_save = {}
        plat_save["cr_id"] = cr["_id"]
        plat_save["cr_name"] = cr["name"]
        plat_save["plat_origin"] = plat
        try:
            result = segmenter.process(plat)
            if result['status_code'] != '0':
                print('Process Failure: ' + result['status'])
                tupleUse = cuttest(plat)
                platforms_term = tupleUse[0]
                platforms_nonu = tupleUse[1]
                platforms_verb = tupleUse[2]
            else:
                for sentence in list(result['result']):
                    for term in sentence:
                        print(term['term'].encode('utf-8'), term['pos'])
                        if re.match("N", term['pos']) != None:
                            platforms_term.append(term['term'])
                            platforms_nonu.append(term['term'])
                        if re.match("V", term['pos']) != None and term['pos'] != 'ADV':
                            platforms_term.append(term['term'])
                            platforms_verb.append(term['term'])
            sleep(2)
        except Exception, e:
            print("error")
            print(e)
            tupleUse = cuttest(plat)
            platforms_term = tupleUse[0]
            platforms_nonu = tupleUse[1]
            platforms_verb = tupleUse[2]
        finally:
            plat_save["platforms_term"] = platforms_term
            plat_save["platforms_nonu"] = platforms_nonu
            plat_save["platforms_verb"] = platforms_verb
            print(plat_save)
            collection_save.save(plat_save)
   