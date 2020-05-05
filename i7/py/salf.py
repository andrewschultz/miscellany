# salf.py
#
# section alphabetizer (for inform files)
#
# separate from salf.pl which is the Alec Smart section alphabetizer
# confusing I know but it needs to be sorted
#
# need to also determine if a file is Windows or Unix line breaks, also determine if there is a difference, is it only due to line breaks?

from collections import defaultdict
from shutil import copy
import os
import sys
import i7
from filecmp import cmp
import mytools as mt
import re

copy_over = True
show_dif = False
force_copy = False
verbose = False
very_verbose = False

include_dict = defaultdict(list)
exclude_dict = defaultdict(list)
sort_start = defaultdict(lambda: defaultdict(int))
sort_end = defaultdict(lambda: defaultdict(int))
got_start_yet = defaultdict(bool)
got_end_yet = defaultdict(bool)
sort_prefix_second = defaultdict(lambda: defaultdict(bool))

alf_file = "c:/writing/scripts/salf.txt"

def rule_removal(x):
    if re.search("a [a-z0-9A-Z- ]+ rule *\(", x, re.IGNORECASE):
        x = re.sub("a [a-z0-9A-Z- ]+ rule *\(", "", x, 0, re.IGNORECASE)
        x = re.sub("\)", "", x, 1)
    return x.strip()

def usage(header="USAGE FOR SALF.PY"):
    print(header)
    print("=" * 50)
    print("-d = show differences if something goes wrong")
    print("-e = edit configs file {}".format(os.path.basename(alf_file)))
    print("-f = force copy-over on different sizes")
    print("-v = verbose")
    exit()

def longhand(proj,sh):
    if sh == 's': return i7.main_src(proj)
    temp = sh.split("-")
    if temp[0] == 'h': return i7.src_file(proj, temp[1])
    sys.exit("Undefined longhand for {:s}/{:s} project/shorthand.".format(proj, sh))

def firstline(q):
    return re.sub(":.*", "", q.partition('\n')[0].lower())

def do_one_sort(sort_string, fout, prefix_second = False):
    split_string = ""
    # not perfect below, but the basic idea is: if we only have one rule so far, don't shuffle the rule's lines themselves
    if "\n\n" in sort_string or "\t" in sort_string:
        if verbose: print("Double-cr sorting rules.")
        divs = sort_string.split("\n\n")
        split_string = "\n\n"
    else:
        if verbose: print("Single-cr sorting definitions.")
        split_string = "\n"
    if not split_string: sys.exit("Oops failed to get split_string.")
    divs = sort_string.split(split_string)
    divs = sorted(divs, key=lambda x: (re.sub(" [a-z\( ]+-", " ", rule_removal(firstline(x))), re.sub("-.*", "", rule_removal(firstline(x)))) if prefix_second else x.lower())
    ow = split_string.join(divs)
    fout.write("\n" + ow + "\n\n")
    return

def main_sect_alf(my_proj, my_file):
    if not my_file:
        print("WARNING no file to alphabetize. Maybe you put in the wrong section header.");
        return
    if not os.path.exists(my_file):
        print("WARNING could not get". my_file, "to run.");
        return
    my_bak = my_file + ".bak"
    fout = open(my_bak, "w", newline="\n")
    print("Alphabetizing sections in", my_file, "...")
    in_sort = False
    sort_name = ''
    sort_string = ''
    alf_next_chunk = False
    alf_next_blank = False
    sort_array = []
    prefix_second = False
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
                    prefix_second = x in sort_prefix_second[my_proj]
                    continue
            for x in sort_end[my_proj].keys():
                if x in line:
                    if not in_sort:
                        print("BAILING: line", line_count, "has", x, "but is not in any sorting area.")
                    do_one_sort(sort_string.strip(), fout, prefix_second)
                    in_sort = False
                    fout.write(line)
                    do_more = False
                    if verbose: print("stopped writing", line_count, x)
                    got_end_yet[x] = True
                    continue
            if alf_next_chunk:
                if line.startswith("["):
                    print("WARNING [postalf] does not need or want [xx/yy/whatever] to sort what is next at line {}.".format(line_count))
                sort_array = []
                if not alf_next_blank and line.strip():
                    alf_next_blank = True
                    alf_next_chunk = False
                    sort_array.append(line)
                    continue
            if alf_next_blank:
                if not line.strip():
                    if verbose: print("Sorting postalf at line", line_count)
                    for q in sort_array: fout.write(q)
                    alf_next_blank = False
                else:
                    sort_array.append(line)
                    continue
            if "[postalf]" in line:
                alf_next_chunk = True
                if verbose: print("Starting postalf at line", line_count)
            if do_more:
                ll = line.lower().strip()
                if re.search("\[(xx|zz)[0-9a-z]+\]", ll) and not ll.startswith("table of "):
                    print("WARNING: line {} has potential unrecognized start/end marker {}. Check salf.txt.".format(line_count, ll))
                if in_sort:
                    sort_string = sort_string + line
                else:
                    fout.write(line)
    fout.close()
    identical_ignoring_eol = mt.compare_unshuffled_lines(my_file, my_bak)
    if show_dif:
        if cmp(my_file, my_bak): print(my_file, "and", my_bak, "are identical. Not showing.")
        elif identical_ignoring_eol: print(my_file, "and", my_bak, "are identical except for line breaks. Not showing.")
        else: i7.wm(my_file, my_bak)
    elif not cmp(my_file, my_bak):
        if identical_ignoring_eol:
            print(my_file, "and", my_bak, "are identical except for line breaks. Not showing.")
        else:
            print("There are differences, but I am not showing them.")
    if copy_over:
        if cmp(my_file, my_bak) or identical_ignoring_eol:
            print("Sorting the rules changed nothing. Not copying {}.".format(os.path.basename(my_file)))
            os.remove(my_bak)
            return
        elif not force_copy and not mt.compare_shuffled_lines(my_file, my_bak):
            print("Content may have been altered between {} and {}. Saved {} for inspection.{}".format(os.path.basename(my_file), my_bak, my_bak, " for inspection.{:s}".format("" if show_dif else " -d shows differences.")))
            return
        print("Changes found, copying back {}.".format(os.path.basename(my_file)))
        copy(my_bak, my_file)
        print("-cn to avoid copying back.")
        os.remove(my_bak)
    else:
        print("Use -c to copy over.")
        print(my_bak, "kept for inspection.")

# start main

my_default_proj = i7.dir2proj()
story_file_only = False
cmd_defined_proj = ""

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'd': show_dif = True
    elif arg == 'f': force_copy = True
    elif arg == 'xv' or arg == 'vx': very_verbose = verbose = True
    elif arg == 'v': verbose = True
    elif arg == 'so': story_only = True
    elif arg == 'nc' or arg == 'cn': copy_over = False
    elif arg == 'all' or arg == 'a': story_only = False
    elif arg == 'e':
        os.system(alf_file)
        exit()
    elif arg == '?': usage()
    elif arg in i7.i7x:
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
        index_second = line.lower().startswith("i2:")
        if index_second: line = line[3:]
        ll = line.strip().lower().split("\t")
        if line.startswith("xz:"): # quick notation for xx(stuff) zz(stuff)
            marker_suffix = line[3:].strip()
            for u in marker_suffix.split(","):
                sort_start[current_project]['xx' + u] = -1
                sort_end[current_project]['zz' + u] = -1
                if index_second: sort_prefix_second[current_project]['xx' + u] = True
            continue
        if ll[0].lower().startswith("project="):
            temp = re.sub("^.*?=", "", ll[0])
            current_project = i7.proj_exp(temp)
            continue
        if ll[0].lower().startswith("include="):
            temp = re.sub("^.*?=", "", ll[0])
            include_dict[current_project] = [longhand(current_project, x) for x in temp.split(',')]
            continue
        if ll[0].lower().startswith("exclude="):
            temp = re.sub("^.*?=", "", ll[0])
            exclude_dict[current_project] = [longhand(current_project, x) for x in temp.split(',')]
            continue
        sort_start[current_project][ll[0]] = -1
        if index_second:
            sort_prefix_second[current_project][ll[0]] = True
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
    if cmd_defined_proj in include_dict:
        print("Going with include-dict of", ', '.join([os.path.basename(x) for x in include_dict[cmd_defined_proj]]), "for", cmd_defined_proj)
        my_files_ary = include_dict[cmd_defined_proj]
    elif cmd_defined_proj in exclude_dict:
        print("Going with exclude-dict of", ', '.join([os.path.basename(x) for x in exclude_dict[cmd_defined_proj]]), "for", cmd_defined_proj)
        my_files_ary = exclude_dict[cmd_defined_proj]
    else: my_files_ary = i7.i7f[cmd_defined_proj]
    for x in my_files_ary: main_sect_alf(cmd_defined_proj, x)
    un_start = [x for x in got_start_yet if got_start_yet[x] == False]
    if len(un_start): print("Start tokens missed:", ', '.join(un_start))
    un_end = [x for x in got_end_yet if got_end_yet[x] == False]
    if len(un_end): print("End tokens missed:", ', '.join(un_end))
