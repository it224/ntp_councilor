#encoding=utf-8
from __future__ import division
import re
import os
import sys
import jieba
import jieba.posseg as pseg
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import math
'''
cr 對所有plat的影響 其topsis的分數
'''

client = MongoClient('mongodb://localhost:27017/')
db                            = client['ntp_councilor']
collection_crs                = db["ntp_crs"]                 #所有政見638筆  ntp_crs
collection_plats              = db["ntp_platform"]
collection_bill_cor           = db["ntp_platform_bill_cor"]     #政見議案關係   ntp_platform_bill_cor
collection_news_cor           = db["ntp_platform_news_cor"]      #政見新聞關係   ntp_platform_news_cor
collection_news_pn_cor        = db["ntp_platform_news_pn_cor"]   #政見新聞正負面  ntp_platform_news_pn_cor
collection_bill_join_cor      = db["ntp_platform_bill_join_cor"] #政見議案參與數  ntp_platform_bill_join_cor

collection_bill               = db['ntp_bills']
collection_news               = db['ntp_news_url_list_ckip']

collection_crs_SAW_compare = db['ntp_crs_SAW_compare']

#把每個 attr 做正規化
def attrbuteNormalize(attribute_list):
    all_count = 0.0
    attribute_return = []
    
    for value in attribute_list:
        all_count = all_count + value

    for value in attribute_list:
        if all_count != 0:
            attribute_return.append(value/all_count)
        else:
            attribute_return.append(0)
    return attribute_return

#用entropy 找出每個 attribute 的 weight
def findWeightEntropy(attributes_decisions):
    weight_list = []
    h0 = -1*(math.log(638))**-1
    d_all = []
    for j in range(0, 4, 1):
        h_duration = 0.0
        for i in range(0, 637, 1):
            if attributes_decisions[j][i] > 0.0:
                h_duration = h_duration + attributes_decisions[j][i] * math.log(attributes_decisions[j][i])
        d_use = 1 - h0*h_duration
        d_all.append(d_use)
    
    d_count = 0
    for j in range(0, len(d_all), 1):
        d_count = d_count + d_all[j]
    
    w_all = []
    for j in range(0, len(d_all), 1):
        w_all.append(d_all[j]/d_count)
    return w_all


#make Vmj matrix
def weightProductAttribute(attribute, weight):
    attribute_return = []
    
    for value in attribute:
        v_value = value * weight
        attribute_return.append(v_value)
    
    return attribute_return

#計算該政見總和分數
def computeDistanceAnd(attributes):

    all_plats_use = []

    pbc = attributes[0]
    pnc = attributes[1]
    npn = attributes[2]
    jbs = attributes[3]

    plat_amount_list = []
    for i in range(0, 638, 1): #0~637
        plat_amount = pbc[i] + pnc[i] + npn[i] + jbs[i]
        plat_amount_list.append(plat_amount)
    return plat_amount_list

if __name__ == "__main__":

    plats = list (collection_plats.find({}, {"_id":1, "cr_id":1, "cr_name":1}))
    crs = list(collection_crs.find({}, {"_id":1, "name":1}))
    plats_bill_cor = list(collection_bill_cor.find({},{"_id":1, "all_bill_dict":1}))
    plats_news_cor = list(collection_news_cor.find({},{"_id":1, "all_news_dict":1}))
    plats_bill_join_cor = list(collection_bill_join_cor.find({},{"_id":1, "all_bill_dict":1}))
    plats_news_pn_cor = list(collection_news_pn_cor.find({},{"_id":1, "all_news_dict":1}))

    for cr in crs:
        cr_dict = {}
        cr_id = cr["_id"]
        cr_name = cr["name"]
        cr_dict["cr_id"] = cr_id
        cr_dict["cr_name"] = cr_name
        ac_value = []
        bill_list = list(collection_bill.find({"$or":[{"proposed_id" : cr_id}, { "petitioned_id" : cr_id}]}, {"_id":1}))
        news_list = list(collection_news.find({"cr_id": cr_id}, {"_id":1}))      


        bill_value_accuracy = []
        bill_join_value_accuracy = []
        news_value_accuracy = []
        news_pn_value_accuracy = []
        for i in range(0, 638, 1): #0~637

            all_bill_dict = plats_bill_cor[i]["all_bill_dict"]
            all_news_dict = plats_news_cor[i]["all_news_dict"]
            all_bill_cor_dict = plats_bill_join_cor[i]["all_bill_dict"]
            all_news_cor_dict = plats_news_pn_cor[i]["all_news_dict"]

            bill_value = 0
            bill_join_value = 0
            for bill_id in bill_list:
                bill_value      = bill_value + all_bill_dict[str(bill_id["_id"])]["cor_value"]
                bill_join_value = bill_join_value + all_bill_cor_dict[str(bill_id["_id"])]["np_cor_value"]
            
            news_value = 0
            news_pn_value = 0
            for news_id in news_list:
                news_value    = news_value + all_news_dict[str(news_id["_id"])]["cor_value"]
                news_pn_value = news_pn_value + all_news_cor_dict[str(news_id["_id"])]["np_cor_value"]

            #comput AR
            if bill_value is not 0:
                bill_value = bill_value/len(bill_list)
            if bill_join_value is not 0:
                bill_join_value = bill_join_value/len(bill_list)
            if news_value is not 0:
                news_value = news_value/len(news_list)
            if news_pn_value is not 0:
                news_pn_value = news_pn_value/len(news_list)

            bill_value_accuracy.append(bill_value)
            bill_join_value_accuracy.append(bill_join_value)
            news_value_accuracy.append(news_value)
            news_pn_value_accuracy.append(news_pn_value)
        #end one cr news, plats get accuracy
        #all value normalize
        plat_bill_cor_list    = attrbuteNormalize(bill_value_accuracy) 
        plat_news_cor_list    = attrbuteNormalize(news_value_accuracy)
        news_p_n_list         = attrbuteNormalize(news_pn_value_accuracy)
        join_bills_list       = attrbuteNormalize(bill_join_value_accuracy)

        #計算每個Attribute的Weight
        attributes_decision = [plat_bill_cor_list, plat_news_cor_list, news_p_n_list, join_bills_list]
        weight_list = findWeightEntropy(attributes_decision)

        #計算 V
        plat_bill_cor = weightProductAttribute(plat_bill_cor_list, weight_list[0])
        plat_news_cor = weightProductAttribute(plat_news_cor_list, weight_list[1])
        news_p_n_cor = weightProductAttribute(news_p_n_list, weight_list[2])
        join_bills_cor = weightProductAttribute(join_bills_list, weight_list[3])

        #總分數
        attributes = [plat_bill_cor, plat_news_cor, news_p_n_cor, join_bills_cor]
        plat_c_list = computeDistanceAnd(attributes)

        plat_c_list_use = []
        for i, plat_c in enumerate(plat_c_list):
            plat_c_list_use.append({"cr_id":plats[i]["cr_id"], "plat_id":plats[i]["_id"], "name":plats[i]["cr_name"], "accuracy":plat_c})
        cr_dict["plat_c_list"] = plat_c_list_use

        print "cr   id : "+ str(cr_id)
        print "save id : "+ str(collection_crs_SAW_compare.save(cr_dict))
        print ""

