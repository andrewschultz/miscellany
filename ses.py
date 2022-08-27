# ses.py
#
# notepad++ session data parsing script
#

import sys
import os
import re
import mytools as mt
import pathlib

from collections import defaultdict
import xml.etree.ElementTree as ET

slink = defaultdict(list)

made_date = defaultdict(str)
orig_file = defaultdict(str)

new_file_description = defaultdict(str)

shuf_name_dict = defaultdict(str)
shuf_name_ord = defaultdict(int)

file_name = mt.np_xml

dfiles = []

totals = 0
unnamed = 0
named = 0
e = ET.parse(file_name)
root = e.getroot()
github_warnings = 0
link_warnings = 0

list_max_size = 10

show_blanks = False
bail_cfg_warnings = True
any_warnings = False

open_in_browser = False

open_wildcard = ""
max_wildcard = 25

ses_cfg = "c:/writing/scripts/sescfg.txt"
results_file = "c:/writing/temp/ses-results.txt"

def usage(my_msg = "General usage"):
    print(my_msg)
    print("=" * 50)
    print("-b/-nb/-bn toggles whether to print blanks")
    print("-ob/obn opens output as a text file in a web browser (or not)")
    print("A number changes the list max size")
    print("ow/oa :/= wildcard of files to open")
    print("bw/nbw or permutations = bail on warnings or not")
    print("e/c = edit cfg file")
    exit()

def desc_new(x):
    if x in new_file_description:
        return " ({})".format(new_file_description[x])
    return ""

def open_in_notepad(my_wildcard):
    count = 0
    for elem in e.iter('File'):
        t = elem.get('filename')
        if my_wildcard in t.lower():
            count += 1
            if count == max_wildcard:
                print("Went over maximum # of wildcard files to open at", t)
                break
            print(t)
            mt.add_postopen(t)
    if not count:
        print("Found nothing to open.")
    mt.postopen()
    sys.exit()

def read_ses_cfg():
    cur_idx = 0
    any_warnings = False
    with open(ses_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if '~' in line:
                ary = line.strip().split("~")
                new_file_description[ary[0].strip()] = ary[1].strip()
                continue
            elif '=' not in line:
                print("Line", line_count, "needs = or ~")
                any_warnings = True
                continue
            ary = line.strip().split("=")
            if "*" in ary[0]:
                temp = pathlib.PurePath(ary[0]).parent
                if not os.path.exists(temp):
                    print("WARNING:", ary[0], "does not exist as a directory for a glob. Please check line", line_count, "and try again.")
                    any_warnings = True
                    continue
            else:
                if not os.path.exists(ary[0]) and not "#bad path" in line:
                    print("WARNING:", ary[0], "does not exist as a directory. Please check line", line_count, "and try again.")
                    any_warnings = True
                    continue
            ary[0] = os.path.normpath(ary[0]).lower()
            cur_idx += 1
            for x in shuf_name_dict:
                if not x.endswith(os.path.sep):
                    x += os.path.sep # this is so, for instance c:/temp and c:/tempstuff aren't marked off
                if ary[0].startswith(x):
                    print("WARNING: ordering of dictionary values means {} is overlapped by parent directory {}.".format(ary[0], x))
                    any_warnings = True
            shuf_name_dict[ary[0]] = mt.zap_comment(ary[1])
            shuf_name_ord[ary[0]] = cur_idx
    if bail_cfg_warnings and any_warnings:
        print("Bailing on cfg warnings. -nbw/-bwn to disable this.")

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
        if show_blanks:
            print("\nNothing started with", starting_text)
    else:
        print(totes, "total such files")

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg.isdigit():
        list_max_size = int(arg)
    elif arg == 'b':
        show_blanks = False
    elif arg == 'nb' or arg == 'bn':
        show_blanks = True
    elif arg == 'bo' or arg == 'ob':
        open_in_browser = True
    elif arg == 'bw' or arg == 'wb':
        bail_cfg_warnings = True
    elif arg == 'nbw' or arg == 'nwb' or arg == 'bwn' or arg == 'wbn':
        bail_cfg_warnings = False
    elif arg == 'e' or arg == 'c':
        mt.npo(ses_cfg)
        exit()
    elif arg.startswith("oa:") or arg.startswith("oa=") or arg.startswith("ow:") or arg.startswith("ow="):
        open_wildcard = arg[3:]
        if not open_wildcard:
            print("You need a wildcard to open multiple files.")
            sys.exit()
    elif arg == '?':
        usage()
    else:
        usage("Unrecognized argument " + arg)
        sys.exit("Only option now is #s for list sizes.")
    cmd_count += 1

if open_wildcard:
    open_in_notepad(open_wildcard)
    sys.exit()

for elem in e.iter('File'):
    t = elem.get('filename')
    if t.startswith('new '):
        base_name = t
        long_name = elem.get('backupFilePath')
        if not os.path.exists(long_name):
            print("You may have recently deleted {}/{}, so I am skipping it.".format(t, long_name))
            continue
        unnamed += 1
        timestamp = re.sub(".*@", "", long_name)
        made_date[base_name] = timestamp
        orig_file[base_name] = long_name
        continue
    else:
        named += 1
    q = os.path.realpath(t).lower()
    if q in slink:
        link_warnings += 1
        print("LINK WARNING: {} file and symbolic link both in notepad:".format(link_warnings))
        print(slink[q], '=>', q)
    slink[q].append(t.lower())
    #print(elem.get('filename'))

read_ses_cfg()

for q in new_file_description:
    if q not in made_date:
        print("Deleted file {} ({}) is no longer in sessions.xml. Check to make sure it wasn't deleted.".format(q, new_file_description[q]))
        any_warnings = True

if any_warnings and bail_cfg_warnings:
    print("Bailing on cfg warnings. -nbw/-bwn to disable this.")
    sys.exit()

if open_in_browser:
    temp = sys.stdout
    sys.stdout = open(results_file, "w")

print("{} earliest-timestamp files:".format(list_max_size))
for x in sorted(made_date, key=made_date.get)[:list_max_size]:
    print("{:7} {} {:74} {}{}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size, desc_new(x)))

files_by_size = sorted(made_date, key=lambda x:os.stat(orig_file[x]).st_size, reverse=True)
print("10 largest new files:")
for x in files_by_size[:list_max_size]:
    print("{:7} {} {:74} {}{}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size, desc_new(x)))

print("{} smallest new files:".format(list_max_size))
for x in reversed(files_by_size[-list_max_size:]):
    print("{:7} {} {:74} {}{}".format(x, made_date[x], orig_file[x], os.stat(orig_file[x]).st_size, desc_new(x)))

for x in sorted(shuf_name_ord, key=shuf_name_ord.get):
    shuffle_out(x)

if len(slink):
    print("\n{} Miscellaneous files:".format(len(slink)))
    for y in sorted(slink):
        print("    " + y)

print(link_warnings, "link warnings", unnamed, "unnamed/new files", named, "standard files", totals, "total tabs open in Notepad")

if open_in_browser:
    sys.stdout.close()
    sys.stdout = temp
    mt.file_in_browser(results_file)
