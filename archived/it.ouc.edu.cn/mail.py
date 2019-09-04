#!/usr/bin/python
#coding: utf-8
__author__ = "Blurgy";

import crawl
import os
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def get_auth(fname = ""):
    try:
        # fname = ".metadata/" + fname + ".sec";
        fname += ".sec";
        with open(fname) as f:
            username = f.readline().strip();
            password = f.readline().strip();
            return [username, password];

    except Exception as e:
        print("global::get_auth() error: %s" % e);
        return None;

def get_to(fname = ""):
    try:
        # fname = ".metadata/" + fname + ".to";
        fname += ".to";
        ret = [];
        with open(fname) as f:
            for line in f.readlines():
                ret.append(line.strip());
        return list(set(ret));

    except Exception as e:
        print("global::get_to() error: %s" % e);
        return None;

def newly_updated_ids():
    stat_fname = ".stat";
    bak_stat_fname = ".metadata/.bak" + stat_fname;
    stat_fname = ".metadata/" + stat_fname;
    ret = []
    current_all = [];
    last_all = [];
    try:
        if(not os.path.exists(stat_fname) or not os.path.exists(bak_stat_fname)):
            crawl.check_status();
        with open(stat_fname) as f:
            tmp = f.readlines();
            for x in tmp:
                current_all.append(x.strip());
        with open(bak_stat_fname) as bakf:
            tmp = bakf.readlines();
            for last_x in tmp:
                last_all.append(last_x.strip());
        for x in current_all:
            if(x == last_all[0]):
                break;
            ret.append(x.strip());
        return ret;
    except Exception as e:
        print("mail.py::newly_updated_ids() error: %s" % e);
        return None;

def sendEmail(Auth, From, To, Subject, Content, ContentType = "plain", From_display = "Jarvis", To_display = "DearU", Host = "smtp.qq.com"):
    try:
        smtp = smtplib.SMTP_SSL(Host);
        # smtp.set_debuglevel(1);
        smtp.login(Auth[0], Auth[1]);
        Mail = MIMEText(Content, ContentType, 'utf-8');
        Mail['Subject'] = Subject;
        Mail['From'] = From_display;
        Mail['To'] = To_display;
        smtp.sendmail(From, To, Mail.as_string());
        smtp.quit();
        return True;

    except Exception as e:
        print("global::sendEmail() error: %s" % e);
        return False;

def log_in_file(msg, fname = ""):
    try:
        fname = ".metadata/" + fname + ".log";
        with open(fname, 'a') as f:
            f.write(msg + '\n');
    except Exception as e:
        print(e);


if(__name__ == "__main__"):
    try:
        # Create directory for hidden files
        if(not os.path.exists(".metadata")):
            os.makedirs(".metadata");

        failed = [];
        fname = ".metadata/.fail";
        while(True):
            current_time = time.asctime(time.localtime(time.time()));
            if(not os.path.exists(fname)):
                with open(fname, 'w') as f:
                    1; # touch $fname
            else:
                with open(fname) as f:
                    failed = f.readlines();
                    for i in range(len(failed)):
                        failed[i] = failed[i].strip();
            with open(fname, 'w') as f:
                pass; # Overwrite
            if(len(failed) > 0 or crawl.check_status()):   # There has been (an) update(s)
                auth = get_auth("my");
                From = auth[0];
                To = get_to();

                x_all = newly_updated_ids();
                for x in failed:
                    x_all.append(x.strip());
                failed = [];
                x_all = list(set(x_all));
                x_all.sort();
                metadata_all = crawl.get_all(x_all);
                print("[%s]: %d update(s) posted" % (current_time, len(metadata_all)));
                for metadata in metadata_all:
                    Subject = "UPDATE - " + metadata[0];
                    Content = metadata[1];
                    send_status = sendEmail(auth, From, To, Subject, Content, "html");
                    if(send_status):
                        log_in_file('[' + current_time + ']' + " - " + metadata[0]);
                        print("    [%s], mail<%s> sent" % (metadata[0], metadata[2]));
                    else:
                        with open(fname, 'a') as f:
                            f.write(metadata[2] + '\n');
                        print("    [%s], mail<%s> not sent" % (metadata[0], metadata[2]));
                    time.sleep(random.randint(1, 5));
                print("You are now up-to-date\n");
            else:                       # No update in this time period
                print("[%s]: No update" % current_time);

            time.sleep(1800);

    except Exception as e:
        print("mail.py::__main__ error: %s" % e);
