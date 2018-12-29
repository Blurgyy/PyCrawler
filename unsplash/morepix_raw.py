#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

"""

Python 3.6.4 

Input: Search terms

Output: Save result images in a search-term-specified directory

"""


import urllib
import urllib.request
import urllib.parse
import socket
import re
import os
import imghdr
import time
import threading

class unsplash:
	def __init__(self, _debug_mode = False, _show_pct_bar = False, _hashes_per_page = 6, _download_time_out = 20.0, _max_items_cnt = 1000):
		self.base_url = "https://unsplash.com/";
		self.headers = {'User-Agent': "Chrome/71.0.3578.98"};
		self.dl_links = [];
		self.dl_links_masked = [];
		self.debug_mode = _debug_mode;
		self.show_pct_bar = _show_pct_bar;
		self.hashes_per_page = _hashes_per_page;
		self.time_out = _download_time_out;
		self.max_items_cnt = _max_items_cnt;
		self.thread_rec = [];
		# socket.setdefaulttimeout(self.time_out);

	def completion(self, a, b, c):
		pct = 100.0 * a * b / c;
		if(pct > 100.0):
			pct = 100.0;
		if self.show_pct_bar:
			print("completion: %.3f%% done" % pct, end = "\r");

	def get_quantity(self):
		src_code = self.get_src_code(self.search_url).decode();
		# _1u88E _1iWCF _27Bp2
		self.quantity_pattern = re.compile(r'_3vsmH _1iWCF xLon9.*?>(.*?)</span>');
		self.quantity = re.findall(self.quantity_pattern, src_code)[0];
		if self.debug_mode:
			print("total: %s image(s)" % (self.quantity));
		tmp = 0.0;
		coeffecient = 1.0;
		dot = False;
		for i in self.quantity:
			if re.match(r'[0-9]', i):
				if not dot:
					tmp *= 10;
				if dot:
					coeffecient *= 0.1;
				tmp += int(i) * coeffecient;
			if re.match('k', i):
				tmp *= 1000;
			if i == '.':
				dot = True;
		self.quantity = tmp;
		if self.debug_mode:
			print("self.quantity = %d, self.max_items_cnt = %d" % (self.quantity, self.max_items_cnt));
		print("%d images found, starting download" % (self.quantity));

	def input_search_terms(self):
		print("Input search terms:");
		self.search_terms = urllib.parse.quote(input());
		self.search_url = self.base_url + "search/photos/" + self.search_terms;
		print("ok reqeusting images of %s" % (self.search_terms));
		if not os.path.exists(self.search_terms + "/downloading/"):
			os.makedirs(self.search_terms + "/downloading/");
			print("Created directory %s" % (self.search_terms + "/downloading/"));
		else:
			print("ok directory %s already exists" % (self.search_terms + "/downloading/"));
		return self.search_terms;

	def get_src_code(self, url):
		try:
			if self.debug_mode:
				print("fetching src_code of %s" % (url));

			socket.setdefaulttimeout(None);
			self.req = urllib.request.Request(url, headers = self.headers);
			self.resp = urllib.request.urlopen(self.req);
			self.src_code = self.resp.read();
			if self.debug_mode:
				print("fetched");
			return self.src_code;
		except urllib.request.URLError as e:
			print("error opening url: %s" % (url));
			if(hasattr(e, "code")):
				print("error code = %s" % (e.code));
			if(hasattr(e, "reason")):
				print("error reason = %s\n" % (e.reason));
			return None;

	def get_json_page_url(self, page_no):
		self.page_url = "https://unsplash.com/napi/search/photos?query=" + self.search_terms + "&xp=&per_page=" + str(self.hashes_per_page) + "&page=" + str(page_no);
		return self.page_url;

	def get_dl_links_masked(self, document):
		try:
			while len(self.dl_links_masked) > 0:
				self.dl_links_masked.pop();
			self.pattern = re.compile(r'"download_location":"https://api.unsplash.com/photos/(.*?)/download"');
			self.all_hash = list(set(re.findall(self.pattern, document)));
			for i in self.all_hash:
				if self.debug_mode:
					print(i);
				self.dl_links_masked.append(self.base_url + "photos/" + i + "/download");
			return self.dl_links_masked;
		except:
			print("error getting masked download_links");
			return None;

	def get_dl_links(self, dl_url):
		if not re.search("download", dl_url):
			print("invalid download link, abort");
			return;
		try:
			socket.setdefaulttimeout(None);
			self.req = urllib.request.Request(dl_url, headers = self.headers);
			self.resp = urllib.request.urlopen(self.req);
			return self.resp.url;
		except urllib.request.URLError as e:
			print("error handling link \"%s\"" % (dl_url));
			if(hasattr(e, "code")):
				print("error code = %s" % (e.code));
			if(hasattr(e, "reason")):
				print("error reason = %s\n" % (e.reason));
			return None;

	def img_type(self, file_location):
		return imghdr.what(file_location);
	def check_directory_path(self, directory_path):
		if os.path.exists(directory_path):
			if self.debug_mode:
				print("ok directory [%s] exists" % (directory_path));
		else:
			os.makedirs(directory_path);
			print("creating new directory [%s] at current location\n" % (directory_path));

	def download(self, link, fpath, fname):
		downloading_path = fpath + "downloading/";
		self.check_directory_path(fpath);
		self.check_directory_path(downloading_path);

		dl_location = downloading_path + fname;
		try:
			socket.setdefaulttimeout(self.time_out);
			if self.debug_mode:
				print("performing download action, url=\"%s\"" % (link));
			urllib.request.urlretrieve(link, dl_location, self.completion);
		except socket.timeout:
			print("image %s timed out" % (dl_location));

		fname = fname + "." + str(self.img_type(dl_location));
		final_file_name = fpath + fname;
		os.rename(dl_location, final_file_name);
		self.dl_cnt += 1;
		print("image downloaded as %s" % (final_file_name));

	def run(self):
		self.input_search_terms();
		self.get_quantity();

		img_id = 0;
		self.dl_cnt = 0;
		self.threads = [];
		for i in range(1, 10000000):
			if (i - 1) * self.hashes_per_page > min(self.quantity, self.max_items_cnt):
				print("all images have been crawled");
				break;
			self.get_json_page_url(i);
			json_document = self.get_src_code(self.page_url).decode();
			self.get_dl_links_masked(json_document);
			while len(self.threads) > 0:
				self.threads.pop();
			while len(self.dl_links) > 0:
				self.dl_links.pop();
			for dl_link_masked in self.dl_links_masked:
				img_id += 1;
				dl_link = self.get_dl_links(dl_link_masked);
				self.dl_links.append(dl_link);
				print("[image no.%d/%d: connecting... it will soon be downloaded]" % (img_id, min(self.max_items_cnt, self.quantity)));
				self.fpath = self.search_terms + "/";
				fname = str(img_id) + "-" + str(int(time.time()));
				
				tmp = threading.Thread(target = self.download, args = (dl_link, self.fpath, fname));
				self.threads.append(tmp);

			while len(self.thread_rec) > 0:
				self.thread_rec.pop();
			while len(self.threads) > 0:
				tmp = self.threads.pop();
				tmp.start();
				self.thread_rec.append(tmp);
				if self.debug_mode:
					print("starting thread");
				time.sleep(0.3);
			if self.debug_mode:
				print("all threads opened, queue.size = %d" % (len(self.threads)));

	def show_finish_message(self):
		for thread in self.thread_rec:
			thread.join();
		print("total: %d/%d images saved to %s" % (self.dl_cnt, min(self.max_items_cnt, self.quantity), self.fpath));

test = unsplash(_debug_mode = True, _hashes_per_page = 10);
test.run();
test.show_finish_message();
