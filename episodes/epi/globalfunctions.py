#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import requests
import re
import html
import random
import socket
import struct
import sys
import threading

def do_nothing():
    pass;
def is_url(x):
    return not not re.match(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', x);
def split_host(x):
    return re.findall(r'(https?://.*?)[/$]', x)[0];
def is_ts(x):
    return not not re.match(r'.*\.ts$', x);
def is_m3u8(x):
    return not not re.match(r'.*\.m3u8', x);
def supervisor(th, current_dlcnt, maximum_dlcnt):
    while(current_dlcnt[0] >= maximum_dlcnt):
        pass;
    current_dlcnt[0] += 1;
    # print("downloading %d items.." % current_dlcnt[0]);
    th.join();
    current_dlcnt[0] -= 1;
def read_terminal_args():
    try:
        default = {
            '_dl_option': 's',
            '_maximum_dlcnt': 8,
            '_dumpfpath': None,
            '_loadfpath': None,
            '_ifpath': None,
            '_ofpath': None,
            '_preselect': None
        };
        ret = default;
        if(len(sys.argv) == 1):
            return ret;
        for i in range(1, len(sys.argv)):
            if(sys.argv[i] == '-c'):    # `-c <n>` download $n items simultaneously
                i += 1;
                _maximum_dlcnt = 8;
                if(sys.argv[i].isdigit()):
                    _maximum_dlcnt = int(sys.argv[i]);
                    if(_maximum_dlcnt == 0):
                        _maximum_dlcnt = 8;
                ret['_maximum_dlcnt'] = _maximum_dlcnt;
            elif(sys.argv[i] == "-d"):  # `-d` (d)elete folder
                ret['_dl_option'] = 'd';
            elif(sys.argv[i] == '-m'):  # `-m <n>` preselect download items
                i += 1;
                _preselect = None;
                if(sys.argv[i].isdigit()):
                    _preselect = int(sys.argv[i]) - 1;
                    if(_preselect < 0):
                        print("\033[1;31m%s\033[0m: invalid parameter" % (sys.argv[i]));
                        _preselect = None;
                else:
                    print("\033[1;31m%s\033[0m: not a integer" % (sys.argv[i]));
                ret['_preselect'] = _preselect;
            elif(sys.argv[i] == "-n"):  # `-n` save with a (n)ew name
                ret['_dl_option'] = 'n';
            elif(sys.argv[i] == '-o'):  # `-o` (o)verwrite
                ret['_dl_option'] = 'o';
            elif(sys.argv[i] == '-r'):
                i += 1;
                ret['_ifpath'] = sys.argv[i];
            elif(sys.argv[i] == '-w'):
                i += 1;
                ret['_ofpath'] = sys.argv[i];
            elif(sys.argv[i] == '-dump'):
                i += 1;
                ret['_dumpfpath'] = sys.argv[i];
            elif(sys.argv[i] == '-load'):
                i += 1;
                ret['_loadfpath'] = sys.argv[i];
        # print(ret);
        return ret;
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31mglobalfunctions.py::read_terminal_args(): %s\033[0m" % e);
        return default;
def create_headers():
    try:
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
            'CLIENT-IP': ip,
            # 'X-FORWARDED-FOR': ip
        }
        return headers;
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31mglobalfunctions.py::create_headers(): %s\033[0m" % e);
        return None;
def get_content(url, headers = create_headers(), proxies = {'http': "http://61.184.109.33:61320", 'https': "https://210.5.10.87:53281"}, timeout = 9.9, ):
    try:
        content = requests.get(url, headers = headers, timeout = timeout).text;
        return html.unescape(content.encode('latin-1', 'ignore').decode('utf-8', 'ignore'));
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31mglobalfunctions.py::get_content(): %s\033[0m" % e);
        return None;

class myThread(threading.Thread):
    def fetch_result(self, ):
        try:
            return self.result;
        except Exception as e:
            print("\033[1;31mglobalfunctions.py::myThread::fetch_result(): %s\033[0m" % e);
            return None;
