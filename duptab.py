# duptab.py
#
# searches for duplicate-ish table entries
#
# todo: specify project (currently just i7)
# todo: allow write-over (?)

from collections import defaultdict
import i7
import re
import sys

dup_yet = defaultdict(int)
dup_reverse = defaultdict(int)
dup_no_space = defaultdict(str)
t2d = defaultdict(int)

# options
check_spaceless = True

table_file = 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\Ailihphilia Tables.i7x'

def usage():
    print("-ns/-sn removes spaceless checks e.g. No Ton ~ Not On")
    print("-s allows spaceless checks (default)")
    exit()

def wordrev(w):
    a = w.split(' ')
    return a[1] + ' ' + a[0]

count = 1

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'ns' or arg == 'sn': check_spaceless = False
    elif arg == 's': check_spaceless = True
    else:
        print("Bad argument", arg)
        usage()
    count += 1

def chop_up(format_str, format_ary):
    ret_str = format_str
    for x in range(0, len(format_ary)):
        brax = '<{:d}>'.format(x)
        if brax in x: ret_str = re.sub(brax, format_ary[x], ret_str)
    return ret_str

format_string = defaultdict(str)

def table_hack(file_name):
    global dupes
    global dupe_without_spaces
    in_table = False
    cur_table = "(none)"
    i7.get_table_row_count(file_name, lower_case = True)
    temp_dup_table = defaultdict(int)
    print("Looking at", file_name)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith('table') and not in_table:
                in_table = True
                cur_table = line.lower().strip()
                temp_dup_table.clear()
                continue
            if not line.strip():
                in_table = False
                continue
            if in_table:
                ll = line.lower().strip().split("\t")
                if cur_table in format_string.keys(): lsort = chop_up(format_string[cur_table], ll)
                else: lsort = ll[0]
                if lsort in temp_dup_table.keys():
                    print(cur_table, '/', lsort, line_count, "duplicates", temp_dup_table[lsort], ':', line.strip())
                else:
                    if re.search("[a-z0-9]", lsort): temp_dup_table[lsort] = line_count
                ignore_ok = 'okdup' in line.lower()
                if not ll[0].startswith('"'): continue
                l0 = re.sub("\"", "", ll[0])
                l0 = re.sub("[^a-z ]", "", l0)
                l1 = re.sub("[^a-z]", "", l0)
                if l0 in dup_yet.keys():
                    if cur_table == t2d[l0]:
                        print("Uh oh, duplicate entry", l0, "in", cur_table, "line", line_count, "~", dup_yet[l0])
                    else:
                        table_delt = i7.table_row_count[cur_table] - i7.table_row_count[t2d[l0]]
                        print("Uh oh, line {:d}/{:s} sz {:d} has >{:s}< which duplicates line {:d}/{:s} sz {:d}. {:s}".format(line_count, cur_table, i7.table_row_count[cur_table], l0, dup_yet[l0], t2d[l0], i7.table_row_count[t2d[l0]], 'EQUAL' if table_delt == 0 else (cur_table if table_delt > 0 else t2d[l0]) + ' BIGGER')) # , "which duplicates line", )
                    dupes += 1
                elif l0 in dup_reverse.keys():
                    print("Reversed duplicate", l0, "vs", wordrev(l0), "at line", line_count, "originally at", dup_reverse[l0])
                elif check_spaceless and l1 in dup_no_space.keys():
                    if not ignore_ok:
                        print("Dup-without-spaces line", line_count, l1, l0, "from line", dup_no_space[l1])
                        dupe_without_spaces += 1
                dup_no_space[l1] = "{:d}/{:s}".format(line_count, l0)
                dup_yet[l0] = line_count
                if l0.count(' ') == 1:
                    dup_reverse[wordrev(l0)] = line_count
                t2d[l0] = cur_table

dupes = 0
dupe_without_spaces = 0

table_hack('story.ni')
table_hack(i7.tafi('ai'))

print(dupes, "total duplicates.")
if dupe_without_spaces: print(dupe_without_spaces, "dupes without spaces e.g. Not On vs No Ton.")