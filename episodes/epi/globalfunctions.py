#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import requests
import os
import re
import html
import random
import socket
import struct
import sys
import inspect
import threading
from urllib.parse import unquote

def do_nothing():
    pass;
def is_url(x):
    if(x == None):
        return False;
    return not not re.match(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', x);
def is_m3u8(x):
    if(x == None):
        return False;
    return not not re.match(r'.*\.m3u8', x);
def is_ts(x):
    if(x == None):
        return False;
    return not not re.match(r'.*\.ts$', x);
def split_host(x):
    if(x == None):
        return None;
    return re.findall(r'(https?://.*?)[/$]', x)[0];
def split_fname(x):
    if(x == None):
        return None;
    full_fname = x.split(os.sep)[-1];
    # print(full_fname);
    # input();
    splt = full_fname.split('.');
    ret = "";
    for i in range(len(splt) - 1):
        if(i == 0):
            ret += splt[i];
        else:
            ret += '.' + splt[i];
    return ret;
def current_fn_name():
    return inspect.stack()[1][3];
def randch():
    return random.choice("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM");
def randstring(length = 6, ):
    ret = "";
    for i in range(length):
        ret += randch();
    return ret;
def bar(finished, total, length, ):
    ret = "";
    go0 = int(finished / total * length);
    go1 = length - go0;
    for i in range(go0):
        ret += '>';
    for i in range(go1):
        ret += ' ';
    return ret;
def read_terminal_args():
    try:
        # sys.getfilesystemencoding = lambda: 'utf-8';
        default = {
            '_dl_option': 's',
            '_maximum_dlcnt': 8,
            '_dumpfpath': None,
            '_loadfpath': None,
            '_ofpath': None,
            '_preselect': None,
            '_search_term': None,
            '_verbose': True
        };
        ret = default;
        if(len(sys.argv) == 1):
            return ret;
        i = 0;
        while(i < len(sys.argv)):
            # print(sys.argv[i], "<br>");
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
                        print("%s: invalid parameter" % (sys.argv[i]));
                        _preselect = None;
                else:
                    print("%s: not a integer" % (sys.argv[i]));
                ret['_preselect'] = _preselect;
            elif(sys.argv[i] == "-n"):  # `-n` save with a (n)ew name
                ret['_dl_option'] = 'n';
            elif(sys.argv[i] == '-o'):  # `-o` (o)verwrite
                ret['_dl_option'] = 'o';
            elif(sys.argv[i] == '-s'):
                i += 1;
                ret['_search_term'] = unquote(sys.argv[i]);
            elif(sys.argv[i] == '-w'):
                i += 1;
                ret['_ofpath'] = sys.argv[i];
            elif(sys.argv[i] == '-dump'):
                i += 1;
                ret['_dumpfpath'] = sys.argv[i];
            elif(sys.argv[i] == '-load'):
                i += 1;
                ret['_loadfpath'] = sys.argv[i];
            elif(sys.argv[i] == '-x'):
                ret['_verbose'] = False;
            i += 1;
        # print(ret);
        return ret;
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("globalfunctions.py::read_terminal_args(): %s" % e);
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
        print("globalfunctions.py::create_headers(): %s" % e);
        return None;
def get_content(url, headers = create_headers(), proxies = {'http': "http://61.184.109.33:61320", 'https': "https://210.5.10.87:53281"}, timeout = 9.9, html_unescape = False, ):
    try:
        content = requests.get(url, headers = headers, timeout = timeout).text;
        # content = content.encode('latin-1', 'ignore').decode('utf-8', 'ignore');
        if(html_unescape):
            return html.unescape(content.encode('latin-1', 'ignore').decode('utf-8', 'ignore'));
            # return html.unescape(content);
        else:
            return content;
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("globalfunctions.py::get_content(): %s" % e);
        return None;

###
class myThread(threading.Thread):
    def __init__(self, target, args=(), ):
        super(myThread, self).__init__();
        self.func = target;
        self.args = args;
    def run(self, ):
        self.result = self.func(*self.args);
    def fetch_result(self, ):
        try:
            threading.Thread.join(self);
            return self.result;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("globalfunctions.py::myThread::fetch_result(): %s" % e);
            return False;

def supervisor(th, opening_thcnt, maximum_thcnt, finished_thcnt, ):
    # where opening_thcnt and finished_thcnt are **list**s, while maximum_thcnt is an **integer** 
    try:
        while(opening_thcnt[0] >= maximum_thcnt):
            pass;
        opening_thcnt[0] += 1;
        # print("downloading %d items.." % opening_thcnt[0]);
        th.join();
        opening_thcnt[0] -= 1;
        finished_thcnt[0] += 1;
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("globalfunctions.py::supervisor(): %s" % e);
