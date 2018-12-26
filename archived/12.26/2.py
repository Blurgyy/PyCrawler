#!/usr/bin/python

# import urllib
import urllib2
# import webbrowser

# url = "https://blog.csdn.net/adfgfdhtrs";
url = "http://szjx.ouc.edu.cn/meol/main.jsp";
req = urllib2.Request(url);
try:
	urllib2.urlopen(req);
except urllib2.HTTPError, e:
	print e.code;
	print e.reason;