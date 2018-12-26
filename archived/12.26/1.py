#!/usr/bin/python

import urllib
import urllib2
import webbrowser

# webbrowser.open("http://jwgl.ouc.edu.cn/")
url = "https://github.com/";
headers = {};
submit_form = {};
data = urllib.urlencode(submit_form);
headers["User-Agent"] = "Chrome/70.0.3538.110"
headers["Referer"] = url;
request = urllib2.Request(url, headers = headers);
response = urllib2.urlopen(request);
pagesrc = response.read();
print pagesrc