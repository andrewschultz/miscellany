import mytools as mt
import sys
import os
import re
from collections import defaultdict
from filecmp import cmp
from shutil import copy

copy_over = True
secure_backup = True

section_text = defaultdict(str)

regex_pattern = defaultdict(str)
from_file = defaultdict(str)
to_file = defaultdict(str)

from_temp = defaultdict(str)
to_temp = defaultdict(str)

my_twiddle_config = "c:/writing/scripts/twid.txt"
my_twiddle_dir = "c:/writing/twiddle"

from_and_to = []

def get_twiddle_mappings():
    with open(my_twiddle_config) as file:
        for (line_count, line) in enumerate (file, 1):
            ary = line.strip().split(",")
            from_file[ary[0]] = ary[1]
            to_file[ary[0]] = ary[2]
            regex_pattern[ary[0]] = ary[3]
    global from_and_to
    from_and_to = list(set(from_file.values()) | set(to_file.values()))
    for q in from_and_to:
        poss_temp = os.path.basename(q)
        dupe_index = 1
        while poss_temp in from_temp:
            poss_temp = "{}-{}".format(dupe_index, os.path.basename(q))
            dupe_index += 1
        to_temp[q] = poss_temp
        from_temp[poss_temp] = q

def twiddle_of(my_file):
    return os.path.join(my_twiddle_dir, os.path.basename(my_file))

def display_diffs(my_file):
    in_section = False
    current_section = ""
    twiddle_file = twiddle_of(to_temp[my_file])
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
                f.write(section_text[ls])
                continue
            if not current_section:
                f.write(line)
                continue
            # if we are in a section, we already wrote the section text, so continue
            continue
    f.close()
    mt.wm(my_file, twiddle_file)
    mt.compare_alphabetized_lines(my_file, twiddle_file)

def pattern_check(my_line):
    for x in sorted(regex_pattern, key=lambda x: (priority[x]))
        if re.search(regex_pattern[x], my_line):
            return x
    return ""

get_twiddle_mappings()

for x in from_file.values():
    with open(x) as file:
        current_section = ""
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("\\"):
                current_section = line.strip()
                if current_section not in section_text:
                    section_text[current_section] = ""
                continue
            temp = pattern_check(line)
            if temp:
                section_text[temp] += line
                continue
            if current_section:
                section_text[current_section] += line
                continue
            section_text['blank'] += line
            for q in regex_pattern:
                if re.search(regex_pattern[q], line):
                    section_text[q] += line
                    print(line, "matches with", q, "pattern", regex_pattern[q])

print("FROM AND TO:", from_and_to)

for x in from_and_to:
    print("TWIDDLY", twiddle_of(to_temp[x]), x)
    display_diffs(x)

if not copy_over:
    sys.exit("-co to copy over")

changed = unchanged = 0

for x in from_and_to:
    twid_from = twiddle_of(to_temp[x])
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
