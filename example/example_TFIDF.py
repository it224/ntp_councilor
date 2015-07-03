#encoding=utf-8
from __future__ import division
import math
import re
import json
import sympy

from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection_same_word = db['same_word_my_country']
collection_bill = db['ntp_bills_example']
collection_news = db['ntp_news_example']

def getValue(termDicArray):
    array_return = []
    for term in termDicArray:
        array_return.append(term["term"])
    return array_return

def parseStopWord():
    json_data=open('../plats_all_relation_computing/stopword.json')
    data = json.load(json_data)
    json_data.close()
    return data
stopword = parseStopWord()

def removeStopWord(array):
    array_return = []
    for item in array:
        if item not in stopword:
            array_return.append(item)
    return array_return

def removeOneTerm(array):
    array_return = []
    for term in array:
        if len(term) > 1:
            array_return.append(term)
    return array_return

def extendWord(plat_terms):
    plat_all_words = list(plat_terms)
    plat_all_words_dict = {}
    plat_times_dict = {}
    for term in plat_terms:
        plat_all_words_dict[term] = plat_terms.index(term)
        termFind = collection_same_word.find({"word":term})
        if termFind.count() > 0:
            for word in list(termFind[0]["same_word"]):
                if word not in plat_all_words:
                    plat_all_words.insert(plat_all_words.index(term)+1, word)
                    plat_all_words_dict[word] = plat_terms.index(term)
            plat_times_dict[plat_terms.index(term)] = len(list(termFind[0]["same_word"]))
    return plat_all_words
'''
bill_list = list(collection_bill.find())
all_bill_term_array = []
for bill_use in bill_list:
    bill_term = getValue(bill_use["description_all_term"])
    bill_term = removeStopWord(bill_term)
    bill_term = removeOneTerm(bill_term)
    bill_term = extendWord(bill_term)
    bill_term = removeStopWord(bill_term)
    bill_term = removeOneTerm(bill_term)
    bill_string = ""
    for term in bill_term:
        bill_string = bill_string+term+" "
    all_bill_term_array.append(bill_string)

vectorizer=CountVectorizer()
transformer=TfidfTransformer()
tfidf=transformer.fit_transform(vectorizer.fit_transform(all_bill_term_array))

word=vectorizer.get_feature_names()
weight=tfidf.toarray()
for i in range(len(weight)):
    bill_use = bill_list[i] #第i篇bill
    bill_term = getValue(bill_use["description_all_term"])
    bill_term = removeStopWord(bill_term)
    bill_term = removeOneTerm(bill_term)
    bill_term = extendWord(bill_term)
    bill_term = removeStopWord(bill_term)
    bill_term = removeOneTerm(bill_term)
    word_dict = {}
    for j in range(len(word)):
        if word[j] in bill_term:
            print word[j],weight[i][j]
            word_dict[word[j]] = weight[i][j]
    bill_use["tfidf_dict"] = word_dict
    collection_bill.save(bill_use)
    print ""
'''

news_list = list(collection_news.find())
all_news_term_array = []
for news_use in news_list:
    news_term = getValue(news_use["story_term_ckip_all_state"])

    news_term = removeStopWord(news_term)
    news_term = removeOneTerm(news_term)
    news_term = extendWord(news_term)
    news_term = removeStopWord(news_term)
    news_term = removeOneTerm(news_term)
    
    news_string = ""
    for term in news_term:
        news_string = news_string+term+" "
    all_news_term_array.append(news_string)

vectorizer=CountVectorizer()
transformer=TfidfTransformer()
tfidf=transformer.fit_transform(vectorizer.fit_transform(all_news_term_array))

word=vectorizer.get_feature_names()
weight=tfidf.toarray()
for i in range(len(weight)):
    news_use = news_list[i] #第i篇bill
    news_term = getValue(news_use["story_term_ckip_all_state"])
    
    news_term = removeStopWord(news_term)
    news_term = removeOneTerm(news_term)
    news_term = extendWord(news_term)
    news_term = removeStopWord(news_term)
    news_term = removeOneTerm(news_term)

    word_dict = {}
    for j in range(len(word)):
        if word[j] in news_term:
            print word[j],weight[i][j]
            word_dict[word[j]] = weight[i][j]
    news_use["tfidf_dict"] = word_dict
    collection_news.save(news_use)
    print ""

        
print "end all"
exit(0)
