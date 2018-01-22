################################
# qq.py
#
# finds all possible TODO
#
# supersedes qq.pl

import re
import os
import sys
import i7

def my_proj(x):
    y = re.split("[\\\/]", x)
    for z in y:
        if z.endswith('.inform'):
            j = re.sub("\.inform.*", "", z, 0, re.IGNORECASE)
            return j
    print("Couldn't get valid inform directory from", x)
    exit()

def file_hunt(x):
    inst = 0
    # print("HUNTING TODOS in", x)
    with open(x) as file:
        line_num = 0
        inst = 0
        first_find = 0
        for line in file:
            line_num = line_num + 1
            ll = line.lower()
            if re.search("\[.*(\?\?|todo)", ll):
                inst = inst + 1
                if first_find == 0: first_find = line_num
                if verbose: print("Line", line_num, "instance", inst, "--", line.strip())
    if inst == 0:
        print("Nothing found for", x)
        print()
        return
    if not verbose: print("      ", inst, "total instances found for", x)
    if launch_first_find:
        cmd = "start \"\" {:s} \"{:s}\" -n{:d}".format(i7.np, x, first_find)
        os.system(cmd)
    print()

def todo_hunt(x):
    x2 = "c:\\games\\inform\\{:s}.inform\\source\\story.ni".format(x)
    x3 = re.sub(r'\\', "/", x2)
    if x2 not in i7.i7f[x] and x3 not in i7.i7f[x]:
        print("WARNING you should maybe have the story.ni file in the i7.py list.")
        file_hunt(x2)
    else:
        print("TRIVIAL CHECK PASSED: story.ni file is in i7.py list...")
    if x in i7.i7f.keys():
        for y in i7.i7f[x]:
            file_hunt(y)

launch_first_find = True
search_all_qs = False
verbose = False

if len(sys.argv) > 1:
    count = 1
    while count < len(sys.argv):
        ll = sys.argv[count].lower()
        if ll == 'a':
            search_all_qs = True
            launch_first_find = False
            verbose = False
        elif ll == 'v':
            verbose = True

if search_all_qs:
    for x in i7.i7xr:
        todo_hunt(x)
else:
    if os.path.exists("story.ni"):
        todo_hunt(my_proj(os.getcwd()))