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

detail_debug = False
copy_not_show = False
track_global_duplicates = True
super_quiet = False

projs = []

count = 1

alpha_level = 2
all_alpha = [ 'section', 'chapter', 'part', 'book', 'volume' ]

def get_alf_level(x):
    x2 = re.sub("a", "", x)
    if len(x2) == 0: return len(all_alpha)
    a1d = int(x2)
    if a1d >= 0 and a1d <= len(all_alpha): return a1d
    else: sys.exit("-a must be between 0 and {:d} inclusive--no arg means them all.".format(len(all_alpha)))

def mistake_compare(x):
    xl = x.lower()
    if xl.startswith('['): return '\n'.join(xl.split("\n")[1:])
    return xl

def usage():
    print("c = copy don't show")
    print("d = detail debug")
    print("g = track global and not just local duplicates")
    print("sq = super_quiet (for commit checks)")
    print("(a)# = outline level to sort. 1 for first, no # for all:", '/'.join(all_alpha))
    print("You can specify multiple projects or abbreviations.")
    exit()

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
    f = open(b, "w", newline=my_newline)
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
    global_duplicates = defaultdict(int)
    local_duplicates = defaultdict(int)
    mf = i7.mifi(pr)
    if not os.path.exists(mf):
        print("No mistake file", mf)
        return
    if not super_quiet: print("Opening", mf)
    current_lines = ""
    sect_to_sort = []
    need_alpha = False
    ignore_dupe_next_line = False
    loc_dupes = 0
    glo_dupes = 0
    f = open(temp_file, "w", newline=my_newline)
    with open(mf) as file:
        for (linecount, line) in enumerate(file, 1):
            ll = line.lower().rstrip()
            if ll.startswith('understand'):
                for x in all_mistakes(ll):
                    if not ignore_dupe_next_line:
                        if x in local_duplicates.keys():
                            print(x, "at line", linecount, "locally duplicated from", local_duplicates[x])
                            loc_dupes += 1
                        elif track_global_duplicates and x in global_duplicates.keys():
                            glo_dupes += 1
                            print(x, "at line", linecount, "globally duplicated from", global_duplicates[x])
                    if not x in local_duplicates.keys(): local_duplicates[x] = linecount
                    if not x in global_duplicates.keys(): global_duplicates[x] = linecount
            elif ll.startswith('u'): sys.exit("Possible misspelling of understand at line {:d} : {:s}".format(linecount, ll))
            if ignore_dupe_next_line: ignore_dupe_next_line = False
            if ll.startswith('[def'): ignore_dupe_next_line = True
            if is_on_heading(line) or is_off_heading(line) or line.strip().endswith('ends here.'):
                if current_lines:
                    print("Need carriage return before line", linecount, ":", line.strip())
                    exit()
                if len(sect_to_sort) > 0:
                    s2 = sorted(sect_to_sort, key=mistake_compare)
                    f.write("\n" + "\n".join(s2) + "\n")
                elif need_alpha:
                    f.write("\n")
                need_alpha = is_on_heading(line)
                f.write(line)
                sect_to_sort = []
                local_duplicates.clear()
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
    i7.file_len_eq(mf, temp_file)
    if cmp(temp_file, mf):
        if not super_quiet: print("No change for", mf)
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
                if not super_quiet: print("Pre/post sorting files are identical. No copying.")
            else:
                if not super_quiet: print("Pre/post sorting files are different. Copying.")
                os.system("wm {:s} {:s}".format(temp_detail_1, temp_detail_2))
                os.remove(temp_detail_1)
                os.remove(temp_detail_2)
    os.remove(temp_file)
    dupe_summary = "{:d} local duplicates".format(loc_dupes)
    if track_global_duplicates: dupe_summary += ", {:d} global duplicates.".format(glo_dupes)
    print(dupe_summary)

unix_newline = True

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c': copy_not_show = True
    elif (arg[0] == 'a' and arg[1:].isdigit()) or arg.isdigit() or (arg[-1:] =='a' and arg[:-1].isdigit()): alpha_level = get_alf_level(arg)
    elif arg == 'd': detail_debug = True
    elif arg == 'g': track_global_duplicates = True
    elif arg == 'sq': super_quiet = True
    elif arg == 'u': unix_newline = True
    elif arg == 'w': unix_newline = False
    elif arg == '?': usage()
    elif not i7.lpro(arg):
        print(arg, "does not map to any project. Showing usage.")
        usage()
    else: projs.append(i7.lpro(arg))
    count = count + 1

my_newline = "\n" if unix_newline else "\r\n"

alpha_on = all_alpha[:alpha_level]
alpha_off = all_alpha[alpha_level:]

if detail_debug:
    print('ON:', ', '.join(alpha_on), '({:d})'.format(len(alpha_on)))
    print('OFF:', ', '.join(alpha_off), '({:d})'.format(len(alpha_off)))

if len(projs) == 0:
    if not super_quiet: print("Using default", default_proj)
    projs = [ default_proj ]

if not super_quiet: print("Okay, processing", ', '.join(projs))

for q in projs:
    sort_mistake(q)