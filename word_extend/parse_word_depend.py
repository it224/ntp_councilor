#encoding=utf-8
from pymongo import MongoClient
from bson.objectid import ObjectId
'''
_id        : id
word   	   : 一個字
word_depend: Aa01A01=
'''
client = MongoClient('mongodb://localhost:27017/')
db = client['same_word']
collection = db["word_depend"]

def returnFile():
	with open("./chinese_word_extend_utf8.txt") as f:
		content = f.readlines()
	return content

def saveMongo(word_depend, words):
	for word in words:
		dic = {"word_depend": word_depend, "word":word}
		print dic
		collection.save(dic)		


def prase_same_word():
	word_list = returnFile()
	for word in word_list:
		words = word.split(" ")
		word_depend = words[0]
		words.pop(0)
		saveMongo(word_depend, words)
	print "end"
	exit(0)
		

prase_same_word()
