#
# isvis.py: looks for "visible" in code
#
# with proper exceptions
#
# usage: (no command parameters if in story.ni)
#
# or, list of projects
#

import re
import os
import i7
import sys

max_vis = 0

ary = []

def usage():
    print("USAGE: m# for max # of visibles, or write in a project.")
    exit()

def viscap(x):
    return re.sub(r'\bvisible\b', "VISIBLE", x)

def ignore_vis(l):
    if "[v]" in l: return True
    if "[v:]" in l: return True #I can do this manually
    if l.startswith("["): return True
    if l.endswith("]") and not "[" in l: return True
    if 'applying to' in l and ('one visible thing' in l) or ('two visible things' in l): return True #actions definitions are okay

def find_vis(proj_name):
    visibles = 0
    count_idx = 0
    ignored = 0
    x = i7.main_src(proj_name)
    if not x:
        print("Bad project name/abbreviation", proj_name)
        return
    print("===================Hunting visibles for", proj_name, "at", x)
    with open(x) as file:
        for (line_count, line) in enumerate(file, 1):
            if not line.startswith("\t"): last_rule = line.strip()
            ll = line.lower().strip()
            if 'visible' in ll and re.search(r'\bvisible\b', ll, re.IGNORECASE):
                if ignore_vis(ll):
                    ignored += 1
                    continue
                x = re.findall(r'\bvisible\b', ll, re.IGNORECASE)
                tv = len(x)
                visibles += tv
                count_idx += 1
                print("Line", line_count, "Incidence", count_idx)
                print('    l{:s}'.format("" if tv == 1 else " +{:d}".format(tv)), visibles, 'tot', last_rule if line.startswith("\t") else "", viscap(line.lower().strip())) #ask codereview about a better way to do this?
    print(count_idx, "total instances of visible for story.ni in project", proj_name)
    if ignored: print(ignored, "instances of VISIBLE ignored in project", proj_name)

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg[0] == 'm' and arg[1:].isdigit(): max_vis = int(arg[1:])
    elif i7.proj_exp(arg, return_nonblank = False):
        ary.append(i7.proj_exp(arg))
    else:
        usage()
    cmd_count += 1

if i7.dir2proj(os.getcwd()) and not len(ary):
    ary = [ i7.dir2proj(os.getcwd()) ]

if not len(ary): sys.exit("Need to be in a source directory or specify a project.")

for q in ary: find_vis(q)
