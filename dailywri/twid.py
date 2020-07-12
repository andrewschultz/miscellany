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

section_text = defaultdict(str)

regex_pattern = defaultdict(str)
from_file = defaultdict(str)
to_file = defaultdict(str)
priority = defaultdict(int)

from_temp = defaultdict(str)
to_temp = defaultdict(str)

my_twiddle_config = "c:/writing/scripts/twid.txt"
my_twiddle_dir = "c:/writing/twiddle"

from_and_to = []

def usage(arg = "general usage"):
    print(arg)
    print('=' * 100)
    print("-ps = print stats, -nps/psn = don't print stats")
    print("-sb/bs = secure backup to my_twiddle_dir/bak directory, (n) negates it")
    exit()

def get_twiddle_mappings():
    with open(my_twiddle_config) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            ary = line.strip().split(",")
            priority[ary[1]] = int(ary[0])
            from_file[ary[1]] = ary[2]
            to_file[ary[1]] = ary[3]
            regex_pattern[ary[1]] = ary[4]
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

def write_out_files(my_file):
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
                print("Writing section text for", ls, section_text[ls].count("\n"))
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
    for x in sorted(regex_pattern, key=lambda x: (-priority[x])):
        if re.search(regex_pattern[x], my_line, re.IGNORECASE):
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
    else:
        usage("Bad parameter " + arg)
    cmd_count += 1

get_twiddle_mappings()

for x in to_temp.values():
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
    write_out_files(x)
    print("TWIDDLY", twiddle_of(to_temp[x]), x)
    if print_stats:
        print("Orig:", os.stat(x).st_size, x)
        print("New:", os.stat(twiddle_of(to_temp[x])).st_size, twiddle_of(to_temp[x]))

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
