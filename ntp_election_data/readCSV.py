#encoding=utf-8
import csv
import re
from pymongo import MongoClient
from bson.objectid import ObjectId


client   		 = MongoClient('mongodb://localhost:27018/')
db     			 = client['ntp_councilor']
cr_collection    = db["ntp_crs"]

crs = list(cr_collection.find({}, {"name":1}))

def findUp(row):
	if row["當選註記"] is not " ":
		cr = list(cr_collection.find({"name":row["姓名"]}))
		array.append(row["姓名"])
		# if len(cr) is not 0:
			# print row["姓名"]
			# array.append(row["姓名"])
			# print ""
		# else:
		# 	print row["姓名"]
		

use_arr = ['ground_99', 'highland_99', 'normal_99']
array = []
for place in use_arr:
	use = 'ntp_'+place+'.csv'
	print use
	with open(use) as csvfile:
		
		reader = csv.DictReader(csvfile)
		place = False
		for row in reader:
			if re.match('新北市', row['地區']):
				place = True
				findUp(row)
			elif place == True and row['地區'] == "":
				findUp(row)
			else:
				place = False
		print len(array)
cr_array = []
for cr in crs:
	cr_array.append(cr["name"].encode('utf-8'))
cr_list = list(set(array).difference(set(cr_array)))
for cr in cr_list:
	print cr
print ""
cr_list = list(set(cr_array).difference(set(array)))
for cr in cr_list:
	print cr