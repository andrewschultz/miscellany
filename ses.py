# ses.py
#
# notepad++ session data parsing script
#

import sys
import os
import re
import mytools as mt

from collections import defaultdict
import xml.etree.ElementTree as ET

slink = defaultdict(list)

made_date = defaultdict(str)
orig_file = defaultdict(str)

shuf_name_dict = defaultdict(str)
shuf_name_ord = defaultdict(int)

file_name = mt.np_xml

dfiles = []

totals = 0
news = 0
olds = 0
e = ET.parse(file_name)
root = e.getroot()
github_warnings = 0
link_warnings = 0

list_max_size = 10

def read_ses_cfg():
    ses_cfg = "c:/writing/scripts/sescfg.txt"
    cur_idx = 0
    with open(ses_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if '=' not in line:
                print("Line", line_count, "needs =")
            ary = line.strip().split("=")
            ary[0] = os.path.normpath(ary[0]).lower()
            shuf_name_dict[ary[0]] = ary[1]
            cur_idx += 1
            shuf_name_ord[ary[0]] = cur_idx
            for x in shuf_name_dict:
                if ary[0].startswith(x):
                    print("WARNING: ordering of dictionary values means {} may overlap {}.".format(ary[0], x))

def shuffle_out(starting_text):
    totes = 0
    any_yet = False
    s2 = slink.copy()
    for s in s2:
        if s.lower().startswith(starting_text):
            if not any_yet:
                print("\nFiles starting with", starting_text)
            any_yet = True
            print("    " + s)
            totes += 1
            slink.pop(s)
    if not any_yet:
        print("\nNothing started with", starting_text)
    else:
        print(totes, "total such files")

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.isdigit():
        list_max_size = int(arg)
    else:
        sys.exit("Only option now is #s for list sizes.")
    cmd_count += 1

for elem in e.iter('File'):
    t = elem.get('filename')
    if t.startswith('new '):
        base_name = t
        long_name = elem.get('backupFilePath')
        if not os.path.exists(long_name):
            print("You may have recently deleted {}/{}, so I am skipping it.".format(t, long_name))
            continue
        news += 1
        timestamp = re.sub(".*@", "", long_name)
        made_date[base_name] = timestamp
        orig_file[base_name] = long_name
        continue
    else:
        olds += 1
    q = mt.follow_link(t).lower()
    if q in slink:
        link_warnings += 1
        print("LINK WARNING: {} file and symbolic link both in notepad:".format(link_warnings))
        print(t, '=>', q)
    slink[q].append(t.lower())
    #print(elem.get('filename'))

print("{} earliest-timestamp files:".format(list_max_size))
for x in sorted(made_date, key=made_date.get)[:list_max_size]:
    print("{:7} {} {:74} {}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size))

files_by_size = sorted(made_date, key=lambda x:os.stat(orig_file[x]).st_size, reverse=True)
print("10 largest new files:")
for x in files_by_size[:list_max_size]:
    print("{:7} {} {:74} {}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size))

print("{} smallest new files:".format(list_max_size))
for x in reversed(files_by_size[-list_max_size:]):
    print("{:7} {} {:74} {}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size))

read_ses_cfg()

for x in sorted(shuf_name_ord, key=shuf_name_ord.get):
    shuffle_out(x)

if len(slink):
    print("\n{} Miscellaneous files:".format(len(slink)))
    for y in sorted(slink):
        print("    " + y)

print(link_warnings, "link warnings", news, "new files", olds, "actual files", totals, "total files")
