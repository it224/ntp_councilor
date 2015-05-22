# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import re
import os
import sys
import jieba
import jieba.posseg as pseg
from pymongo import MongoClient
from bson.objectid import ObjectId
from time import sleep
import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['councilor']
collection = db['ntp_news_url_list']
collection_save = db['ntp_news_url_list_ckip']

def returnFile():
    with open("./diff_ids.txt") as f:
        content = f.readlines()
        return content
def parse():
    news_list = returnFile()
    for news_id in news_list:
        news_id = news_id.split("\n")[0]
        news = collection.find_one({"_id":ObjectId(news_id)})    
        if "story" in news:
	    print(news['story'].encode('utf-8'))
            if(len(news['story'])>3):
                try:
                    dic_news_save = news
                    story_term_ckip_all = []
                    story_term_ckip_noun = []
                    story_term_ckip_verb = []
                    story_term_ckip_tc_all = []
                    story_term_ckip_tc_noun = []
                    story_term_ckip_tc_verb = []
                    story = news['story'].split('\n')
                    for ind, sy in enumerate(story):
                        one_sentence = sy
                        if len(one_sentence) > 0:
                            result = pseg.cut(one_sentence)
                            for term in result:
                                print(term.word.encode('utf-8'), term.flag.encode('utf-8'))
                                if re.match("n", term.flag) != None:
                                    if ind <=3:
                                        story_term_ckip_tc_all.append(term.word)
                                        story_term_ckip_tc_noun.append(term.word)
                                    story_term_ckip_all.append(term.word)
                                    story_term_ckip_noun.append(term.word)
                                if re.match("v", term.flag) != None:
                                    if ind <=3:
                                        story_term_ckip_tc_all.append(term.word)
                                        story_term_ckip_tc_verb.append(term.word)
                                    story_term_ckip_all.append(term.word)
                                    story_term_ckip_verb.append(term.word)
                            sleep(3)
                        else:
                            print("no content")
                            print("")
                    dic_news_save["story_term_ckip_all"] = story_term_ckip_all
                    dic_news_save["story_term_ckip_noun"] = story_term_ckip_noun
                    dic_news_save["story_term_ckip_verb"] = story_term_ckip_verb
                    dic_news_save["story_term_ckip_tc_all"] = story_term_ckip_tc_all
                    dic_news_save["story_term_ckip_tc_noun"] = story_term_ckip_tc_noun
                    dic_news_save["story_term_ckip_tc_verb"] = story_term_ckip_tc_verb
                    print("save")
                    print(news["_id"])
                    print("")
                    collection_save.save(dic_news_save)
                except Exception, e:
                    print(e)
                    print("error with id")
                    print(news["_id"])
                    f = open("./error_for_jebia.txt", "a")
                    f.write(str(news["_id"])+"\n")
                    f.close()
                    sleep(3)
parse()
