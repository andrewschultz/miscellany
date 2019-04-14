# salf.py
#
# section alphabetizer (for inform files)
#
# separate from salf.pl which is the Alec Smart section alphabetizer
# confusing I know but it needs to be sorted
#

from collections import defaultdict
from shutil import copy
import os
import sys
import i7
from filecmp import cmp
from mytools import nohy
import re

copy_over = True
show_dif = False
force_copy = False
verbose = False
very_verbose = False

sort_start = defaultdict(str)
sort_end = defaultdict(str)

def usage(header="USAGE FOR SALF.PY"):
    print(header)
    print("=" * 50)
    print("-d = show differences if something goes wrong")
    print("-f = force copy-over on different sizes")
    print("-v = verbose")
    exit()

def do_one_sort(sort_string, fout, zap_prefix = False):
    divs = sort_string.split("\n\n")
    ow = "\n\n".join(sorted(divs, key=lambda x: (re.sub(" [a-z]+-", "", x.lower()) if zap_prefix else x.lower())))
    fout.write("\n" + ow + "\n\n")
    return

# start main

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = nohy(sys.argv[cmd_count])
    if arg == 'd': show_dif = True
    elif arg == 'f': force_copy = True
    elif arg == 'vv': very_verbose = verbose = True
    elif arg == 'v': verbose = True
    elif arg == '?': usage()
    elif arg in i7x: i7.go_proj(sys.argv[1])
    else:
        usage("Invalid parameter " + arg)
else:
    print("Using current directory.")

if not os.path.exists('story.ni'):
    print("No story.ni in path. Please check and try again.")
    exit()


if not os.path.exists("salf.txt"): sys.exit("Need salf.txt in path to do anything.")

with open("salf.txt") as file:
    for line in file:
        if line.startswith(';'): break
        if line.startswith('#'): continue
        ll = line.strip().lower().split("\t")
        sort_start[ll[0]] = ll[1]
        sort_end[ll[1]] = ll[0]

def main_sect_alf(my_file):
    my_bak = my_file + ".bak"
    fout = open(my_bak, "w", newline="\n")
    print("Alphabetizing sections in", my_file, "...")
    in_sort = False
    sort_name = ''
    sort_string = ''
    alf_next_chunk = False
    alf_next_blank = False
    sort_array = []
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            do_more = True
            for x in sort_start.keys():
                if x in line:
                    if in_sort:
                        print("BAILING: line", line_count, "has", x, "but already in sort area", x)
                    in_sort = True
                    sort_name = x
                    if verbose: print("Starting", x, "line", line_count)
                    fout.write(line)
                    sort_string = ''
                    do_more = False
                    continue
            for x in sort_end.keys():
                if x in line:
                    if sort_end[x] != sort_name:
                        print("Conflict:", x, start_of[x], "line", )
                        exit()
                    do_one_sort(sort_string.strip(), fout, 'i7x' in my_file)
                    in_sort = False
                    fout.write(line)
                    do_more = False
                    if verbose: print("stopped writing", line_count)
                    continue
            if alf_next_chunk:
                sort_array = []
                if not alf_next_blank and line.strip():
                    alf_next_blank = True
                    alf_next_chunk = False
                    sort_array.append(line)
                    continue
            if alf_next_blank:
                if not line.strip():
                    sort_array = sorted(sort_array, key=lambda x:x.lower())
                    for q in sort_array: fout.write(q)
                    alf_next_blank = False
                else:
                    sort_array.append(line)
                    continue
            if "[postalf]" in line:
                alf_next_chunk = True
            if do_more:
                if in_sort:
                    sort_string = sort_string + line
                else:
                    fout.write(line)
    fout.close()
    if show_dif:
        if cmp(my_file, my_bak): print(my_file, "and", my_bak, "are identical. Not showing.")
        else: i7.wm(my_file, my_bak)
    else:
        print("Not showing differences.")
    s1 = os.stat(my_file).st_size
    s2 = os.stat(my_bak).st_size
    if copy_over:
        if cmp(my_file, my_bak):
            print("Sorting the rules changed nothing. Not copying.")
            os.remove(my_bak)
            return
        elif s1 != s2 and not force_copy:
            print("Sizes unequal. Use -f to force copy over. Saved", my_bak, "for inspection.{:s}".format("" if show_dif else " -d shows differences."))
            print(my_file, s1)
            print(my_bak, s2)
            if show_dif: i7.wm(my_file, my_bak)
            return
        print("Changes found, copying back.")
        copy(my_bak, my_file)
    else:
        print("Use -c to copy over.")
    os.remove(my_bak)
    
main_sect_alf("story.ni")
if "very" in os.getcwd():
    main_sect_alf(i7.tafi("vvff"))