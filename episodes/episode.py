#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import re
import os
import shutil
import sys
import select
from globalfunctions import *


#### class episode
class episode:
    def __init__(self, _base_url = None, _epid = None, _from_series = None, HASH = None, _m3u8_url = None, ):
        try:
            # print("initalizing episode with (%s, %s, %s), m3u8_url = %s" % (_base_url, str(_epid), _from_series, _m3u8_url));
            self.base_url = _base_url;
            self.epid = _epid;
            self.from_series = _from_series;
            self._hash = HASH;
            self.m3u8_url = _m3u8_url;
            self.tvid = None;
            self.m3u8 = None;
            self.dl_option = "";
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::episode::__init__(): %s\033[0m" % e);

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
            print("\033[1;31mepisodes.py::episode::g_tvid(): %s\033[0m" % e);
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
            print("\033[1;31mepisodes.py::episodes::m3u8_unify(): %s\033[0m" % e);
            return None;

    def Download(self, ):   # as *.m3u8, returns True if a download action has been done, returns False otherwise.
        try:
            # self.g_tvid();
            self.dl_option = self.from_series.dl_option;
            if(self.dl_option == "dd" or self.dl_option == "ddd"):
                return False;
            select_timeout = 6;
            if(not os.path.exists(self.from_series.sname)):
                os.makedirs(self.from_series.sname);
            fname = self.from_series.sname + '/' + str(self.epid) + ".m3u8";
            if(os.path.exists(fname)):
                # print("file [%s] already exists, skipping..." % fname);
                if(self.dl_option == ""):
                    print("\033[1;37;43mfile [%s] already exists.\033[0m" % fname);
                    print("""\t\033[1;32mn\033[0m: download, but using a different name (only this file)
\t\033[1;32mN\033[0m: download, but using different names (all following duplicated files)
\t\033[1;32mo\033[0m: overwrite (only this file)
\t\033[1;32mO\033[0m: overwrite (all following duplicated files)
\t\033[1;32ms\033[0m: skip (only this file)
\t\033[1;32mS\033[0m: skip (all following duplicated files)
\t\033[1;32md\033[0m: delete (only this file) and skip
\t\033[1;32mdd\033[0m: delete (all files in this folder, but keep the folder) and abort
\t\033[1;32mddd\033[0m: delete (this whole folder, not keeping the folder) abort
\nselect an option from above, and press \033[1;34mENTER\033[0m\n(%d seconds of inactivity will be considered as entering \033[1;32ms\033[0m): """ % (select_timeout, ), end = "");
                    # self.dl_option = input().strip();
                    self.dl_option = 's';
                    a, b, c = select.select([sys.stdin], [], [], select_timeout);
                    if(a):
                        self.dl_option = sys.stdin.readline().strip();
                    print("\n");
                if(self.dl_option == 'N' or self.dl_option == 'O' or self.dl_option == 'S' or self.dl_option == "dd" or self.dl_option == "ddd"):
                    self.from_series.dl_option = self.dl_option;
                if(self.dl_option == 'n' or self.dl_option == 'N'):
                    duplicate_id = 2;
                    fname = self.from_series.sname + '/' + str(self.epid) + "(%d).m3u8" % (duplicate_id);
                    while(os.path.exists(fname)):
                        duplicate_id += 1;
                        fname = self.from_series.sname + '/' + str(self.epid) + "(%d).m3u8" % (duplicate_id);
                elif(self.dl_option == 'o' or self.dl_option == 'O'):
                    do_nothing();
                elif(self.dl_option == 'd'):
                    os.remove(fname);
                    return False;
                elif(self.dl_option == 'dd'):
                    print("ok deleting files in folder [%s]" % (self.from_series.sname, ));
                    shutil.rmtree(self.from_series.sname);
                    os.makedirs(self.from_series.sname);
                    return False;
                elif(self.dl_option == 'ddd'):
                    print("ok deleting folder [%s]" % (self.from_series.sname, ));
                    shutil.rmtree(self.from_series.sname);
                    return False;
                else:
                    # do_nothing();
                    return False;
                # return False;
            if(self.m3u8_unify()):
                # print(self.m3u8);
                with open(fname, 'wb') as f:
                    f.write(self.m3u8.encode());
                print("\033[1m[%s] episode [%s] downloaded as [%s]\033[0m" % (self.from_series.sname, str(self.epid), fname));
                return True;
            else:
                return False;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::episode::Download(): %s\033[0m" % e);
            return False;
