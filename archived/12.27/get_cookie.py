#!/usr/bin/python

import cookielib
import urllib2
import re

# url = "https://www.unsplash.com/"
print "input url: "
url = raw_input();
pattern = re.compile(r"http")
if(re.match(pattern, url)):
	# url = "https://" + url;
	print "url status: ok";
else:
	url = "https://" + url;
print "getting cookies from", [url];

cookie = cookielib.CookieJar();
handler = urllib2.HTTPCookieProcessor(cookie);
opener = urllib2.build_opener(handler);
response = opener.open(url);

for item in cookie:
	print "Name = %s\nValue = %s\n" % (item.name, item.value);