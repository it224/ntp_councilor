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
def weightProductAttribute(attribute, weight):
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
(plat_bill_cor, plat_bill_cor_b, plat_bill_cor_s)  = weightProductAttribute(plat_bill_cor, weight_fuzzy_list["VH"]) 
(plat_news_cor, plat_news_cor_b, plat_news_cor_s)  = weightProductAttribute(plat_news_cor, weight_fuzzy_list["VH"])
(news_p_n, news_p_n_b, news_p_n_s)                 = weightProductAttribute(news_p_n, weight_fuzzy_list["H"])
(join_bills, join_bills_b, join_bills_s)           = weightProductAttribute(join_bills, weight_fuzzy_list["H"])
#A+, A-
aPlus = [plat_bill_cor_b, plat_news_cor_b, news_p_n_b, join_bills_b]
aMinc = [plat_bill_cor_s, plat_news_cor_s, news_p_n_s, join_bills_s]

