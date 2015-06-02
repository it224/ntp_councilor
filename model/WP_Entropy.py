#encoding=utf-8
'''
FUZZY TOPSIS model
四個attribute
'''
from __future__ import division
import re
import os
import math
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
ntp_crs                    = db["ntp_platform"]                 #所有政見638筆  ntp_crs
ntp_platform_bill_cor      = db["ntp_platform_bill_extend_cor"]     #政見議案關係   ntp_platform_bill_cor
ntp_platform_news_cor      = db["ntp_platform_news_extend_cor"]      #政見新聞關係   ntp_platform_news_cor
ntp_platform_news_pn_cor   = db["ntp_platform_news_pn_extend_cor"]   #政見新聞正負面  ntp_platform_news_pn_cor
ntp_platform_bill_join_cor = db["ntp_platform_bill_join_extend_cor"] #政見議案參與數  ntp_platform_bill_join_cor
ntp_platform_WP            = db["ntp_platform_WP_entropy_extend"]

#把每個 attr 做正規化
def attrbuteNormalize(attribute, key):
    all_count = 0.0
    attribute_return = []
    
    for attr_ele in attribute:
        value = attr_ele[key] #有分數的key
        all_count = all_count + value

    for attr_ele in attribute:
        one_element = attr_ele
        value = attr_ele[key] #有分數的key
        one_element["x_nomailze"] = value/all_count #正規化
        attribute_return.append(one_element)
    return attribute_return

#用entropy 找出每個 attribute 的 weight
def findWeightEntropy(attributes_decisions):
    weight_list = []
    h0 = -1*(math.log(638))**-1
    d_all = []
    for j in range(0, 4, 1):
        h_duration = 0.0
        for i in range(0, 637, 1):
            if attributes_decisions[j][i]["x_nomailze"] != 0.0:
                h_duration = h_duration + attributes_decisions[j][i]["x_nomailze"] * math.log(attributes_decisions[j][i]["x_nomailze"])
        d_use = 1 - h0*h_duration
        d_all.append(d_use)
    
    d_count = 0
    for j in range(0, len(d_all), 1):
        d_count = d_count + d_all[j]
    w_all = []
    for j in range(0, len(d_all), 1):
        w_all.append(d_all[j]/d_count)

    print "w_all"
    print len(w_all)
    print w_all

    return w_all


#make Vmj matrix, 
def weightProductAttribute(attribute, weight):
    attribute_return = []
    
    for attr_ele in attribute:
        one_element = attr_ele
        value = attr_ele["x_nomailze"] #正規化後的分數
        v_value = value ** weight
        one_element["v"] = v_value
        attribute_return.append(one_element)
    
    return attribute_return

#計算該政見總和分數
def computeDistanceAnd(attributes):

    all_plats_use = []

    pbc = attributes[0]
    pnc = attributes[1]
    npn = attributes[2]
    jbs = attributes[3]

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

        
        dic["plat_amount"] = pbc[i]["v"] + pnc[i]["v"] + npn[i]["v"] + jbs[i]["v"]
        print "plat number i "+ str(i)
        print dic
        ntp_platform_WP.save(dic)
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

#計算每個Attribute的Weight
attributes_decision = [plat_bill_cor, plat_news_cor, news_p_n, join_bills]
weight_list = findWeightEntropy(attributes_decision)

#計算 V
plat_bill_cor = weightProductAttribute(plat_bill_cor, weight_list[0])
plat_news_cor = weightProductAttribute(plat_news_cor, weight_list[1])
news_p_n_cor = weightProductAttribute(news_p_n, weight_list[2])
join_bills_cor = weightProductAttribute(join_bills, weight_list[3])

#總分數
attributes = [plat_bill_cor, plat_news_cor, news_p_n_cor, join_bills_cor]
computeDistanceAnd(attributes)
