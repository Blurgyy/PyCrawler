#!/usr/bin/python

import epi

args = epi.read_terminal_args();
# print(args);

x = epi.crawler(\
	_dl_option = args['_dl_option'],\
	_maximum_dlcnt = args['_maximum_dlcnt'],\
	_ifpath = args['_ifpath'],\
	_ofpath = args['_ofpath'],\
	);
x.search();
x.download();
x.close();
