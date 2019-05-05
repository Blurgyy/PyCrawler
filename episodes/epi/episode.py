#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import re
import os
import shutil
import time
from .globalfunctions import *


#### class episode
class episode:
    def __init__(self, _base_url = None, _epid = None, _from_series = None, HASH = None, _m3u8_url = None, ):
        try:
            # print("initalizing episode with (%s, %s, %s), m3u8_url = %s" % (_base_url, str(_epid), _from_series, _m3u8_url));
            self.base_url = _base_url;
            self.epid = _epid;
            self.from_series = _from_series;
            self.fname = self.from_series.sname + '/' + str(self.epid) + ".m3u8";
            self._hash = HASH;
            self.m3u8_url = _m3u8_url;
            self.tvid = None;
            self.m3u8 = None;
            self.dl_option = self.from_series.dl_option;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisode.py::episode::__init__(): %s\033[0m" % e);

    def g_tvid(self, ):
        try:
            content = get_content(self.base_url);
            # print(self.base_url);
            # with open("1.html", 'w') as f:
            #     f.write(content);
            #     print("f written");
            if(re.search('tvid="', content)):
                if(re.search(r'tvid="(.*/)(.*?m3u8.*?)"', content)):
                    self.tvid = re.findall(r'tvid="(.*/)(.*?m3u8).*?"', content)[0];
                else:
                    self.tvid = re.findall(r'tvid="(.*?)"', content)[0];
                    self.tvid = re.findall(r'(.*/)(\w+)', self.tvid)[0];
            else:
                print("no tvid found");
            return self.tvid;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisode.py::episode::g_tvid(): %s\033[0m" % e);
            return None;

    def m3u8_unify(self, url = None):
        try:
            url = self.m3u8_url;
            if(url == None):
                self.g_tvid();
                url = self.tvid[0] + self.tvid[1];
            # print("in m3u8_unify: ", url);
            # print(self.tvid);
            if(not is_url(url)):
                print("no url found during download, abort");
                return None;
            if(is_m3u8(url)):
                content = get_content(url);
                nurl = url;
                for line in content.splitlines():
                    if(re.match(r'^#(.*?)$', line)):
                        continue;
                    if(is_m3u8(line)):
                        nurl = None;
                        if(line[0] == '/'):
                            nurl = split_host(url) + line;
                        else:
                            nurl = re.sub(url.split('/')[-1], line, url);
                        # print("nurl = ", nurl);
                        content = get_content(nurl);
                        break;
                    else:
                        break;
                self.m3u8 = "";
                for line in content.splitlines():
                    if(not is_url(line) and is_ts(line)):
                        if(line[0] == '/'):
                            host = split_host(url);
                            line = host + line;
                        else:
                            line = re.sub(line, re.sub(nurl.split('/')[-1], line, nurl), line);
                    self.m3u8 += line + '\n';
            else:
                content = get_content(url);
                nurl = re.findall(r'"(.*?m3u8)', content)[0];
                if(not is_url(nurl)):
                    nurl = split_host(url) + nurl;
                self.m3u8_unify(nurl);
            return self.m3u8;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisode.py::episodes::m3u8_unify(): %s\033[0m" % e);
            return None;

    def Download(self, ):   # as *.m3u8, returns True if a redownload action needs to be performed
        try:
            if(not os.path.exists(self.from_series.sname)):
                os.makedirs(self.from_series.sname);
            # if(self.dl_option == 'd'):
            #     print("ok deleting folder [%s]" % (self.from_series.sname));
            #     shutil.rmtree(self.from_series.sname);
            #     return False;
            if(os.path.exists(self.fname)):
                if(self.dl_option == 'n'):
                    print("[%s] duplicated, " % (self.fname), end = "");
                    duplicate_id = 2;
                    self.fname = self.from_series.sname + '/' + str(self.epid) + "(%d).m3u8" % (duplicate_id);
                    while(os.path.exists(self.fname)):
                        duplicate_id += 1;
                        self.fname = self.from_series.sname + '/' + str(self.epid) + "(%d).m3u8" % (duplicate_id);
                    print("downloading as [%s]" % (self.fname));
                elif(self.dl_option == 'o'):
                    print("[%s] duplicated, overwriting" % (self.fname));
                    # do_nothing();
                elif(self.dl_option == 's'):
                    print("[%s] duplicated, skipping" % (self.fname));
                    return False;
            with open(self.fname, 'w') as f:
                do_nothing();
            if(self.m3u8_unify()):
                # print(self.m3u8);
                with open(self.fname, 'w') as f:
                    f.write(self.m3u8);
                print("\033[1m[%s] episode [%s] downloaded as [%s]\033[0m" % (self.from_series.sname, str(self.epid), self.fname));
                return False;
            else:
                return False;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisode.py::episode::Download(): %s\033[0m" % e);
            return True;

    def renew_mtime(self, ):    # renew file's last modified time (if the file exists) to current time
        try:
            if(os.path.exists(self.fname)):
                os.utime(self.fname);
                time.sleep(0.05);
            else:
                do_nothing();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisode.py::episode::renew_mtime(): %s\033[0m" % e);
            return True;
