#! /usr/bin/env python3

"""
List all Firefox tabs with title and URL

Supported input: json or jsonlz4 recovery files
Default output: title (URL)
Output format can be specified as argument
"""

import sys
import pathlib
import lz4.block
import json
import os
import re

from collections import defaultdict

print_all_pages = True

def domain_of(my_url):
    x = re.sub(".*\/\/", "", my_url)
    retval = x.split('/')[0]
    if retval == 'c:':
        return '(local)'
    elif retval.startswith('about'):
        return '(about pages)'
    return retval

dupe_page = defaultdict(int)
domain_count = defaultdict(int)

if os.name == 'nt':
    path = pathlib.Path(os.environ['APPDATA']).joinpath('Mozilla\\Firefox\\Profiles')
else:
    path = pathlib.Path.home().joinpath('.mozilla/firefox')
files = path.glob('*default*/sessionstore-backups/recovery.js*')

template = '%s (%s)'

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if '%s' in arg:
        template = arg
    elif arg == 'p':
        print_all_pages = False
    elif arg in ( 'np', 'pn' ):
        print_all_pages = True

count = 0

for f in files:
    b = f.read_bytes()
    if b[:8] == b'mozLz40\0':
        b = lz4.block.decompress(b[8:])
    j = json.loads(b)
    for w in j['windows']:
        for t in w['tabs']:
            i = t['index'] - 1
            count += 1
            my_url = t['entries'][i]['url']
            dupe_page[my_url] += 1
            my_domain = domain_of(my_url)
            domain_count[my_domain] += 1

d2 = [x for x in dupe_page if dupe_page[x] > 1]

def eq_print(*args):
    buffer = 30
    str_args = [str(x) for x in args]
    str_args[0] = '=' * buffer + str_args[0] + '=' * buffer
    print(' '.join([str(x) for x in args]))

if len(d2):
    eq_print("DUPLICATE PAGES", len(d2), "pages", sum([dupe_page[x] for x in d2]), "total duplicates")
    for x in dupe_page:
        if dupe_page[x] > 1:
            print(x, dupe_page[x])

eq_print("=====================DOMAIN COUNT======================", len(domain_count), "total domains", count, "total pages")
for x in sorted(domain_count, key=lambda x:(domain_count[x], x), reverse=True):
    print(x, domain_count[x])

if print_all_pages:
    eq_print("ALL PAGES")