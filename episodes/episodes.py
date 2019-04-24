#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import requests
import re
import html
import os
import time
import random
import socket
import struct
from urllib.parse import quote
import shutil
import sys
import select


def do_nothing():
    pass;
def is_url(x):
    return not not re.match(r'^https?://\w.+$', x);
def split_host(x):
    return re.findall(r'(https?://.*?)[/$]', x)[0];
def is_ts(x):
    return not not re.match(r'.*\.ts$', x);
def is_m3u8(x):
    return not not re.match(r'.*\.m3u8', x);
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
        print("\033[1;31mepisodes.py::create_headers(): %s\033[0m" % e);
        return None;

def get_content(url, headers = create_headers(), proxies = {'http': "http://61.184.109.33:61320", 'https': "https://210.5.10.87:53281"}, timeout = 9.9, ):
    try:
        content = requests.get(url, headers = headers, timeout = timeout).text;
        return html.unescape(content.encode('latin-1', 'ignore').decode('utf-8', 'ignore'));
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31mepisodes.py::get_content(): %s\033[0m" % e);
        return None;

#### Episodes
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

#### Series
class tvseries:
    def __init__(self, htmltext = None, jsontext = None):
        try:
            self.sname = None;
            self.base_url = None;
            self._hash = None;
            self.episodes = [];
            self.dl_option = "";
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
            print("\033[1;31mepisodes.py::tvseries::__init__(): %s\033[0m" % e);

    def parse_html(self, htmltext, ):
        try:
            tmp = re.findall(r'<a title=".*?/(.*?)在线.*?".*?href="(.*?)"', htmltext)[0];
            self.sname = tmp[0].replace('/', '-').strip();
            self.base_url = tmp[1].strip();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::tvseries::parse_html(): %s\033[0m" % e);

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
            print("\033[1;31mepisodes.py::tvseries::parse_json(): %s\033[0m" % e);

    def process(self, ):
        try:
            ret = False;
            self.episodes = [];
            content = get_content(self.base_url);
            if(split_host(self.base_url) == "https://91mjw.com"):
                all_episodes_raw = re.findall(r'<div id="video_list_li" class="video_list_li">.*?</div>', content, flags = re.S)[1];
                single_episodes_raw = re.findall(r'<a.*?href="(.*?)">(.*?)</a>', all_episodes_raw);
                print("[%s]: %d video(s) found" % (self.sname, len(single_episodes_raw)));
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
                    episode_id = int(m3u8_url[-1].strip('",)'));
                    current_episode = single_episodes_raw[episode_id-1];
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
            print("\033[1;31mepisodes.py::tvseries::process(): %s\033[0m" % e);
            return ret;

    def Download(self, ):
        try:
            for ep in self.episodes:
                if(ep.Download()):  # Download performed normaly
                    time.sleep(random.randint(1, 3));
                else:
                    continue;
            print("\033[1;42;37mall pending downloads have been done, exiting\033[0m");
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::tvseries::Download(): %s\033[0m" % e);


#### Global
class crawl:
    def __init__(self, ):
        try:
            self.base_url = ["https://91mjw.com/", "http://v.mtyee.com/", ];
            self.s_url = [];
            self.s_url.append(self.base_url[0] + "?s=");
            self.s_url.append(self.base_url[1] + "sssv.php?top=10&q=")
            self.series = [];
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::crawl::__init__(): %s\033[0m", e);

    def search(self, term = "", ):
        try:
            while(len(term) == 0):
                print("input search terms: ", end = "");
                term = input().strip();
            self.series = [];
            try: # base_url[0]
                targ_url = self.s_url[0] + quote(str(term));
                content = get_content(targ_url);
                search_results_raw = re.findall(r'(m-movies.*?</article></div>)', content, flags = re.S)[0];
                series_metadata_raw = re.findall(r'(<article class="u-movie">.*?</article>)', search_results_raw);
                for htmltext in series_metadata_raw:
                    x = tvseries(htmltext);
                    if(x.sname != None):
                        self.series.append(x);
            except KeyboardInterrupt:
                print("\n KeyboardInterrupt, exiting");
                exit();
            except Exception as e:
                print("\033[1;31m%s, skipping\033[0m" % e);

            try: # base_url[1]
                targ_url = self.s_url[1] + quote(str(term));
                # print(targ_url);
                content = get_content(targ_url, headers = {'Origin': "http://www.fjisu.com"});
                series_metadata_raw = re.findall(r'(\{.*?\})', content, flags = re.S);
                for jsontext in series_metadata_raw:
                    x = tvseries(jsontext = jsontext);
                    if(x.sname != None):
                        self.series.append(x);
                if(len(self.series) == 0):
                    print("No TVseries Found about %s" % str(term));
            except KeyboardInterrupt:
                print("\n KeyboardInterrupt, exiting");
                exit();
            except Exception as e:
                print("\033[1;31m%s, skipping\033[0m" % e);
            return self.series;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::crawl::search(): %s\033[0m" % e);
            return None;

    def select(self, ):
        try:
            if(len(self.series) == 0):
                print("nothing to select, abort");
                return None;
            print("Search Results(\033[1m%d\033[0m):" % len(self.series));
            for i in range(len(self.series)):
                print("\t\033[1;32m%02d\033[0m. \033[4m%s\033[0m" % (i+1, self.series[i].sname));
            # print("\nselect by entering the id of the desired TVseries (enter ! to abort): ", end = "");
            entryid = "";
            ret = [];
            while(len(entryid) == 0):
                print("select by entering the id of the desired TVseries (enter \033[1;34m!\033[0m to abort): ", end = "");
                entryid = input().strip();
                entrylist = entryid.split();
                for i in entrylist:
                    if(len(i) == 0):
                        continue;
                    elif(re.match(r'\*', i)):
                        print("ok selected all");
                        ret = [];
                        for iid in range(len(self.series)):
                            ret.append(iid);
                        return ret;
                    elif(re.match(r'!+', i)):
                        print("signal captured, abort");
                        return None;
                    elif(re.search(r'[\D]', i) or int(i) < 1 or int(i) > len(self.series)):
                        continue;
                        # print("invalid input, please re-enter: ", end = "");
                        # entryid = "";
                    else:
                        print("ok selected [%02d. %s]" % (int(i), self.series[int(i)-1].sname));
                        ret.append(int(i)-1);
                if(len(ret) == 0):
                    entryid = "";
                else:
                    print();
                    return ret;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::crawl::select(): %s\033[0m" % e);
            return None;

    def Download(self, Id = None):
        try:
            if(Id == None):
                Id = self.select();
            if(Id != None):
                for i in Id:
                    if(self.series[i].process()):
                        self.series[i].Download();
                    else:
                        continue;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mepisodes.py::crawl::Download(): %s\033[0m" % e);


if(__name__ == "__main__"):
    try:
        # print(is_url(input()));
        x = crawl();
        x.search("game of thrones");
        x.Download();
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31m???????, %s\033[0m" % e);
