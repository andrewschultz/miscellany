#
# dsort.py
# python extension of former perl dsort updater
#

import i7
import sys
import re
import os
from collections import defaultdict
import datetime

now = datetime.datetime.now()

file_name = defaultdict(str)
file_comment = defaultdict(lambda:defaultdict(str))
cfg_line = defaultdict(lambda:defaultdict(str))
changed_out_files = defaultdict(bool)
daily_done_with = defaultdict(bool)
or_dict = defaultdict(str)
text_out = defaultdict(str)

need_tabs = defaultdict(bool)

default_section_name = "ide"

#def sort_backslash_sections()
base_dir = "c:/writing"
daily_dir = "c:/writing/daily"
done_dir = "c:/writing/daily/done"
temp_dir = "c:/writing/temp"
backup_dir = "c:/writing/backup"
idea_hash = "c:/writing/idea-tab.txt"

wm_diff = False

copy_over = True
to_temp_only = True

print_warnings = False
stderr_warnings = False
to_temp_only = True
return_after_first_bug = False

blank_counter = False

def show_section_add(): # only used for debugging
    to = sorted(text_out.keys())
    for q in to:
        print(q, "====")
        print(text_out[q] + "===")
    print("Sections added:", ", ".join(to))

def search_for_spaces(my_f):
    if 'hthws' in my_f: return
    if 'sb.otl' in my_f: return
    last_blank = 0
    my_f_full = to_temp(my_f, base_dir)
    cur_section = ""
    skip_next = False
    with open(my_f_full) as file:
        for (line_count, line) in enumerate(file, 1):
            # print(line_count, q, line[:30], sep="-/-")
            if line.startswith("[") and line.rstrip().endswith("]"):
                print("Ignoring comment at line", line_count, "in", my_f_full)
                skip_next = True
                continue
            if skip_next:
                skip_next = False
                continue
            if not line.strip():
                if not cur_section and line_count - last_blank > 1:
                    print("Extra blank line at", line_count, "file", my_f_full)
                last_blank = line_count
                cur_section = ""
                continue
            q = space_section(line)
            if q:
                if cur_section: print("Double defined section at", line_count, "file", my_f_full)
                # else: print("New section", q, "at", line_count)
                cur_section = q

def space_section(x):
    x1 = x.rstrip()
    if x1.startswith("\\"):
        return re.sub("=.*", "", x1[1:].lower())
    if x1.startswith("H=") or x.startswith("h="):
        temp = re.sub("^.*?\"", "", x)
        return re.sub("\"", "", temp)
    if x1.startswith("= V4"):
        return "Intro-outline"
    return ""

def usage():
    print("U# = upper bound")
    print("L# = lower bound")
    print("B/D# = days back")
    print("Numbers are right after the letters, with no spaces.")
    print("WM = show WinMerge differences, WN/NW = turn it off, default = {:s}".format(i7.on_off[wm_diff]))
    print("? = this")
    exit()

def go_back(q):
    then = now - datetime.timedelta(days=q)
    return "{:d}{:02d}{:02d}".format(then.year, then.month, then.day)

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
    return file_list

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
                    continue
                    # print(line_count, section_name, ll, sep="-/-")
            loc_text_out[section_name] += line
    for y in loc_text_out.keys():
        print("Saw", y, "(", file_name[y], ")", "in", x)
        if not y:
            print("Skipping empty section", y, "in", x)
            continue
        if not file_name[y]: sys.exit("Could not find file name for section {:s}.".format(y))
        changed_out_files[file_name[y]] = True
        if y in need_tabs.keys(): loc_text_out[y] = "\t" + loc_text_out[x]
        text_out[y] += loc_text_out[y]
    daily_done_with[x] = True
    print("Got stuff from", x)

lower_bound = "20170101.txt"
days_back_start = 0
days_back_end = 0
upper_bound = "20170909.txt"
count = 1
total_files = 0

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg.startswith("-"): arg = arg[1:]
    if arg == 'wm': wm_diff = True
    elif arg == 'nw' or arg == 'wn': wm_diff = False
    elif arg == 'bc':
        blank_counter = True
    elif arg.startswith('u'):
        upper_bound = arg[1:]
        if len(upper_bound) < 8: upper_bound += '9' * (8 - len(upper_bound))
    elif arg.startswith('l'):
        lower_bound = arg[1:]
        if len(lower_bound) < 8: upper_bound += '0' * (8 - len(upper_bound))
    elif arg.startswith('tf'):
        try:
            total_files = int(arg[2:])
        except:
            sys.exit("You need a number after -tf.")
    elif arg.startswith('e'):
        if not arg[1:].isdigit(): sys.exit("-e needs digits after for days back end.")
        days_back_end = int(arg[1:])
    elif arg.startswith('s'):
        if not arg[1:].isdigit(): sys.exit("-s needs digits after for days back start.")
        days_back_start = int(arg[1:])
    else:
        print("Invalid command/flag", arg[0], arg)
        usage()
    count += 1

if days_back_start or days_back_end:
    upper_bound = go_back(days_back_end)
    lower_bound = go_back(days_back_start) if days_back_start else '20170000'
    print("Days back overrides in effect: upper bound={:s}, lower bound={:s}".format(upper_bound, lower_bound))

if lower_bound > upper_bound: sys.exit("Lower bound > upper bound")

my_files = read_hash_file()

if blank_counter:
    for mf in my_files: search_for_spaces(mf)
    exit()

os.chdir(daily_dir)
readdir = [x for x in os.listdir(daily_dir) if os.path.isfile(x)]

daily_files_processed = 0

for file in readdir:
    if not re.search("^20[0-9]{6}\.txt$", file.lower()): continue
    fb = file[:8] # strip the .txt ending
    if fb < lower_bound:
        warn_print("Skipping {:s} too low".format(fb))
        continue
    if fb > upper_bound:
        warn_print("Skipping {:s} too high".format(fb))
        continue
    daily_files_processed += 1
    get_stuff_from_one_file(file)

if not daily_files_processed: sys.exit("Nothing processed. I am copying nothing over.")

# show_section_add()

if copy_over: # maybe we should put this into a function
    cur_out = ""
    last_backslash = 0
    cmds = []
    print("First, writing to temp dir:")
    for x in changed_out_files.keys():
        x2 = to_temp(x, base_dir)
        x3 = to_temp(x, temp_dir)
        if not os.path.exists(x2):
            print("Could not find path for", x, "/", x2)
            exit()
        with open(x2) as file:
            f = open(x3, "w")
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("\\"):
                    if cur_out: sys.exit("Ruh roh two backslashes without a line break curline={:d}/{:s} {:d} in file {:s}.".format(line_count, line.strip(), last_backslash, x))
                    cur_out = re.sub("=.*", "", line[1:].strip())
                    last_backslash = line_count
                    f.write(line)
                    continue
                if cur_out:
                    if not line.strip():
                        if cur_out in text_out.keys():
                            if not text_out[cur_out].endswith("\n"): text_out[cur_out] += "\n"
                            crs = text_out[cur_out].count("\n")
                            f.write(text_out[cur_out])
                            text_out.pop(cur_out)
                            changed_out_files[file_name[cur_out]] = True
                            print("Added {:d} line{:s} to section {:s} ({:d}-{:d}) in file {:s}.".format(crs, i7.plur(crs), cur_out, last_backslash, line_count, x))
                        cur_out = ""
                f.write(line)
        f.close()
        if wm_diff: cmds.append("wm \"{:s}\" \"{:s}\"".format(x2, x3))
    if len(text_out.keys()) != 0:
        print("Uh oh! Some keys weren't resolved:")
        sys.exit(", ".join(sorted(text_out.keys())))
    for c in cmds: os.system(c)
    exit()
    if to_temp_only:
        print("Look in", temp_dir, "for", '/'.join(changed_out_files.keys()))
    else:
        for x in changed_out_files.keys():
            the_temp = to_temp(x)
            print(the_temp, x)
            # copy(the_temp, x)
            os.remove(the_temp)
        for j in daily_done_with.keys():
                print("Move", j, to_temp(j))
                # os.move(j, to_temp(j))
