#
# isvis.py: looks for "is visible" in code
#

import re
import os
import i7
import sys

max_vis = 0

ary = []

def ignore_vis(l):
    if "[v]" in l: return True
    if "[v:]" in l: return True #I can do this manually
    if l.startswith("["): return True
    if l.endswith("]") and not "[" in l: return True
    if 'applying to' in l and 'one visible thing' in l: return True #actions definitions are okay

def find_vis(proj_name):
    visibles = 0
    count_idx = 0
    x = i7.main_src(proj_name)
    if not x:
        print("Bad project name/abbreviation", proj_name)
        return
    print("Hunting visibles for", proj_name, "at", x)
    with open(x) as file:
        for (line_count, line) in enumerate(file, 1):
            if not line.startswith("\t"): last_rule = line.strip()
            ll = line.lower().strip()
            if 'visible' in ll and not ignore_vis(ll):
                x = re.findall(r'\bvisible\b', ll, re.IGNORECASE)
                tv = len(x)
                if tv:
                    visibles += tv
                    count_idx += 1
                    print(line_count, count_idx, 'l{:s}'.format("" if tv == 1 else " +{:d}".format(tv)), visibles, 'tot', last_rule if line.startswith("\t") else "", line.lower().strip()) #ask codereview about a better way to do this?
    print(count_idx, "total")

if i7.dir2proj(os.getcwd()) and not len(ary):
    ary = [ i7.dir2proj(os.getcwd()) ]

if not len(ary): sys.exit("Need to be in a source directory or specify a project.")

for q in ary: find_vis(q)
