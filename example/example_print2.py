#encoding=utf-8
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
main_array = ["bill", "news"]
# main_array = ["bill"]

for main in main_array:
    collection_print_v1 = db['ntp_platform_'+main+'_cor_example_v1']
    collection_print_v2 = db['ntp_platform_'+main+'_cor_example_v2']
    collection_print_v3 = db['ntp_platform_'+main+'_cor_example_v3']
    collection_print_v4 = db['ntp_platform_'+main+'_cor_example_v4']
    collection_print_v5 = db['ntp_platform_'+main+'_cor_example_v5']
    print_list_v1 = list(collection_print_v1.find())
    # print_list_v2 = list(collection_print_v2.find())
    # print_list_v3 = list(collection_print_v3.find())
    # print_list_v4 = list(collection_print_v4.find())
    # print_list_v5 = list(collection_print_v5.find())
    for i in range(len(print_list_v1)):

        id_use = print_list_v1[i]["_id"]
        v2 = list(collection_print_v2.find({"_id":id_use}))[0]
        v3 = list(collection_print_v3.find({"_id":id_use}))[0]
        v4 = list(collection_print_v4.find({"_id":id_use}))[0]
        v5 = list(collection_print_v5.find({"_id":id_use}))[0]

        f = open("./example_out/plat_"+main+".json", "a")
        f.write("id ~~~~~~~~~~~~~~~~~"+"\n")
        f.write(print_list_v1[i]["_id"]+"\n")
        f.write("plat ~~~~~~~~~~~~~~~~~"+"\n")
        f.write(print_list_v1[i]["plat_origin"].encode('utf-8')+"\n")
        f.write(main+" ~~~~~~~~~~~~~~~~~"+"\n")
        if main == "news":
            f.write(print_list_v1[i]["parse_url_name"].encode('utf-8')+"\n")
        else:
            f.write(print_list_v1[i]["description"].encode('utf-8')+"\n")
        f.write("plat term............"+"\n")
        for term in print_list_v1[i]["plat_terms"]:
            f.write(term.encode('utf-8')+" ")
        f.write("\n")
        f.write("news term.........."+"\n")
        for term in print_list_v1[i][main+"_term"]:
            f.write(term.encode('utf-8')+" ")
        f.write("\n")
        f.write("interArr------------"+"\n")
        for term in print_list_v1[i]["interArr"]:
            f.write(term.encode('utf-8')+" ")
        f.write("\n")
        f.write("pso term=========="+"\n")
        for term in print_list_v1[i]["pso_term"]:
            f.write(term.encode('utf-8')+" ")
        f.write("\n")
        f.write("nso term========"+"\n")
        for term in print_list_v1[i]["nso_term"]:
            f.write(term.encode('utf-8')+" ")
        f.write("\n")
        f.write("----------------"+"\n")
        f.write(" so_v1 : "+str(print_list_v1[i]["so"])+" so_v2 : "+str(v2["so"])+" so_v3 : "+str(v3["so"])+" so_v4 : "+str(v4["so"])+" so_v5 : "+str(v5["so"])+ "\n")
        f.write("\n")
        f.close()
                
print "end all"
exit(0)
