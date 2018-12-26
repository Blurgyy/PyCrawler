#!/usr/bin/python

from urllib import urlopen

url = raw_input()
html = urlopen(url).read();
print(html)

# 
# 
# 
# 
