import mytools as mt
import sys
import os
import re
from collections import defaultdict
from filecmp import cmp
from shutil import copy

copy_over = True
secure_backup = True
print_stats = False
alphabetical_comparisons = True
overall_comparisons = True

track_line_delta = True

section_text = defaultdict(str)

regex_pattern = defaultdict(lambda:defaultdict(str))
from_file = defaultdict(lambda:defaultdict(str))
to_file = defaultdict(lambda:defaultdict(str))
priority = defaultdict(lambda:defaultdict(int))

from_temp = defaultdict(lambda:defaultdict(str))
to_temp = defaultdict(lambda:defaultdict(str))

before_lines = defaultdict(int)

my_twiddle_config = "c:/writing/scripts/twid.txt"
my_twiddle_dir = "c:/writing/twiddle"

from_and_to = []

my_project = "spo"

def usage(arg = "general usage"):
    print(arg)
    print('=' * 100)
    print("-ps = print stats, -nps/psn = don't print stats")
    print("-sb/bs = secure backup to my_twiddle_dir/bak directory, (n) negates it")
    print("-a/c/n combinations = alphabetical compare, winmerge compare toggles")
    exit()

def get_twiddle_mappings():
    current_project = ""
    with open(my_twiddle_config) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if line.startswith("project:"):
                current_project = re.sub("^.*?:", "", line.strip())
                continue
            if not current_project:
                sys.exit("Need current project defined.")
            ary = line.strip().split(",")
            priority[current_project][ary[1]] = int(ary[0])
            from_file[current_project][ary[1]] = ary[2]
            to_file[current_project][ary[1]] = ary[3]
            regex_pattern[current_project][ary[1]] = ary[4]
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
    if overall_comparisons:
        mt.wm(my_file, twiddle_file)
    if alphabetical_comparisons:
        mt.compare_alphabetized_lines(my_file, twiddle_file)

def pattern_check(my_line):
    for x in sorted(regex_pattern[my_project], key=lambda x: (-priority[my_project][x])):
        if re.search(regex_pattern[my_project][x], my_line, re.IGNORECASE):
            return x
    return ""

################################### main file

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'ps':
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
    elif arg == 'ld':
        track_line_delta = True
    elif arg == 'nld' or arg == 'ldn':
        track_line_delta = False
    else:
        usage("Bad parameter " + arg)
    cmd_count += 1

get_twiddle_mappings()

for x in to_temp[my_project]:
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
            if temp:
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

print("FROM AND TO:", from_and_to)

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
