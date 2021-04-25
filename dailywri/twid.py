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

#####################start classes

class twiddle_project:
    def __init__(self, name): #alphabetical, except when similar are lumped together
        # this covers the regex/text patterns that direct us to certain sections
        self.match_pattern = defaultdict(tuple)

        # these two cover all the files that may be edited under a specific project.
        self.from_file = defaultdict(str)
        self.to_file = defaultdict(str)

        # these two define the tempfiles we write to. Most of the times tempfile = basename(x) unless there is more than one with the same basename.
        self.from_temp = defaultdict(str)
        self.to_temp = defaultdict(str)

        self.movefrom_locked = defaultdict(str) # don't move anything from this section
        self.moveto_locked = defaultdict(str) # don't move anything to this section

        self.flag_text_chunks = []
        self.flag_regexes = []

        self.shuffle_end = ''

#####################end classes

NO_CHANGES = 0
CHANGED = 1

REGEX = 0
TEXT = 1

TO_LOCKED_FLAG = 1
FROM_LOCKED_FLAG = 2

#####################start options

max_changes_overall = 0
max_changes_per_file = 0
max_text_tweaks = 0

postopen_to_fix = True

copy_over = False
force_copy = False
secure_backup = True
print_stats = False
alphabetical_comparisons = True
overall_comparisons = True

track_line_delta = True

check_sectioning = False

to_wildcard = ''
from_wildcard = ''

#####################end options

my_twiddle_projects = defaultdict(twiddle_project)

section_text = defaultdict(str)
post_text = defaultdict(str)
before_lines = defaultdict(int)

my_twiddle_config = "c:/writing/scripts/twid.txt"
my_twiddle_dir = "c:/writing/twiddle"

force_locks = []

from_and_to = []

my_default_project = ''
my_project = ''

def usage(arg = "general usage"):
    print(arg)
    print('=' * 100)
    print("-ps = print stats, -nps/psn = don't print stats")
    print("-sb/bs = secure backup to my_twiddle_dir/bak directory, (n) negates it")
    print("-a/c/n combinations = alphabetical compare, winmerge compare toggles")
    print("-co = copy over, -fc = force copy even with corrupted information")
    print("-e = edit config file")
    print("-ld = track line delta, nld/ldn = don't, -cs = check sections")
    print("mf/fm/mo/om = max shifts per file or overall, mt/tm = maximum tweaks")
    print("to: = copy to a certain wildcard")
    print("fr: = copy from a certain wildcard")
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
                if current_project in my_twiddle_projects:
                    print("WARNING duplicate current project marker for {} at line {}.".format(current_project, line_count))
                else:
                    my_twiddle_projects[current_project] = twiddle_project(current_project)
                cur_twiddle = my_twiddle_projects[current_project]
                continue
            elif prefix == 'regex':
                cur_twiddle.flag_regexes.append(data)
                continue
            elif prefix == 'shufend':
                cur_twiddle.shuffle_end = (data)
                continue
            elif prefix == 'text':
                cur_twiddle.flag_text_chunks.append(data)
                continue
            if not current_project:
                sys.exit("Need current project defined at line {}.".format(line_count))
            ary = line.strip().split(",")
            if len(ary) <= 3:
                print("WARNING CSV file needs priority, from and to at line {}.".format(line_count))
                continue
            try:
                local_priority = int(ary[0])
            except:
                print("Need integer value of prioirity for {} at line {}. Defaulting to zero.".format(ary[1], line_count))
                local_priority = 0
            cur_twiddle.from_file[ary[1]] = ary[2]
            if ary[3] == '.':
                cur_twiddle.to_file[ary[1]] = ary[2]
            else:
                cur_twiddle.to_file[ary[1]] = ary[3]
            cur_twiddle.movefrom_locked[ary[1]] = cur_twiddle.moveto_locked[ary[1]] = False
            for x in range(4, len(ary)):
                write_status = ary[x].lower()
                if write_status == 'fromonly' or write_status == 'blockto' or write_status == 'toblock':
                    cur_twiddle.moveto_locked[ary[1]] = True
                    continue
                elif write_status == 'toonly' or write_status == 'blockfrom' or write_status == 'fromblock':
                    cur_twiddle.movefrom_locked[ary[1]] = True
                    continue
                elif write_status == 'locked':
                    cur_twiddle.movefrom_locked[ary[1]] = cur_twiddle.moveto_locked[ary[1]] = True
                    continue
                if write_status.startswith("txt:"):
                    cur_twiddle.match_pattern[ary[x][4:]] = (local_priority, TEXT, ary[1])
                else:
                    cur_twiddle.match_pattern[ary[x]] = (local_priority, REGEX, ary[1])

    global from_and_to
    for proj in my_twiddle_projects:
        from_and_to = list(set(my_twiddle_projects[proj].from_file.values()) | set(my_twiddle_projects[proj].to_file.values()))
        for q in from_and_to:
            poss_temp = os.path.basename(q)
            dupe_index = 1
            while poss_temp in my_twiddle_projects[proj].from_temp:
                poss_temp = "{}-{}".format(dupe_index, os.path.basename(q))
                dupe_index += 1
            my_twiddle_projects[proj].to_temp[q] = poss_temp
            my_twiddle_projects[proj].from_temp[poss_temp] = q

def twiddle_of(my_file):
    return os.path.join(my_twiddle_dir, os.path.basename(my_file))

def write_out_files(my_file):
    in_section = False
    current_section = ""
    twiddle_file = twiddle_of(my_twiddle_projects[my_project].to_temp[my_file])
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
                f.write(section_text[ls] + "\n")
                if ls in post_text:
                    f.write(post_text[ls])
                continue
            if not current_section:
                f.write(line)
                continue
            # if we are in a section, we already wrote the section text, so continue
            continue
    f.close()
    if cmp(my_file, twiddle_file): # just bail if nothing happened
        return NO_CHANGES
    if alphabetical_comparisons:
        mt.compare_alphabetized_lines(my_file, twiddle_file)
    if overall_comparisons:
        mt.wm(my_file, twiddle_file)
    return CHANGED

def pattern_check(my_line):
    for x in sorted(this_twiddle.match_pattern, key=lambda x: (-this_twiddle.match_pattern[x][0])):
        if this_twiddle.moveto_locked[this_twiddle.match_pattern[x][2]]:
            continue
        this_match = this_twiddle.match_pattern[x]
        if this_match[1] == REGEX:
            if re.search(x, my_line, re.IGNORECASE):
                return this_match[2]
        elif this_match[1] == TEXT:
            if x.lower() in my_line.lower:
                return this_match[2]
    return ""

def copy_back_from_temp(this_twiddle, from_and_to):
    changed = unchanged = 0

    for x in from_and_to:
        twid_from = twiddle_of(this_twiddle.to_temp[x])
        if cmp(x, twid_from):
            print("Skipping", x, twid_from, "no changes.")
            unchanged += 1
            continue
        if secure_backup:
            print("Backing up", x, twid_from)
            copy(x, os.path.join(my_twiddle_dir, "bak", os.path.basename(x)))
        temp = mt.alfcomp(x, twid_from, show_winmerge = False, acknowledge_comparison = False)
        print("{} and {} {}have identical information.".format(x, twid_from, '' if temp else 'do not '))

        if not temp:
            if force_copy:
                print("Force-copying {} back over {} despite significant information change.".format(twid_from, x))
            else:
                print("Not copying back over due to possible meaningful data loss. Use -fc to force-copy.")
                continue
        else:
            print("Copying", twid_from, x)

        copy(twid_from, x)
        changed += 1

    print(changed, "changed", unchanged, "unchanged")

def force_lock_wildcard(string_to_process):
    string_chunk = string_to_process[3:]
    flag_char = string_to_process[1]
    if flag_char == 'l':
        flags = TO_LOCKED_FLAG | FROM_LOCKED_FLAG
    elif flag_char == 'o':
        flags = 0
    elif flag_char == 'f':
        flags = FROM_LOCKED_FLAG
    elif flag_char == 't':
        flags = TO_LOCKED_FLAG
    else:
        print("Unrecognized flag char in", string_to_process, "so ignoring.")
        return

    for l in my_twiddle_projects[my_project].moveto_locked:
        if string_chunk in l:
            print("Switching", l, flags)
            my_twiddle_projects[my_project].moveto_locked[l] = flags & TO_LOCKED_FLAG
            my_twiddle_projects[my_project].movefrom_locked[l] = flags & FROM_LOCKED_FLAG

################################### main file

get_twiddle_mappings()

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    argraw = sys.argv[cmd_count]
    if argraw in my_twiddle_projects:
        if my_project:
            print("Warning: redefining my project from {} to {}.".format(my_project, argraw))
        my_project = argraw
        cmd_count += 1
        continue
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
    elif arg == 'po' or arg == 'op':
        postopen_to_fix = True
    elif arg == 'pn' or arg == 'np':
        postopen_to_fix = False
    elif arg == 'a':
        alphabetical_comparisons = True
    elif arg == 'ca':
        overall_comparisons = True
        copy_over = True
        alphabetical_comparisons = True
    elif arg == 'co':
        copy_over = True
        alphabetical_comparisons = False
        overall_comparisons = False
    elif arg == 'cd':
        copy_over = True
        alphabetical_comparisons = True
    elif arg == 'fc':
        force_copy = False
    elif arg == 'cs':
        check_sectioning = True
    elif arg[:3] == 'fl:' or arg[:3] == 'fo:' or arg[:3] == 'ff:' or arg[:3] == 'ft:':
        force_locks.append(arg)
    elif arg == 'nc':
        copy_over = False
    elif arg == 'ld':
        track_line_delta = True
    elif arg == 'nld' or arg == 'ldn':
        track_line_delta = False
    elif arg[:2] == 'p=' or arg[:2] == 'p:':
        my_project = arg[2:]
    elif arg[:2] == 'mt' or arg[:2] == 'tm':
        if arg[2:].isdigit():
            max_text_tweaks = int(arg[2:])
    elif arg[:2] == 'mf' or arg[:2] == 'fm':
        if arg[2:].isdigit():
            max_changes_per_file = int(arg[2:])
        else:
            print("You need a number after fm/mf. {} doesn't work".format(arg[2:] if arg[2:] else 'A blank value'))
    elif arg[:2] == 'mo' or arg[:2] == 'om':
        if arg[2:].isdigit():
            max_changes_overall = int(arg[2:])
        else:
            print("You need a number after om/mo. {} doesn't work".format(arg[2:] if arg[2:] else 'A blank value'))
    elif arg[:3] == 'to:':
        to_wildcard = arg[3:]
        if not to_wildcard:
            sys.exit("Need something after to:")
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

if my_project not in my_twiddle_projects:
    sys.exit("FATAL ERROR {} not in list of projects: {}".format(my_project, ', '.join(my_twiddle_projects)))

max_overall_reached = False
overall_changes = 0

if to_wildcard and from_wildcard:
    sys.exit("Can't have focused to- and from- wildcards.")

this_twiddle = my_twiddle_projects[my_project]

if to_wildcard:
    got_any = False
    for m in this_twiddle.movefrom_locked:
        if re.search(r'{}'.format(to_wildcard), m):
            this_twiddle.moveto_locked[m] = False
            this_twiddle.movefrom_locked[m] = True
            got_any = True
            print("Got match:", m, to_wildcard)
        else:
            this_twiddle.moveto_locked[m] = True
            this_twiddle.movefrom_locked[m] = False
    if not got_any:
        sys.exit("Did not get any to_wildcard matches for {}. Check what sections it can match against.".format(to_wildcard))

if from_wildcard:
    got_any = False
    for m in this_twiddle.movefrom_locked:
        if re.search(r'{}'.format(from_wildcard), m):
            this_twiddle.movefrom_locked[m] = False
            this_twiddle.moveto_locked[m] = True
            got_any = True
            print("Got match:", m, from_wildcard)
        else:
            this_twiddle.movefrom_locked[m] = True
            this_twiddle.moveto_locked[m] = False
    if not got_any:
        sys.exit("Did not get any to_wildcard matches for {}. Check what sections it can match against.".format(from_wildcard))

for f in force_locks:
    force_lock_wildcard(f)

if check_sectioning:
    for x in this_twiddle.to_temp:
        mt.check_properly_sectioned(x)

for x in this_twiddle.to_temp: # I changed this once. The "to-temp," remember, points TO the file in the temp directory, FROM an absolute path. 
    max_file_reached = False
    cur_file_changes = 0
    cur_text_tweaks = 0
    xb = os.path.basename(x)
    past_ignore = False
    with open(x) as file:
        last_section = ''
        current_section = ''
        for (line_count, line) in enumerate (file, 1):
            if not past_ignore and this_twiddle.shuffle_end:
                if line.startswith(this_twiddle.shuffle_end):
                    print("Found the end line", line_count)
                    past_ignore = True
            if line.startswith("#"):
                if current_section:
                    section_text[current_section] += line
                    before_lines[current_section] += 1
                elif last_section:
                    post_text[last_section] += line
                else:
                    section_text['blank'] += line
                continue
            if line.startswith("\\"):
                current_section = line.strip()
                if current_section not in section_text:
                    section_text[current_section] = ""
                continue
            if not line.strip():
                if current_section:
                    last_section = current_section
                elif last_section:
                    post_text[last_section] += line
                current_section = ''
                continue
            if current_section:
                before_lines[current_section] += 1
            if past_ignore:
                section_text['blank' if not current_section else current_section] += line
                continue
            temp = pattern_check(line)
            lcut = mt.no_comment(line.strip().lower())
            if (not max_text_tweaks) or cur_text_tweaks <= max_text_tweaks:
                for t_match in this_twiddle.flag_text_chunks:
                    if t_match in lcut:
                        cur_text_tweaks += 1
                        if max_text_tweaks and cur_text_tweaks > max_text_tweaks:
                            print("Went over max text tweaks at line {} of {}. Increase with -mt.".format(line_count, xb))
                            break
                        print("Flagged exact bad-text match <{}> at line {} of {}: {}".format(t_match, line_count, xb, line.strip()))
                        mt.add_postopen(x, line_count)
                for r_match in this_twiddle.flag_regexes:
                    if re.search(r_match, lcut, re.IGNORECASE):
                        cur_text_tweaks += 1
                        if max_text_tweaks and cur_text_tweaks > max_text_tweaks:
                            print("Went over max text tweaks at line {} of {}.".format(line_count, xb))
                            break
                        print("Flagged exact bad-regex match <{}> at line {} of {}: {}".format(r_match, line_count, xb, line.strip()))
                        mt.add_postopen(x, line_count)
            if temp and current_section != temp and not this_twiddle.movefrom_locked[current_section] and not this_twiddle.moveto_locked[temp] and not max_file_reached and not max_overall_reached:
                if max_changes_overall and overall_changes == max_changes_overall:
                    print("You went over the maximum overall changes allowed in all files.")
                    max_overall_reached = True
                if max_changes_per_file and cur_file_changes == max_changes_per_file:
                    print("You went over the maximum # of changes for {}.".format(x))
                    max_file_reached = True
                if not max_file_reached and not max_overall_reached:
                    cur_file_changes += 1
                    overall_changes += 1
                    section_text[temp] += line
                    continue
            if current_section:
                section_text[current_section] += line
                continue
            if last_section:
                post_text[last_section] += line
            section_text['blank'] += line
    if cur_file_changes:
        print("Total changes in {}: {}".format(x, cur_file_changes))
    else:
        print("No changes in", x)

for x in from_and_to:
    if write_out_files(x) == NO_CHANGES:
        continue
    to_of_x = this_twiddle.to_temp[x]
    if check_sectioning:
        mt.check_properly_sectioned(to_of_x)
    print("TWIDDLY", twiddle_of(to_of_x), x)
    if print_stats:
        print("Orig:", os.stat(x).st_size, x)
        print("New:", os.stat(twiddle_of(to_of_x)).st_size, twiddle_of(to_of_x))

if not copy_over:
    print("-co to copy over")
else:
    copy_back_from_temp(this_twiddle, from_and_to)

if postopen_to_fix:
    mt.postopen_files()
