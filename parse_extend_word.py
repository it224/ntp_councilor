#encoding=utf-8
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
		return result["_id"]
	else:
		dic = {"word":word, "sameIds":[]}
		id_use = collection.save(dic)
		return id_use

def addToArray(id, same_ids):
	word = collection.find_one({"_id":id})
	same_list = list(set(word["sameIds"]) | set(same_ids))
	same_list.remove(id)
	word["sameIds"] = same_list
	collection.save(word)

def findSame(words):
	same_word_list = []
	for word in words:
		same_word_list.append(findOneOrCreate(word))
	for same_word_id in same_word_list:
		addToArray(same_word_id, same_word_list)

def prase_same_word():
	word_list = returnFile()
	count = 0
	for word in word_list:
		words = word.split(" ")
		if words[0][7] == u"=":
			words.pop(0)
			findSame(words)
			count = count + 1
		if count == 10:
			print("10 end")
			break

prase_same_word()
