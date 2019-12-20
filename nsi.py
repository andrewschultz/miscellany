# nsi.py: notes sort internal

import i7
from collections import defaultdict
from shutil import copy
import os
import re
import sys
import mytools as mt

my_regexes = defaultdict(str)
my_sect = defaultdict(str)
sect_text = defaultdict(str)
indices = defaultdict(int)
ideas = defaultdict(int)

unalphabetized_check = False
alphabetized_check = False
open_after = False
copy_back = False
keep_prev = False

my_proj = 'pl'

def usage(bad_cmd = ""):
    if bad_cmd: print("=" * 30, bad_cmd, "=" * 30)
    print("a for alphabetized listing, o for open after, ao/oa for both, or n for neither.")
    print("c copies the sorted file back over and does not preserve a backup of the original. ck/kc copies and keeps a backup.")
    exit()

def this_sect(line):
    for q in my_regexes:
        if re.search(my_regexes[q], line):
            return q
    return "unsorted"

def print_sect(x):
    print(x, "goes to", this_sect(x))

def do_tests():
    print_sect("rowdy owdy ray")
    print_sect("rowdy owdy feyy")
    print_sect("rowdy owdy fayy")
    print_sect("rowdy owdy fey f")
    print_sect("rowdy owdy fay f")
    sys.exit()

def write_sorted_stuff():
    global of
    of.write("\n")
    print(len(sect_text), "sections used:", ', '.join(["{} ({})".format(x, ideas[x]) for x in sorted(sect_text, key=ideas.get, reverse = True)]))
    for idx in sorted(sect_text, key=indices.get):
        of.write("#sect: {}\n{}\n".format(idx, sect_text[idx]))
    # print sections

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'a':
        alphabetized_check = True
        open_after = False
    elif arg == 'o':
        alphabetized_check = True
        open_after = False
    elif arg == 'ao' or arg == 'oa':
        alphabetized_check = open_after = True
    elif arg == 'u':
        unalphabetized_check = True
        open_after = False
    elif arg == 'uo' or arg == 'ou':
        unalphabetized_check = open_after = True
    elif arg == 'n':
        alphabetized_check = open_after = False
    elif arg == 'c':
        copy_back = True
        keep_prev = False
    elif arg == 'ck' or arg == 'kc':
        copy_back = keep_prev = True
    else:
        usage()
    cmd_count += 1

i7.go_proj(my_proj)
in_file = "notes.txt"
out_file = "notes-sort.txt"
data_file = "nsi.txt"

in_before = True
in_after = False
current_comments = ""
cur_idx = 0

with open(data_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith(";"): break
        if line.startswith("#"): continue
        if line.startswith("~"):
            print("simple word boundary regex at line {}.".format(line_count))
            ary = line[1:].strip().split(",")
            for x in ary:
                y = x.replace("|", " or ")
                if y in my_regexes:
                    print("WARNING ignoring redefinition of {} at line {}.".format(y, line_count))
                    continue
                my_regexes[y] = "\\b{}\\b".format(x.lower())
                cur_idx += 1
                indices[y] = cur_idx
                #print("Abbrev-add", x, my_regexes[x])
            continue
        if not "\t" in line:
            print("WARNING line {} needs tab delimiter: {}.".format(line_count, line.strip()))
        if line.count("\t") > 1:
            print("WARNING line {} can only have one tab delimiter for now: {}.".format(line_count, line.strip()))
        ary = line.strip().lower().split("\t")
        if ary[0] in my_regexes:
            print("WARNING ignoring redefinition of {} at line {}.".format(ary[0], line_count))
            continue
        my_regexes[ary[0]] = ary[1]
        cur_idx += 1
        indices[ary[0]] = cur_idx

cur_idx += 1
indices["unsorted"] = cur_idx

#do_tests()

of = open(out_file, "w")

with open(in_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if in_before or in_after:
            of.write(line)
        if "==begin;" in line:
            if not in_before: sys.exit("Two ==begin; lines, bailing.")
            in_before = False
            continue
        if "==end;" in line:
            if in_before: sys.exit("==end; before ==begin, bailing.")
            if in_after: sys.exit("Two ==end; , bailing.")
            write_sorted_stuff()
            of.write(line)
            in_after = True
        if in_before or in_after: continue
        if line.startswith("#"):
            if not line.startswith("#sect=") and not line.startswith("#sect:"):
                current_comments += line
            continue
        if not line.strip(): continue
        my_sect = this_sect(line.lower())
        sect_text[my_sect] += current_comments + line
        current_comments = ""
        ideas[my_sect] += 1
        continue

of.close()

if unalphabetized_check:
    mt.wm(in_file, out_file)

if alphabetized_check:
    mt.alfcomp(in_file, out_file)

if copy_back:
    if mt.compare_unshuffled_lines(in_file, out_file):
        print("Nothing changed. No copying.")
        os.remove(out_file)
        exit()
    if keep_prev:
        copy(in_file, emergency_file)
    copy(out_file, in_file)
    os.remove(out_file)
else:
    print("-c to copy back.")

if open_after:
    if os.exists(out_file):
        os.system(out_file)
    else:
        os.system(in_file)