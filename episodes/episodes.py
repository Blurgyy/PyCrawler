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
    except Exception as e:
        print("episodes.py::create_headers(): %s" % e);
        return None;

def get_content(url, headers = create_headers(), proxies = {'http': "http://61.184.109.33:61320", 'https': "https://210.5.10.87:53281"}, timeout = 6.0, ):
    try:
        content = requests.get(url, headers = headers, timeout = timeout).text;
        return html.unescape(content.encode('latin-1', 'ignore').decode('utf-8', 'ignore'));
    except Exception as e:
        print("episodes.py::get_content(): %s" % e);
        return None;

#### Episodes
class episode:
    def __init__(self, _base_url = None, _epid = None, _from_series = None, HASH = None, _m3u8_url = None):
        try:
            # print("initalizing episode with (%s, %s, %s), m3u8_url = %s" % (_base_url, str(_epid), _from_series, _m3u8_url));
            self.base_url = _base_url;
            self.epid = _epid;
            self.from_series = _from_series;
            self._hash = HASH;
            self.m3u8_url = _m3u8_url;
            self.tvid = None;
            self.m3u8 = None;
        except Exception as e:
            print("episodes.py::episode::__init__(): %s" % e);

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
        except Exception as e:
            print("episodes.py::episode::g_tvid(): %s" % e);
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
        except Exception as e:
            print("episodes.py::episodes::m3u8_unify(): %s" % e);
            return None;

    def Download(self, ):   # as *.m3u8
        try:
            # self.g_tvid();
            if(not os.path.exists(self.from_series.sname)):
                os.makedirs(self.from_series.sname);
            fname = self.from_series.sname + '/' + str(self.epid) + ".m3u8";
            if(os.path.exists(fname)):
                print("file [%s] already exists, skipping..." % fname);
                return False;
            if(self.m3u8_unify()):
                # print(self.m3u8);
                with open(fname, 'wb') as f:
                    f.write(self.m3u8.encode());
                print("[%s] episode [%s] downloaded as [%s]" % (self.from_series.sname, str(self.epid), fname));
                return True;
            else:
                return False;
        except Exception as e:
            print("episodes.py::episode::Download(): %s" % e);
            return False;

#### Series
class tvseries:
    def __init__(self, htmltext = None, jsontext = None):
        try:
            self.sname = None;
            self.base_url = None;
            self._hash = None;
            self.episodes = [];
            if(htmltext != None):
                self.parse_html(htmltext);
            elif(jsontext != None):
                self.parse_json(jsontext);
            else:
                print("class <tvseries> need more argument");
        except Exception as e:
            print("episodes.py::tvseries::__init__(): %s" % e);

    def parse_html(self, htmltext, ):
        try:
            tmp = re.findall(r'<a title=".*?/(.*?)在线.*?".*?href="(.*?)"', htmltext)[0];
            self.sname = tmp[0].replace('/', '-').strip();
            self.base_url = tmp[1].strip();
        except Exception as e:
            print("episodes.py::tvseries::parse_html(): %s" % e);

    def parse_json(self, jsontext, ):
        try:
            # print("parsing json!\n%s" % jsontext);
            tmp = re.findall(r'url":"(.*?)".*?"title":"(.*?)"', jsontext, flags = re.S)[0];
            self.sname = tmp[1].replace('/', '-').strip();
            self.base_url = tmp[0].strip();
            self._hash = self.base_url.strip('/').split('/')[-1];
        except Exception as e:
            print("episodes.py::tvseries::parse_json(): %s" % e);

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
                # print(all_episodes_raw);
                single_episodes_raw = re.findall(r'<a.*?href="(.*?)" title="(.*?)">', all_episodes_raw);
                single_episodes_raw = list(reversed(single_episodes_raw));
                # print("single_episodes_raw is fine");
                # print("??????????   \n", single_episodes_raw);
                req_m3u8_urls = re.findall(r'src="(.*?%s.*?)"' % self._hash, requests.get(self.base_url + single_episodes_raw[0][0]).text);
                _m3u8_url = [];
                for url in req_m3u8_urls:
                    m3u8_metadata = get_content(url);
                    # print(m3u8_metadata);
                    # tmp_m3u8_url = re.findall(r'(http[s]?://.*?m3u8)', m3u8_metadata);
                    tmp_m3u8_url = re.findall(r'(http[s]?://[a-zA-Z0-9-/_\.]*?m3u8)', m3u8_metadata);
                    # print(tmp_m3u8_url);
                    if(len(_m3u8_url) < len(tmp_m3u8_url)):
                        _m3u8_url = tmp_m3u8_url;
                iterator = 0;
                # print("len = %d, %d" % (len(single_episodes_raw), len(_m3u8_url)));
                print("[%s]: %d url(s) found" % (self.sname, len(single_episodes_raw)));
                print("%d viedo(s) will be downloaded" % (len(_m3u8_url)));
                for single_episode in single_episodes_raw:
                    # print("%d-th url:" % iterator, end = "");
                    # print(" %s" % (_m3u8_url[iterator]));
                    self.episodes.append(episode(_base_url = self.base_url + single_episode[0], _epid = (single_episode[1].strip()), _from_series = self, HASH = self._hash, _m3u8_url = _m3u8_url[iterator]));
                    ret = True;
                    iterator += 1;
                return ret;
            else:
                print("inexplicit info when processing %s(%s), abort" % (self.sname, self.base_url));
                return ret;
        except Exception as e:
            print("episodes.py::tvseries::process(): %s" % e);
            return ret;

    def Download(self, ):
        try:
            for ep in self.episodes:
                if(ep.Download()):  # Download performed normaly
                    time.sleep(random.randint(2, 5));
                else:
                    continue;
        except Exception as e:
            print("episodes.py::tvseries::Download(): %s" % e);


#### Global
class crawl:
    def __init__(self, ):
        try:
            self.base_url = ["https://91mjw.com/", "http://v.mtyee.com/", ];
            self.s_url = [];
            self.s_url.append(self.base_url[0] + "?s=");
            self.s_url.append(self.base_url[1] + "sssv.php?top=10&q=")
            self.series = [];
        except Exception as e:
            print("episodes.py::crawl::__init__(): %s", e);

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
            except Exception as e:
                print("%s, skipping" % e);

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
            except Exception as e:
                print("%s, skipping" % e);
            return self.series;
        except Exception as e:
            print("episodes.py::crawl::search(): %s" % e);
            return None;

    def select(self, ):
        try:
            if(len(self.series) == 0):
                print("nothing to select, abort");
                return None;
            print("Search Results(%d):" % len(self.series));
            for i in range(len(self.series)):
                print("\t%02d. %s" % (i+1, self.series[i].sname));
            # print("\nselect by entering the id of the desired TVseries (enter ! to abort): ", end = "");
            entryid = "";
            ret = [];
            while(len(entryid) == 0):
                print("select by entering the id of the desired TVseries (enter ! to abort): ", end = "");
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
        except Exception as e:
            print("episodes.py::crawl::select(): %s" % e);
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
        except Exception as e:
            print("episodes.py::crawl::Download(): %s" % e);


if(__name__ == "__main__"):
    try:
        # print(is_url(input()));
        x = crawl();
        x.search("钢铁侠");
        x.Download();
    except Exception as e:
        print("???????, %s" % e);
