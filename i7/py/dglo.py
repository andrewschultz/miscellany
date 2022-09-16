# dglo.py: sends variables to global or definitions file

import sys
import re
import os
import i7
import mytools as mt
import colorama

globals = []
main_file = []

new_main_temp = "c:/writing/temp/dglo-from.txt"
new_global_temp = "c:/writing/temp/dglo-to.txt"

def valid_variable(my_line):
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

def track_globals(main_file, global_file):
    if main_file == global_file:
        return
    globals = []
    non_globals = []
    dupe_set = set()
    with open(main_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if valid_variable(line):
                x = re.sub(" .*", "", line.strip())
                if x in dupe_set:
                    print(colorama.Fore.YELLOW + "WARNING DUPLICATE {} {}".format(x, line_count) + colorama.Style.RESET_ALL)
                else:
                    dupe_set.add(x)
                    globals.append(line)
            else:
                non_globals.append(line)
    if not len(globals):
        print(colorama.Fore.RED + "No globals found to shift over in {}.".format(main_file) + colorama.Style.RESET_ALL)
        return
    if not os.path.exists(global_file):
        for x in globals:
            print(x, end='')
        print("You may need to create a global file for", global_file)
        return
    mout = open(new_main_temp, "w")
    gin = open(global_file, "r")
    global_in_lines = gin.readlines()
    gout = open(new_global_temp, "w")
    written_yet = False
    for i in global_in_lines:
        gout.write(i)
        if ' unsorted' in i:
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
    mt.wm(main_file, new_main_temp)
    mt.wm(global_file, new_global_temp)

x = i7.dir2proj()

for fi in i7.i7f[x]:
    track_globals(fi, i7.hdr(x, 'glo'))
