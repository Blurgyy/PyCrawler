#!/usr/bin/python

import re
import urllib2
import cookielib

print "input url:"
url = raw_input();
http_pattern = re.compile(r"http");
if(re.match(http_pattern, url)):
	print "url stat: ok"
else:
	url = "http://" + url;
print "getting cookies from", [url];

file_name = "cookie.txt"
cookie = cookielib.MozillaCookieJar(file_name);
handler = urllib2.HTTPCookieProcessor(cookie);
header = {}
header['User-Agent'] = "Chrome/71.0.3578.98"
opener = urllib2.build_opener(handler);
response = opener.open(url, headers = header);
cookie.save(ignore_discard = True, ignore_expires = True)
print "cookie file", file_name, "generated";