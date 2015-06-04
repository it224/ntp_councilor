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
import difflib
'''
每個 sort 結果之間的距離
'''
client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
col_ntp_platform_TOPSIS_entropy = db['ntp_platform_TOPSIS_entropy_extend']
col_ntp_platform_SAW_entropy = db['ntp_platform_SAW_entropy_extend']
col_ntp_platform_WP_entropy = db['ntp_platform_WP_entropy_extend']
col_ntp_platform_PAIRWISE_sort = db['ntp_platform_PAIRWISE_sort_extend']



topsis_sort = list(col_ntp_platform_TOPSIS_entropy.find({}, {"_id":1}).sort("plat_c"))
saw_sort = list(col_ntp_platform_SAW_entropy.find({}, {"_id":1}).sort("plat_amount"))
wp_sort = list(col_ntp_platform_WP_entropy.find({}, {"_id":1}).sort("plat_amount"))
pairwise_sort = list(col_ntp_platform_PAIRWISE_sort.find({}, {"_id":1}).sort("sort"))
pairwise_sort.reverse()

def levenshteinDistance(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]

def levenshteinDistance_list(list1,list2):
    distances = range(len(list1) + 1)
    for index2,element2 in enumerate(list2):
        newDistances = [index2+1]
        for index1,element1 in enumerate(list1):
            if str(element1["_id"]) == str(element2["_id"]):
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]

def getIdFromDict(array):
    array_return = []
    for dic in array:
        array_return.append(str(dic["_id"]))
    return array_return

def difflib_compare(array1, array2):
    sm=difflib.SequenceMatcher(None,array1,array2)
    return sm.ratio()
 
# print(levenshteinDistance("rosettacode","raisethysword"))
# print levenshteinDistance_list(topsis_sort, saw_sort)
topsis_sort   = getIdFromDict(topsis_sort)
saw_sort      = getIdFromDict(saw_sort)
pairwise_sort = getIdFromDict(pairwise_sort)
wp_sort       = getIdFromDict(wp_sort)


print "ratio of topsis, wp : "      +str(difflib_compare(topsis_sort, wp_sort))
print "ratio of topsis, saw : "     +str(difflib_compare(topsis_sort, saw_sort))
print "ratio of topsis, pairwise : "+str(difflib_compare(topsis_sort, pairwise_sort))
print "ratio of saw, wp : "         +str(difflib_compare(saw_sort, wp_sort))
print "ratio of saw, pairwise : "   +str(difflib_compare(saw_sort, pairwise_sort))
print "ratio of wp, pairwise : "    +str(difflib_compare(wp_sort, pairwise_sort))