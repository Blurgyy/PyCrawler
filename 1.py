#!/usr/bin/python
import requests
import urllib
from urllib import urlopen
import bs4
from bs4 import BeautifulSoup
import webbrowser

# data = {'newwindow': '1', 'safe': 'active', 'ei': '-EsjXMTkJKqV0gKE0YzoAw', 'q': 'this is a test', 'oq': 'this is a test', 'gs_l': 'psy-ab.12..0i71l5.0.0..81132...0.0..0.0.0.......0......gws-wiz.nD7BsK3TXDA'}
data = {}
print "(1)"
r = requests.post('https://www.google.com/webhp', data=data)
print "(2)"
webbrowser.open(r.url)