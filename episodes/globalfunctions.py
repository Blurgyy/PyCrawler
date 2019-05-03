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
    th.join();
    current_dlcnt[0] -= 1;
def read_shell_args():
    ret = {
        '_dl_option': 's',
    };
    if(len(sys.argv) == 1):
        return ret;
    for i in range(1, len(sys.argv)):
        if(sys.argv[i] == "-d"):    # `-d` (d)elete folder
            ret['_dl_option'] = 'd';
        elif(sys.argv[i] == "-n"):  # `-n` save with a (n)ew name
            ret['_dl_option'] = 'n';
        elif(sys.argv[i] == '-o'):  # `-o` (o)verwrite
            ret['_dl_option'] = 'o';
    return ret;
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
