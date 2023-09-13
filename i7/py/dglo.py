# dglo.py: sends variables to global or definitions file

import sys
import re
import os
from shutil import copy
import i7
import mytools as mt
import colorama

new_main_temp = "c:/writing/temp/dglo-from.txt"
new_global_temp = "c:/writing/temp/dglo-to.txt"

copy_back = False

def unsorted_start(my_line):
    if my_line.startswith("volume unsorted"):
        return True
    return False

def valid_global_variable(my_line):
    if 'is a truth state that varies' in my_line:
        return True
    if 'is a number that varies' in my_line:
        return True
    if 'is a person that varies' in my_line:
        return True
    if 'is a room that varies' in my_line:
        return True
    if re.search("is a list of [a-z ]+ variable\.", my_line):
        return True
    if re.search("^[a-z-]+ is [0-9]+\.", my_line):
        return True
    return False

def valid_definition(my_line):
    if my_line.lower().startswith('definition:'):
        return True
    if my_line.lower().startswith('to decide whether'):
        return True
    if my_line.lower().startswith('to decide which'):
        return True
    if my_line.lower().startswith('to determine '):
        return True
    return False

def track_definitions(main_file, defs_file):
    if main_file == defs_file:
        return False
    defs = []
    non_defs = []
    dupe_set = set()
    in_definitions = False
    with open(main_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if valid_definition(line):
                in_definitions = True
            if in_definitions:
                defs.append(line)
            else:
                non_defs.append(line)
            if not line.strip():
                in_definitions = False
    if not os.path.exists(defs_file):
#        for x in defs:
#            print(x, end='')
        print("You may need to create a defs file for", defs_file)
        return False
    if not len(defs):
        print(colorama.Fore.YELLOW + "No definitions found to shift over in {}.".format(main_file) + colorama.Style.RESET_ALL)
        return False
    mout = open(new_main_temp, "w")
    gin = open(defs_file, "r")
    global_in_lines = gin.readlines()
    gout = open(new_global_temp, "w")
    written_yet = False
    for i in global_in_lines:
        gout.write(i)
        if unsorted_start(i):
            for x in defs:
                gout.write(x)
            written_yet = True
    if not written_yet:
        print("write-over ops usually require UNSORTED.")
        for x in defs:
            gout.write(x)
    last_blank = False
    for i in non_defs:
        if last_blank and not i.strip():
            continue
        mout.write(i)
        last_blank = not i.strip()
    gin.close()
    gout.close()
    mout.close()
    mt.wm(main_file, new_main_temp)
    mt.wm(defs_file, new_global_temp)
    return True

def track_globals(main_file, global_file):
    if main_file == global_file:
        return False
    globals = []
    non_globals = []
    dupe_set = set()
    with open(main_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if valid_global_variable(line):
                x = re.sub(" .*", "", line.strip())
                if x in dupe_set:
                    mt.warn("WARNING DUPLICATE {} {}".format(x, line_count))
                else:
                    dupe_set.add(x)
                    globals.append(line)
            else:
                non_globals.append(line)
    if not len(globals):
        mt.okay("No globals found to shift over in {}.".format(main_file))
        return False
    if not os.path.exists(global_file):
        for x in globals:
            print(x, end='')
        mt.warn("You will need to create the file {} for me to create compares.".format(global_file))
        return False
    mout = open(new_main_temp, "w")
    gin = open(global_file, "r")
    global_in_lines = gin.readlines()
    gout = open(new_global_temp, "w")
    written_yet = False
    for i in global_in_lines:
        gout.write(i)
        if unsorted_start(i):
            for x in globals:
                gout.write(x)
            written_yet = True
    if not written_yet:
        print("write-over ops usually require UNSORTED.")
        for x in globals:
            gout.write(x)
    last_blank = False
    for i in non_globals:
        if last_blank and not i.strip():
            continue
        mout.write(i)
        last_blank = not i.strip()
    gin.close()
    gout.close()
    mout.close()
    if copy_back:
        copy(main_file, new_main_temp)
        copy(global_file, new_global_temp)
    else:
        mt.warn("To copy back automatically, use the -c flag.")
        mt.wm(main_file, new_main_temp)
        mt.wm(global_file, new_global_temp)
    return True

default_proj = i7.dir2proj()
user_proj = ''

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'c':
        copy_back = True
    elif i7.main_abb(arg):
        arg = i7.long_name(arg)
        print("Switching to project", arg)
        user_proj = arg
    else:
        sys.exit("Bad argument {}.".format(arg))
    cmd_count += 1

if user_proj:
    this_proj = user_proj
else:
    this_proj = default_proj

results = 0

if this_proj not in i7.i7f:
    if i7.main_abbr(this_proj) in i7.i7f:
        sys.exit("Expand {} to its full name in i7p.txt.".format(this_proj))
    sys.exit("Can't find project {}. Specify it on the command line or move to a directory with a project.".format(this_proj))

for fi in i7.i7f[this_proj]:
    results += track_globals(fi, i7.hdr(this_proj, 'glo'))
    results += track_definitions(fi, i7.hdr(this_proj, 'def'))

if not results:
    mt.okay("No changes were needed!")
else:
    mt.fail("{} change{} needed!".format(results, mt.plur(results)))
