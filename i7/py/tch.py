#tch.py
#
# table tab checker
#
# makes sure tabs are consistent
#

import os
import sys
import re
import i7
import mytools as mt

show_short_columns = False

project = ''
default_project = 'roi'
dir_project = i7.dir2proj()

def tab_sort(q):
    get_tabs = False
    columns = 0
    err_count = 0
    qb = os.path.basename(q)
    print("Tab sorting", qb)
    with open(q) as file:
        for (line_count, line) in enumerate(file, 1):
            if columns and "\t\t" in line.strip():
                print("Double tabs in", q, line_count)
                continue
            if line.startswith('table of'):
                get_tabs = True
                my_table = line.strip()
                continue
            if get_tabs:
                get_tabs = False
                l2 = re.sub("\t\[.*", "", line.strip())
                columns = len(re.split("\t+", l2))
            if not line.strip():
                columns = 0
            if line.count('"') % 2:
                print("ODD NUMBER OF QUOTES {} line {}:\n    {}".format(qb, line_count, re.sub("\t", " <TAB> ", line.strip())))
            if columns:
                l2 = re.sub("\t+ *\[.*", "", line.strip())
                ll = len(re.split("\t+", l2))
                if ll > columns:
                    print(re.split("\t+", l2))
                    err_count += 1
                    print("WAY TOO MANY", q)
                    print(my_table, line_count, "has", ll, "columns, should have", columns)
                    print(err_count, "Culprit:", line.strip())
                    print("END TABS REMOVED:", l2)
                    columns = 0
                    mt.add_postopen_file_line(q, line_count)
                elif ll < columns and show_short_columns:
                    err_count += 1
                    print(q, my_table, line_count, "has", ll, "columns, should have", columns)
                    print(err_count, "Culprit:", line.strip())
                    mt.add_postopen_file_line(q, line_count)

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg in i7.i7x.keys():
        if project: sys.exit("Tried to define 2 projects at once.")
        project = i7.i7x[arg]
        if not project: sys.exit("No such project/shortcut {}.".format(project))
    cmd_count += 1

if project in i7.i7x.keys():
    print(project, "=>", i7.i7x[project])
    project = i7.i7x[project]

if not project:
    if dir_project:
        print("Current dir project", dir_project)
        project = dir_project
    elif default_project:
        print("Default project", default_project)

if project in i7.i7f.keys():
    for q in i7.i7f[project]:
        tab_sort(q)
else:
    tab_sort(i7.src(project))

mt.postopen_files()
