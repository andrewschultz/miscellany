#
# malf.py
#
# this alphabetizes a mistake file by the possible mistakes inside the chapters/sections.
#
# most useful for Ailihphilia and the Stale Tales Slate.
#
# usage: malf.py ai
#        malf.py roi sa

import os
import sys
import i7
import re
from filecmp import cmp
from shutil import copy
from collections import defaultdict

temp_file = "c:\\games\\inform\\mist.i7x"
temp_detail_1 = "c:\\games\\inform\\mist1.i7x"
temp_detail_2 = "c:\\games\\inform\\mist2.i7x"

default_proj = 'ai'

# these -could- be changed via command line but it's low priority
detail_debug = False
copy_not_show = False
track_global_mistakes = True

projs = []

count = 1

alpha_on = [ 'chapter', 'section' ]
alpha_off = [ 'volume', 'book', 'part' ]

def breakdowns(e):
    any_slashes = False
    return_array = []
    for f in range(len(e)):
        if '/' in e[f]:
            any_slashes = True
            g = e[f].split('/')
            for h in g:
                duplist = list(e)
                duplist[f] = h
                return_array += breakdowns(duplist)
    if not any_slashes:
        return [' '.join(e)]
    return return_array

def all_mistakes(a):
    b = re.sub("^understand *\"", "", a).lower()
    b = re.sub("\" *as a mistake.*", "", b)
    c = re.split("\" *and *\"", b)
    e = []
    f = []
    for d in c:
        if '/' not in d:
            f.append(d)
            continue
        e = d.split(" ")
        f = f + breakdowns(e)
    return f

def toalf(a, b):
    f0 = open(a, "r")
    f = open(b, "w", newline="\n")
    l = f0.readlines()
    for l2 in sorted(l): f.write(l2)
    f.close()

def is_on_heading(a):
    a2 = a.lower()
    for x in alpha_on:
        if a2.startswith(x): return True
    return False

def is_off_heading(a):
    a2 = a.lower()
    for x in alpha_off:
        if a2.startswith(x): return True
    return False

def sort_mistake(pr):
    global_mistakes = defaultdict(int)
    local_mistakes = defaultdict(int)
    mf = i7.mifi(pr)
    if not os.path.exists(mf):
        print("No mistake file", mf)
        return
    print("Opening", mf)
    current_lines = ""
    sect_to_sort = []
    need_alpha = False
    f = open(temp_file, "w", newline="\n")
    with open(mf) as file:
        for (linecount, line) in enumerate(file):
            if line.lower().startswith('understand'):
                for x in all_mistakes(line.lower().strip()):
                    if x in local_mistakes.keys():
                        print(x, "at line", linecount, "locally duplicated from", local_mistakes[x])
                    elif track_global_mistakes and x in global_mistakes.keys():
                        print(x, "at line", linecount, "globally duplicated from", global_mistakes[x])
                    local_mistakes[x] = linecount
                    global_mistakes[x] = linecount
            if is_on_heading(line) or is_off_heading(line) or line.strip().endswith('ends here.'):
                if current_lines:
                    print("Need carriage return before line", linecount, ":", line.strip())
                    exit()
                if len(sect_to_sort) > 0:
                    s2 = sorted(sect_to_sort, key=str.lower)
                    f.write("\n" + "\n".join(s2) + "\n")
                elif need_alpha:
                    f.write("\n")
                need_alpha = is_on_heading(line)
                f.write(line)
                sect_to_sort = []
                local_mistakes.clear()
                continue
            if not need_alpha:
                f.write(line)
                continue
            if not line.strip():
                if current_lines:
                    sect_to_sort.append(current_lines)
                    current_lines = ""
                continue
            current_lines += line
    if current_lines: sect_to_sort.append(current_lines)
    if len(sect_to_sort):
        s2 = sorted(sect_to_sort, key=str.lower)
        f.write("\n" + "\n".join(s2) + "\n")
    elif need_alpha:
        f.write(line)
    f.close()
    if cmp(temp_file, mf):
        print("No change for", mf)
    else:
        if copy_not_show:
            copy(temp_file, mf)
        else:
            os.system("wm \"{:s}\" \"{:s}\"".format(mf, temp_file))
        if detail_debug:
            print(os.path.getsize(mf), os.path.getsize(temp_file))
            toalf(mf, temp_detail_1)
            toalf(temp_file, temp_detail_2)
            if cmp(temp_detail_1, temp_detail_2):
                print("Files are identical except for sorting.")
            else:
                os.system("wm {:s} {:s}".format(temp_detail_1, temp_detail_2))
                os.remove(temp_detail_1)
                os.remove(temp_detail_2)
    os.remove(temp_file)

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg == 'c': copy_not_show = True
    elif arg == 'd': detail_debug = True
    else: projs.append(i7.lpro(arg))
    count = count + 1

if len(projs) == 0:
    print("Using default", default_proj)
    projs = [ default_proj ]

print("Okay, processing", ', '.join(projs))

for q in projs:
    sort_mistake(q)