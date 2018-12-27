#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import urllib
import urllib2
import re

"""

Input: One parameter `page_no` as input

Output: All stories in url"https://www.qiushibaike.com/hot/page/${page_no}", images displayed as src_url

"""

class qsbk:
	def __init__(self):
		# self.page_no = 1;
		self.user_agent = "Chrome/71.0.3578.98";
		self.headers = {};
		self.headers["User-Agent"] = self.user_agent;
		self.base_url = "https://www.qiushibaike.com/hot/page/";

	def get_page_src_code(self, page_no):
		url = self.base_url + str(page_no);
		print "getting page", (url), "src code..."
		try:
			req = urllib2.Request(url, headers = self.headers);
			resp = urllib2.urlopen(req);
			src_code = resp.read();
			return src_code;
		except urllib2.URLError, err:
			if(hasattr(e, "code")):
				print "err code =", e.code;
			if(hasattr(e, "reason")):
				print "err reason =", e.reason;
			return None;

	def has_img(self, item):
		if(re.search("thumb", item[1])):
			return True;
		return False;

	def get_page_items(self, page_no):
		print "getting page items..."
		src_code = self.get_page_src_code(page_no);
		if(not src_code):
			print "connection lost";
			return None;
		all_in_page = [];
		pattern = re.compile(r'<div.*?article block untagged mb15.*?id.*?>.*?<div.*?"content".*?span>(.*?)</span>.*?<!--.*?-->(.*?)</div>', re.S);
		items = re.findall(pattern, src_code);
		img_pattern = re.compile(r'src="(.*?)"');
		for i in items:
			if(self.has_img(i)):
				img_url = "https:" + re.findall(img_pattern, i[1])[0];
				all_in_page.append([i[0].strip(), img_url]);
			else:
				all_in_page.append([i[0].strip()]);
		return all_in_page;

	def out_put(self, all_in_page):
		for i in all_in_page:
			for j in i:
				print j;
			print "";

	def run(self, page_no):
		all_in_page = self.get_page_items(page_no);
		self.out_put(all_in_page);

test = qsbk();
page_no = raw_input();
print "page_no =", page_no, "\nrunning...";
test.run(page_no);
print("finished");