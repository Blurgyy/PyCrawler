#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import re
import os
import shutil
import time
from .m3u8 import m3u8
from .globalfunctions import *


#### class episode
class episode:
    def __init__(self, _base_url = None, _epname = None, _from_series = None, HASH = None, _m3u8_url = None, _verbose = True, ):
        try:
            # print("initalizing episode with (%s, %s, %s), m3u8_url = %s" % (_base_url, str(_epname), _from_series, _m3u8_url));
            self.base_url = _base_url;
            self.from_series = _from_series;
            self.dl_option = self.from_series.dl_option;
            self.epname = _epname;
            self.verbose = _verbose;
            self.fname = str(self.epname);
            self.fpath = self.from_series.sname + '/' + self.fname + ".m3u8";
            self._hash = HASH;
            self.vid = None;
            if(_m3u8_url == None):
                self.getvid();
                _m3u8_url = self.vid[0] + self.vid[1];
            self.m3u8 = None;
            self.m3u8 = m3u8(_base_url = _m3u8_url, _from_ep = self, );
            if(self.m3u8 == None):
                raise Exception("m3u8 initalization failed");
            self.duplicate_id = 1;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("episode.py::episode::__init__(): %s" % e);

    def getvid(self, ):
        try:
            content = get_content(self.base_url);
            # print(self.base_url);
            # with open("1.html", 'w') as f:
            #     f.write(content);
            #     print("'1.html' written");
            if(re.search('vid="', content)):
                if(re.search(r'vid="(.*/)(.*?m3u8.*?)"', content)):
                    self.vid = re.findall(r'vid="(.*/)(.*?m3u8).*?"', content)[0];
                else:
                    self.vid = re.findall(r'vid="(.*?)"', content)[0];
                    self.vid = unquote(self.vid);
                    self.vid = re.findall(r'(.*/)([\.\w]+)', self.vid)[0];
                # print("in getvid:", self.vid);
            else:
                print("no vid found");
            return self.vid;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("episode.py::episode::getvid(): %s" % e);
            return None;

    def download(self, ):   # as *.m3u8, returns True if a redownload action needs to be performed
        try:
            if(not os.path.exists(self.from_series.sname)):
                # print("directory created: %s" % (self.from_series.sname));
                os.makedirs(self.from_series.sname);
            if(os.path.exists(self.fpath)):
                if(self.dl_option == 'n'):
                    if(self.verbose):
                        print("-- [%s] duplicated, " % (self.fpath), end = "");
                    self.duplicate_id += 1;
                    self.fname = str(self.epname) + "(%d)" % (self.duplicate_id);
                    self.fpath = self.from_series.sname + '/' + self.fname + ".m3u8";
                    while(os.path.exists(self.fpath)):
                        self.duplicate_id += 1;
                        self.fname = str(self.epname) + "(%d)" % (self.duplicate_id);
                        self.fpath = self.from_series.sname + '/' + self.fname + ".m3u8";
                    if(self.verbose):
                        print("downloading as [%s]" % (self.fpath));
                elif(self.dl_option == 'o'):
                    if(self.verbose):
                        print("-- [%s] duplicated, overwriting" % (self.fpath));
                    do_nothing();
                elif(self.dl_option == 's'):
                    if(self.verbose):
                        print("-- [%s] duplicated, skipping" % (self.fpath));
                    return False;
            with open(self.fpath, 'w') as f:
                do_nothing();
            if(self.m3u8.unify()):
                # print(self.m3u8.content);
                with open(self.fpath, 'wb') as f:
                    f.write(self.m3u8.content.encode());
                if(self.verbose):
                    print("-- [%s] episode [%s] downloaded as [%s]" % (self.from_series.sname, str(self.epname), self.fpath));
                return False;
            else:
                if(os.path.exists(self.fpath)):
                    os.remove(self.fpath);
                return False;
        except KeyboardInterrupt:
            if(os.path.exists(self.fpath)):
                os.remove(self.fpath);
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            if(os.path.exists(self.fpath)):
                os.remove(self.fpath);
            print("episode.py::episode::download(): %s" % e);
            return True;

    def renew_mtime(self, ):    # renew file's last modified time (if the file exists) to current time
        try:
            if(os.path.exists(self.fpath)):
                os.utime(self.fpath);
                time.sleep(0.05);
            else:
                do_nothing();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("episode.py::episode::renew_mtime(): %s" % e);
            return True;
