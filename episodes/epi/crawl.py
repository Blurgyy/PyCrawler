#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = "Blurgy";

import re
import os
from urllib.parse import quote
from .tvseries import tvseries
from .globalfunctions import *


#### Global
class crawler:
    def __init__(self, _dl_option = None, _maximum_dlcnt = 8, _ifpath = None, _ofpath = None):
        try:
            self.base_url = ["https://91mjw.com/", "http://v.mtyee.com/", ];
            self.s_url = [];
            self.s_url.append(self.base_url[0] + "?s=");
            self.s_url.append(self.base_url[1] + "sssv.php?top=10&q=")
            self.series = [];
            self.dl_option = _dl_option;
            self.maximum_dlcnt = _maximum_dlcnt;
            self.ifpath = _ifpath;
            self.ofpath = _ofpath;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::__init__(): %s\033[0m", e);

    def search(self, search_term = None, ):
        try:
            search_term = self.read_search_term_from_file();
            while(search_term == None or len(search_term) == 0):
                print("input search terms: ", end = "");
                search_term = input().strip();
            self.series = [];
            try: # base_url[0]
                targ_url = self.s_url[0] + quote(str(search_term));
                content = get_content(targ_url);
                search_results_raw = re.findall(r'(m-movies.*?</article></div>)', content, flags = re.S)[0];
                series_metadata_raw = re.findall(r'(<article class="u-movie">.*?</article>)', search_results_raw);
                for htmltext in series_metadata_raw:
                    x = tvseries(htmltext, _dl_option = self.dl_option, _maximum_dlcnt = self.maximum_dlcnt);
                    if(x.sname != None):
                        self.series.append(x);
            except KeyboardInterrupt:
                print("\n KeyboardInterrupt, exiting");
                exit();
            except Exception as e:
                print("\033[1;31m%s, skipping\033[0m" % e);

            try: # base_url[1]
                targ_url = self.s_url[1] + quote(str(search_term));
                # print(targ_url);
                content = get_content(targ_url, headers = {'Origin': "http://www.fjisu.com"});
                series_metadata_raw = re.findall(r'(\{.*?\})', content, flags = re.S);
                for jsontext in series_metadata_raw:
                    x = tvseries(jsontext = jsontext, _dl_option = self.dl_option, _maximum_dlcnt = self.maximum_dlcnt);
                    if(x.sname != None):
                        self.series.append(x);
                if(len(self.series) == 0):
                    print("No TVseries Found about %s" % str(search_term));
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
            print("\033[1;31mcrawl.py::crawler::search(): %s\033[0m" % e);
            return None;

    def read_search_term_from_file(self, ):
        try:
            ret = None;
            with open(self.ifpath) as f:
                ret = f.read().strip();
            if(len(ret) > 30):
                print("file too large");
                x = ret;
                ret = "";
                for ch in x:
                    ret += ch;
            return ret;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::read_search_term_from_file(): %s\033[0m" % e);
            return None;

    def select(self, ):
        try:
            if(len(self.series) == 0):
                print("nothing to select, abort");
                return None;
            print("Search Results(\033[1m%d\033[0m):" % len(self.series));
            for i in range(len(self.series)):
                print("\t\033[1;32m%02d\033[0m. \033[4m%s\033[0m" % (i+1, self.series[i].sname));
            self.output_select_list();
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
            print("\033[1;31mcrawl.py::crawler::select(): %s\033[0m" % e);
            return None;

    def output_select_list(self, ):
        try:
            if(self.ofpath):
                while(len(self.ofpath) == 0 or os.path.exists(self.ofpath)):
                    print("[%s] is occupied, enter another path: " % (self.ofpath), end = "");
                    self.ofpath = input().strip();
                    if(self.ofpath[0] == '$'):
                        self.ofpath = self.ofpath.strip(' \n$');
                        break;
                with open(self.ofpath, 'w') as f:
                    for x in self.series:
                        f.write("%s\n" % (x.sname));
            else:
                do_nothing();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::output_select_list(): %s\033[0m" % e);
            return None;

    def download(self, Id = None):
        try:
            if(Id == None):
                Id = self.select();
            if(Id != None):
                for i in Id:
                    if(self.series[i].process()):
                        self.series[i].download();
                    else:
                        continue;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::download(): %s\033[0m" % e);

    def close(self, ):
        try:
            if(self.ofpath):
                os.remove(self.ofpath);
            else:
                do_nothing();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::close(): %s\033[0m" % e);


if(__name__ == "__main__"):
    try:
        # print(is_url(input()));
        x = crawler();
        x.search("game of thrones");
        x.download();
        x.close();
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31m???????, %s\033[0m" % e);
