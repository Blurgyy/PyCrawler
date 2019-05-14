#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import re
import os
import time
import random
import shutil
from .episode import episode
from .globalfunctions import *

#### Series
class tvseries:
    def __init__(self, htmltext = None, jsontext = None, _dl_option = None, _maximum_dlcnt = 8, _verbose = True, ):
        try:
            print("<br><br>(%s)<br><br>" % _verbose);
            # print("initializing class 'tvseries' with (_dl_option = %s, _maximum_dlcnt = %s)" % (_dl_option, _maximum_dlcnt));
            self.sname = None;
            self.base_url = None;
            self._hash = None;
            self.episodes = [];
            self.dl_option = _dl_option;
            self.maximum_dlcnt = _maximum_dlcnt;
            self.verbose = _verbose;
            if(htmltext != None):
                self.parse_html(htmltext);
            elif(jsontext != None):
                self.parse_json(jsontext);
            else:
                print("class <tvseries> need more argument");
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::__init__(): %s\033[0m" % e);

    def parse_html(self, htmltext, ):
        try:
            tmp = re.findall(r'<a title=".*?/(.*?)在线.*?".*?href="(.*?)"', htmltext)[0];
            self.sname = tmp[0].replace('/', '-').strip();
            self.base_url = tmp[1].strip();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::parse_html(): %s\033[0m" % e);

    def parse_json(self, jsontext, ):
        try:
            # print("parsing json!\n%s" % jsontext);
            tmp = re.findall(r'url":"(.*?)".*?"title":"(.*?)"', jsontext, flags = re.S)[0];
            self.sname = tmp[1].replace('/', '-').strip();
            self.base_url = tmp[0].strip();
            self._hash = self.base_url.strip('/').split('/')[-1];
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::parse_json(): %s\033[0m" % e);

    def process(self, ):    # returns True if one or more download actions need to be performed, False otherwise
        try:
            ret = False;
            if(self.dl_option == 'd'):
                if(os.path.exists(self.sname)):
                    shutil.rmtree(self.sname);
                    if(self.verbose):
                        print("\033[1;33mok deleted folder: [%s]\033[0m" % (self.sname));
                else:
                    if(self.verbose):
                        print("no such folder as [%s], file structure unchanged" % (self.sname));
                return ret;
            self.episodes = [];
            content = get_content(self.base_url);
            if(split_host(self.base_url) == "https://91mjw.com"):
                all_episodes_raw = re.findall(r'<div id="video_list_li" class="video_list_li">.*?</div>', content, flags = re.S);
                single_episodes_raw = [];
                for x in all_episodes_raw:
                    single_episodes_raw += re.findall(r'<a.*?href=".*?".*?id="(.*?)">(.*?)</a>', x);
                if(self.verbose):
                    # print("[%s]: %d video(s) found" % (self.sname, len(single_episodes_raw)));
                    print("[%s]: %d url(s) found" % (self.sname, len(single_episodes_raw)));
                    # print("%d video(s) will be downloaded" % (len(single_episodes_raw)));
                for single_episode in single_episodes_raw:
                    # print(single_episode[0]);
                    self.episodes.append(episode(\
                        _base_url = split_host(self.base_url) + "/vplay/" + single_episode[0] + ".html",\
                        _epname = (single_episode[1].strip()),\
                        _from_series = self, _verbose = self.verbose\
                        ));
                    ret = True;
                return ret;
            elif(split_host(self.base_url) == "http://www.fjisu.com"):
                # print(content);
                all_episodes_raw = re.findall(r'(<ul class="details-con2-list">.*?</ul|<ul class="details-con2-list">.*?</div)', content, flags = re.S)[0];
                # print(all_episodes_raw);
                # print("all_episodes_raw is fine");
                single_episodes_raw = re.findall(r'<a.*?href="(.*?)" title="(.*?)">', all_episodes_raw);
                single_episodes_raw = list(reversed(single_episodes_raw));
                # print("single_episodes_raw is fine");
                # print("single_episodes_raw = %s" % single_episodes_raw);
                req_m3u8_urls = re.findall(r'src="(.*?%s.*?)"' % self._hash, get_content(self.base_url + single_episodes_raw[0][0]));
                # print(req_m3u8_urls);
                _m3u8_url = [];
                for url in req_m3u8_urls:
                    # print(url);
                    m3u8_metadata = get_content(url);
                    # print("\nm3u8_metadata = %s\n" % m3u8_metadata);
                    # tmp_m3u8_url = re.findall(r'(http[s]?://.*?m3u8)', m3u8_metadata);
                    tmp_m3u8_url = re.findall(r'(http[s]?://[a-zA-Z0-9-/_\.]*m3u8.*?)"', m3u8_metadata);
                    for x in range(len(tmp_m3u8_url)):
                        tmp_m3u8_url[x] = tmp_m3u8_url[x].split(',');
                    _m3u8_url += tmp_m3u8_url;
                    # print("ITERING: tmp_m3u8_url = %s" % tmp_m3u8_url);
                # print("len = %d, %d" % (len(single_episodes_raw), len(_m3u8_url)));
                if(self.verbose):
                    print("[%s]: %d url(s) found" % (self.sname, len(single_episodes_raw)));
                print("%d video(s) will be downloaded" % (len(_m3u8_url)));
                for m3u8_url in _m3u8_url:
                    # print(m3u8_url);
                    current_episode = None;
                    if(m3u8_url[-1].isdigit()):
                        episode_id = int(m3u8_url[-1].strip('",)'));
                        current_episode = single_episodes_raw[episode_id-1];
                    else:
                        episode_id = m3u8_url[-1].replace('%', '\\');
                        episode_id = episode_id.encode('latin-1').decode('unicode-escape').strip();
                        for x in single_episodes_raw:
                            if(x[1].strip() == episode_id):
                                current_episode = x;
                                break;
                        if(current_episode == None):
                            current_episode = ["tvseries::processing_generated", episode_id];
                    self.episodes.append(episode(\
                        _base_url = self.base_url + current_episode[0],\
                        _epname = (current_episode[1].strip()),\
                        _from_series = self,\
                        HASH = self._hash,\
                        _m3u8_url = m3u8_url[0], _verbose = self.verbose\
                        ));
                    ret = True;
                return ret;
            else:
                if(self.verbose):
                    print("inexplicit info when processing %s(%s), abort" % (self.sname, self.base_url));
                return ret;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::process(): %s\033[0m" % e);
            return ret;

    def download(self, ):
        try:
            current_dlcnt = [0];
            # maximum_dlcnt = 8;  # allows at most 8 downloads simultaneously
            th_supervisor_list = [];
            for ep in self.episodes:
                th = myThread(target = ep.download, );
                th_supervisor = myThread(target = supervisor, args = (th, current_dlcnt, self.maximum_dlcnt));
                th_supervisor_list.append(th_supervisor);
                th.start();
                th_supervisor.start();
                time.sleep(0.05);
                # if(ep.download()):  # download performed normaly
                #     time.sleep(random.randint(1, 3));
                # else:
                #     continue;
            for th_supervisor in th_supervisor_list:
                th_supervisor.join();
            if(os.listdir(self.sname)):
                print("\033[1;33mrenewing modify time for downloaded items...\033[0m", end = "\r");
                for ep in self.episodes:
                    ep.renew_mtime();
            else:
                os.rmdir(self.sname);
            print("\033[1;32mall pending downloads have been done         \033[0m");
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::download(): %s\033[0m" % e);
