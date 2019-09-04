#!/usr/bin/python
#coding: utf-8
__author__ = "Blurgy";

import os
import re
import requests

base_url = "http://it.ouc.edu.cn/";
url = base_url + "Display/Index.aspx";

def g_url(id):
    try:
        return base_url + "Display/Content.aspx?id=" + id;
    except Exception as e:
        print("crawl.py::g_url(): %s" % e);
        return None;

def g_ids():
    try:
        content = requests.get(url).text;
        anotice_pat = re.compile(r'<div class="hp-notice">(.*?)<a href="ClickMore', flags = re.S);
        all_notice = re.findall(anotice_pat, content)[0];
        ids_pat = re.compile(r'<li>\s+?<p>.*?<span>.*?</span></p>\s+?<a href="Content\.aspx\?id=(.*?)" target="_blank">.*?</a>\s+?</li>', flags = re.S);
        ids = re.findall(ids_pat, all_notice);
        # print(ids);
        return ids;

    except Exception as e:
        print("crawl.py::gids(): %s" % e);
        return None;

def check_status(): # True: There has been an untracked update
                    # False: Everything is up-to-date
    try:
        stat_fname = ".stat";
        bak_stat_fname = ".metadata/.bak" + stat_fname; # '.bak.stat'
        stat_fname = ".metadata/" + stat_fname;
        ids = g_ids();
        if(not os.path.exists(stat_fname)):
            with open(stat_fname, 'w') as f:
                for i in ids:
                    f.write(i.strip() + '\n');
            if(not os.path.exists(bak_stat_fname)):
                with open(bak_stat_fname, 'w') as bakf:
                    for i in range(5, len(ids)):
                        bakf.write(ids[i].strip() + '\n');
            return True;
        else:
            with open(stat_fname) as f:
                with open(bak_stat_fname, 'w') as bakf:
                    bakf.write(f.read());
            with open(stat_fname) as f:
                firstid = f.readline().strip();
                if(ids[0] == firstid):
                    return False;
                else :
                    with open(stat_fname, 'w') as fw:
                        for i in ids:
                            fw.write(i.strip() + '\n');
                    return True;

    except Exception as e:
        print("crawl.py::check_status(): %s" % e);
        return None;

def unify_src(html_text):
    try:
        img_src_pat = re.compile(r'<img src="/(.*?)"');
        html_text = re.sub(img_src_pat, lambda x : '<img src=\"' + base_url + re.findall(img_src_pat, x.group())[0] + '"', html_text);

        href_pat = re.compile(r'href="/(.*?)"');
        html_text = re.sub(href_pat, lambda x : 'href="' + base_url + re.findall(href_pat, x.group())[0] + '"', html_text);
        return html_text;

    except Exception as e:
        print("crawl.py::unify_src(): %s" % e);
        return None;

def get_single(x):
    try:
        x = x.strip();
        url = g_url(x);
        content = requests.get(url).text;
        title_pat = re.compile(r'<div class="content-tittle">\s+<h1>(.*?)</h1>');
        body_pat = re.compile(r'(<div class="content-tittle">.*?</script>)', flags = re.S);
        title = re.findall(title_pat, content)[0];
        body = re.findall(body_pat, content)[0];
        body = unify_src(body);
        return [title, body, x];
    except Exception as e:
        print("crawl.py::get_single(): %s" % e);
        return None;

def get_all(lst):
    try:
        ret = [];
        for x in lst:
            ret.append(get_single(x.strip()));
        return ret;

    except Exception as e:
        print("crawl.py::get_all(): %s" % e);
        return None;

if(__name__ == "__main__"):
    try:
        # print(check_status());
        print(get_newest(3172)[0]);

    except Exception as e:
        print("crawl.py::__main__: %s" % e);
