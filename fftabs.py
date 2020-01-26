#! /usr/bin/env python3

# fftabs.py
"""
find all Firefox tabs. Look for duplicates and top_domains etc.
"""

from collections import defaultdict
import os
import sys
import pathlib
import lz4.block
import json
import re
import mytools as mt
import codecs

any_duplicate_pages_yet = False
any_full_domains_yet = False
any_top_domains_yet = False

print_keep = False
print_to_stdout = False
open_out_after = False
open_in_browser_after = True
out_file = "c:/coding/perl/proj/fftabs.txt"
del_file = "c:/coding/perl/proj/fftabs-del.txt"

def usage():
    print("A = after, B = browser after")
    print("P = print to stdout, PO=only print to stdout, PK=keep old fftabs file")
    exit()

def domain(link, full_domain = True):
    if link.startswith("file"): return "<local>"
    temp = re.sub("^.*?//", "", link)
    if temp.startswith("www."): temp = temp[4:]
    x = temp.split("/")
    if full_domain: return x[0]
    y = x[0].split(".")
    for q in range(len(y)-1, 0, -1):
        if len(y[q]) >= 4:
            return y[q]
    return y[0]

def print_out(my_dict, header_text = "<UNDEFINED HEADER TEXT>", ):
    any_gotten_yet = False
    dupe_count = 0
    for q in sorted(my_dict, key=my_dict.get, reverse=True):
        if my_dict[q] == 1: continue
        dupe_count += my_dict[q] - 1
        if not any_gotten_yet:
            any_gotten_yet = True
            fout.write("=" * 20 + "DUPLICATE " + header_text + "=" * 20 + "\n")
        fout.write("{:3d} of {}\n".format(my_dict[q], q))
    if not any_gotten_yet:
        print("Found no {}.".format(header_text.lower()))
    else:
        fout.write("Total deletable duplicates: {}\n".format(dupe_count))

counts = defaultdict(int)
top_domains = defaultdict(int)
full_domains = defaultdict(int)

path = pathlib.WindowsPath("C:/Users/Andrew/AppData/Roaming/Mozilla/Firefox/Profiles/o72qwk6f.default")
files = path.glob('sessionstore-backups/recovery.js*')

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'b':
        open_out_after = False
        open_in_browser_after = True
    elif arg == 'a':
        open_out_after = True
        open_in_browser_after = False
    elif arg == 'p':
        print_to_stdout = True
    elif arg == 'pk' or arg == 'kp':
        print_to_stdout = True
        print_keep = True
    elif arg == 'po' or arg == 'op':
        print_to_stdout = True
        open_out_after = False
        open_in_browser_after = False
    elif arg == 'pn' or arg == 'np':
        print_to_stdout = False
    else:
        usage()
    cmd_count += 1

if not (print_to_stdout or open_out_after or open_in_browser_after):
    sys.exit("Your command line options specified nothing to do. Default.")

video_titles = []

for f in files:
    b = f.read_bytes()
    if b[:8] == b'mozLz40\0':
        b = lz4.block.decompress(b[8:])
    j = json.loads(b)
    for w in j['windows']:
        for t in w['tabs']:
            i = t['index'] - 1
            my_url = t['entries'][i]['url']
            counts[my_url] += 1
            top_domains[domain(my_url, False)] += 1
            full_domains[domain(my_url, True)] += 1
            if 'youtube' in my_url:
                if t['entries'][i]['url'] not in video_titles:
                    t1 = re.sub("^\([0-9]+\) *", "", t['entries'][i]['title'])
                    video_titles.append(t1)

if print_keep:
    out_file = del_file

fout = codecs.open(out_file, "w", "utf-8")

print_out(counts, "PAGES")
print_out(full_domains, "FULL DOMAINS")
print_out(top_domains, "TOP DOMAINS")

if len(video_titles):
    fout.write("YouTube video titles:\n")
    for vt in video_titles:
        try:
            fout.write("  * {}\n".format(vt))
        except:
            print("!", vt)
            fout.write("  * {}\n".format(vt.encode('cp1252','replace')))

fout.close()

if print_to_stdout:
    with open(out_file, 'r') as fin:
        print(fin.read(), end="")

if open_out_after:
    os.system(out_file)
if open_in_browser_after:
    mt.text_in_browser(out_file)
