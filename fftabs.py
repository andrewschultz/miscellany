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

any_duplicate_pages_yet = False
any_full_domains_yet = False
any_top_domains_yet = False

open_out_after = True
out_file = "c:/coding/perl/proj/fftabs.txt"

fout = open(out_file, "w")

def domain(link, full_domain = True):
    temp = re.sub("^.*?//", "", link)
    if temp.startswith("www."): temp = temp[4:]
    x = temp.split("/")
    if full_domain: return x[0]
    y = x[0].split(".")
    for q in range(len(y)-1, 0, -1):
        if len(y[q]) >= 4:
            return y[q]
    return y[0]

counts = defaultdict(int)
top_domains = defaultdict(int)
full_domains = defaultdict(int)

path = pathlib.WindowsPath("C:/Users/Andrew/AppData/Roaming/Mozilla/Firefox/Profiles/o72qwk6f.default")
files = path.glob('sessionstore-backups/recovery.js*')

try:
    template = sys.argv[1]
except IndexError:
    template = '%s (%s)'

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
            
for q in counts:
    if counts[q] == 1: continue
    if not any_duplicate_pages_yet:
        any_duplicate_pages_yet = True
        fout.write("==============DUPLICATE PAGES==============\n")
    fout.write("{} ~ {}\n".format(q, counts[q]))

if not any_duplicate_pages_yet: fout.write("No repeating individual pages.\n")

for q in sorted(full_domains, key=full_domains.get):
    if full_domains[q] == 1: continue
    if not any_full_domains_yet:
        any_full_domains_yet = True
        fout.write("==============FULL DOMAINS==============\n")
    fout.write("{} ~ {}\n".format(q, full_domains[q]))

if not any_full_domains_yet: fout.write("No repeating full domains.\n")

for q in sorted(top_domains, key=top_domains.get):
    if top_domains[q] == 1: continue
    if not any_top_domains_yet:
        any_top_domains_yet = True
        fout.write("==============TOP DOMAINS==============\n")
    fout.write("{} ~ {}\n".format(q, top_domains[q]))

if not any_top_domains_yet: fout.write("No repeating top domains.\n")

fout.close()

if open_out_after:
    os.system(out_file)