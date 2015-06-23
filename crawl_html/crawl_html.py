#encoding=utf-8
import sys
import urllib, urllib2
from urllib import quote, unquote
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
import requests
import datetime
from time import sleep

mainURL = 'http://udndata.com/'
client = MongoClient('mongodb://localhost:27017/')
db = client['councilor']
collection = db['ntp_crs']
crs = collection.find()
crs_list = list(crs)
news_url_list_collection = db['ntp_news_url_list']
# news_collection = db['new']
s = requests.Session()
s.auth = ('user', 'pass')
s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) \
                  AppleWebKit/537.36 (KHTML, like Gecko) \
                  Chrome/35.0.1916.153 Safari/537.36'})

def parseNewsList(news_list_url):
	data = s.get(news_list_url)
	soup = BeautifulSoup(data.text)
	tables = soup.find_all('table', {"width" :"95%"})
	if len(tables) > 0:
		try:
			for index, use in enumerate(tables):
				try:
					td_content = use.find('td',{"class":"title02"})
					td_date = use.find('span',{"class":"date"})
					date = datetime.datetime.strptime(td_date.text.encode('utf-8').split("．")[0], '%Y-%m-%d')
					
					print td_content.a.text.encode('utf-8')
					print td_content.a['href']
					print td_date
					print date
					print name
					print ""
					
					
					one_news_list = {
						"parse_url_name": td_content.a.text.encode('utf-8'),
						"parse_url": td_content.a['href'],
						"cr": name,
						"cr_id": cr["_id"],
						"date": date
					}
					print "one_news_list"
					print one_news_list
					news_url_list_collection.save(one_news_list)
				except Exception, e:
					print "not target element"
					pass
					

			# find next page
			nextPage = ""
			for span in soup.findAll('span', {"class":"s"}):
				for a in span.findAll('a'):
					if unicode(a.string).encode('utf-8') == "下一頁":
						if len(nextPage) == 0:
							# print a["href"]
							nextPage = a["href"]
							break
			if(len(nextPage)!=0):
				parseNewsList(mainURL+nextPage)
			else:
				print "no next page"
				sleep(10)
				return
		except Exception, e:
			print e
			print "error no any element"
			print name.encode("utf-8")
			sleep(30)
			return
	else:
		print "error no any element"
		sleep(30)
		return


def parseNewsContent(news_Content_url, cr, cr_id):
	# one_news = urllib2.urlopen(news_Content_url)
	one_news = s.get(news_Content_url)
	soup_one_data = BeautifulSoup(one_news.text)
	print ""
	# print soup_one_data

	title = ""
	for span_title in soup_one_data.findAll('span', {"class":"story_title"}):
		title = title + " " + getUtf8String(removeHtmlTag(span_title.string))

	sub_title = ""
	for sub_span_title in soup_one_data.findAll('span', {"class":"story_sub_title"}):
		sub_title = getUtf8String(sub_span_title)
	content = ""
	for td in soup_one_data.findAll('td', {"class":"story"}):
		for p in td.findAll('p'):
			content = content + " " + getUtf8String(removeHtmlTag(p.string))

	one_news_save = {
		"title": title,
		"sub_title": sub_title,
		"content": content,
		"url":news_Content_url,
		"cr":cr,
		"cr_id": cr_id
	}
	# print one_news_save

def getUtf8String(strUse):
	return unicode(strUse).encode('utf-8')

def removeHtmlTag(strWithTag):
	p = re.compile(r"(?i)<\/?\w+((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>")
	return p.sub('', strWithTag)


if __name__ == '__main__':
	# s.get("http://0-udndata.com.millennium.lib.ntust.edu.tw/ndapp/member/MbFixLogin?344114965", verify=False)
	# data =s.get("http://0-udndata.com.millennium.lib.ntust.edu.tw/ndapp/Index", verify=False)
	# print data.text.encode('utf-8')
	
	for cr in crs_list:
		try:
			print cr["name"].encode('utf-8')
			if cr["name"] == u"夷將‧拔路兒 Icyang‧Parod":
				name = cr["name"].split(" ")[0]
				name = re.sub(u"‧", " ", name)
				print name.encode('utf-8')
			else:
				name = cr["name"]
			# name = u"林世宗"

			use = name + u"+日期>=20100101+日期<=20141225+報別=聯合報|經濟日報|聯合晚報|Upaper"
			use =  quote(use.encode('big5'))
			url = "http://udndata.com/ndapp/Searchdec2007?udndbid=udnfree&page=1&SearchString="+use+"&sharepage=50&select=1&kind=2"
			# url = "http://0-udndata.com.millennium.lib.ntust.edu.tw/ndapp/Searchdec2007?udndbid=udndata&page=1&SearchString="+use+"&sharepage=50&select=1&kind=2"
			# url = "http://0-udndata.com.millennium.lib.ntust.edu.tw/ndapp/member/MbFixLogin?041878920"
			print url
		# 	print ""
			# if cr["name"].encode('utf-8') == "吳思瑤":
			parseNewsList(url)
		except Exception, e:
			print e
			f = open("errorName.txt", 'a')
			f.write(name+"\n")
			f.close()
	print "finish"
	exit(0)