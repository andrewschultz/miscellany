# i7clash.py: this searches for clashes between command line options and i7 project names or headers.
#
# key candidates to check: ni.py
#
# todo:
# wed out not-fully-ascii
# have "ignore"
# check only headers or only projects
# (this means rejigging the command line too)

import sys
import os
import i7
import mytools as mt

try:
    x = sys.argv[1]
except:
    mt.fail("You need a file name to check.")

cmdvar = 'cmd_count'

def left_space(my_string):
    return len(my_string) - len(my_string.lstrip(' '))

def actual_path(file_name, bail = True):
    if os.path.exists(file_name):
        return file_name
    for x in viable_paths:
        fp = os.path.join(x, file_name)
        if os.path.exists(fp):
            return fp
    if bail:
        mt.bail("No file in any paths labeled {}.".format(file_name))
    return ""

x2 = actual_path(x)

init_spaces = 0
in_param_loop = False
ever_param_loop = False

fails = 0

with open(x2) as file:
    for (line_count, line) in enumerate (file, 1):
        if 'while' in line and cmdvar in line:
            in_param_loop = True
            ever_param_loop = True
            init_spaces = left_space(line)
            continue
        if not in_param_loop:
            continue
        if not line.strip():
            in_param_loop = False
            continue
        if line.startswith('#'):
            continue
        if left_space(line) == init_spaces:
            in_param_loop = False
            continue
        apos = line.strip().lower().split("'")[1::2]
        if not len(apos):
            continue
        for a in apos:
            if a in i7.i7hfx:
                mt.warn("Uh-oh, {} clashes with a header abbreviation, {}->{}.".format(a, a, i7.i7hfx[a]))
                fails += 1
            if a in i7.i7x:
                mt.warn("Uh-oh, {} clashes with a project abbreviation, {}->{}.".format(a, a, i7.i7x[a]))
                fails += 1

if not ever_param_loop:
    mt.bailfail("Could not find while loop with {} in it in {}.".format(cmdvar, x2))

if not fails:
    mt.okay("Success! No obvious conflicts.")
else:
    mt.bailfail("{} total failure{}.".format(fails, '' if fails == 1 else 's'))