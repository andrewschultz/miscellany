#
# isvis.py: looks for "is visible" in code
#

import os
import i7

ary = []

def ignore_vis(l):
    if "[v]" in l: return True
    if "[v:]" in l: return True
    if 'applying to one visible thing' in l: return True

def find_vis(proj_name):
    count_idx = 0
    x = i7.main_src(proj_name)
    if not x:
        print("Bad project name/abbreviation", proj_name)
        return
    print("Hunting visibles for", proj_name, "at", x)
    with open(x) as file:
        for (line_count, line) in enumerate(file, 1):
            if not line.startswith("\t"): last_rule = line.strip()
            if 'visible' in line and not ignore_vis(line):
                print(line_count, count_idx, last_rule if line.startswith("\t") else "", line.lower().strip())
                count_idx += 1
    print(count_idx, "total")

if i7.dir2proj(os.getcwd()) and not len(ary):
    ary = [ i7.dir2proj(os.getcwd()) ]

if not len(ary): sys.exit("Need to be in a source directory or specify a project.")

for q in ary: find_vis(q)
