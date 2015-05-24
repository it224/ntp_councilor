#encoding=utf-8
'''
_id    : id
word   : 一個字
smaeIds: [{word:"", id: ""}]
'''
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['same_word']
collection = db["same_word"]

def returnFile():
	with open("./chinese_word_extend_utf8.txt") as f:
		content = f.readlines()
	return content

def findOneOrCreate(word):
	result = collection.find_one({"word":word})
	if result:
		return (result["_id"], word)
	else:
		dic = {"word":word, "sameIds":[]}
		id_use = collection.save(dic)
		return (id_use, word)

def addToArray(id_word, same_ids):
	word = collection.find_one({"_id":id_word[0]})
	new_array = []
	for arr in word["sameIds"]:
		new_array.append(tuple(arr))
	same_list = list(set(new_array) | set(same_ids))
	same_list.remove(id_word)
	word["sameIds"] = same_list
	print word["sameIds"]
	collection.save(word)

def findSame(words):
	same_word_list = []
	for word in words:
		same_word_list.append(findOneOrCreate(word))
	print same_word_list
	for same_word_id in same_word_list:
		addToArray(same_word_id, same_word_list)

def prase_same_word():
	word_list = returnFile()
	for word in word_list:
		words = word.split(" ")
		if words[0][7] == u"=":
			words.pop(0)
			findSame(words)
	print "end"
	exit(0)
		

prase_same_word()
