#
# dsort.py
# python extension of former perl dsort updater
#
# the "done" directory is an original copy of things
# the actual directory may be modified
#
# lc = outline check (e.g. update what backslashes point where)
#
# this grabs everything from a file
# use dgrab to grab a specific sort of section, which is more flexible
# dff.py is what supersedes it

import daily
import i7
import sys
import re
import os
from collections import defaultdict
from shutil import copy
import datetime

import mytools as mt

# the lower and upper bounds may be changed for testing etc.
dir_to_proc = ""

now = datetime.datetime.now()

full_out_file_list = defaultdict(bool)
file_name = defaultdict(str)
file_comment = defaultdict(lambda:defaultdict(str))
cfg_line = defaultdict(lambda:defaultdict(str))
changed_out_files = defaultdict(bool)
daily_proc_with = defaultdict(bool)
or_dict = defaultdict(str)
text_out = defaultdict(str)

ignore_header_hash = defaultdict(int)

need_tabs = defaultdict(bool)

default_section_name = "ide"

#def sort_backslash_sections()
base_dir = "c:/writing"
temp_dir = "c:/writing/temp"
backup_dir = "c:/writing/backup"
idea_hash = "c:/writing/idea-tab.txt"
undef_file = "undef.txt"

wm_diff = False

write_to_undef = False

copy_over = False
to_full_only = True

print_warnings = False
stderr_warnings = False
to_full_only = True
return_after_first_bug = False

outline_check = False
blank_counter = False

start_latest = False
max_files = 0

def obscure_header(x):
    if re.search("^nam-[a-z]{2}$", x): return True
    if re.search("^sp[0-9]$", x): return True
    if x == 'unsorted' or x == 'unsure': return True
    return False

def compare_hash_to_outline():
    in_out_files = defaultdict(str)
    last_blank = False
    need_cr = 0
    for q in full_out_file_list.keys():
        q1 = to_full(q, base_dir)
        with open(q1) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("\\"):
                    if last_blank:
                        ll = line[1:].strip()
                        ll = re.sub("=.*", "", ll)
                        in_out_files[ll] = q1
                    else:
                        print("Need CR before backslash {:s} line {:d}.".format(q, line_count))
                        need_cr += 1
                last_blank = len(line.strip()) == 0
    my_list = list(set(in_out_files.keys()) - set(file_name.keys()) - set(ignore_header_hash.keys()))
    my_list_2 = [x for x in my_list if not obscure_header(x)]
    print(need_cr if need_cr else "!!!!HOORAY!!! No", "excess backslash error{:s}.".format(i7.plur(need_cr)))
    if len(my_list_2):
        for x in sorted(my_list_2):
            print("Out_file", in_out_files[x], "has key", x, "but it is not in the idea hash's keys.")
        print(len(my_list_2), "total file name keys to fill in in the hash file.")
    else:
        print("****YAY!!!! All output file headers are defined in the hash file!!!!")
    my_list = list(set(file_name.keys()) - set(in_out_files.keys()))
    if not len(my_list): print("****WOOHOO!!!! All entries in idea hash are defined in some output file.")
    else:
        for x in sorted(my_list): print("idea hash has", x, "which is not defined in any output file.")
        print(len(my_list), "total idea hashed not defined in any output file.")
    exit()

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
    my_f_full = to_full(my_f, base_dir)
    cur_section = ""
    skip_next = False
    with open(my_f_full) as file:
        for (line_count, line) in enumerate(file, 1):
            # print(line_count, q, line[:30], sep="-/-")
            if line.startswith("#"): continue
            if line.startswith(";"): break
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

def usage_sorting_check():
    print("ih = idea hash")
    print("lc = outline check (e.g. does {:s} match the out files)".format(idea_hash))
    exit()

def usage():
    print("U# = upper bound")
    print("L# = lower bound")
    print("E# = end of days back, S# = start of days back")
    print("FE(#)/EF(#) = earliest first, FL(#)/LF(#) = latest first")
    print("Numbers are right after the letters, with no spaces.")
    print("WM = show WinMerge differences, WN/NW = turn it off, default = {:s}".format(i7.on_off[wm_diff]))
    print("WU/UW = write to undef file, NU/UN = don't write to undef file, default = {:s}".format(i7.on_off[write_to_undef]))
    print("? = this")
    print("?? = sorting check stuff")
    exit()

def go_back(q):
    then = now - datetime.timedelta(days=q)
    return "{:d}{:02d}{:02d}".format(then.year, then.month, then.day)

def to_backups():
    for q in file_name.keys(): copy(q, to_full(q, backup_dir))

def to_section(x, fill_in_default = False):
    x = x[1:]
    if x in daily.preferred_header: return daily.preferred_header[x]
    return ""

def warn_print(x):
    if print_warnings:
        print(x)
    elif stderr_warnings:
        stderr.write(x)

def read_hash_file():
    stuff = defaultdict(bool)
    with open(idea_hash) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if line.startswith("FILES:"):
                lp = re.sub("^[a-z]*?:", "", line.lower().strip())
                for q in lp.split(","): full_out_file_list[q] = True
                continue
            if line.startswith("IGNORE:"):
                lp = re.sub("^[a-z]*?:", "", line.lower().strip())
                for q in lp.split(","):
                    if q in ignore_header_hash.keys(): print("Double hash {:s} {:d} {:d}".format(q, line_count, ignore_header_hash[q]))
                    else: ignore_header_hash[q] = line_count
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
    if not len(full_out_file_list.keys()):
        print("Couldn't find a FILES: in {:s}.".format(idea_hash))
        print("SUGGESTION:")
        sys.exit("FILES:{:s}".format(','.join(sorted(stuff.keys()))))
    return sorted(full_out_file_list.keys())

def compare_hash_with_files():
    with open(idea_hash) as file:
        for (line_count, line) in file:
            hash_file_val[l0] = line_count

def to_full(x, backup_dir = temp_dir):
    return os.path.join(backup_dir, os.path.basename(x))

def get_stuff_from_one_file(x):
    print("Getting stuff from", x)
    loc_text_out = defaultdict(str)
    loc_sections = defaultdict(int)
    last_line = defaultdict(int)
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
                    section_name = to_section(ll, True)
                    check_section = to_section(ll, False)
                    ls = ll[1:]
                    if not check_section:
                        print(ls, "may be bad section in", x, "line", line_count)
                        sys.exit()
                    if ls in loc_sections.keys(): sys.exit("{:s} has 2 local sections of {:s}: line {:d} and {:d}.".format(x, ls, line_count, loc_sections[ls]))
                    loc_sections[ls] = line_count
                    if section_name in loc_text_out.keys(): print("WARNING {:s} has semi-duplicate section {:s}/{:s} at line {:d}/{:d}.".format(x, ls, section_name, line_count, last_line[section_name]))
                    last_line[section_name] = line_count
                    continue
                    # print(line_count, section_name, ll, sep="-/-")
            loc_text_out[section_name] += line
    for y in loc_text_out.keys():
        if not loc_text_out[y]:
            print("Skipping empty section", y, "in", x)
            continue
        # if y in file_name.keys(): print("Saw", y, "(", file_name[y], ")", "in", x)
        if not daily.mapping[y] and not write_to_undef: sys.exit("Could not find file name for section {:s}. Set write undef flag -wu/-uw.".format(y))
        changed_out_files[daily.mapping[y]] = True
        if y in need_tabs.keys(): loc_text_out[y] = "\t" + loc_text_out[x]
        text_out[y] += loc_text_out[y]
    daily_proc_with[x] = True
    print("Got stuff from", x)

##############################main program

daily.read_section_sort_cfg()
daily.read_main_daily_config()
days_back_start = daily.days_back_start
days_back_end = daily.days_back_end
lower_bound = daily.lower_bound
upper_bound = daily.upper_bound

daily_dir = "c:/writing/daily"
daily_proc = daily.to_proc(daily_dir)
gdrive_dir = "c:/coding/perl/proj/from_drive/drive_mod"
gdrive_done = daily.to_proc(gdrive_dir)

count = 1

mt.warn("****************************************")
mt.warn("****** WARNING USE DFF.PY INSTEAD ******")
mt.warn("****************************************")

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg.startswith("-"): arg = arg[1:]
    if arg == 'wm': wm_diff = True
    elif arg == 'd': dir_to_proc = daily_dir
    elif arg == 'g': dir_to_proc = gdrive_dir
    elif arg.startswith("fl") or arg.startswith("fl"):
        start_latest = True
        if len(arg) > 2 and arg[2:].isdigit:
            max_files = int(arg[2:])
    elif arg.startswith("fe") or arg.startswith("fe"):
        start_latest = False
        if len(arg) > 2 and arg[2:].isdigit:
            max_files = int(arg[2:])
    elif arg == 'wu' or arg == 'uw': write_to_undef = True
    elif arg == 'nu' or arg == 'un': write_to_undef = False
    elif arg == 'nw' or arg == 'wn': wm_diff = False
    elif arg == 'lc': outline_check = True
    elif arg == 'ih': i7.npo(idea_hash)
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
    elif arg == '?': usage()
    elif arg == '??': usage_sorting_check()
    else:
        print("Invalid command/flag", arg[0], arg)
        usage()
    count += 1

if not dir_to_proc:
    x = os.getcwd()
    if daily.slashy_equals(x, [gdrive_dir, daily_dir]):
        print("Using current directory", x)
        dir_to_proc = x
    else:
        print("Need to specify a directory with -g (google drive) or -d (daily) or be in that directory.")
        sys.exit("{0} / {1} / {2}".format(x, gdrive_dir, daily_dir))

if days_back_start or days_back_end:
    upper_bound = go_back(days_back_end)
    lower_bound = go_back(days_back_start) if days_back_start else '20170000'
    print("Days back overrides in effect: upper bound={:s}, lower bound={:s}".format(upper_bound, lower_bound))

if lower_bound > upper_bound: sys.exit("Lower bound {0} > upper bound {1}. Fix this before continuing.".format(lower_bound, upper_bound))

my_files = read_hash_file()

if outline_check:
    compare_hash_to_outline()

if blank_counter:
    for mf in my_files: search_for_spaces(mf)
    exit()

os.chdir(dir_to_proc)
list_of_dailies = [x for x in os.listdir(dir_to_proc) if os.path.isfile(x) and x.lower().endswith(".txt")]
if start_latest: list_of_dailies = reverse(list_of_dailies)

daily_files_processed = 0

for file in list_of_dailies:
    if max_files and daily_files_processed > 1:
        print("Stopping at", file)
        break
    if not daily.valid_file(file, dir_to_proc): continue
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
        if not x: continue
        x2 = to_full(x, base_dir)
        x3 = to_full(x, temp_dir)
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
    any_undef_written = False
    if write_to_undef:
        f1 = to_full(undef_file, base_dir)
        f2 = to_full(undef_file, temp_dir)
        copy(f1, f2)
        f = open(f2, "a")
        tso = sorted(text_out.keys())
        for q in tso:
            if q not in file_name.keys() or not file_name[q]:
                if not any_undef_written:
                    any_undef_written = True
                    print("Writing undefined headers to", undef_file)
                    changed_out_files[undef_file] = True
                    f.write("UNDEF idea dump (python) at {:s}\n\n".format(now.strftime("%Y-%m-%d %H:%m:%S")))
                    if wm_diff: cmds.append("wm \"{:s}\" \"{:s}\"".format(f1, f2))
                f.write("\\{:s}\n{:s}\n".format(q, text_out[q]))
                text_out.pop(q)
        f.close()
    if len(text_out.keys()) != 0:
        print("Uh oh! Some keys weren't resolved:")
        t = ["{:s}({:s})".format(x, file_name[x]) for x in sorted(text_out.keys())]
        sys.exit("    " + ", ".join(sorted(t)))
    for c in cmds: os.system(c)
    exit()
    if to_full_only:
        print("Look in", temp_dir, "for", '/'.join(changed_out_files.keys()))
    else:
        for x in changed_out_files.keys():
            the_temp = to_full(x)
            the_base = to_full(x, basedir)
            print(the_temp, the_base)
            # copy(the_temp, the_base)
            os.remove(the_temp)
        for j in daily_proc_with.keys():
            j1 = to_full(j, daily_dir)
            j2 = to_full(j, daily_proc)
            print("Move", j1, j2)
            # os.move(j1, j2)
