#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

from urllib.parse import unquote
from .globalfunctions import *

class m3u8:
    def __init__(self, _base_url = None, _from_ep = None, ):
        try:
            # print("initializing class m3u8 with (base_url = %s, from_ep = %s)" % (_base_url, _from_ep, ));
            self.base_url = _base_url;
            if(not is_url(self.base_url)):
                self.base_url = unquote(self.base_url);
            if(not is_url(self.base_url)):
                raise Exception("invalid m3u8 url");
            self.from_ep = _from_ep;
            self.content = None;
            # self.fetch();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mm3u8.py::m3u8::__init__(): %s\033[0m" % e);

    def unify(self, url = None, ):  # download, and unify the m3u8 document to a universal version (i.e. playable)
        try:
            if(url == None):
                url = self.base_url;
            if(not is_url(url)):
                raise Exception("no url found during download");
            if(is_m3u8(url)):
                content = get_content(url);
                nurl = url;
                for line in content.splitlines():
                    if(re.match(r'^#.*?$', line)):
                        continue;
                    if(is_m3u8(line)):
                        nurl = None;
                        if(line[0] == '/'):
                            nurl = split_host(url) + line;
                        else:
                            nurl = re.sub(url.split('/')[-1], line, url);
                        # print("nurl =", nurl);
                        nurl = nurl.strip();
                        content = get_content(nurl);
                        break;
                    else:
                        break;
                self.content = "";
                for line in content.splitlines():
                    if(not is_url(line) and is_ts(line)):
                        if(line[0] == '/'):
                            host = split_host(url);
                            line = host + line;
                        else:
                            line = re.sub(line, re.sub(nurl.split('/')[-1], line, nurl), line);
                    self.content += line + '\n';
            else:   # what's this
                content = get_content(url);
                nurl = re.findall(r'"(.*?m3u8)', content)[0];
                if(not is_url(nurl)):
                    nurl = split_host(url) + nurl;
                # print(nurl);
                self.unify(nurl);
            return self.content;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mm3u8.py::m3u8::unify(): %s\033[0m" % e);
            return None;

    def download(self, fname, ext = "ts", ): # convert the m3u8 document to a video file, default extension name is *.ts
        try:
            do_nothing();   # does nothing, for now
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mm3u8.py::m3u8::download(): %s\033[0m" % e);
            return True;

