# dglo.py: sends variables to global or definitions file

import os
import i7
import mytools as mt

globals = []
main_file = []

global_from_temp = "c:/writing/temp/dglo-from.txt"
global_to_temp = "c:/writing/temp/dglo-to.txt"

def valid_variable(my_line):
    if 'is a truth state that varies' in my_line:
        return True
    return False

def track_globals(my_file, global_file):
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if valid_variable(line):
                globals.append(line)
            else:
                main_file.append(line)
    if not len(globals):
        return
    if not os.path.exists(global_file):
        for x in globals:
            print(x, end='')
        print("You may need to create a global file for", global_file)
        return
    fin = open(global_file, "w")
    in_lines = fin.readlines()
    fout = open(global_to_temp, "w")
    written_yet = False
    for i in in_lines:
        fout.write(i)
        if ' unsorted' in i:
            for x in globals:
                fout.write(x)
            written_yet = True
    if not written_yet:
        for x in globals:
            fout.write(x)
    fin.close()
    fout.close()
    mt.wm(my_file, global_from_temp)
    mt.wm(global_file, global_to_temp)

x = i7.dir2proj()

track_globals(i7.main_src(x), i7.hdr(x, 'glo'))
