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
        if re.match("n", word_use.flag) != None and word_use.word not in  noun_terms_arr:
            noun_terms_arr.append(word_use.word)
        if re.match("v", word_use.flag) != None and word_use.word not in  verb_terms_arr:
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
collection = db['ntp_bills']
# collection_save = db['test']
bills = list(collection.find())

for bill in bills:
    description_verb = []
    description_nonu = []
    description_term = []
    try:
        result = segmenter.process(bill["description"])
        if result['status_code'] != '0':
            print('Process Failure: ' + result['status'])
            tupleUse = cuttest(bill["description"])
            description_term = tupleUse[0]
            description_nonu = tupleUse[1]
            description_verb = tupleUse[2]
        else:
            for sentence in list(result['result']):
                for term in sentence:
                    print(term['term'].encode('utf-8'), term['pos'])
                    if re.match("N", term['pos']) != None and term['term'] not in description_nonu:
                        description_term.append(term['term'])
                        description_nonu.append(term['term'])
                    if re.match("V", term['pos']) != None and term['pos'] != 'ADV' and term['term'] not in description_verb:
                        description_term.append(term['term'])
                        description_verb.append(term['term'])
        sleep(2)
    except Exception, e:
        print("error")
        print(e)
        tupleUse = cuttest(bill["description"])
        description_term = tupleUse[0]
        description_nonu = tupleUse[1]
        description_verb = tupleUse[2]
    finally:
        bill["description_term"] = description_term
        bill["description_nonu"] = description_nonu
        bill["description_verb"] = description_verb
        print(bill)
        collection.save(bill)
   