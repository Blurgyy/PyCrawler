#!/usr/bin/python

import requests
import webbrowser
from urllib import urlopen

url = "https://paste.ubuntu.com"
hdoc = urlopen(url).read()
file_ = open('./submit')
content = file_.read()

print "getting content"
form_ = {'poster': 'what a test', 'syntax': 'python', 'expiration': 'day', 'content': content}
print "content got"

cnt = 0
while True:
	print [cnt], "submitting"
	r = requests.post(url, data = form_)
	print [cnt], "submitted"
	webbrowser.open(r.url)
	cnt = cnt + 1
	print ""