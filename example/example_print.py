#encoding=utf-8
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27018/')
db = client['ntp_councilor']
# main_array = ["bill", "news"]
main_array = ["bill"]
json_array = ["1", "2", "3", "4", "5"]

for main in main_array:
    for index in json_array:
        collection_print = db['ntp_platform_'+main+'_cor_example_v'+index]
        print_list = list(collection_print.find().sort("so",-1))
        for print_use in print_list:
            f = open("./example_out/plat_"+main+"_v"+index+".json", "a")
            f.write("id ~~~~~~~~~~~~~~~~~"+"\n")
            f.write(print_use["_id"]+"\n")
            f.write("plat ~~~~~~~~~~~~~~~~~"+"\n")
            f.write(print_use["plat_origin"].encode('utf-8')+"\n")
            f.write(main+" ~~~~~~~~~~~~~~~~~"+"\n")
            if main == "news":
                f.write(print_use["parse_url_name"].encode('utf-8')+"\n")
            else:
                f.write(print_use["description"].encode('utf-8')+"\n")
            f.write("plat term............"+"\n")
            for term in print_use["plat_terms"]:
                f.write(term.encode('utf-8')+" ")
            f.write("\n")
            f.write("news term.........."+"\n")
            for term in print_use[main+"_term"]:
                f.write(term.encode('utf-8')+" ")
            f.write("\n")
            f.write("interArr------------"+"\n")
            for term in print_use["interArr"]:
                f.write(term.encode('utf-8')+" ")
            f.write("\n")
            f.write("pso term=========="+"\n")
            for term in print_use["pso_term"]:
                f.write(term.encode('utf-8')+" ")
            f.write("\n")
            f.write("nso term========"+"\n")
            for term in print_use["nso_term"]:
                f.write(term.encode('utf-8')+" ")
            f.write("\n")
            f.write("----------------"+"\n")
            f.write(" so : "+str(print_use["so"])+"\n")
            f.write("\n")
            f.close()
                
                # break
print "end all"
exit(0)
