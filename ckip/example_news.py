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
import datetime

def traverse(root):
    """Helper function to traverse all leaf nodes of the given tree root."""
    if 'child' in root:
        for child in root['child']:
            for leaf in traverse(child):
                yield leaf
    else:
        yield root

segmenter = CKIPSegmenter('gcsn', 'rb303147258')
parser = CKIPParser('gcsn', 'rb303147258')

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection = db['ntp_news_url_list']
collection_save = db['ntp_news_example']

def cuttest_story(story):
    story_term_ckip_all = []
    for ind, sy in enumerate(story):
        one_sentence = sy
        if len(one_sentence) > 0:
            arr = cuttest(one_sentence)
            story_term_ckip_all.extend(arr)
    return story_term_ckip_all

def cuttest(sent):
    result_arr = []
    words_use = pseg.cut(sent)
    for word_use in words_use:
        result_arr.append({"pos":word_use.flag, "term":word_use.word})
    print("no ckip")
    return result_arr

def returnFile():
    with open("./error_id3.txt") as f:
        content = f.readlines()
        return content
def parse():
    # news_list = returnFile()
    news_list = list(collection.find().limit(50))
    # news_list = list(news_list)
    for news in news_list:
    # for news_id in news_list:
        # news_id = news_id.split("\n")[0]
        # news = collection.find_one({"_id":ObjectId(news_id)})
        d = datetime.datetime.now()
        h = d.hour + d.minute / 60. + d.second / 3600.
        if h < 5.4 or h > 7.3:
            if "story" in news:
                if(len(news['story'])>3):
                    try:
                        dic_news_save = news
                        story_term_ckip_all = []
                        story = news['story'].split('\n')
                        for ind, sy in enumerate(story):
                            one_sentence = sy
                            if len(one_sentence) > 0:
                                result = parser.process(one_sentence)
                                # if result['status_code'] != '0':
                                #     print('Process Failure: ' + result['status'])
                                #     story_term_ckip_all = cuttest(one_sentence)
                                # for sentence in result['result']:
                                #     for term in traverse(sentence['tree']):
                                #         print(term['term'].encode('utf-8'), term['pos'])
                                if result['status_code'] != '0':
                                    print('Process Failure: ' + result['status'])
                                for sentence in list(result['result']):
                                    for term in traverse(sentence['tree']):
                                        print(term['term'].encode('utf-8'), term['pos'])
                                        if term['pos'] != u"PERIODCATEGORY" and term['pos'] != u"COMMACATEGORY" and term['pos'] != u"PAUSECATEGORY" and term['pos'] != u"PARENTHESISCATEGORY":
                                            dict_use = {"pos":term['pos'], "term":term['term']}
                                            story_term_ckip_all.append(dict_use)
                                sleep(3)
                            else:
                                print("")
                       
                    except Exception, e:
                        print(e)
                        print("error with id")
                        story_term_ckip_all = cuttest_story(story)
                        print(story_term_ckip_all)
                        # print(news["_id"])
                        # f = open("./error_id3.txt", "a")
                        # f.write(str(news["_id"])+"\n")
                        # f.close()
                        # sleep(3)
                    finally:
                        dic_news_save["story_term_ckip_all_state"] = story_term_ckip_all
                        print("save")
                        print(news["_id"])
                        print("")
                        collection_save.save(dic_news_save)
        else:
            print("sleep 7200(兩小時)")
            sleep(7200)
parse()