#!/usr/bin/python

import requests
import urllib
from urllib import urlopen
import bs4
from bs4 import BeautifulSoup
import webbrowser

url = "https://www.unsplash.com/"
search_url = url + "search/photos/"
query = raw_input();
query_url = search_url + query;
# query_url correct
webbrowser.open(query_url);