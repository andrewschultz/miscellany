#
# talf.py
#
# table alphabetizer/sorter in python
#

from collections import defaultdict
from shutil import copy
import os
import sys
import i7
import re

ignore_sort = defaultdict(lambda:defaultdict(str))
table_sort = defaultdict(lambda:defaultdict(str))
default_sort = defaultdict(str)

onoff = ['off', 'on']

table_default_file = "c:/writing/scripts/talf.txt"

copy_over = False
launch_dif = True
override_source_size_differences = False
override_omissions = False

def usage():
    print("-l/-nl decides whether or not to launch, default is", onoff[copy_over])
    print("-c/-nc decides whether or not to copy back over, default is", onoff[copy_over])
    print("-os overrides size differences")
    print("-oo overrides tables omitted from the data file")
    print("-e edits the data file. -ec edits the code file.")
    print("You can use a list of projects or an individual project abbreviation.")
    exit()

def tab(a, b, c): # b = boolean i = integer q = quote l = lower case
    if 'l' in c: a = a.lower()
    ary = re.split("\t+", a)
    if 'b' in c:
        return ary[b].lower() == 'true'
    if 'i' in c:
        try:
            return int(ary[b])
        except:
            return 0
    if 'q' in c:
        r = re.sub("^\"", "", lc(ary[b]), 0, re.IGNORECASE)
        r = re.sub("^[the|a|\(] ", "", r, 0, re.IGNORECASE)
        r = re.sub("\".*", "", r, 0, re.IGNORECASE)
        return r
    return ary[b]

def process_table_array(sort_orders, table_rows, file_stream):
    # print(type(sort_orders), sort_orders)
    # print(type(table_rows), table_rows)
    for q in sort_orders:
        ary = q.split('/')
        my_type = ''
        my_col = 0
        try:
            my_col = int(ary[0])
        except:
            print("Need integer in first value of", q)
        if len(ary) > 1:
            my_type = ary[1]
        reverse_order = len(ary) > 2 and ary[2] == 'r'
        count = 0
        for y in table_rows:
            count = count + 1
        # print("Before:")
        # print('\n'.join(table_rows) + '\n')
        # for y in table_rows: print(">>", y, "/", my_col, "/", my_type, "/", tab(y, my_col, my_type))
        table_rows = sorted(table_rows, key = lambda x:tab(x, my_col, my_type), reverse=reverse_order)
        # print("After:")
        # print('\n'.join(table_rows) + '\n')
    file_stream.write('\n'.join(table_rows) + '\n')

def read_table_and_default_file():
    cur_file = ""
    line_count = 0
    prev_def = defaultdict(int)
    with open(table_default_file) as file:
        for line in file:
            line_count = line_count + 1
            ll = line.lower().strip()
            if line.startswith('#'): continue
            if line.startswith(';'): break
            if '=' in line:
                right_side = re.sub(".*=", "", line.strip())
                if ll.startswith("f="):
                    cur_file = right_side
                    continue
                if ll.startswith("file="):
                    cur_file = right_side
                    continue
                if ll.startswith("ignore="):
                    ignore_sort[cur_file][right_side] = True
                    continue
                if line.lower().startswith("default="):
                    if not cur_file:
                        print("WARNING defined default with no cur_file at line", line_count)
                        continue
                    if cur_file in default_sort.keys():
                        print("WARNING: ignoring redefined default sort for", cur_file," at line", line_count, "previous line", prev_def[cur_line])
                        continue
                    default_sort[cur_file] = right_side
                    prev_def[cur_file] = line_count
                    continue
                print("Unknown = at line", line_count, ll)
                exit()
            if ':' in line:
                ary = ll.split(':')
                table_sort[cur_file][ary[0]] = ary[1]
                print(ary[0], "goes to", ary[1])
            else:
                print("Line", line_count, "needs :")

def ignorable(a, b, c):
    for a in ignore_sort[b].keys():
        if a in c:
            return True
    return False

def table_alf_one_file(f, launch=False, copy_over=False):
    print(default_sort)
    if f not in table_sort.keys() and f not in default_sort.keys():
        print(f, "has no table sort keys or default sorts. Returning.")
        return
    f2 = f + "2"
    row_array = []
    need_head = False
    in_table = False

    print("Writing", f)

    temp_out = open(f2, "w", newline="\n")
    has_default = f in default_sort.keys()
    with open(f) as file:
        for line in file:
            if need_head:
                temp_out.write(line)
                need_head = False
                continue
            if in_table:
                if line.startswith("[") or not line.strip():
                    process_table_array(what_to_sort, row_array, temp_out)
                    # print("Wrote", cur_table)
                    in_table = False
                    temp_out.write(line)
                else:
                    row_array.append(line.strip())
                continue
            if not in_table and line.startswith('table'):
                if has_default:
                    if ignorable(x, f, line):
                        print("Ignoring default for table", x, "/", line)
                        temp_out.write(line)
                        continue
                    cur_table = line.strip()
                    what_to_split = default_sort[f]
                    if cur_table in table_sort[f].keys():
                        what_to_split = table_sort[f][cur_table]
                    what_to_sort = what_to_split.split(',')
                    temp_out.write(line)
                    # if line.startswith("table"): print(">>", line.strip())
                    in_table = True
                    row_array = []
                    need_head = True
                    continue
            if line.startswith("table"): print(">>", line.strip())
            temp_out.write(line)
    if in_table:
        if line.startswith("["):
            print(line)
        if line.startswith("\[") or not line.strip():
            process_table_array(table_sort[f][cur_table], row_array, temp_out)
            in_table = False
            temp_out.write(line)
    temp_out.close()
    print("Done writing to", f2)
    if launch:
        os.system("wm \"{:s}\" \"{:s}\"".format(f, f2))
    if copy_over:
        if os.stat.getsize(f) != os.stat.getsize(f2):
            if override_source_size_differences:
                print("Different sizes, but copying anyway.")
            else:
                print(f, '=', os.stat.getsize(f), "bytes")
                print(f2, '=', os.stat.getsize(f2), "bytes")
                print('Use -os to ignore this size differences, but do verify no information was lost, first.')
                exit()
        copy(f2, f)

count = 1
projects = []
while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg in i7.i7c.keys():
        projects = projects + i7.i7c[arg]
        count = count + 1
        continue
    elif arg in i7.i7x.keys():
        projects.append(i7.i7x[arg])
        count = count + 1
        continue
    if arg.startswith('-'): arg = arg[1:]
    if arg == 'l':
        launch_dif = True
    elif arg == 'nl':
        launch_dif = False
    elif arg == 'c':
        copy_over = True
    elif arg == 'ec':
        open_source()
    elif arg == 'e':
        os.system(table_default_file)
    elif arg == 'os':
        override_source_size_differences = True
    elif arg == 'oo':
        override_omissions = True
    elif arg == 'nc':
        copy_over = False
    elif arg == '?':
        usage()
    else:
        print(arg, "is an invalid parameter.")
        usage()
    count = count + 1

projset = set(projects)
diff = len(projects) - len(projset)

if len(projects) == 0:
    print("Need to write in a project.")
    exit()

if diff > 0:
    print(diff, "duplicate project" + ("s" if diff > 1 else ""), "weeded out")
    projects = list(projset)

read_table_and_default_file()

for x in projects:
    for y in i7.i7f[x]:
        table_alf_one_file(y.lower(), launch_dif, copy_over)
