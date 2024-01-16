#ialf.py
#
#a section sorter and reporter for daily/weekly file sections
#
#replaces perl alphabetizer for BTP/Alec Smart
#also organizes spoonerisms
#
# not really useful since
#   1. alphabetization is low priority
#   2. more important organizers out there

import i7
import sys
import re
import os
from collections import defaultdict

alphabetize = True
ignore_differences = False
copy_back = False
compare_it = True

show_sections_instead = False
default_proj = 'cw'
proj = ''

count = 1

def usage():
    print("-a = alphabetize sections, -an/-na = don't")
    print("-id = ignore differences, -cb = copy back, -nc = copy no compare")
    exit()

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'a': alphabetize = True
    elif arg == 'na' or arg == 'an': alphabetize = False
    elif arg == 'id': ignore_differences = True
    elif arg == 'cb': copy_back = True
    elif arg == 'nc':
        copy_back = True
        compare_it = False
    elif arg == '?': usage()
    elif arg == 's': show_sections_instead = True
    elif arg == 'p':
        count += 1
        proj = sys.argv[count].lower()
    else:
        print("Bad argument", arg)
        usage()
    count += 1

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def alec_smart_org(a, cs):
    if a.startswith("AUTH") or a.startswith("AUT") or a.startswith("AUTHOR"): return "btp-auth"
    if a.startswith("FEM"): return "btp-fem"
    if a.startswith("FARM"): return "btp-farm"
    return cs

def spoonerism_org(a, cs):
    b = re.search("=([1-9])", a)
    if b: return 'sp' + b.group(1)
    b = re.search("([1-9])=", a)
    if b: return 'sp' + b.group(1)
    b = re.search("([1-9])$", a)
    if b: return 'sp' + b.group(1)
    if '**'in a: return "spopro"
    if '*'in a: return "sw"
    return cs

def comment_and_alf_sort_by_mult(a):
    is_comment = a.startswith('#')
    b = re.sub("^#*", "", a).lower()
    b = re.sub("^ +", "", b)
    c = sorted(b.split(" *(\*|[0-9]*=[0-9]*) *"))
    return(is_comment, c[0])

def comment_and_alf_sort(a):
    is_comment = a.startswith('#')
    b = re.sub("^#*", "", a).lower()
    b = re.sub("^ +", "", b)
    return(is_comment, b)

def alfit(mystr):
    if not mystr.strip(): return ""
    return "\n".join(sorted(mystr.strip().split("\n"), key=comment_and_alf_sort)) + "\n"

def ailihphilia_sort(a):
    b = re.sub("^[^0-9]*", "", a)
    b = re.sub("[^0-9].*", "", b)
    return b

def run_sample_sort(a):
    my_ary = [ 'a', 'b', '#a', '#b', 'c', '#c' ]
    print(my_ary)
    print(sorted(my_ary, key=comment_and_alf_sort))

def show_sections(a):
    count = 0
    with open(a) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("\\"):
                l2 = re.sub("=.*", "", line[1:].strip())
                la = l2.split("|")
                for ll in la:
                    if ll in main_sect.keys(): sys.exit("{:s} defined twice. Bail at line {:d}.".format(ll, line_count))
                    main_sect[ll] = line.strip()
                section_rollup[line.strip()] = ""
                print("Adding blank", line)
                order_dict[line.strip()] = line_count

def process_sections(a, loc_func, show_sections_instead):
    if show_sections_instead:
        show_sections(a)
        return
    tf = "c:/writing/temp-ialf.txt"
    f = open(tf, "w")
    backslash_yet = False
    current_section = ""
    print("Main section keys:", main_sect.keys())
    with open(a) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("\\"):
                current_section = re.sub("=.*", "", line[1:].strip())
                current_section_full[current_section] = line.strip()
                backslash_yet = True
                print("Start at line", line_count, current_section, line.strip())
                continue
            if not backslash_yet:
                f.write(line)
                continue
            if not line.strip(): continue
            asort = loc_func(line, current_section)
            if asort not in main_sect.keys():
                print(line_count, line.strip(), "!", asort, "! not in main section keys")
                print(sorted(main_sect.keys()))
                exit()
            section_rollup[main_sect[asort]] += line
    for x in sorted(section_rollup.keys(), key=order_dict.get):
        print("Writing out", x)
        f.write(x + '\n')
        if alphabetize: f.write(alfit(section_rollup[x]))
        else: f.write(section_rollup[x])
        f.write("\n")
    f.close()
    print(os.path.getsize(a), os.path.getsize(tf))
    print(file_len(a), file_len(tf))
    if compare_it: os.system("wm {:s} {:s}".format(a, tf))
    if file_len(a) != file_len(tf) and not ignore_differences:
        sys.exit("File size differences. Bailing. Use -id to override.")
    if copy_back: copy(tf, a)
    exit()

def sample_section_sorts():
    print(spoonerism_org("abc =2 def"))
    print(spoonerism_org("abc = def 2"))
    print(spoonerism_org("abc = def"))
    exit()

main_sect = defaultdict(str)
order_dict = defaultdict(int)
section_rollup = defaultdict(str)
current_section_full = defaultdict(str)

#see about dictionary of functions?

if not proj:
    proj = default_proj
    mt.warn("No user project defined. Going with {}.".format(default_proj))

if proj == 'btp' or proj == 'as' or proj == 'ss':
    process_sections(i7.smart, alec_smart_org, show_sections_instead)
elif proj == 'cw' or proj == 'ws':
    process_sections(i7.spoon, spoonerism_org, show_sections_instead)
else:
    sys.exit("Undefined project " + proj)

#show_sections(i7.smart)
#show_sections(i7.spoon)

exit()