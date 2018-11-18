#
# malf.py
#
# this alphabetizes a mistake file by the possible mistakes inside the chapters/sections.
#
# Currently useful for:
#   Ailihphilia, Stale Tales Slate, (2019 project).
#
# usage: malf.py ai
#        malf.py roi sa
#        malf.py sts opo (opolis games have no mistake file, but appropriate error is thrown, so this is equivalent to the above)

import os
import sys
import i7
import re
from filecmp import cmp
from shutil import copy
from collections import defaultdict
from collections import OrderedDict

malf_cfg = "c:/writing/scripts/malf.txt"

temp_file = "c:\\games\\inform\\mist.i7x"
temp_detail_1 = "c:\\games\\inform\\mist1.i7x"
temp_detail_2 = "c:\\games\\inform\\mist2.i7x"

default_proj = i7.dir2proj()
if not default_proj: default_proj = 'ai'

sort_level = defaultdict(str)

detail_debug = False
copy_not_show = False
track_global_duplicates = True
super_quiet = False

projs = []

count = 1

alpha_level = 2
all_alpha = [ 'section', 'chapter', 'part', 'book', 'volume' ]

post_open = True
post_open_line = 0

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

def read_cfg_file():
    with open(malf_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            ll = line.strip().lower()
            if "=" not in ll:
                print("Line", line_count, "does not have = to split the project and what should be sorted.")
                continue
            la = ll.split("=")
            sort_level[la[0]] = la[1]

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
    global post_open_line
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
    flag_actual_code = False
    loc_dupes = 0
    glo_dupes = 0
    f = open(temp_file, "w", newline=my_newline)
    mfs = os.path.basename(mf)
    last_sorted_header = ""
    last_sorted_line = 0
    with open(mf) as file:
        for (line_count, line) in enumerate(file, 1):
            ll = line.lower().rstrip()
            if pr in sort_level.keys():
                q = i7.is_outline_start(ll)
                if q:
                    if q == sort_level[pr]:
                        if ll < last_sorted_header:
                            print("Chapter alphabetizing: line", line_count, ll.upper(), "behind last sorted header", last_sorted_header.upper())
                            if not post_open_line: post_open_line = line_count
                        last_sorted_header = ll
                        last_sorted_line = line_count
                    elif i7.outline_val_hash[q] > i7.outline_val_hash[sort_level[pr]]:
                        last_sorted_header = ""
            if flag_actual_code and ll and ' DOCUMENTATION ' not in line:
                sys.exit("Uh oh. Line {:d} in {:s} has code it shouldn't. You need to adjust the 'ends here' line.".format(line_count, mfs))
            if ll.startswith('understand'):
                for x in all_mistakes(ll):
                    if not ignore_dupe_next_line:
                        if x in local_duplicates.keys():
                            print(x, "at line", line_count, "locally duplicated from", local_duplicates[x])
                            loc_dupes += 1
                        elif track_global_duplicates and x in global_duplicates.keys():
                            glo_dupes += 1
                            print(x, "at line", line_count, "globally duplicated from", global_duplicates[x])
                    if not x in local_duplicates.keys(): local_duplicates[x] = line_count
                    if not x in global_duplicates.keys(): global_duplicates[x] = line_count
            elif ll.startswith('u'): sys.exit("Possible misspelling of understand at line {:d} : {:s}".format(line_count, ll))
            if ignore_dupe_next_line: ignore_dupe_next_line = False
            if ll.startswith('[def'): ignore_dupe_next_line = True
            if is_on_heading(line) or is_off_heading(line) or line.strip().endswith('ends here.'):
                if line.strip().endswith('ends here.'): flag_actual_code = True
                if current_lines:
                    print("Need carriage return before line", line_count, ":", line.strip())
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
    if not flag_actual_code:
        sys.exit("You should never hit this error, but if you do, you need a line saying\n{:s} ends here.\n".format(mfs))
    if current_lines: sect_to_sort.append(current_lines)
    if len(sect_to_sort):
        s2 = sorted(sect_to_sort, key=str.lower)
        f.write("\n" + "\n".join(s2) + "\n")
    elif need_alpha:
        f.write(line)
    f.close()
    i7.file_len_eq(mf, temp_file, True, True)
    if cmp(temp_file, mf):
        if not super_quiet: print("No change for", mf)
    else:
        if copy_not_show:
            copy(temp_file, mf)
        else:
            os.system("wm \"{:s}\" \"{:s}\"".format(mf, temp_file))
            print("Only showing. Use -c to copy back over.")
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
    elif arg in i7.i7com.keys():
        projs += i7.i7com[arg].split(",")
    elif not i7.lpro(arg):
        print(arg, "does not map to any project. Showing usage.")
        usage()
    else: projs.append(i7.lpro(arg))
    count = count + 1

my_newline = "\n" if unix_newline else "\r\n"

alpha_on = all_alpha[:alpha_level]
alpha_off = all_alpha[alpha_level:]

read_cfg_file()

if detail_debug:
    print('ON:', ', '.join(alpha_on), '({:d})'.format(len(alpha_on)))
    print('OFF:', ', '.join(alpha_off), '({:d})'.format(len(alpha_off)))

if len(projs) == 0:
    if not super_quiet: print("Using default", default_proj)
    projs = [ default_proj ]

if not super_quiet: print("Okay, processing", ', '.join(projs))

pod = OrderedDict.fromkeys(projs)

for q in pod:
    sort_mistake(q)
    if post_open and post_open_line:
        i7.npo(i7.mifi(q), post_open_line, True, False)
    post_open_line = 0