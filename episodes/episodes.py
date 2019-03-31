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


def is_url(x):
    return not not re.match(r'^https?://\w.+$', x);
def split_host(x):
    return re.findall(r'(https?://.*?)/', x)[0];
def is_ts(x):
    return not not re.match(r'.*\.ts$', x);
def is_m3u8(x):
    return not not re.match(r'.*\.m3u8', x);
def create_headers():
    try:
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        headers = {
            # 'Cookies': "UM_distinctid=169ce771d23748-0814577fe36b88-15231708-1fa400-169ce771d24747; PHPSESSID=bltpfnmosonbp0tvb9c2ch96q5; CNZZDATA1261174353=2079538977-1553945734-%7C1553951134",
            # 'Cookies': "XSRF-TOKEN=eyJpdiI6IjZkZkJSZFZta1RqZlU0VTZkZ1hOdlE9PSIsInZhbHVlIjoiV3RpQkE3bVc0WEY2QmdnSDFNcmtWb051WDhmNUc3MTg2OHBsY0ZrQmRLVmhpM1RMNlB0UnlYb3JmM3hFRHRVUCIsIm1hYyI6ImI1Nzk3Yzg3YjYzYmViZWRhZDgzMjc5NTNkNWMzNTcxMjVlZjAwZjA2ZDNmODIyZjE3MjNjMWZmZDVjZWIwNzQifQ%3D%3D; laravel_session=eyJpdiI6Ik1BN1wvenJ6dUdHdmhuK2JwVDF4OU5BPT0iLCJ2YWx1ZSI6InlXdFE5ZitVbml1UEhrNDhaZWoxRHAySCs4K2JzbDRlaktNa2pyU0ZoTXdlSWZ6aXBiMnFpNHVRNXBJS2ZQQ3YiLCJtYWMiOiI4YWM3YzNjZjRmZTQyNjllNGE3Y2FlMTI3MzkxZGIyNjk2YTRlZGQ3NGQyODIyMDU3YzlmNmUwMDMzM2MwMjMzIn0%3D",
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
            'CLIENT-IP': ip
            # 'X-FORWARDED-FOR': ip
        }
        return headers;
    except Exception as e:
        print("episodes.py::create_headers() error: %s" % e);
        return None;

def get_content(url, headers = create_headers(), proxies = {'http': "http://61.184.109.33:61320", 'https': "https://210.5.10.87:53281"}, timeout = 9.9, ):
    try:
        content = requests.get(url, headers = headers, timeout = timeout).text;
        return html.unescape(content.encode('latin-1', 'ignore').decode('utf-8', 'ignore'));
    except Exception as e:
        print("episodes.py::get_content() error: %s" % e);
        return None;

#### Episodes
class episode:
    def __init__(self, _base_url = None, _epid = None, _from_series = None):
        try:
            self.base_url = _base_url;
            self.epid = _epid;
            self.from_series = _from_series;
            self.tvid = None;
            self.m3u8 = None;
        except Exception as e:
            print("episodes.py::episode::__init__() error: %s" % e);

    def g_tvid(self, ):
        try:
            content = get_content(self.base_url);
            if(re.search(r'tvid="(.*/)(.*?m3u8.*?)"', content)):
                self.tvid = re.findall(r'tvid="(.*/)(.*?m3u8).*?"', content)[0];
            else:
                self.tvid = re.findall(r'tvid="(.*?)"', content)[0];
                self.tvid = re.findall(r'(.*/)(\w+)', self.tvid)[0];
            return self.tvid;
        except Exception as e:
            print("episodes.py::episode::g_tvid() error: %s" % e);
            return None;

    def m3u8_unify(self, url = None):
        try:
            if(url == None):
                url = self.tvid[0] + self.tvid[1];
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
                        nurl = re.sub(url.split('/')[len(url.split('/'))-1], line, url);
                        content = get_content(nurl);
                        break;
                    else:
                        break;
                self.m3u8 = "";
                for line in content.splitlines():
                    if(not is_url(line) and is_ts(line)):
                        line = re.sub(line, re.sub(nurl.split('/')[len(nurl.split('/'))-1], line, nurl), line);
                    self.m3u8 += line + '\n';
            else:
                content = get_content(url);
                nurl = re.findall(r'"(.*?m3u8)', content)[0];
                if(not is_url(nurl)):
                    nurl = split_host(url) + nurl;
                self.m3u8_unify(nurl);
            return self.m3u8;
        except Exception as e:
            print("episodes.py::episodes::m3u8_unify() error: %s" % e);
            return None;

    def Download(self, ):   # as *.m3u8
        try:
            self.g_tvid();
            if(not os.path.exists(self.from_series.sname)):
                os.makedirs(self.from_series.sname);
            fname = self.from_series.sname + '/' + str(self.epid) + ".m3u8";
            if(os.path.exists(fname)):
                print("file [%s] already exists, skipping..." % fname);
                return False;
            if(self.m3u8_unify()):
                with open(fname, 'wb') as f:
                    f.write(self.m3u8.encode());
                print("[%s] episode [%d] downloaded as [%s]" % (self.from_series.sname, self.epid, fname));
                return True;
            else:
                return False;
        except Exception as e:
            print("episodes.py::episode::Download() error: %s" % e);
            return False;

#### Series
class tvseries:
    def __init__(self, htmltext = None, ):
        try:
            self.sname = None;
            self.base_url = None;
            self.episodes = [];
            if(htmltext != None):
                self.parse_html(htmltext);
            else:
                print("class 'tvseries' need more argument");
        except Exception as e:
            print("episodes.py::tvseries::__init__() error: %s" % e);

    def parse_html(self, htmltext, ):
        try:
            tmp = re.findall(r'<a title=".*?/(.*?)在线.*?".*?href="(.*?)"', htmltext)[0];
            self.sname = tmp[0].strip();
            self.base_url = tmp[1].strip();
        except Exception as e:
            print("episodes.py::tvseries::parse_html() error: %s" % e);

    def process(self, ):
        try:
            self.episodes = [];
            content = get_content(self.base_url);
            all_episodes_raw = re.findall(r'<div id="video_list_li" class="video_list_li">.*?</div>', content, flags = re.S)[1];
            single_episodes_raw = re.findall(r'<a.*?href="(.*?)">(.*?)</a>', all_episodes_raw);
            for single_episode in single_episodes_raw:
                self.episodes.append(episode(_base_url = self.base_url + single_episode[0], _epid = int(single_episode[1].strip()), _from_series = self));
        except Exception as e:
            print("episodes.py::tvseries::process() error: %s" % e);

    def Download(self, ):
        try:
            for ep in self.episodes:
                if(ep.Download()):  # Download finished normaly
                    time.sleep(random.randint(2, 5));
        except Exception as e:
            print("episodes.py::tvseries::Download() error: %s" % e);


#### Global
class crawl:
    def __init__(self, ):
        try:
            self.base_url = "https://91mjw.com/";
            self.s_url = self.base_url + "?s=";
            self.series = [];
        except Exception as e:
            print("episodes.py::crawl::__init__() error: %s", e);

    def search(self, term = "", ):
        try:
            while(len(term) == 0):
                print("input search terms: ", end = "");
                term = input().strip();
            self.series = [];
            targ_url = self.s_url + str(term);
            content = get_content(targ_url);
            search_results_raw = re.findall(r'(m-movies.*?</article></div>)', content, flags = re.S)[0];
            series_metadata_raw = re.findall(r'(<article class="u-movie">.*?</article>)', search_results_raw);
            if(len(series_metadata_raw) == 0):
                print("No TVseries Found about %s" % str(term));
            else:
                for htmltext in series_metadata_raw:
                    self.series.append(tvseries(htmltext));
            return self.series;
        except Exception as e:
            print("episodes.py::crawl::search() error: %s" % e);
            return None;

    def select(self, ):
        try:
            if(len(self.series) == 0):
                print("nothing to select, abort");
                return None;
            print("Search Results(%d):" % len(self.series));
            for i in range(len(self.series)):
                print("\t%02d. %s" % (i+1, self.series[i].sname));
            print("\nselect by entering the id of the desired TVseries (enter ! to abort): ", end = "");
            entryid = "";
            while(len(entryid) == 0):
                entryid = input().strip();
                if(len(entryid) == 0):
                    continue;
                elif(re.search('!', entryid)):
                    print("signal captured, abort");
                    return -1;
                elif(re.search(r'[^1234567890]', entryid) or int(entryid) < 1 or int(entryid) > len(self.series)):
                    print("invalid input, please re-enter: ", end = "");
                    entryid = "";
                else:
                    print("ok selected [%02d. %s]\n" % (int(entryid), self.series[int(entryid)-1].sname));
                    return int(entryid) - 1;
        except Exception as e:
            print("episodes.py::crawl::select() error: %s" % e);
            return None;

    def Download(self, Id = None):
        try:
            if(Id == None):
                Id = self.select();
            self.series[Id].process();
            self.series[Id].Download();
        except Exception as e:
            print("episodes.py::crawl::Download() error: %s" % e);


if(__name__ == "__main__"):
    try:
        # print(is_url(input()));
        x = crawl();
        x.search("爱 死亡 机器人");
        x.Download(x.select());
    except Exception as e:
        print("???????, %s" % e);
