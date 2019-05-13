#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = "Blurgy";

import re
import os
import pickle
import chardet
from urllib.parse import quote
from .tvseries import tvseries
from .globalfunctions import *


#### Global
class crawler:
    def __init__(self, _dl_option = None, _maximum_dlcnt = 8,\
        _dumpfpath = None, _loadfpath = None,\
        _ofpath = None, _preselect = None, _search_term = None):
        try:
            self.base_url = ["https://91mjw.com/", "http://v.mtyee.com/", ];
            self.s_url = [];
            self.s_url.append(self.base_url[0] + "?s=");
            self.s_url.append(self.base_url[1] + "sssv.php?top=10&q=")
            self.series = [];
            self.search_term = _search_term;
            self.Id = _preselect;
            self.dl_option = _dl_option;
            self.maximum_dlcnt = _maximum_dlcnt;
            self.dumpfpath = _dumpfpath;
            self.loadfpath = _loadfpath;
            self.ofpath = _ofpath;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::__init__(): %s\033[0m", e);

    def run(self, dump = False, load = False):
        try:
            # do_nothing();
            if(load):
                if(os.path.exists(self.loadfpath)):
                    tmp_dumpfpath = self.dumpfpath;
                    tmp_loadfpath = self.loadfpath;
                    tmp_Id = self.Id;
                    with open(self.loadfpath, 'rb') as f:
                        self = pickle.load(f);
                    self.loadfpath = tmp_loadfpath;
                    self.dumpfpath = tmp_dumpfpath;
                    self.Id = tmp_Id;
                else:
                    print("[%s]: dump file not found" % (self.loadfpath));
                    self.search();
            else:
                self.search();
                if(self.ofpath):
                    self.write_select_list();
            if(dump):
                while(self.dumpfpath and os.path.exists(self.dumpfpath)):
                    if(self.dumpfpath):
                        print("[%s] is occupied, enter another path: " % (self.dumpfpath), end = "");
                    else:
                        print("enter another path: ", end = "");
                    self.dumpfpath = input().strip();
                with open(self.dumpfpath, 'wb') as f:
                    pickle.dump(self, f);
            else:
                self.select();
                self.download();
            # self.close();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::run(): %s\033[0m", e);

    def search(self, ):
        try:
            search_term = self.search_term;
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
                    print("no TVseries found about \"%s\"" % str(search_term));
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

    def select(self, ):
        try:
            ret = [];
            if(len(self.series) == 0):
                print("nothing to select, abort");
                self.Id = ret;
                return ret;
            if(self.Id):
                return self.Id;
            else:
                print("Search Results(\033[1m%d\033[0m):" % len(self.series));
                for i in range(len(self.series)):
                    print("\t\033[1;32m%02d\033[0m. \033[4m%s\033[0m" % (i+1, self.series[i].sname));
                # print("\nselect by entering the id of the desired TVseries (enter ! to abort): ", end = "");
            entryid = "";
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
                        self.Id = ret;
                        return ret;
                    elif(re.match(r'!+', i)):
                        print("signal captured, abort");
                        ret = [];
                        self.Id = ret;
                        return ret;
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
                    self.Id = ret;
                    return ret;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::select(): %s\033[0m" % e);
            return None;

    def write_select_list(self, ):
        try:
            if(self.ofpath):
                while(not self.ofpath or os.path.exists(self.ofpath)):
                    if(self.ofpath):
                        print("[%s] is occupied, enter another path: " % (self.ofpath), end = "");
                    else:
                        print("enter another path: ", end = "");
                    self.ofpath = input().strip();
                    if(self.ofpath[0] == '$'):
                        self.ofpath = self.ofpath.strip(' \n$');
                        break;
                # print("generating slist file<br>");
                with open(self.ofpath, 'w') as f:
                    do_nothing();
                with open(self.ofpath, 'wb') as f:
                    for x in self.series:
                        f.write((x.sname + "\n").encode('utf-8'));
                print("select list written as [%s]" % (self.ofpath));
            else:
                do_nothing();
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::write_select_list(): %s\033[0m" % e);
            return None;

    def download(self, ):
        try:
            if(self.Id == None):
                self.select();
            if(isinstance(self.Id, int)):
                self.Id = [self.Id];
            if(self.Id != None):
                for i in self.Id:
                    if(self.series[i].process()):
                        self.series[i].download();
                    else:
                        continue;
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt, exiting");
            exit();
        except Exception as e:
            print("\033[1;31mcrawl.py::crawler::download(): %s\033[0m" % e);

    # def close(self, ):
    #     try:
    #         if(self.ofpath and os.path.exists(self.ofpath)):
    #             os.remove(self.ofpath);
    #         else:
    #             do_nothing();
    #     except KeyboardInterrupt:
    #         print("\n KeyboardInterrupt, exiting");
    #         exit();
    #     except Exception as e:
    #         print("\033[1;31mcrawl.py::crawler::close(): %s\033[0m" % e);


if(__name__ == "__main__"):
    try:
        # print(is_url(input()));
        x = crawler();
        x.search("game of thrones");
        x.download();
        # x.close();
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt, exiting");
        exit();
    except Exception as e:
        print("\033[1;31m???????, %s\033[0m" % e);
