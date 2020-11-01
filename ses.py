import os
import re
import mytools as mt

from collections import defaultdict
import xml.etree.ElementTree as ET

slink = defaultdict(list)

made_date = defaultdict(str)
orig_file = defaultdict(str)

file_name = mt.np_xml

dfiles = []

totals = 0
news = 0
olds = 0
e = ET.parse(file_name)
root = e.getroot()
github_warnings = 0
link_warnings = 0
for elem in e.iter('File'):
    t = elem.get('filename')
    if t.startswith('new '):
        news += 1
        base_name = t
        long_name = elem.get('backupFilePath')
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

print("10 earliest-timestamp files:")
for x in sorted(made_date, key=made_date.get)[:10]:
    print("{:7} {} {:73} {}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size))

files_by_size = sorted(made_date, key=lambda x:os.stat(orig_file[x]).st_size, reverse=True)
print("10 largest new files:")
for x in files_by_size[:10]:
    print("{:7} {} {:73} {}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size))

print("10 smallest new files:")
for x in reversed(files_by_size[-10:]):
    print("{:7} {} {:73} {}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size))

print(link_warnings, "link warnings", news, "new files", olds, "actual files", totals, "total files")
