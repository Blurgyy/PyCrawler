#!/usr/bin/python

import crawl
from globalfunctions import *


shell_args = read_shell_args();

x = crawl.crawler(_dl_option = shell_args['_dl_option']);
x.search();
x.Download();
