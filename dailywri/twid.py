#
# twid.py
#
# twiddles sections internal to a file
#

import mytools as mt
import sys
import os
import re
from collections import defaultdict
from filecmp import cmp
from shutil import copy

#####################start options

max_changes_per_file = 0

copy_over = False
secure_backup = True
print_stats = False
alphabetical_comparisons = True
overall_comparisons = True

track_line_delta = True

#####################end options

section_text = defaultdict(str)

regex_pattern = defaultdict(lambda:defaultdict(str))
from_file = defaultdict(lambda:defaultdict(str))
to_file = defaultdict(lambda:defaultdict(str))
priority = defaultdict(lambda:defaultdict(int))

from_temp = defaultdict(lambda:defaultdict(str))
to_temp = defaultdict(lambda:defaultdict(str))

read_locked = defaultdict(lambda:defaultdict(int))
write_locked = defaultdict(lambda:defaultdict(int))

before_lines = defaultdict(int)

my_twiddle_config = "c:/writing/scripts/twid.txt"
my_twiddle_dir = "c:/writing/twiddle"

from_and_to = []

my_default_project = ''
my_project = ''

def usage(arg = "general usage"):
    print(arg)
    print('=' * 100)
    print("-ps = print stats, -nps/psn = don't print stats")
    print("-sb/bs = secure backup to my_twiddle_dir/bak directory, (n) negates it")
    print("-a/c/n combinations = alphabetical compare, winmerge compare toggles")
    print("-e = edit config file")
    print("-ld = track line delta, nld/ldn = don't")
    print("Specify project with p= or p:. Default is", my_default_project)
    exit()

def get_twiddle_mappings():
    current_project = ""
    global my_default_project
    with open(my_twiddle_config) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if not line.strip(): continue
            (prefix, data) = mt.cfg_data_split(line.strip())
            prefix = prefix.lower()
            if prefix == "copyover":
                copy_over = mt.truth_state_of(data)
                if copy_over == -1:
                    sys.exit("Bad copyover value at line {}.".format(line_count))
                continue
            elif prefix == 'default':
                if my_default_project:
                    sys.exit("Redefinition of default project at line {}.".format(line_count))
                my_default_project = re.sub("^.*?:", "", line.strip())
                continue
            elif prefix == 'project':
                current_project = re.sub("^.*?:", "", line.strip())
                continue
            if not current_project:
                sys.exit("Need current project defined at line {}.".format(line_count))
            ary = line.strip().split(",")
            priority[current_project][ary[1]] = int(ary[0])
            from_file[current_project][ary[1]] = ary[2]
            to_file[current_project][ary[1]] = ary[3]
            regex_pattern[current_project][ary[1]] = ary[4]
            if len(ary) > 5:
                write_status = ary[5].lower()
                if write_status == 'readonly' or write_status == 'locked':
                    write_locked[current_project][ary[1]] = True
                elif write_status == 'writeonly' or write_status == 'locked':
                    read_locked[current_project][ary[1]] = True
                else:
                    print("INVALID cfg entry 5 read/write at line {}.".format(line_count))
    global from_and_to
    for proj in priority:
        from_and_to = list(set(from_file[proj].values()) | set(to_file[proj].values()))
        for q in from_and_to:
            poss_temp = os.path.basename(q)
            dupe_index = 1
            while poss_temp in from_temp[proj]:
                poss_temp = "{}-{}".format(dupe_index, os.path.basename(q))
                dupe_index += 1
            to_temp[proj][q] = poss_temp
            from_temp[proj][poss_temp] = q

def twiddle_of(my_file):
    return os.path.join(my_twiddle_dir, os.path.basename(my_file))

def write_out_files(my_file):
    in_section = False
    current_section = ""
    twiddle_file = twiddle_of(to_temp[my_project][my_file])
    f = open(twiddle_file, "w")
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("\\"):
                ls = line.strip()
                if ls not in section_text:
                    sys.exit("Uh oh, section", ls, "vanished.")
                else:
                    pass
                    # print("Processing", ls, "section")
                current_section = ls
                f.write(line)
                if track_line_delta:
                    if before_lines[ls] == section_text[ls].count("\n"):
                        pass
                    else:
                        print("Section text for", ls, "previously", before_lines[ls], "increased" if before_lines[ls] < section_text[ls].count("\n") else "decreased", "to", section_text[ls].count("\n"))
                f.write(section_text[ls])
                continue
            if not current_section:
                f.write(line)
                continue
            # if we are in a section, we already wrote the section text, so continue
            continue
    f.close()
    if cmp(my_file, twiddle_file):
        return
    if alphabetical_comparisons:
        mt.compare_alphabetized_lines(my_file, twiddle_file)
    if overall_comparisons:
        mt.wm(my_file, twiddle_file)

def pattern_check(my_line):
    for x in sorted(regex_pattern[my_project], key=lambda x: (-priority[my_project][x])):
        if re.search(regex_pattern[my_project][x], my_line, re.IGNORECASE):
            return x
    return ""

################################### main file

get_twiddle_mappings()

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'e':
        mt.npo(my_twiddle_config)
    elif arg == 'ps':
        print_stats = True
    elif arg == 'nps' or arg == 'psn':
        print_stats = False
    elif arg == 'nbs' or arg == 'bsn' or arg == 'nsb' or arg == 'sbn':
        secure_backup = False
    elif arg == 'bs' or arg == 'sb':
        secure_backup = True
    elif arg == 'an' or arg == 'na':
        alphabetical_comparisons = False
    elif arg == 'cn' or arg == 'nc':
        overall_comparisons = False
    elif arg == 'a':
        alphabetical_comparisons = True
    elif arg == 'c':
        overall_comparisons = True
    elif arg == 'co':
        copy_over = True
    elif arg == 'nc':
        copy_over = False
    elif arg == 'ld':
        track_line_delta = True
    elif arg == 'nld' or arg == 'ldn':
        track_line_delta = False
    elif arg[:2] == 'p=' or arg[:2] == 'p:':
        my_project = arg[2:]
    elif arg[:2] == 'mf' or arg[:2] == 'fm':
        if arg[2:].isdigit():
            max_changes_per_file = int(arg[2:])
        else:
            print("You need a number after fm/mf. {} doesn't work".format(arg[2:] if arg[2:] else 'A blank value'))
    elif arg == '?':
        usage()
    else:
        usage("Bad parameter " + arg)
    cmd_count += 1

if not my_project:
    if my_default_project:
        print("Going with default project", my_default_project)
        my_project = my_default_project
    else:
        sys.exit("There is no default project in the config file. You need to specify one on the command line.")

if my_project not in to_temp:
    sys.exit("FATAL ERROR {} not in list of projects: {}".format(my_project, ', '.join(to_temp)))

for x in to_temp[my_project]:
    max_file_reached = False
    cur_file_changes = 0
    with open(x) as file:
        current_section = ""
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("\\"):
                current_section = line.strip()
                if current_section not in section_text:
                    section_text[current_section] = ""
                continue
            temp = pattern_check(line)
            if current_section:
                before_lines[current_section] += 1
            if temp and not read_locked[my_project][current_section] and not write_locked[my_project][temp] and not max_file_reached:
                if max_changes_per_file and cur_file_changes == max_changes_per_file and temp != current_section:
                    print("You went over the maximum # of changes for", x)
                    max_file_reached = True
                else:
                    if temp != current_section:
                        cur_file_changes += 1
                    section_text[temp] += line
                    continue
            if current_section:
                section_text[current_section] += line
                continue
            section_text['blank'] += line
            for q in regex_pattern[my_project]:
                if re.search(regex_pattern[my_project][q], line):
                    section_text[q] += line
                    print(line, "matches with", q, "pattern", regex_pattern[my_project][q])
    print("Total changes in {}: {}".format(x, cur_file_changes))

for x in from_and_to:
    write_out_files(x)
    print("TWIDDLY", twiddle_of(to_temp[my_project][x]), x)
    if print_stats:
        print("Orig:", os.stat(x).st_size, x)
        print("New:", os.stat(twiddle_of(to_temp[my_project][x])).st_size, twiddle_of(to_temp[my_project][x]))

if not copy_over:
    sys.exit("-co to copy over")

changed = unchanged = 0

for x in from_and_to:
    twid_from = twiddle_of(to_temp[my_project][x])
    if cmp(x, twid_from):
        print("Skipping", x, twid_from, "no changes.")
        unchanged += 1
        continue
    if secure_backup:
        print("Backing up", x, twid_from)
        copy(x, os.path.join(my_twiddle_dir, "bak", os.path.basename(x)))
    print("Copying", twid_from, x)
    copy(twid_from, x)
    changed += 1

print(changed, "changed", unchanged, "unchanged")
