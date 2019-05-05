#!/usr/bin/python

import crawl
from globalfunctions import *


terminal_args = read_terminal_args();

x = crawl.crawler(_dl_option = terminal_args['_dl_option']);
x.search();
x.Download();
