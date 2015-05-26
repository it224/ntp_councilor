#encoding=utf-8
'''
FUZZY TOPSIS model
四個attribute
'''
from __future__ import division
import re
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

weight_fuzzy_list = {"VL":[0.0, 0.0, 0.1], "L":[0, 0.1, 0.3], "ML":[0.1, 0.3, 0.5], "M":[0.3, 0.5, 0.7], "MH":[0.5, 0.7, 0.9], "H":[0.7, 0.9, 1.0], "VH":[0.9, 1.0, 1.0]}

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
ntp_crs                    = db["ntp_platform"]                 #所有政見638筆  ntp_crs
ntp_platform_bill_cor      = db["ntp_platform_bill_cor"]     #政見議案關係   ntp_platform_bill_cor
ntp_platform_news_cor      = db["ntp_platform_news_cor"]      #政見新聞關係   ntp_platform_news_cor
ntp_platform_news_pn_cor   = db["ntp_platform_news_pn_cor"]   #政見新聞正負面  ntp_platform_news_pn_cor
ntp_platform_bill_join_cor = db["ntp_platform_bill_join_cor"] #政見議案參與數  ntp_platform_bill_join_cor
ntp_platform_TOPSIS        = db["ntp_platform_TOPSIS"]

#把每個 attr 做正規化
def attrbuteNormalize(attribute, key):
    all_count = 0.0
    attribute_return = []
    
    for attr_ele in attribute:
        value = attr_ele[key] #第四個key, 就是有分數的那個
        all_count = all_count + value

    for attr_ele in attribute:
        one_element = attr_ele
        value = attr_ele[key] #第四個key, 就是有分數的那個
        one_element["x_nomailze"] = value/all_count
        attribute_return.append(one_element)
    return attribute_return

#四個屬性 plat_bill_cor:VH, plat_news_cor:VH, news_p_n:H, join_bills:H
#make Vmj matrix，而且要找出A+的矩陣
def weightProductAttribute(attribute, weight, key):
    attribute_return = []
    
    #biggest
    bL = 0
    bM = 0
    bR = 0
    #smalest
    sL = 0
    sM = 0
    sR = 0

    for attr_ele in attribute:
        one_element = attr_ele
        value = attr_ele["x_nomailze"] #正規化後的分數
        # value = attr_ele[key]
        left  = value* weight[0]
        mid   = value* weight[1]
        right = value* weight[2]
        one_element["v"] = [left, mid, right]
        attribute_return.append(one_element)

        #找最大的一組
        if left > bL:
            bL = left
        if mid > bM:
            bM = mid
        if right > bR:
            bR = right
        #找最小的一組
        if left < sL:
            sL = left
        if mid < sM:
            sM = mid
        if right < sR:
            sR = right
    b_attr = [bL, bM, bR]
    m_attr = [sL, sM, sR]
    
    return (attribute_return, b_attr, m_attr)

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
    for i in range(0, 638, 1): #0~637

        dic = {"_id":pbc[i]["_id"], "name":pbc[i]["name"], "cr_id":pbc[i]["cr_id"]}
        
        dic["pbc_x"] = pbc[i]["accuracy"]
        dic["pbc_x_normalize"] = pbc[i]["x_nomailze"]
        dic["pbc_v"] = pbc[i]["v"]
        
        dic["pnc_x"] = pnc[i]["accuracy"]
        dic["pnc_x_normalize"] = pnc[i]["x_nomailze"]
        dic["pnc_v"] = pnc[i]["v"]

        dic["npn_x"] = npn[i]["all_so"]
        dic["npn_x_normalize"] = npn[i]["x_nomailze"]
        dic["npn_v"] = npn[i]["v"]

        dic["jbs_x"] = jbs[i]["join_count"]
        dic["jbs_x_normalize"] = jbs[i]["x_nomailze"]
        dic["jbs_v"] = jbs[i]["v"]

        pbc_dis_b_dura = ((1/3)*((pbc[i]["v"][0] - pbc_bw[0])**2 + (pbc[i]["v"][1] - pbc_bw[1])**2 + (pbc[i]["v"][2] - pbc_bw[2])**2)) #一個 attr與最佳的距離
        pnc_dis_b_dura = ((1/3)*((pnc[i]["v"][0] - pnc_bw[0])**2 + (pnc[i]["v"][1] - pnc_bw[1])**2 + (pnc[i]["v"][2] - pnc_bw[2])**2))
        npn_dis_b_dura = ((1/3)*((npn[i]["v"][0] - npn_bw[0])**2 + (npn[i]["v"][1] - npn_bw[1])**2 + (npn[i]["v"][2] - npn_bw[2])**2))
        jbs_dis_b_dura = ((1/3)*((jbs[i]["v"][0] - jbs_bw[0])**2 + (jbs[i]["v"][1] - jbs_bw[1])**2 + (jbs[i]["v"][2] - jbs_bw[2])**2))
        plat_bdis = pbc_dis_b_dura + pnc_dis_b_dura + npn_dis_b_dura + jbs_dis_b_dura
        plat_bdis = plat_bdis**0.5

        pbc_dis_w_dura = ((1/3)*((pbc[i]["v"][0] - pbc_ww[0])**2 + (pbc[i]["v"][1] - pbc_ww[1])**2 + (pbc[i]["v"][2] - pbc_ww[2])**2)) #一個 attr與最佳的距離
        pnc_dis_w_dura = ((1/3)*((pnc[i]["v"][0] - pnc_ww[0])**2 + (pnc[i]["v"][1] - pnc_ww[1])**2 + (pnc[i]["v"][2] - pnc_ww[2])**2))
        npn_dis_w_dura = ((1/3)*((npn[i]["v"][0] - npn_ww[0])**2 + (npn[i]["v"][1] - npn_ww[1])**2 + (npn[i]["v"][2] - npn_ww[2])**2))
        jbs_dis_w_dura = ((1/3)*((jbs[i]["v"][0] - jbs_ww[0])**2 + (jbs[i]["v"][1] - jbs_ww[1])**2 + (jbs[i]["v"][2] - jbs_ww[2])**2))
        plat_wdis = pbc_dis_w_dura + pnc_dis_w_dura + npn_dis_w_dura + jbs_dis_w_dura
        plat_wdis = plat_wdis**0.5

        plat_c = plat_wdis/(plat_wdis+plat_bdis)

        dic["plat_bdis"] = plat_bdis
        dic["plat_wdis"] = plat_wdis
        dic["plat_c"] = plat_c
        print "plat number i "+ str(i)
        print dic
        ntp_platform_TOPSIS.save(dic)
        print ""
        



#make attribute matrix  m=638, n=4
#638個排名
all_plats        = list(ntp_crs.find({}, {"_id":1, "cr_id":1, "plat_origin":1, "cr_name":1 }))
#4個屬性
plat_bill_cor    = list(ntp_platform_bill_cor.find({}, {"_id":1, "cr_id":1, "name":1, "accuracy":1}))
plat_news_cor    = list(ntp_platform_news_cor.find({}, {"_id":1, "cr_id":1, "name":1, "accuracy":1}))
news_p_n         = list(ntp_platform_news_pn_cor.find({}, {"_id":1, "cr_id":1, "name":1, "all_so":1}))
join_bills       = list(ntp_platform_bill_join_cor.find({}, {"_id":1, "cr_id":1, "name":1, "join_count":1}))
#每個值正規化
plat_bill_cor    = attrbuteNormalize(plat_bill_cor, "accuracy") 
plat_news_cor    = attrbuteNormalize(plat_news_cor, "accuracy")
news_p_n         = attrbuteNormalize(news_p_n, "all_so")
join_bills       = attrbuteNormalize(join_bills, "join_count")
#計算 V, A+, A-
plat_bill_cor_tuple = weightProductAttribute(plat_bill_cor, weight_fuzzy_list["VH"], "accuracy") #(plat_bill_cor, plat_bill_cor_b, plat_bill_cor_s)
plat_news_cor_tuple = weightProductAttribute(plat_news_cor, weight_fuzzy_list["VH"], "accuracy") #(plat_news_cor, plat_news_cor_b, plat_news_cor_s)
news_p_n_tuple = weightProductAttribute(news_p_n, weight_fuzzy_list["H"], "all_so") #(news_p_n, news_p_n_b, news_p_n_s)
join_bills_tuple = weightProductAttribute(join_bills, weight_fuzzy_list["H"], "join_count") #(join_bills, join_bills_b, join_bills_s)
#A+, A-
aPlus_list = [plat_bill_cor_tuple[1], plat_news_cor_tuple[1], news_p_n_tuple[1], join_bills_tuple[1]]
aMinc_list = [plat_bill_cor_tuple[2], plat_news_cor_tuple[2], news_p_n_tuple[2], join_bills_tuple[2]]

#d+, d-, correlation
attributes = [plat_bill_cor_tuple, plat_news_cor_tuple, news_p_n_tuple, join_bills_tuple]
computeDistanceAnd(attributes, aPlus_list, aMinc_list)
