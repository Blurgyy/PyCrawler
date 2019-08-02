#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import os
from os import environ as env
import time
import hashlib
import shutil
import requests
from urllib.parse import unquote
from .globalfunctions import *

class m3u8:
    def __init__(self, _base_url = None, _from_ep = None, _from_file = None, ):
        try:
            # print("initializing class m3u8 with (base_url = %s, from_ep = %s)" % (_base_url, _from_ep, ));
            self.base_url = _base_url;
            if(self.base_url != None):
                if(not is_url(self.base_url)):
                    self.base_url = unquote(self.base_url);
                if(not is_url(self.base_url)):
                    print("invalid m3u8 url");
            self.from_ep = _from_ep;
            self.from_file = _from_file;
            self.content = None;
            self.hash = None; # hash of self.content
            if(self.from_file != None):
                if(os.path.exists(self.from_file)):
                    self.content = open(self.from_file).read();
                else:
                    raise ValueError("%s not found" % self.from_file);
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("m3u8.py::m3u8::__init__(): %s" % e);

    def calculate_hash(self, ):
        fn_name = "m3u8.py::m3u8::calculate_hash()";
        try:
            self.hash = hashlib.md5(self.content.strip().encode('utf-8')).hexdigest();
            return self.hash;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));
            return None;

    def check(self, document = None, ):
        # checks whether document(hls format) is playable 
        fn_name = "m3u8.py::m3u8::check()";
        try:
            if(document):
                for line in document.splitlines():
                    if(re.match(r'^#.*$', line)):
                        continue;
                    if(is_url(line) and is_ts(line)):
                        continue;
                    return False;
                return True;
            else:
                document = self.content;
                if(document):
                    return self.check(document);
                return False;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));
            return False;

    def unify(self, url = None):
        fn_name = "m3u8.py::m3u8::unify()";
        try:
            url = self.base_url if url == None else url;
            if(self.check()):
                self.calculate_hash();
                return self.content;
            if(not is_url(url)):
                raise ValueError("'%s' is not an url, abort" % url);
            document = get_content(url);
            if(self.check(document)):
                self.content = document;
                self.calculate_hash();
                return self.content;
            if(is_m3u8(url)):
                for line in document.splitlines():
                    if(re.match(r'^#.*$', line)):
                        continue;
                    if(is_m3u8(line)):
                        if(line[0] == '/'):
                            url = split_host(url) + line;
                        else:
                            url = re.sub(url.split('/')[-1], line, url);
                        url = url.strip();
                        document = get_content(url);
                    break;
                ret = "";
                for line in document.splitlines():
                    if(not is_url(line) and is_ts(line)):
                        if(line[0] == '/'):
                            line = split_host(url) + line;
                        else:
                            line = re.sub(url.split('/')[-1], line, url);
                    ret += line + '\n';
            else:
                host = split_host(url);
                url = re.findall(r'"(.*?\.m3u8)', document)[0];
                if(not is_url(url)):
                    url = host + url;
                self.unify(url);
            self.content = ret;
            self.calculate_hash();
            return self.content;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));

    def download(self, dldir = None): # dldir: absolute path
        self.unify();
        self.url_pool = [];
        # self.retry_pool = [];
        self.is_downloading = False;
        self.running_threads = 0;
        self.maximum_threads = 4;
        self.success_threads = 0;
        self.video_idname = self.from_ep.epname if(self.from_ep) else split_fname(self.from_file);
        self.cache_dir = None;
        if(os.name == "nt"):
            self.cache_dir = os.path.join(os.getcwd(), ".cache", self.hash);
        elif(os.name == "posix"):
            self.cache_dir = os.path.join(env["HOME"], ".cache/blurgy/m3u8Download", self.hash);
        self.cache_fname = os.path.join(self.cache_dir, self.video_idname + ".ts");
        for line in self.content.splitlines():
            if(is_url(line) and is_ts(line)):
                self.url_pool.append(line);
        self.dl_fname = None;

        fn_name = "m3u8.py::m3u8::download()";
        try:
            if(dldir == None):
                if(os.name == "nt"):
                    dldir = os.getcwd();
                elif(os.name == "posix"):
                    dldir = os.path.join(env["HOME"], "Downloads/m3u8Download");
            if(not os.path.exists(dldir)):
                os.makedirs(dldir);
            self.dl_fname = self.update_fname(dldir, self.video_idname);
            while(self.success_threads != len(self.url_pool)):
                if(self.success_threads == 0):
                    print("-- caching ..");
                else:
                    print("-- validating: [%d / %d] .." % (self.success_threads, len(self.url_pool)))
                self.cache();
                time.sleep(0.1);
            print("-- cache complete, concatenating..");
            self.concatenate();
            shutil.copy(self.cache_fname, self.dl_fname);
            print("-- concatenate complete, file saved at [%s]" % (self.dl_fname))
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));
            return False;

    def hold_dir(self, directory, ):
        fn_name = "m3u8.py::m3u8::hold_dir()";
        try:
            while(self.is_downloading):
                if(not os.path.exists(directory)):
                    os.makedirs(directory);
                time.sleep(0.1);
        except KeyboardInterrupt:
            self.is_downloading = False;
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));
            return False;

    def write_bin(self, url, target_file, ):
        fn_name = "m3u8.py::m3u8::write_bin()";
        try:
            if(self.is_downloading):
                if(not os.path.exists(target_file)):
                    with open(target_file, 'wb') as f:
                        f.write(requests.get(url, timeout = 9.9).content);
            return True;
        except KeyboardInterrupt:
            os.remove(target_file);
            self.is_downloading = False;
            print("\n KeyboardInterrupt, exiting");
            return False;
        except Exception as e:
            os.remove(target_file);
            # print("%s: %s" % (fn_name, e));
            return False;

    def cache(self, ):
        fn_name = "m3u8.py::m3u8::cache()";
        try:
            if(not os.path.exists(self.cache_dir)):
                os.makedirs(self.cache_dir);
            origin_dir = os.getcwd();
            os.chdir(self.cache_dir);

            self.is_downloading = True;
            self.running_threads = 0;
            self.maximum_threads = 6;
            self.success_threads = 0;
            progbar = myThread(target = self.progressbar, args = ());
            progbar.start();
            holddir = myThread(target = self.hold_dir, args = (self.cache_dir, ));
            holddir.start();
            self.supervisor_list = [];
            for i in range(len(self.url_pool)):
                url = self.url_pool[i];
                th = myThread(target = self.write_bin, args = (url, "%09d"%(i)));
                sup = myThread(target = self.supervisor, args = (th, ));
                sup.start();
                self.supervisor_list.append(sup);
            for sup in self.supervisor_list:
                sup.join();
            self.is_downloading = False;
            holddir.join();
            progbar.join();

            os.chdir(origin_dir);
        except KeyboardInterrupt:
            self.is_downloading = False;
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));

    def concatenate(self, ):
        fn_name = "m3u8.py::m3u8::concatenate()";
        try:
            if(self.is_downloading):
                print("download not finished, abort concatenating");
                return;

            if(os.path.exists(self.cache_fname)):
                return;
            fname = self.cache_fname;
            fd = open(fname, 'wb');
            for root, dirs, files in os.walk(self.cache_dir):
                files.sort();
                for file in files:
                    if(re.match(r'\d{9}', file)):
                        abspath = os.path.join(root, file);
                        with open(abspath, 'rb') as f:
                            fd.write(f.read());
            fd.close();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));

    def update_fname(self, fpath = None, fname = None, extname = ".ts", ):
        fn_name = "m3u8.py::m3u8::update_fname()";
        try:
            if(not os.path.exists(fpath)):
                os.makedirs(fpath);
            if(fname == None):
                fname = self.video_idname;
            ret = fname;
            idx = 1;
            while(os.path.exists(os.path.join(fpath, ret + extname))):
                idx += 1;
                ret = fname + " (%d)"%(idx);
            return fpath + '/' + ret + extname;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));
            return randstring();

    def supervisor(self, th, ):
        fn_name = "m3u8.py::m3u8::supervisor()";
        try:
            while(self.running_threads >= self.maximum_threads):
                pass;
                time.sleep(0.1);
            th.start();
            self.running_threads += 1;
            th.join();
            self.running_threads -= 1;
            if(th.fetch_result() == False):
                try:
                    os.remove(th.args[1]);
                except Exception as e:
                    pass;
            else:
                self.success_threads += 1;
        except KeyboardInterrupt:
            try:
                os.remove(th.args[1]);
            except Exception as e:
                pass;
            self.is_downloading = False;
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            try:
                os.remove(th.args[1]);
            except Exception as e:
                pass;
            print("%s: %s" % (fn_name, e));

    def progressbar(self, ):
        fn_name = "m3u8.py::m3u8::progressbar()";
        try:
            while(self.is_downloading):
                width = os.get_terminal_size().columns;
                length = width - 13;
                percent = self.success_threads / len(self.url_pool) * 100;
                # print(percent);
                print("\r [%s] %02.2f%%" % (bar(self.success_threads, len(self.url_pool), length), percent), end = '\r');
                time.sleep(0.3);
            percent = self.success_threads / len(self.url_pool) * 100;
            print(" [%s] %02.2f%%" % (bar(self.success_threads, len(self.url_pool), length), percent));
        except KeyboardInterrupt:
            self.is_downloading = False;
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("%s: %s" % (fn_name, e));
