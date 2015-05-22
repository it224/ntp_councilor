#encoding=utf-8
import mechanize
import cookielib
import urllib
import logging
import sys
import pymongo
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from time import sleep
from pymongo import MongoClient
from bs4 import BeautifulSoup
import urllib, urllib2
import re

client = MongoClient('mongodb://localhost:27017/')
db = client['councilor']
collection_crs = db['ntp_crs']
collection_news_list = db['ntp_news_url_list']

def parseToMongo():
    crs = list(collection_crs.find())
    for cr in crs:
        id = cr["_id"]
        cr_ntp_news_list = list(collection_news_list.find({"cr_id":ObjectId(id)}))
        for news in cr_ntp_news_list:
            newsId = str(news["_id"])
            try:
                data = urllib2.urlopen("file:///Users/man27382210/Desktop/self_manage/paper_g0v/ntp_news_html/"+newsId+".html").read()
                soup = BeautifulSoup(data)
                story = soup.find('td',{"class":"story"})
                story = re.sub('<[^<]+?>', '', story.text)
                editor_first = story.find(u"【")
                editor_last = story.find(u"】")+1
                editor_char = story[editor_first:editor_last]
                story = story.replace(editor_char, "")
                print story.encode('utf-8')
                news["story"] = story
                collection_news_list.save(news)
            except Exception, e:
                print e
                f = open("./error_parse_news.txt", "a")
                f.write(newsId+"\n")
                f.close()
parseToMongo()