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
from filecmp import cmp

copy_over = True
show_dif = False
force_copy = False
verbose = False

f1 = 'story.ni'
f2 = 'story.ni2'

sort_start = defaultdict(str)
sort_end = defaultdict(str)

def do_one_sort(sort_string, out_file):
    divs = sort_string.split("\n\n")
    ow = "\n\n".join(sorted(divs, key=lambda x: x.lower()))
    fout.write("\n" + ow + "\n\n")
    return

# start main

if len(sys.argv) > 1:
    go_proj(sys.argv[1])
else:
    print("Using current directory.")

if not os.path.exists('story.ni'):
    print("No story.ni in path. Please check and try again.")
    exit()

fout = open(f2, "w", newline="\n")

with open("salf.txt") as file:
    for line in file:
        if line.startswith(';'): break
        if line.startswith('#'): continue
        ll = line.strip().lower().split("\t")
        sort_start[ll[0]] = ll[1]
        sort_end[ll[1]] = ll[0]

line_num = 0
in_sort = False
sort_name = ''
sort_string = ''

with open(f1) as file:
    for line in file:
        line_num += 1
        do_more = True
        for x in sort_start.keys():
            if x in line:
                if in_sort:
                    print("BAILING: line", line_num, "has", x, "but already in sort area", x)
                in_sort = True
                sort_name = x
                if verbose: print("Starting", x, "line", line_num)
                fout.write(line)
                sort_string = ''
                do_more = False
                continue
        for x in sort_end.keys():
            if x in line:
                if sort_end[x] != sort_name:
                    print("Conflict:", x, start_of[x], "line", )
                    exit()
                do_one_sort(sort_string.strip(), fout)
                in_sort = False
                fout.write(line)
                do_more = False
                if verbose: print("stopped writing", line_num)
                continue
        if do_more:
            if in_sort:
                sort_string = sort_string + line
            else:
                fout.write(line)

fout.close()

if show_dif:
    if cmp(f1, f2):
        print(f1, "and", f2, "are identical. Not showing.")
    else:
        os.system("wm {:s} {:s}".format(f1, f2))
else:
    print("Not showing differences.")

s1 = os.stat(f1).st_size
s2 = os.stat(f2).st_size

if copy_over:
    if cmp(f1, f2):
        print("Sorting the rules changed nothing. Not copying.")
        os.remove(f2)
        exit()
    elif s1 != s2 and not force_copy:
        print("Sizes unequal. Use -f to copy over. Saved", f2, "for inspection.")
        print(f1, s1)
        print(f2, s2)
        exit()
    print("Changes found, copying back.")
    copy(f2, f1)
else:
    print("Use -c to copy over.")

os.remove(f2)