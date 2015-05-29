#encoding=utf-8
import csv
import re
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['ntp_councilor']
collection = db['same_word_my_country']

# space 是 \xe3\x80\x80
#、 是 \xef\xb9\x91
#、 也是 \xe3\x80\x81

def removeSpace(sameWord):
	if '\xe3\x80\x80' in sameWord:
		sameWord_return = []
		sameWord_list = sameWord.split('\xe3\x80\x80')
		for use in sameWord_list:
			if " " in use:
				use.replace(" ", "")
			sameWord_return.append(use)
		return(type(sameWord_return), sameWord_return)
	elif " " in sameWord:
		sameWord_return = []
		sameWord_list = sameWord.split(' ')
		for use in sameWord_list:
			if " " in use:
				use.replace(" ", "")
			sameWord_return.append(use)
		return(type(sameWord_return), sameWord_return)
	else:
		return(type(sameWord), sameWord)

def removeSimbolList(sameWord_list):
	sameWord_returnList = []
	
	for sameWord in sameWord_list:
		if len(sameWord)>0:
			sameWordType, sameWord_use = removeSimbolNumber(sameWord)
			if sameWordType is type(''):
				sameWord_returnList.append(sameWord_use)
			if sameWordType is type([]):
				sameWord_returnList.extend(sameWord_use)
	return(type(sameWord_returnList), sameWord_returnList)

def removeSimbolNumber(sameWord):
	if "." in sameWord:
		sameWord_list = sameWord.split('.')
		for same_compare in sameWord_list:
			if len(same_compare) > 1:
				sameWord = same_compare
				break

	if '\xef\xb9\x91' in sameWord:
		sameWord = sameWord.split('\xef\xb9\x91')
	if '\xe3\x80\x81' in sameWord:
		sameWord = sameWord.split('\xe3\x80\x81')
	return (type(sameWord), sameWord)

fileNameList = [1,2,3]
for file_number in fileNameList:
	with open('dict_revised_2014_20150303_'+str(file_number)+'.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if len(row["相似詞"]) is not 0:
				sameWordtype, sameWord = removeSpace(row["相似詞"])
				if sameWordtype is type(''):
					sameWordtype, sameWord = removeSimbolNumber(sameWord)
				elif sameWordtype is type([]):
					sameWordtype, sameWord = removeSimbolList(sameWord)

				words_array = []
				print row["字詞名"]+" : "+ row["相似詞"]
				if sameWordtype is type([]):
					for word in sameWord:
						print word
					words_array.extend(sameWord)
				else:
					print sameWord
					words_array.append(sameWord)
				print ""
				dic = {"word":row["字詞名"], "same_word":words_array}
				print collection.save(dic)