#!/usr/bin/python
from bs4 import BeautifulSoup
from urllib import urlopen
import re
import random
import time
import webbrowser

# print re
# print bs4

# base_url = "https://zh.wikipedia.org/wiki"
# his = ["/%E4%B8%AD%E5%9B%BD%E6%B5%B7%E6%B4%8B%E5%A4%A7%E5%AD%A6"]
base_url = "https://baike.baidu.com"
his = ["/item/%E7%BD%91%E7%BB%9C%E7%88%AC%E8%99%AB/5162711"]

url = base_url + his[-1]
# print 'url = ', url

hdoc = urlopen(url).read()
soup = BeautifulSoup(hdoc, features = 'lxml')

sub_urls = soup.find_all("img", {'src': re.compile('https*')})
cnt = 0
for i in sub_urls:
	webbrowser.open(i['src'])
	print cnt, "\b.", i['src']
	cnt += 1