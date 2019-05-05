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
    def __init__(self, htmltext = None, jsontext = None, _dl_option = None):
        try:
            self.sname = None;
            self.base_url = None;
            self._hash = None;
            self.episodes = [];
            self.dl_option = _dl_option;
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
                    print("\033[1;37;43mok deleted folder: [%s]\033[0m" % (self.sname));
                else:
                    print("no such folder as [%s], file structure unchanged" % (self.sname));
                return ret;
            self.episodes = [];
            content = get_content(self.base_url);
            if(split_host(self.base_url) == "https://91mjw.com"):
                all_episodes_raw = re.findall(r'<div id="video_list_li" class="video_list_li">.*?</div>', content, flags = re.S)[1];
                single_episodes_raw = re.findall(r'<a.*?href="(.*?)">(.*?)</a>', all_episodes_raw);
                # print("[%s]: %d video(s) found" % (self.sname, len(single_episodes_raw)));
                print("[%s]: %d url(s) found" % (self.sname, len(single_episodes_raw)));
                print("%d video(s) will be downloaded" % (len(single_episodes_raw)));
                for single_episode in single_episodes_raw:
                    self.episodes.append(episode(_base_url = self.base_url + single_episode[0], _epid = (single_episode[1].strip()), _from_series = self));
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
                        episode_id = episode_id.encode('latin-1').decode('unicode-escape');
                        for x in single_episodes_raw:
                            if(x[1].strip() == episode_id):
                                current_episode = x;
                                break;
                        if(current_episode == None):
                            current_episode = ["tvseries::processing_generated", episode_id];
                    self.episodes.append(episode(_base_url = self.base_url + current_episode[0], _epid = (current_episode[1].strip()), _from_series = self, HASH = self._hash, _m3u8_url = m3u8_url[0]));
                    ret = True;
                return ret;
            else:
                print("inexplicit info when processing %s(%s), abort" % (self.sname, self.base_url));
                return ret;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::process(): %s\033[0m" % e);
            return ret;

    def Download(self, ):
        try:
            current_dlcnt = [0];
            maximum_dlcnt = 8;  # allows at most 8 downloads simultaneously
            th_supervisor_list = [];
            for ep in self.episodes:
                th = myThread(target = ep.Download, );
                th_supervisor = myThread(target = supervisor, args = (th, current_dlcnt, maximum_dlcnt));
                th_supervisor_list.append(th_supervisor);
                th.start();
                th_supervisor.start();
                time.sleep(0.05);
                # if(ep.Download()):  # Download performed normaly
                #     time.sleep(random.randint(1, 3));
                # else:
                #     continue;
            for th_supervisor in th_supervisor_list:
                th_supervisor.join();
            print("\033[1;37;43mrenewing modify time for downloaded items...\033[0m", end = "\r");
            for ep in self.episodes:
                ep.renew_mtime();
            print("\033[1;42;37mall pending downloads have been done, exiting\033[0m");
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mtvseries.py::tvseries::Download(): %s\033[0m" % e);