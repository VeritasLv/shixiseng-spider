import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import time 
import re
import random
import pymongo
from config import *
from urllib.parse import urlencode


client = pymongo.MongoClient('localhost')
db = client['shixiseng']

#思路：
#找到每一条找平信息的URL，在去解析
def get_page_html(page,keyword):
	#获取索引页的HTML
	query_data = {'k':keyword,'p':page}
	url = 'https://www.shixiseng.com/interns/' + AREA +'?'+urlencode(query_data)

	try:
		response = requests.get(url,headers=HEADERS)
		if response.status_code == 200:
			return response.text
		return None
	except Exception:
		print('请求索引页失败' + url)
		return None
def get_onepage_detail_url(html):
	#获取一页索引页中所有的detailURL
	doc = pq(html)
	items = doc('.font .info1').items()
	# print(items)
	url_append_list = []
	for item in items:
		url_append_list.append(item('.name').attr('href'))
	return url_append_list
def get_detail_html(url):
	#获取详情页的HTML
	try:
		response = requests.get(url,headers=HEADERS)
		if response.status_code == 200:
			return response.text
		return None
	except Exception:
		print('请求详情页失败' + url)
		return None
def parse_detail_page(html):
	#解析详情页
	doc = pq(html)
	
	position = doc('.new_job_name').text().strip(),
	update_time = doc('.job_date').text().strip(),
	company = doc('.job_com_name').text().strip(),
	salary = doc('.job_money.cutom_font').text().strip(),
	academic = doc('.job_academic').text().strip(),
	day_per_week = doc('.job_week.cutom_font').text().strip(),
	duration = doc('.job_time.cutom_font').text().strip(),

	job_content = doc('.job_detail p').text()
	address = doc('.com_position').text()

	info = {
	'position':position,
	'update_time':update_time,
	'company':company,
	'salary':salary,
	'academic':academic,
	'day_per_week':day_per_week,
	'duration':duration,
	'job_content':job_content,
	'address':address
	}
	return info
	
def get_last_pagenum(html):
	doc = pq(html)
	last_page_num = doc('#pagebar ul li:eq(2) a').attr('title')[-2]
	return last_page_num
def save2mongo(data):
	if db['guangzhou_fund'].update({'position':data['position']},{'$set':data},True):
		print('success save to mongo',data['position'])
	else:
		print('Failed save to mongo',data['position'])
	# if db['guangzhou_fund'].update({'position': data['position']}, {'$set': data}, True):
 #    	print('Saved to Mongo', data['position'])
	# else:
 #        print('Saved to Mongo Failed', data['position'])



if __name__ == '__main__':
	
	max_page = get_last_pagenum(get_page_html(1,KEYWORD))
	for i in range(int(max_page)):
		page_index_html = get_page_html(i+1,KEYWORD)
		time.sleep(random.random()*5)
		url_append = get_onepage_detail_url(page_index_html)

		for j in url_append:
			detail_url = BASEURL + j
			detail_html = get_detail_html(detail_url)
			time.sleep(random.random()*3)
			soup = BeautifulSoup(detail_html,'html.parser')
			text = soup.prettify()
			for key,value in REPLACE_DICT.items():
				text = text.replace(key,value)
			info = parse_detail_page(text)
			save2mongo(info)
