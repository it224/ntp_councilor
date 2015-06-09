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

db = client['ntp_councilor']
collection_crs     = db['ntp_crs']

collection_bill_cor = db['ntp_platform_bill_cor']
collection_news_cor = db['ntp_platform_news_cor']
collection_bill_join_cor = db['ntp_platform_bill_join_cor']
collection_news_pn_cor = db['ntp_platform_news_pn_cor']

collection_bill               = db['ntp_bills']
collection_news               = db['ntp_news_url_list_ckip']

collection_topsis_each_cr = db['ntp_platform_topsis_each_cor']

weight = [0.26572995922121334, 0.1712942571414487, 0.24504991347682614, 0.3179258701605118]
best   = [0.0010035056237514398, 0.0006300605893592465, 0.0011283455338391207, 0.001350507386932311]
worest = [0, 0, 0, 0]

if __name__ == "__main__":
    crs = list(collection_crs.find())
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

            #normalize
            if bill_value is not 0:
                bill_value = bill_value/len(bill_list)
            if bill_join_value is not 0:
                bill_join_value = bill_join_value/len(bill_list)
            if news_value is not 0:
                news_value = news_value/len(news_list)
            if news_pn_value is not 0:
                news_pn_value = news_pn_value/len(news_list)

            #product weight
            bill_value = bill_value * weight[0]
            news_value = news_value * weight[1]
            news_pn_value = news_pn_value * weight[2]
            bill_join_value = bill_join_value * weight[3]
            print bill_value
            print news_value
            print news_pn_value
            print bill_join_value
            

            #compute C
            pbc_dis_b_dura = ((bill_value - best[0])**2) #一個 attr與最佳的距離
            pnc_dis_b_dura = ((news_value - best[1])**2)
            npn_dis_b_dura = ((news_pn_value - best[2])**2)
            jbs_dis_b_dura = ((bill_join_value - best[3])**2)
            plat_bdis = pbc_dis_b_dura + pnc_dis_b_dura + npn_dis_b_dura + jbs_dis_b_dura
            plat_bdis = plat_bdis**0.5

            pbc_dis_w_dura = ((bill_value - worest[0])**2) #一個 attr與最佳的距離
            pnc_dis_w_dura = ((news_value - worest[1])**2)
            npn_dis_w_dura = ((news_pn_value - worest[2])**2)
            jbs_dis_w_dura = ((bill_join_value - worest[3])**2)
            plat_wdis = pbc_dis_w_dura + pnc_dis_w_dura + npn_dis_w_dura + jbs_dis_w_dura
            plat_wdis = plat_wdis**0.5

            plat_c = plat_wdis/(plat_wdis+plat_bdis)
            print plat_c
            print ""
            ac_dict = {"plat_id": plats_bill_cor[i]["_id"], "plat_c":plat_c}
            ac_value.append(ac_dict)
            break
        cr_dict["ac_value"] = ac_value
        # collection_topsis_each_cr.save(cr_dict)
