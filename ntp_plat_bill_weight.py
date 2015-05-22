#encoding=utf-8
# 計算一個政見與多個議案相關分數後的打程度
# 特殊的地方是有八個結果 分兩組
# 第一組是議案平均分佈的表準差在25%(0.172798086405)以上當作是有相關的 ntp_plat_bill_cor_weight_one_fourth
# 第二組是議案平均分佈的表準差在1/3(0.153573211884)以上當作是有相關的 ntp_plat_bill_cor_weight_one_third
# 四個值中
#     final_plat_bills_value              是加上 cor_value （覆議*0.5）最後除以有相關的議案總數
#     final_plat_bills_value_mince        是加上 cor_value （覆議*0.5）但是有相關卻沒提/覆的議案會扣分最後除以有相關的議案總數
#     final_plat_bills_value_no_cor       是有相關且提議則+2、覆議+1 最後除以有相關的議案總數
#     final_plat_bills_value_no_cor_mince 是有相關且提議則+2、覆議+1、沒提議覆議-1 最後除以有相關的議案總數

from __future__ import division
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['councilor']
collection_bills = db["ntp_bills"]
collection_cr_plat = db['ntp_platform']
collection_plat_bill = db['ntp_plat_bill_cor']
collection_plat_bill_weight = db['ntp_plat_bill_cor_weight_one_fourth']

if __name__ == "__main__":
    plat_bill_list = list(collection_plat_bill.find())
    for plat_bill in plat_bill_list:
        cr_id = plat_bill["cr_id"]
        bill_list = plat_bill["bill_list"]
        final_plat_bills_value = 0
        final_plat_bills_value_no_cor = 0
        final_plat_bills_value_mince = 0
        final_plat_bills_value_no_cor_mince = 0
        all_relation_bills = 0
        for bill in bill_list:
            bill_use = list(collection_bills.find({"_id":bill["bill_id"]}))[0]
            # 25% -> 0.172798086405
            # 1/3 -> 0.153573211884
            if bill["cor_value"] > 0.172798086405:
                all_relation_bills = all_relation_bills+1
                if cr_id in bill_use["proposed_id"]:
                    final_plat_bills_value = final_plat_bills_value + bill["cor_value"]
                    final_plat_bills_value_mince = final_plat_bills_value_mince + bill["cor_value"]
                    final_plat_bills_value_no_cor = final_plat_bills_value_no_cor + 2
                    final_plat_bills_value_no_cor_mince = final_plat_bills_value_no_cor_mince +2
                elif cr_id in bill_use["petitioned_id"]:
                    final_plat_bills_value = final_plat_bills_value + bill["cor_value"]*0.5
                    final_plat_bills_value_mince = final_plat_bills_value_mince + bill["cor_value"] *0.5
                    final_plat_bills_value_no_cor = final_plat_bills_value_no_cor + 1
                    final_plat_bills_value_no_cor_mince = final_plat_bills_value_no_cor_mince+1
                else:
                    final_plat_bills_value_mince = final_plat_bills_value_mince + bill["cor_value"] *-1
                    final_plat_bills_value_no_cor_mince = final_plat_bills_value_no_cor_mince -1
        
        if all_relation_bills is not 0:
            final_plat_bills_value = final_plat_bills_value/ all_relation_bills
            final_plat_bills_value_no_cor = final_plat_bills_value_no_cor/ all_relation_bills
            final_plat_bills_value_mince = final_plat_bills_value_mince/ all_relation_bills
            final_plat_bills_value_no_cor_mince = final_plat_bills_value_no_cor_mince /all_relation_bills
        print "name : "+plat_bill["name"].encode('utf-8')
        print plat_bill["plat_id"]
        print "weight_ac : {0}".format(final_plat_bills_value)
        print "origin_ac : {0}".format(plat_bill["origin_ac"])
        print "weight_ac_no_cor : {0}".format(final_plat_bills_value_no_cor)
        print "weight_ac_mince : {0}".format(final_plat_bills_value_mince)
        print "weight_ac_no_cor_mince : {0}".format(final_plat_bills_value_no_cor_mince)
        plat_bill["weight_ac_with_cor"] = final_plat_bills_value
        plat_bill["weight_ac"] = final_plat_bills_value_no_cor
        plat_bill["weight_ac_with_cor_mince"] = final_plat_bills_value_mince
        plat_bill["weight_ac_mince"] = final_plat_bills_value_no_cor_mince
        collection_plat_bill_weight.save(plat_bill)
        print ""