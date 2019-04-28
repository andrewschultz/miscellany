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

sort_start = defaultdict(lambda: defaultdict(int))
sort_end = defaultdict(lambda: defaultdict(int))
got_start_yet = defaultdict(bool)
got_end_yet = defaultdict(bool)

alf_file = "c:/writing/scripts/salf.txt"

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

def main_sect_alf(my_proj, my_file):
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
            for x in sort_start[my_proj].keys():
                if x in line:
                    if in_sort:
                        print("BAILING: line", line_count, "has", x, "but already in sort area", sort_name)
                    in_sort = True
                    sort_name = x
                    if verbose: print("Starting", x, "line", line_count)
                    fout.write(line)
                    sort_string = ''
                    do_more = False
                    got_start_yet[x] = True
                    continue
            for x in sort_end[my_proj].keys():
                if x in line:
                    if not in_sort:
                        print("BAILING: line", line_count, "has", x, "but is not in any sorting area.")
                    do_one_sort(sort_string.strip(), fout, 'i7x' in my_file)
                    in_sort = False
                    fout.write(line)
                    do_more = False
                    if verbose: print("stopped writing", line_count, x)
                    got_end_yet[x] = True
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

# start main

my_default_proj = i7.dir2proj()
story_file_only = False
cmd_defined_proj = ""

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = nohy(sys.argv[cmd_count])
    if arg == 'd': show_dif = True
    elif arg in i7.i7x: cmd_defined_proj = arg
    elif arg == 'f': force_copy = True
    elif arg == 'xv' or arg == 'vx': very_verbose = verbose = True
    elif arg == 'v': verbose = True
    elif arg == 'so': story_only = True
    elif arg == 'all' or arg == 'a': story_only = False
    elif arg == '?': usage()
    elif arg in i7x:
        if cmd_defined_proj: sys.exit("Redefined project from {:s} to {:s}.".format(cmd_defined_proj, i7.proj_exp(arg)))
        i7.go_proj(arg)
        cmd_defined_proj = i7.proj_exp(arg)
    else:
        usage("Invalid parameter " + arg)
    cmd_count += 1

current_project = ""

with open(alf_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith(';'): break
        if line.startswith('#'): continue
        ll = line.strip().lower().split("\t")
        print(line_count)
        if ll[0].lower().startswith("project="):
            temp = re.sub("^.*?=", "", ll[0])
            current_project = i7.proj_exp(temp)
            continue
        sort_start[current_project][ll[0]] = -1
        sort_end[current_project][ll[1]] = -1

if not cmd_defined_proj:
    cmd_defined_proj = i7.proj_exp(my_default_proj)
    if not cmd_defined_proj: sys.exit("Need to be in a project directory or request one on the command line.")

if cmd_defined_proj not in sort_start: sys.exit("Could not find {:s} in projects for {:s}".format(cmd_defined_proj, alf_file))

for x in sort_start[cmd_defined_proj]: got_start_yet[x] = False
for x in sort_end[cmd_defined_proj]: got_end_yet[x] = False

if story_file_only:
    main_sect_alf(cmd_defined_proj, i7.main_src(cmd_defined_proj))
else:
    for x in i7.i7f[cmd_defined_proj]: main_sect_alf(cmd_defined_proj, x)
    un_start = [x for x in got_start_yet if got_start_yet[x] == False]
    if len(un_start): print("Start tokens missed:", ', '.join(un_start))
    un_end = [x for x in got_end_yet if got_end_yet[x] == False]
    if len(un_end): print("End tokens missed:", ', '.join(un_end))
