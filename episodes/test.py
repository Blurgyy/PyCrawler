#!/usr/bin/python

import epi

terminal_args = epi.read_terminal_args();

x = epi.crawler(_dl_option = terminal_args['_dl_option']);
x.search();
x.download();
