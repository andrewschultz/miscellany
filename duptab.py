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

dupes = 0
dupe_without_spaces = 0
in_table = False
line_num = 0
cur_table = "(none)"

count = 1

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'ns' or arg == 'sn':
        check_spaceless = False
    elif arg == 's':
        check_spaceless = True
    else:
        print("Bad argument", arg)
        usage()
    count += 1

i7.get_table_row_count('ai', lower_case = True)

with open(table_file) as file:
    for line in file:
        line_num += 1
        if line.startswith('table'):
            in_table = True
            cur_table = line.lower().strip()
            continue
        if not line.strip():
            in_table = False
            continue
        if in_table:
            ll = line.lower().strip().split("\t")
            ignore_ok = 'okdup' in line.lower()
            if not ll[0].startswith('"'): continue
            l0 = re.sub("\"", "", ll[0])
            l0 = re.sub("[^a-z ]", "", l0)
            l1 = re.sub("[^a-z]", "", l0)
            if l0 in dup_yet.keys():
                if cur_table == t2d[l0]:
                    print("Uh oh, duplicate entry", l0, "in", cur_table, "line", line_num, "~", dup_yet[l0])
                else:
                    table_delt = i7.table_row_count[cur_table] - i7.table_row_count[t2d[l0]]
                    print("Uh oh, line {:d}/{:s} sz {:d} has >{:s}< which duplicates line {:d}/{:s} sz {:d}. {:s}".format(line_num, cur_table, i7.table_row_count[cur_table], l0, dup_yet[l0], t2d[l0], i7.table_row_count[t2d[l0]], 'EQUAL' if table_delt == 0 else (cur_table if table_delt > 0 else t2d[l0]) + ' BIGGER')) # , "which duplicates line", )
                dupes += 1
            elif l0 in dup_reverse.keys():
                print("Reversed duplicate", l0, "vs", wordrev(l0), "at line", line_num, "originally at", dup_reverse[l0])
            elif check_spaceless and l1 in dup_no_space.keys():
                if not ignore_ok:
                    print("Dup-without-spaces line", line_num, l1, l0, "from line", dup_no_space[l1])
                    dupe_without_spaces += 1
            dup_no_space[l1] = "{:d}/{:s}".format(line_num, l0)
            dup_yet[l0] = line_num
            if l0.count(' ') == 1:
                dup_reverse[wordrev(l0)] = line_num
            t2d[l0] = cur_table

print(dupes, "total duplicates.")
if dupe_without_spaces: print(dupe_without_spaces, "dupes without spaces e.g. Not On vs No Ton.")