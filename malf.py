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
from filecmp import cmp
from shutil import copy

temp_file = "c:\\games\\inform\\mist.i7x"

default_proj = 'ai'
# these -could- be changed via command line but it's low priority
detail_debug = False
show_difs = False

projs = []

count = 1

alpha_on = [ 'chapter', 'section' ]
alpha_off = [ 'volume', 'book', 'part' ]

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
        copy(temp_file, mf)
    if show_difs:
        os.system("wm \"{:s}\" \"{:s}\"".format(mf, temp_file))
    if detail_debug:
        print(os.path.getsize(mf), os.path.getsize(temp_file))
        toalf(mf, 'mist1.txt')
        toalf(temp_file, 'mist2.txt')
        os.system("wm mist1.txt mist2.txt")
        os.remove('mist1.txt')
        os.remove('mist2.txt')
    os.remove(temp_file)

while count < len(sys.argv):
    arg = sys.argv[count]
    projs.append(i7.lpro(arg))
    count = count + 1

if len(projs) == 0:
    print("Using default", default_proj)
    projs = [ default_proj ]

for q in projs:
    sort_mistake(q)