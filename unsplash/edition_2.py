#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

"""

Runs on Python 2.7.15rc1 

Input: Search terms

Output: Save result images(quantity: 0 to 10) in a search-term-specified directory

"""


import urllib
import urllib2
import re
import os
import imghdr
import time

def completion(a, b, c):
	pct = 100.0 * a * b / c;
	if(pct > 100.0):
		pct = 100.0;
	print "\x1B[1Acompletion: %.3f%% done" % pct;

class unsplash:
	def __init__(self, debug__mode = False):
		self.base_url = "https://unsplash.com/";
		self.headers = {'User-Agent': "Chrome/71.0.3578.98"};
		self.dl_links = [];
		self.dl_links_masked = [];
		self.debug_mode = debug__mode;

	def input_search_terms(self):
		print "Input search terms:";
		self.search_terms = raw_input();
		self.search_url = self.base_url + "search/photos/" + self.search_terms;
		print "ok reqeusting images of %s" % (self.search_terms);
		return self.search_terms;

	def get_src_code(self, url):
		try:
			if self.debug_mode:
				print "fetching src_code of %s" % (url);
			self.req = urllib2.Request(url, headers = self.headers);
			self.resp = urllib2.urlopen(self.req);
			self.src_code = self.resp.read();
			if self.debug_mode:
				print "fetched";
			return self.src_code;
		except urllib2.URLError, e:
			print "error opening url: %s" % (url);
			if(hasattr(e, "code")):
				print "error code = %s" % (e.code);
			if(hasattr(e, "reason")):
				print "error reason = %s\n" % (e.reason);
			return None;

	def get_dl_links_masked(self):
		try:
			self.pattern = re.compile(r'login_from_photo=(.*?)"');
			self.all_hash = list(set(re.findall(self.pattern, self.src_code)));
			for i in self.all_hash:
				if self.debug_mode:
					print i;
				self.dl_links_masked.append(self.base_url + "photos/" + i + "/download");
			return self.dl_links_masked;
		except:
			print "error getting masked download_links";
			return None;

	def get_dl_links(self, dl_url):
		if not re.search("download", dl_url):
			print "invalid download link, abort"
			return;
		try:
			self.req = urllib2.Request(dl_url, headers = self.headers);
			self.resp = urllib2.urlopen(self.req);
			return self.resp.url;
		except urllib2.URLError, e:
			print "error handling link \"%s\"" % (dl_url);
			if(hasattr(e, "code")):
				print "error code = %s" % (e.code);
			if(hasattr(e, "reason")):
				print "error reason = %s\n" % (e.reason);
			return None;

	def img_type(self, file_location):
		return imghdr.what(file_location);

	def download(self, link, fpath, fname):
		# self.req = urllib2.Request(link, headers = headers);
		# self.resp = urllib2.urlopen(self.req);
		# self.tmp_img_data = self.get_src_code(link);
		if not os.path.exists(fpath):
			print "creating new directory [%s] at current location\n" % (fpath);
			os.makedirs(fpath);

		dl_location = fpath + fname;
		urllib.urlretrieve(link, dl_location, completion);
		# dl_img = open(dl_location, 'wb');
		# dl_img.write(self.tmp_img_data);
		# dl_img.close();
		fname = fname + "." + str(self.img_type(dl_location));
		final_file_name = fpath + fname;
		os.rename(dl_location, final_file_name);
		print "image downloaded as %s\n" % (final_file_name);

	def run(self):
		self.input_search_terms();
		self.get_src_code(self.search_url);
		self.get_dl_links_masked();

		img_id = 0;
		for dl_link_masked in self.dl_links_masked:
			img_id += 1;
			dl_link = self.get_dl_links(dl_link_masked);
			self.dl_links.append(dl_link);
			if self.debug_mode:
				print "downloading %d-th image..." % (img_id);
			fpath = self.search_terms + "/";
			fname = str(img_id) + "-" + str(int(time.time()));
			self.download(dl_link, fpath, fname);

test = unsplash();
test.run();

"""
base_url;
headers;
download_links;
search_url;
search_terms;
req, resp;
src_code;
pattern;
all_hash;
-------------
__init__();
input_search_terms();
get_src_code();
get_dl_links_masked();
get_dl_links();
download();	
"""