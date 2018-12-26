#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import urllib2
from urllib2 import urlopen

hdoc = urlopen("https://morvanzhou.github.io/static/scraping/table.html").read()
# print(hdoc)
soup = BeautifulSoup(hdoc, features = "lxml")
# print(soup)

img_links = soup.find_all("img", {"src": re.compile('.*?\.jpg')})
for i in img_links:
	print(i['src']);