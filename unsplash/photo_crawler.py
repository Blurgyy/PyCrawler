#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

"""

Input: search terms

Output: several (could be 0) download links according to search terms

"""

import urllib
import urllib2
import re
import os
import imghdr
import webbrowser

user_agent = "Mozilla/5.0 (X11; Linux x86_64)";
header = {};
header['User-Agent'] = user_agent;

base_url = "https://unsplash.com/";
search_url = base_url + "search/photos/";
print "Input search terms:"
search_terms = raw_input();
search_url = search_url + search_terms;
print "ok requesting images about", search_terms;
try:
	req = urllib2.Request(search_url, headers = header);
	resp = urllib2.urlopen(req);
	src_code = resp.read();
	# print(src_code);
	print "connection status: OK";
except urllib2.URLError, err:
	if(hasattr(err, "code")):
		print "error code =", err.code;
	if(hasattr(err, "reason")):
		print "error reason =", err.reason;

hash_pattern = re.compile(r'login_from_photo=(.*?)"');
all_hash = re.findall(hash_pattern, src_code);
all_hash = list(set(all_hash));
pic_no = 0;
download_url = [];
for i in all_hash:
	pic_no = pic_no + 1;
	download_url.append(base_url + "photos/" + str(i) + "/download");

print "%d picture(s) in total." % (pic_no);
for i in download_url:
	print i;

pic_no = 0;
for i in download_url:
	try:
		pic_no += 1;
		print "downloading image no.%d..." % (pic_no);
		data = urllib2.urlopen(i).read();
		file_name = "./" + search_terms + "/" + search_terms + "-" + str(pic_no);
		f = open(file_name, 'wb');
		f.write(data);
		f.close();
		img_type = imghdr.what(file_name);
		image_file_name = file_name + "." + img_type;
		os.rename(file_name, image_file_name);
		print "downloaded image as", [image_file_name];
		print "";
	# except urllib2.ULRError, err:
	# 	print "connection lost on %d-th image" % (pic_no);
	# 	if(hasattr(err, "code")):
	# 		print "error code =", err.code;
	# 	if(hasattr(err, "reason")):
	# 		print "error reason", err.reason;
	except:
		print "Unknown error occured";
		pic_no -= 1;	
print "download finished, abort."

# webbrowser.open(search_url);

"""

https://unsplash.com/photos/uGPBqF1Yls0/download?force=true
https://unsplash.com/photos/uGPBqF1Yls0/

"""