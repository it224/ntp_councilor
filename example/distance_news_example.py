#encoding=utf-8
from __future__ import division
import math
import re
import os
import sys
import json
import sympy
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection_plat = db['ntp_platform_example']
collection_news = db['ntp_news_example']
collection_same_word = db['same_word_my_country']
collection_correlation = db['ntp_term_correlation']
collection_save = db['ntp_platform_news_cor_example_v5']

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
    return (plat_all_words, plat_all_words_dict, plat_times_dict)

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

#v1
def pnso_value(term_dict, term_times_dict, interArr, pnso_term):
    distance_all = 0
    if len(interArr)>0:
        if len(pnso_term)>0:
            for inter in interArr:
                interIndex = term_dict[inter]
                for pnso in pnso_term:
                    pnsoIndex = term_dict[pnso]
                    distance = (math.fabs(interIndex - pnsoIndex))*-1
                    distance = math.exp(distance)
                    if pnsoIndex in term_times_dict.keys():
                        distance = distance/term_times_dict[pnsoIndex]
                    distance_all = distance_all+distance
    return distance_all
#v2
def wpnso_value(len_number, term_dict, term_times_dict, interArr, pnso_term):
    distance_all = 0
    if len(interArr)>0:
        if len(pnso_term)>0:
            for inter in interArr:
                interIndex = term_dict[inter]
                for pnso in pnso_term:
                    pnsoIndex = term_dict[pnso]
                    distance = (math.fabs(interIndex - pnsoIndex))*-1
                    distance = math.exp(distance)
                    
                    #compute weight
                    number = pnsoIndex//len_number+1 #找pso在第幾個位置
                    if number>5:
                        number = 5
                    x= sympy.symbols('x')
                    weight = sympy.integrate(12*(x-(1/2))**2, (x, 0.2*(number-1), 0.2*number))
                    distance = distance*weight
                    
                    if pnsoIndex in term_times_dict.keys():
                        distance = distance/term_times_dict[pnsoIndex]
                    distance_all = distance_all+distance
    return distance_all

#v3
def tfidfpnso_value(tfidfDict, term_dict, term_times_dict, interArr, pnso_term):
    distance_all = 0
    if len(interArr)>0:
        if len(pnso_term)>0:
            for inter in interArr:
                interIndex = term_dict[inter]
                for pnso in pnso_term:
                    pnsoIndex = term_dict[pnso]
                    distance = (math.fabs(interIndex - pnsoIndex))*-1
                    distance = math.exp(distance)
                    
                    #compute getTFIDF
                    tfidf = tfidfDict[pnso]
                    print "tfidf : "+str(tfidf)
                    distance = distance*tfidf
                    print "distance : "+str(distance)
                    if pnsoIndex in term_times_dict.keys():
                        distance = distance/term_times_dict[pnsoIndex] #字與相關字的次數
                    distance_all = distance_all+distance
    return distance_all

#v4
def wtfidfpnso_value(len_number, tfidfDict, term_dict, term_times_dict, interArr, pnso_term):
    distance_all = 0
    if len(interArr)>0:
        if len(pnso_term)>0:
            for inter in interArr:
                interIndex = term_dict[inter]
                for pnso in pnso_term:
                    pnsoIndex = term_dict[pnso]
                    distance = (math.fabs(interIndex - pnsoIndex))*-1
                    distance = math.exp(distance)
                    
                    #compute weight
                    number = pnsoIndex//len_number+1 #找pso在第幾個位置
                    if number>5:
                        number = 5
                    x= sympy.symbols('x')
                    weight = sympy.integrate(12*(x-(1/2))**2, (x, 0.2*(number-1), 0.2*number))
                    distance = distance*weight

                    #compute getTFIDF
                    tfidf = tfidfDict[pnso]
                    print "tfidf : "+str(tfidf)
                    distance = distance*tfidf
                    print "distance : "+str(distance)
                    if pnsoIndex in term_times_dict.keys():
                        distance = distance/term_times_dict[pnsoIndex] #字與相關字的次數
                    distance_all = distance_all+distance
    return distance_all

#v5
def corpnso_value(term_dict, term_times_dict, termArr, pnso_term):
    distance_all = 0    
    if len(pnso_term)>0:
        for term in termArr:
            if term in term_dict.keys():
                interIndex = term_dict[term]
                main_term = list(collection_correlation.find({"main_word":term}))
                if len(main_term)>0:
                    main_term = main_term[0]
                    term_valueDict = main_term["term_value"]
                    for pnso in pnso_term:
                        if pnso in term_valueDict.keys():
                            pnsoIndex = term_dict[pnso]
                            distance = (math.fabs(interIndex - pnsoIndex))*-1
                            distance = math.exp(distance)
                            #correlation value
                            print "term : "+term
                            print "pnso : "+pnso
                            print "term_valueDict[pnso] : "+ str(term_valueDict[pnso])
                            distance = distance* term_valueDict[pnso]
                            print "distance : "+ str(distance)
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
    plat_terms, plat_term_dict, plat_times_dict = extendWord(plat_terms)
    # #刪除stopword(第二次)
    plat_terms = removeStopWord(plat_terms)
    # #刪除一個字的(第二次)
    plat_terms = removeOneTerm(plat_terms)

    for news_use in news_list:
        news_dict = {}
        news_term = getValue(news_use["story_term_ckip_all_state"])
        tfidf_dict = news_use["tfidf_dict"]
        #刪除stopword
        news_term = removeStopWord(news_term)
        #擴張詞彙
        news_term, news_term_dict, news_times_dict = extendWord(news_term)
        #刪除stopword(第二次)
        news_term = removeStopWord(news_term)
        #刪除一個字的(第二次)
        news_term = removeOneTerm(news_term)

        #取交集
        interArr = list(set(news_term).intersection(set(plat_terms)))
        
        pso_term = list(set(news_term).intersection(set(positive_lists)))
        nso_term = list(set(news_term).intersection(set(negative_lists)))
        


        #v1 normal distance
        # pso_value = pnso_value(news_term_dict, news_times_dict, interArr, pso_term)
        # nso_value = pnso_value(news_term_dict, news_times_dict, interArr, nso_term)
        
        #v2 U shaped
        # len_number = round(len(news_term)/5)
        # if len_number>1:
        #     pso_value = wpnso_value(len_number, news_term_dict, news_times_dict, interArr, pso_term)
        #     nso_value = wpnso_value(len_number, news_term_dict, news_times_dict, interArr, nso_term)
        # else:
        #     pso_value = pnso_value(news_term_dict, news_times_dict, interArr, pso_term)
        #     nso_value = pnso_value(news_term_dict, news_times_dict, interArr, nso_term)
        
        #v3 tfidf weight
        # pso_value = tfidfpnso_value(tfidf_dict, news_term_dict, news_times_dict, interArr, pso_term)
        # nso_value = tfidfpnso_value(tfidf_dict, news_term_dict, news_times_dict, interArr, nso_term)

        # v4 U shaped+tfidf weight
        # len_number = round(len(news_term)/5)
        # if len_number>1:
        #     pso_value = wtfidfpnso_value(len_number, tfidf_dict, news_term_dict, news_times_dict, interArr, pso_term)
        #     nso_value = wtfidfpnso_value(len_number, tfidf_dict, news_term_dict, news_times_dict, interArr, nso_term)
        # else:
        #     pso_value = tfidfpnso_value(tfidf_dict, news_term_dict, news_times_dict, interArr, pso_term)
        #     nso_value = tfidfpnso_value(tfidf_dict, news_term_dict, news_times_dict, interArr, nso_term)
        
        # v5 correlation
        pso_value = corpnso_value(news_term_dict, news_times_dict, plat_terms, pso_term)
        nso_value = corpnso_value(news_term_dict, news_times_dict, plat_terms, nso_term)  

        so = math.log((pso_value+1)/(nso_value+1)) #+1避免為0
        so_plus = pso_value- nso_value
        
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
        save_dict = {}
        save_dict["_id"] = str(plat["_id"])+"_"+str(news_use["_id"])
        save_dict["plat_id"] = plat["_id"]
        save_dict["news_id"] = news_use["_id"]
        save_dict["plat_origin"] = plat["plat_origin"]
        save_dict["parse_url_name"] = news_use["parse_url_name"]
        save_dict["story"] = news_use["story"]
        save_dict["plat_terms"] = plat_terms
        save_dict["news_term"] = news_term
        save_dict["interArr"] = interArr
        save_dict["pso_term"] = pso_term
        save_dict["nso_term"] = nso_term
        # save_dict["pso_value"] = pso_value
        # save_dict["nso_value"] = nso_value
        save_dict["so"] = so
        # save_dict["so_origin"] = so_plus
        print collection_save.save(save_dict)
        print "pso_value : "+str(pso_value) +" nso_value : "+str(nso_value) + " so : "+str(so) + " so_origin : "+str(so_plus)
        print ""
        
        # f = open("./plat_news_v2.json", "a")
        # f.write("plat ~~~~~~~~~~~~~~~~~"+"\n")
        # f.write(plat["plat_origin"].encode('utf-8')+"\n")
        # f.write("news ~~~~~~~~~~~~~~~~~"+"\n")
        # f.write(news_use["parse_url_name"].encode('utf-8')+"\n")
        # f.write("plat term............"+"\n")
        # for term in plat_terms:
        #     f.write(term.encode('utf-8')+" ")
        # f.write("\n")
        # f.write("news term.........."+"\n")
        # for term in news_term:
        #     f.write(term.encode('utf-8')+" ")
        # f.write("\n")
        # f.write("interArr------------"+"\n")
        # for term in interArr:
        #     f.write(term.encode('utf-8')+" ")
        # f.write("\n")
        # f.write("pso term=========="+"\n")
        # for term in pso_term:
        #     f.write(term.encode('utf-8')+" ")
        # f.write("\n")
        # f.write("nso term========"+"\n")
        # for term in nso_term:
        #     f.write(term.encode('utf-8')+" ")
        # f.write("\n")
        # f.write("----------------"+"\n")
        # f.write("pso_value : "+str(pso_value) +" nso_value : "+str(nso_value) + " so : "+str(so) + " so_origin : "+str(so_plus)+"\n")
        # f.write("\n")
        # f.close()
        
        # break
print "end all"
exit(0)
