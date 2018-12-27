#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy"

import urllib
import urllib2
import re

base_url = "http://www.qiushibaike.com/hot/page/";
page_no = 1;
url = base_url + str(page_no);
user_agent = "Mozilla/5.0 (X11; Linux x86_64)";
headers = {};
headers['User-Agent'] = user_agent;

try:
	req = urllib2.Request(url, headers = headers);
	resp = urllib2.urlopen(req);
	content = resp.read();#.decode("utf-8");
	# print content.encode("utf-8");
	print "getting items";
	# pattern = re.compile(r"<div.*?class.*?article block untagged mb15 typs_long.*?qiushi_tag_(.*?)\'.*?author.*?<img.*?>.*?<div.*?content\">.*?<span>(.*?)/span>.*?contentForAll.*?>", re.S);
	pattern = re.compile(r'<div.*?article block untagged mb15.*?id.*?>.*?<div.*?"content".*?span>(.*?)</span>.*?<!--.*?-->(.*?)</div>', re.S);
	print "pattern got";
	items = re.findall(pattern, content);
	print "items got";
	# print str(items).decode('utf-8');
	for i in items:
		if(not re.search("thumb", i[1])):
			print i[0];

except urllib2.URLError, e:
	print "error", [url];
	if(hasattr(e, "code")):
		print "err code =", e.code;
	if(hasattr(e, "reason")):
		print "err reason =", e.reason;