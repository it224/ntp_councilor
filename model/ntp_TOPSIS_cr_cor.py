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

collection_crs_TOPSIS_compare = db['ntp_crs_TOPSIS_compare']

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
def findWeight(attributes_decisions):
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

#make Vmj matrix，而且要找出A+的矩陣
def weightProductAttribute(attribute, weight):
    attribute_return = []
    
    #biggest
    bg = 0
    #smalest
    sm = 0

    for value in attribute:
        v_value = value*weight
        attribute_return.append(v_value)

        #找最大的一組
        if v_value>bg:
           bg = v_value 
        #找最小的一組
        if v_value<sm:
            sm - v_value
        
    
    return (attribute_return, bg, sm)

#計算 d+, d-
def computeDistanceAnd(attributes, bestSolution, worestSolution):

    all_plats_use = []

    pbc = attributes[0][0]
    pnc = attributes[1][0]
    npn = attributes[2][0]
    jbs = attributes[3][0]

    pbc_bw = bestSolution[0]
    pnc_bw = bestSolution[1]
    npn_bw = bestSolution[2]
    jbs_bw = bestSolution[3]

    pbc_ww = worestSolution[0]
    pnc_ww = worestSolution[1]
    npn_ww = worestSolution[2]
    jbs_ww = worestSolution[3]
    plat_c_list = []
    for i in range(0, 638, 1): #0~637

        pbc_dis_b_dura = ((pbc[i] - pbc_bw)**2) #一個 attr與最佳的距離
        pnc_dis_b_dura = ((pnc[i] - pnc_bw)**2)
        npn_dis_b_dura = ((npn[i] - npn_bw)**2)
        jbs_dis_b_dura = ((jbs[i] - jbs_bw)**2)
        plat_bdis = pbc_dis_b_dura + pnc_dis_b_dura + npn_dis_b_dura + jbs_dis_b_dura
        plat_bdis = plat_bdis**0.5

        pbc_dis_w_dura = ((pbc[i] - pbc_ww)**2) #一個 attr與最佳的距離
        pnc_dis_w_dura = ((pnc[i] - pnc_ww)**2)
        npn_dis_w_dura = ((npn[i] - npn_ww)**2)
        jbs_dis_w_dura = ((jbs[i] - jbs_ww)**2)
        plat_wdis = pbc_dis_w_dura + pnc_dis_w_dura + npn_dis_w_dura + jbs_dis_w_dura
        plat_wdis = plat_wdis**0.5

        plat_c = plat_wdis/(plat_wdis+plat_bdis)
        plat_c_list.append(plat_c)
    return plat_c_list

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
        weight_list = findWeight(attributes_decision)


        #計算 V, A+, A-
        plat_bill_cor_tuple = weightProductAttribute(plat_bill_cor_list, weight_list[0]) #(plat_bill_cor, plat_bill_cor_b, plat_bill_cor_s)
        plat_news_cor_tuple = weightProductAttribute(plat_news_cor_list, weight_list[1]) #(plat_news_cor, plat_news_cor_b, plat_news_cor_s)
        news_p_n_tuple = weightProductAttribute(news_p_n_list, weight_list[2]) #(news_p_n_cor, news_p_n_b, news_p_n_s)
        join_bills_tuple = weightProductAttribute(join_bills_list, weight_list[3]) #(join_bills_cor, join_bills_b, join_bills_s)

        #A+, A-
        aPlus_list = [plat_bill_cor_tuple[1], plat_news_cor_tuple[1], news_p_n_tuple[1], join_bills_tuple[1]]
        aMinc_list = [plat_bill_cor_tuple[2], plat_news_cor_tuple[2], news_p_n_tuple[2], join_bills_tuple[2]]


        #d+, d-, correlation
        attributes = [plat_bill_cor_tuple, plat_news_cor_tuple, news_p_n_tuple, join_bills_tuple]
        plat_c_list = computeDistanceAnd(attributes, aPlus_list, aMinc_list)

        plat_c_list_use = []
        for i, plat_c in enumerate(plat_c_list):
            plat_c_list_use.append({"cr_id":plats[i]["cr_id"], "plat_id":plats[i]["_id"], "name":plats[i]["cr_name"], "accuracy":plat_c})
        cr_dict["plat_c_list"] = plat_c_list_use

        print "cr   id : "+ str(cr_id)
        print "save id : "+ str(collection_crs_TOPSIS_compare.save(cr_dict))
        print ""

