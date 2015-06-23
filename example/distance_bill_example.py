#encoding=utf-8
import math
import re
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
collection_plat = db['ntp_platform_example']
collection_bill = db['ntp_bills_example']
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
bill_list = list(collection_bill.find())
for plat in plat_list:
    save_dict ={}
    save_dict["_id"]=plat["_id"]
    save_dict["cr_id"]=plat["cr_id"]
    save_dict["name"]=plat["cr_name"]
    

    all_bill_dict = {}
    bill_arr = []
    all_count = 0

    plat_terms = getValue(plat["platforms_term"])
    #刪除stopword
    plat_terms = removeStopWord(plat_terms)
    #刪除一個字的(第一次)
    plat_terms = removeOneTerm(plat_terms)
    #擴張詞彙
    plat_terms, plat_term_dict = extendWord(plat_terms)
    #刪除stopword(第二次)
    plat_terms = removeStopWord(plat_terms)
    #刪除一個字的(第二次)
    plat_terms = removeOneTerm(plat_terms)
    
    for bill_use in bill_list:
        bill_dict = {}
        bill_term = getValue(bill_use["description_all_term"])
        #刪除stopword
        bill_term = removeStopWord(bill_term)
        #擴張詞彙
        bill_term, bill_term_dict = extendWord(bill_term)
        #刪除stopword(第二次)
        bill_term = removeStopWord(bill_term)
        #刪除一個字的(第二次)
        bill_term = removeOneTerm(bill_term)

        #取交集
        interArr = list(set(bill_term).intersection(set(plat_terms)))
        
        pso_term = list(set(bill_term).intersection(set(positive_lists)))
        nso_term = list(set(bill_term).intersection(set(negative_lists)))
        
        pso_value = pnso_value(bill_term_dict, interArr, pso_term)
        nso_value = pnso_value(bill_term_dict, interArr, nso_term)
        so = math.log((pso_value+1)/(nso_value+1)) #+1避免為0
        so_plus = pso_value- nso_value
        if so != 0.0:
            print "plat ~~~~~~~~~~~~~~~~~"
            print plat["plat_origin"]
            print "bill ~~~~~~~~~~~~~~~~~"
            print bill_use["description"]
            print "plat term............"
            for term in plat_terms:
                print term,
            print ""
            print "bill term.........."
            for term in bill_term:
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


        # pso_positive = len(list(set(bill_term_ckip_all).intersection(set(positive_lists))))+1 #避免為0
        # nso_negative = len(list(set(bill_term_ckip_all).intersection(set(negative_lists))))+1 #避免為0

        # #算比例
        # so = math.log(pso_positive/nso_negative)
        # so = so *cr_all_bill_dict[str(bill["_id"])]["cor_value"]

    #     cor_value = 0
    #     if(len(interArr)!=0):
    #         cor_value = len(interArr)/len(plat_terms)
    #     bill_dict["bill_id"] = bill["_id"]
    #     bill_dict["interWord"] = interArr
    #     bill_dict["cor_value"] = cor_value
    #     all_bill_dict[str(bill["_id"])] = bill_dict
    #     bill_arr.append(bill_dict)
    #     all_count = all_count+cor_value
    # if len(bill_arr) != 0:
    #     ac = all_count/len(bill_arr)
    # else:
    #     ac = 0
    # save_dict["accuracy"] = ac
    # save_dict["bill_list"]  = bill_arr
    # save_dict["all_bill_dict"] = all_bill_dict
    # print "save_dict"
    # print save_dict
    # print ""
    # collection_plat_bill.save(save_dict)
print "end all"
exit(0)
