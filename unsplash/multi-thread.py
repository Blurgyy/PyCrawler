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
import threading


class unsplash:
	def __init__(self, _debug_mode = False, _show_pct_bar = True):
		self.base_url = "https://unsplash.com/";
		self.headers = {'User-Agent': "Chrome/71.0.3578.98"};
		self.dl_links = [];
		self.dl_links_masked = [];
		self.debug_mode = _debug_mode;
		self.show_pct_bar = _show_pct_bar;

	def completion(self, a, b, c):
		pct = 100.0 * a * b / c;
		if(pct > 100.0):
			pct = 100.0;
		if self.show_pct_bar:
			print "\x1B[1Acompletion: %.3f%% done" % pct;

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
	def check_directory_path(self, directory_path):
		if os.path.exists(directory_path):
			if self.debug_mode:
				print "ok directory [%s] exists" % (directory_path);
		else:
			os.makedirs(directory_path);
			print "creating new directory [%s] at current location\n" % (directory_path);

	def download(self, link, fpath, fname):
		# self.req = urllib2.Request(link, headers = headers);
		# self.resp = urllib2.urlopen(self.req);
		# self.tmp_img_data = self.get_src_code(link);
		downloading_path = fpath + "downloading/";
		self.check_directory_path(fpath);
		self.check_directory_path(downloading_path);

		dl_location = downloading_path + fname;
		urllib.urlretrieve(link, dl_location, self.completion);
		fname = fname + "." + str(self.img_type(dl_location));
		final_file_name = fpath + fname;
		os.rename(dl_location, final_file_name);
		print "image downloaded as %s\n" % (final_file_name);

	def run(self):
		self.input_search_terms();
		self.get_src_code(self.search_url);
		self.get_dl_links_masked();

		self.threads = [];
		img_id = 0;
		for dl_link_masked in self.dl_links_masked:
			img_id += 1;
			dl_link = self.get_dl_links(dl_link_masked);
			self.dl_links.append(dl_link);
			if self.debug_mode:
				print "downloading %d-th image..." % (img_id);
			fpath = self.search_terms + "/";
			fname = str(img_id) + "-" + str(int(time.time()));
			
			tmp = threading.Thread(target = self.download, args = (dl_link, fpath, fname));
			# tmp.start();
			self.threads.append(tmp);

		cnt = 0;
		for i in self.threads:
			cnt += 1;
			if self.debug_mode:
				print "start runs %d" % (cnt);
			if not i.is_alive():
				i.start();
		cnt = 0;
		# for i in self.threads:
		# 	cnt += 1;
		# 	if self.debug_mode:
		# 		print "join runs %d" % (cnt);
		# 	i.join();
		# 	# self.download(dl_link, fpath, fname);

test = unsplash();	# default: debug_mode = False, show_pct_bar = True
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