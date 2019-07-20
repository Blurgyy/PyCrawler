#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import os
import time
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
            if(self.from_file != None):
                if(os.path.exists(self.from_file)):
                    self.content = open(self.from_file).read();
                else:
                    raise Exception("%s not found" % self.from_file);
            self.is_downloading = False;
            self.retry_pool = [];
            # self.fetch();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mm3u8.py::m3u8::__init__(): %s\033[0m" % e);

    def unify(self, url = None, ):  # download and unify the m3u8 document to a universal version (i.e. playable)
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

    # def write_bin(self, url, fname, logger, logger_fname, ):  # logger is a **set**
    #     try:
    #         if(self.is_downloading):
    #             if(not is_url(url)):
    #                 raise Exception("invalid ts url");
    #             fname += ".ts";
    #             if((fname in logger) or os.path.exists(fname)):
    #                 pass;
    #             else:
    #                 with open(fname, 'wb') as f:
    #                     r = requests.get(url, stream = True);
    #                     for chunk in r.iter_content(chunk_size = 1):
    #                         f.write(chunk);
    #                 #     f.write(requests.get(url).content);
    #                 logger.add(fname);
    #                 with open(logger_fname, 'a') as f:
    #                     f.write(fname + '\n');
    #     except KeyboardInterrupt:
    #         print("\n KeyboardInterrupt, exiting");
    #         self.is_downloading = False;
    #         exit();
    #     except Exception as e:
    #         print("\033[1;31mm3u8.py::m3u8::write_bin(): %s\033[0m" % e);
    #         self.retry_pool.append([url, fname]);

    # def download(self, fname = None, ext = "ts", ): # convert the m3u8 document to a video file, default extension name is *.ts
    #     try:
    #         if(self.content == None):
    #             self.unify();
    #         if(fname == None):
    #             if(self.from_file != None):
    #                 fname = self.from_file.split('./')[-2];
    #             else:
    #                 fname = hash(self.content);
    #         fname += '.' + ext;
    #         print("video will be saved as [%s], starting download" % (fname));
    #         splitted_src = [];
    #         for line in self.content.splitlines():
    #             if(is_url(line) and is_ts(line)):
    #                 splitted_src.append(line);
    #         tmp_dl_dir = fname + ".download";
    #         if(not os.path.exists(tmp_dl_dir)):
    #             os.makedirs(tmp_dl_dir);
    #         os.chdir(tmp_dl_dir);
    #         toturlcnt = len(splitted_src);
    #         th_supervisor_list = [];
    #         current_dlcnt = [0];
    #         logger = set();
    #         logger_fname = ".download.log";
    #         if(os.path.exists(logger_fname)):
    #             logger = set(open(logger_fname).read().strip().splitlines());
    #             print("\033[33mlogfile found, resuming previous download (%d/%d)...\033[0m" % (len(logger), toturlcnt));
    #         else:
    #             pass;
    #         downloaded_cnt = [0];
    #         self.is_downloading = True;
    #         progbar_thread = myThread(target = self.progress_bar, args = (downloaded_cnt, toturlcnt, ));
    #         progbar_thread.start();
    #         for (root, dirs, files) in os.walk('.'):
    #             if(root == '.'):
    #                 for x_name in files:
    #                     if(x_name in logger):
    #                         pass;
    #                     else:
    #                         os.remove(x_name);
    #         with open(logger_fname, 'w') as f:
    #             for x in logger:
    #                 f.write(x + '\n');
    #         for i in range(toturlcnt):
    #             if(self.is_downloading):
    #                 th = myThread(target = self.write_bin, args = (splitted_src[i], "%06d"%(i), logger, logger_fname));
    #                 th_supervisor = myThread(target = supervisor, args = (th, current_dlcnt, 12, downloaded_cnt));
    #                 th_supervisor_list.append(th_supervisor);
    #                 th.start();
    #                 th_supervisor.start();
    #             else:
    #                 break;
    #         for th_supervisor in th_supervisor_list:
    #             if(self.is_downloading):
    #                 th_supervisor.join();
    #             else:
    #                 break;
    #         if(len(self.retry_pool) > 0):
    #             print("\nretrying failed items one more time...");
    #             th_supervisor_list = [];
    #             for retry_item in self.retry_pool:
    #                 print(retry_item[1]);
    #                 th = myThread(target = self.write_bin, args = (retry_item[0], retry_item[1], logger, logger_fname));
    #                 th_supervisor = myThread(target = supervisor, args = (th, current_dlcnt, 12, downloaded_cnt));
    #                 th_supervisor_list.append(th_supervisor);
    #                 th.start();
    #                 th_supervisor.start();
    #             for th_supervisor in th_supervisor_list:
    #                 th_supervisor.join();
    #         self.is_downloading = False;
    #         progbar_thread.join();
    #         os.chdir("..");
    #         print("\ndownload completed, stitching into one file...");
    #         with open(fname, 'wb') as f:
    #             x_name_list = [];
    #             for (root, dirs, files) in os.walk(tmp_dl_dir):
    #                 if(root == tmp_dl_dir):
    #                     for x in files:
    #                         x_name = root + '/' + x;
    #                         if(is_ts(x_name)):
    #                             x_name_list.append(x_name);
    #             x_name_list.sort();
    #             for x_name in x_name_list:
    #                 with open(x_name, 'rb') as fx:
    #                     f.write(fx.read());
    #         print("\033[32mcompleted\033[0m");
    #         shutil.rmtree(tmp_dl_dir);
    #     except KeyboardInterrupt:
    #         print("\n KeyboardInterrupt, exiting");
    #         self.is_downloading = False;
    #         exit();
    #     except Exception as e:
    #         print("\033[1;31mm3u8.py::m3u8::download(): %s\033[0m" % e);
    #         self.is_downloading = False;
    #         return True;

    # def progress_bar(self, downloaded_cnt, total_cnt, ):
    #     try:
    #         while(self.is_downloading):
    #             length = os.get_terminal_size().columns - 2 - 5 - 1;
    #             percent = downloaded_cnt[0] / total_cnt;
    #             done = int(percent * length);
    #             # print("\r[", end = "");
    #             bar = "\r[";
    #             for i in range(done):
    #                 # print('>', end = "");
    #                 bar += '>';
    #             for i in range(length-int(done)):
    #                 # print('-', end = "");
    #                 bar += '-';
    #             # print(']', end = "");
    #             bar += ']';
    #             # print("%02.2f%%" % (percent * 100), end = "\r");
    #             bar += "%02.2f%%" % (percent * 100);
    #             print(bar, end = "");
    #             if(downloaded_cnt[0] == total_cnt):
    #                 print('\n');
    #                 return;
    #             time.sleep(0.05);
    #     except KeyboardInterrupt:
    #         print("\n KeyboardInterrupt, exiting");
    #         self.is_downloading = False;
    #         exit();
    #     except Exception as e:
    #         print("\033[1;31mm3u8.py::m3u8::progress_bar(): %s\033[0m" % e);
    #         return True;

