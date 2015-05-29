#encoding=utf-8
from __future__ import division
import os
import sys
import jieba
import jieba.posseg as pseg
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import re, math
from collections import Counter
'''
platform 之間的相似度
'''
client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection_same_word = db['same_word_my_country']
collection_cr_plat = db['ntp_platform']
collection = db['ntp_platform_relation']

plats = list(collection_cr_plat.find())

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

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

for plat in plats:
    v1_extend = extendWord(removeOneTerm(plat["platforms_term"]))
    dic = {"_id":plat["_id"], "extend_word":v1_extend}
    vector1 = Counter(v1_extend)
    dic_other = {}
    for plat_other in plats:
        vector2 = Counter(extendWord(removeOneTerm(plat_other["platforms_term"])))
        cosine = get_cosine(vector1, vector2)
        dic_other[str(plat_other['_id'])]= cosine
        print plat["_id"]
        print plat_other["_id"]
        print 'Cosine:', cosine
        print ""
    dic["cosine_other"] = dic_other
    collection.save(dic)
    print ""
    break