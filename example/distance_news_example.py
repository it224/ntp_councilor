#encoding=utf-8
import math
import re
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection_plat = db['ntp_platform_example']
collection_news = db['ntp_news_example']
collection_same_word = db['same_word_my_country']

# math.exp(-distance)

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


def returnFile(path):
    content_use = list()
    with open("../plats_all_relation_computing/ntusd/ntusd-"+path+".txt") as f:
        content = f.readlines()
    for word in content:
        content_use.append(word.decode('utf-8').split('\n')[0])
    return content_use
positive_lists = returnFile("positive")
negative_lists = returnFile("negative")

def extendWord(plat_terms):
    plat_all_words = list(plat_terms)
    plat_all_words_dict = {}
    for term in plat_terms:
        plat_all_words_dict[term] = plat_terms.index(term)
        termFind = collection_same_word.find({"word":term})
        if termFind.count() > 0:
            for word in list(termFind[0]["same_word"]):
                if word not in plat_all_words:
                    plat_all_words.insert(plat_all_words.index(term)+1, word)
                    plat_all_words_dict[word] = plat_terms.index(term)
    return (plat_all_words, plat_all_words_dict)

def removeOneTerm(array):
    array_return = []
    for term in array:
        if len(term) > 1:
            array_return.append(term)
    return array_return

def removeStopWord(array):
    array_return = []
    for item in array:
        if item not in stopword:
            array_return.append(item)
    return array_return

def pnso_value(term_dict, interArr, pnso_term):
    distance_all = 0
    if len(interArr)>0:
        if len(pnso_term)>0:
            for inter in interArr:
                interIndex = term_dict[inter]
                for pnso in pnso_term:
                    pnsoIndex = term_dict[pnso]
                    distance = (math.fabs(interIndex - pnsoIndex) -1)*-1
                    distance = math.exp(distance)
                    distance_all = distance_all+distance
    return distance_all


plat_list = list(collection_plat.find())
news_list = list(collection_news.find())
for plat in plat_list:
    save_dict ={}
    save_dict["_id"]=plat["_id"]
    save_dict["cr_id"]=plat["cr_id"]
    save_dict["name"]=plat["cr_name"]
    

    all_news_dict = {}
    news_arr = []
    all_count = 0

    plat_terms = getValue(plat["platforms_term"])
    #刪除stopword
    plat_terms = removeStopWord(plat_terms)
    #刪除一個字的(第一次)
    plat_terms = removeOneTerm(plat_terms)
    #擴張詞彙
    plat_terms, plat_term_dict = extendWord(plat_terms)
    # #刪除stopword(第二次)
    plat_terms = removeStopWord(plat_terms)
    # #刪除一個字的(第二次)
    plat_terms = removeOneTerm(plat_terms)

    for news_use in news_list:
        news_dict = {}
        news_term = getValue(news_use["story_term_ckip_all_state"])
        #刪除stopword
        news_term = removeStopWord(news_term)
        #擴張詞彙
        news_term, news_term_dict = extendWord(news_term)
        #刪除stopword(第二次)
        news_term = removeStopWord(news_term)
        #刪除一個字的(第二次)
        news_term = removeOneTerm(news_term)

        #取交集
        interArr = list(set(news_term).intersection(set(plat_terms)))
        
        pso_term = list(set(news_term).intersection(set(positive_lists)))
        nso_term = list(set(news_term).intersection(set(negative_lists)))
        
        pso_value = pnso_value(news_term_dict, interArr, pso_term)
        nso_value = pnso_value(news_term_dict, interArr, nso_term)
        so = math.log((pso_value+1)/(nso_value+1)) #+1避免為0
        so_plus = pso_value- nso_value
        if so != 0.0:
            print "plat ~~~~~~~~~~~~~~~~~"
            print plat["plat_origin"]
            print "news ~~~~~~~~~~~~~~~~~"
            print news_use["parse_url_name"]
            print "plat term............"
            for term in plat_terms:
                print term,
            print ""
            print "news term.........."
            for term in news_term:
                print term,
            print ""
            print "interArr------------"
            for term in interArr:
                print term,
            print ""
            print "pso term=========="
            for term in pso_term:
                print term,
            print ""
            print "nso term========"
            for term in nso_term:
                print term,
            print ""
            print "----------------"
            print "pso_value : "+str(pso_value) +" nso_value : "+str(nso_value) + " so : "+str(so) + " so plus : "+str(so_plus)
            print ""
print "end all"
exit(0)
