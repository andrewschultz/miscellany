#
# dsort.py
# python extension of former perl dsort updater
#

import sys
import re
import os
from collections import defaultdict

file_name = defaultdict(str)
file_comment = defaultdict(lambda:defaultdict(str))
cfg_line = defaultdict(lambda:defaultdict(str))
modified_files = defaultdict(bool)
done_with = defaultdict(bool)
or_dict = defaultdict(str)
text_out = defaultdict(str)

need_tabs = defaultdict(bool)

default_section_name = "not"

#def sort_backslash_sections()
daily_dir = "c:/writing/daily"
done_dir = "c:/writing/daily/done"
temp_dir = "c:/writing/temp"
backup_dir = "c:/writing/backup"
idea_hash = "c:/writing/idea-tab.txt"
to_temp_only = True

print_warnings = False
stderr_warnings = False
to_temp_only = True
return_after_first_bug = False

def usage():
    print("U = upper bound")
    print("L = lower bound")
    print("B/D = days back")
    print("? = this")
    exit()

def to_backups():
    for q in file_name.keys(): copy(q, to_temp(q, backup_dir))

def to_section(x):
    x = re.sub("^\\\\", "", x)
    if x in file_name.keys(): return x
    if x in or_dict.keys(): return or_dict[x]
    return ""

def warn_print(x):
    if print_warnings:
        print(x)
    elif stderr_warnings:
        stderr.write(x)

def read_hash_file():
    stuff = defaultdict(bool)
    file_list = []
    with open(idea_hash) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if line.startswith("FILES:"):
                lp = re.sub("^[a-z]*?:", "", line.lower().strip())
                file_list = lp.split(",")
                continue
            if line.startswith("NEEDTABS:"):
                lp = re.sub("^[a-z]*?:", "", line.lower().strip())
                for q in lp.split(","):
                    need_tabs[q] = True
                continue
            if line.count("\t") >= 1:
                l0 = line.lower().strip().split("\t")
                stuff[l0[1]] = True
                if l0[0] in file_name.keys() or l0[0] in file_comment.keys():
                    print(line_count, line)
                    sys.exit("{:s} is already defined in {:s}, but you are trying to redefine it in file {:s}.".format(l0[0], file_name[l0[0]], l0[1]))
                ors = l0[0].split("|")
                for q in ors:
                    if q in or_dict.keys():
                        sys.exit("Duplicate or-ish definition of {:s} at line {:d}: {:s} overlaps {:s} from line {:d}.".format(q, line_count, l0[0], or_dict[q], cfg_line[or_dict[q]]))
                    or_dict[q] = l0[0]
                file_name[l0[0]] = l0[1]
                file_comment[l0[0]] = "none" if len(l0) < 3 else l0[2]
                cfg_line[l0[0]] = line_count
    if not len(file_list):
        print("Couldn't find a FILES: in {:s}.".format(idea_hash))
        print("SUGGESTION:")
        sys.exit("FILES:{:s}".format(','.join(sorted(stuff.keys()))))

def compare_hash_with_files():
    with open(idea_hash) as file:
        for (line_count, line) in file:
            hash_file_val[l0] = line_count

def to_temp(x, backup_dir = temp_dir):
    return os.path.join(backup_dir, os.path.basename(x))

def get_stuff_from_one_file(x):
    print("Getting stuff from", x)
    loc_text_out = defaultdict(str)
    section_name = default_section_name
    last_bad_start = 0
    with open(x) as file:
        for (line_count, line) in enumerate(file, 1):
            ll = line.strip()
            if not ll:
                if section_name:
                    section_name = ""
                    continue
                warn_print("Double line break at {:d} of {:s}.".format(line_count, x))
                continue
            if not section_name:
                if not ll.startswith("\\"):
                    if line_count - last_bad_start > 1:
                        print("Bad starting line", line_count, "file", x,":", ll)
                    last_bad_start = line_count
                    found_error = True
                    if return_after_first_bug: return
                else:
                    section_name = to_section(ll)
                    # print(line_count, section_name, ll, sep="-/-")
            loc_text_out[section_name] += line
    for y in loc_text_out.keys():
        modified_files[file_name[y]] = True
        if y in need_tabs.keys(): loc_text_out[y] = "\t" + loc_text_out[x]
        text_out[y] += loc_text_out[y]
    done_with[x] = True
    print("Got stuff from", x)

lower_bound = "20170101.txt"
days_back = 0
upper_bound = "20190101.txt"
count = 1

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg.startswith("-"): arg = arg[1:]
    if arg.startswith('u'):
        upper_bound = arg[1:]
    if len(upper_bound) < 8: upper_bound += '9' * (8 - len(upper_bound))
    elif arg.startswith('l'): lower_bound = arg[1:]
    elif arg.startswith('b') or arg.startswith("d"):
        if not arg[1:].isdigit(): sys.exit("-b/d needs digits after for days back.")
        days_back = int(arg[1:])
    else:
        print("Invalid command/flag", arg[0], arg)
    usage()
    count += 1

if days_back:
    print("Days back overrides")
    upper_bound = go_back(0)
    lower_bound = go_back(days_back)

if lower_bound > upper_bound: sys.exit("Lower bound > upper bound")

os.chdir(daily_dir)
readdir = [x for x in os.listdir(daily_dir) if os.path.isfile(x)]

read_hash_file()

for file in readdir:
    if not re.search("^20[0-9]{6}\.txt$", file.lower()): continue
    fb = file[:8] # strip the .txt ending
    if fb < lower_bound: print("Skipping", fb, "too low")
    if fb > upper_bound: print("Skipping", fb, "too high")
    get_stuff_from_one_file(file)

exit()

if copy_over: # maybe we should put this into a function
    last_backslash = 0
    for x in modified_files:
        f = to_temp(x)
        with open(x) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("\\"):
                    if cur_out: sys.exit("Ruh roh two backslashes in one section {:d} {:d} in file {:s}.".format(line_count, last_backslash, x))
                    cur_out = re.sub("=.*", "", line[1:].strip())
                    last_backslash = line_count
                    f.write(line)
                    continue
                if cur_out and not line.strip() and cur_out in text_out.keys():
                    f.write(text_out[cur_out])
                    print("Added {:d} lines to section {:s} in file {:s}.".format(text_out[cur_out].count("\n"), cur_out, x))
    if not to_temp_only:
        for x in changed_files.keys():
            the_temp = to_temp(x)
            copy(the_temp, x)
            os.remove(the_temp)
    for j in done_with.keys():
            os.move(j, to_temp(j))

