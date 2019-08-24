#tch.py
#
# table tab checker
#
# makes sure tabs are consistent
#

import re
import i7

show_short_columns = False

project = 'roi'

def tab_sort(q):
    get_tabs = False
    columns = 0
    err_count = 0
    print("Tab sorting", q)
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
                elif ll < columns and show_short_columns:
                    err_count += 1
                    print(q, my_table, line_count, "has", ll, "columns, should have", columns)
                    print(err_count, "Culprit:", line.strip())

if project in i7.i7x.keys():
    print(project, "=>", i7.i7x[project])
    project = i7.i7x[project]

if project in i7.i7f.keys():
    for q in i7.i7f[project]:
        tab_sort(q)
else:
    tab_sort(i7.src(project))