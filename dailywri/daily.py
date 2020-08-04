#
# daily.py
#
# common code for dsort.py and dgrab.py
#

import sys
from shutil import copy
import re
import os
import pendulum
from collections import defaultdict
import glob
import mytools as mt
from pathlib import Path

today_file = pendulum.now().format("YYYYMMDD") + ".txt"

lower_bound = "20170101.txt"
upper_bound = today_file

days_back_start = days_back_end = total_files = 0

wri_temp = "c:/writing/temp"

dg_cfg = "c:/writing/scripts/dgrab.txt"
flat_cfg = os.path.basename(dg_cfg)

#these map sections and files
mapping = defaultdict(str)
preferred_header = defaultdict(str)
regex_sect = defaultdict(str)
regex_comment = defaultdict(str)
file_regex = defaultdict(str)
globs = defaultdict(str)
where_to_insert = defaultdict(str)

default_sect = ""
glob_default = "da"

open_on_warn = False

dir_keywords = [ "daily", "from_drive", "from_keep" ]

def is_true_string(x):
    if x == '0' or x == 'false': return False
    return True

def read_main_daily_config():
    global lower_bound
    global upper_bound
    global days_back_start
    global days_back_end
    global total_files
    with open("c:/writing/scripts/daily.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): continue
            if '=' not in line:
                print("CFG read warning: line {0} needs =".format(line_count))
                continue
            l = line.lower().strip().split("=")
            if l[0] == 'lower_bound': lower_bound = l[1]
            elif l[0] == 'upper_bound': upper_bound = l[1]
            elif l[0] == 'days_back_start': days_back_start = int(l[1])
            elif l[0] == 'days_back_end': days_back_end = int(l[1])
            elif l[0] == 'total_files': total_files = int(l[1])
            else: print("Uh oh unknown CFG value line {0} is {1}.".format(line_count, l[0]))
    if lower_bound > upper_bound:
        print("UH OH! Lower and upper bound are switched in the CFG. Flipping them.")
        (lower_bound, upper_bound) = (upper_bound, lower_bound)

def read_section_sort_cfg(cfg_bail = False):
    global default_sect
    cfg_edit_line = 0
    mapping_check = defaultdict(str)
    with open(dg_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            l0 = re.sub("^.*?=", "", line.strip())
            lary = l0.split(",")
            my_args = lary[0].split("|")
            if line.startswith("MAPPING="):
                my_regex_1 = r'^\\({:s})'.format(lary[0])
                my_regex_2 = r' *#({:s})\b'.format(lary[0])
                if len(lary) < 3:
                    print("You need to have 3 arguments in a MAPPING: headers, file, and headers-in-file to insert after (empty is ok).")
                    mt.npo(dg_cfg, line_count)
                for q in my_args:
                    if q in preferred_header:
                        print("Uh oh, duplicate header definition", q, "points to", preferred_header[q], "reassigned to", my_args[0], "at line", line_count)
                        mt.add_postopen(dg_cfg, line_count)
                        cfg_bail = True
                    preferred_header[q] = my_args[0]
                    mapping[q] = lary[1]
                    regex_sect[q] = my_regex_1
                    regex_comment[q] = my_regex_2
                    where_to_insert[q] = lary[2]
            elif line.startswith("DEFAULT="): default_sect = lary[0]
            elif line.startswith("GLOBDEF="): glob_default = lary[0]
            elif line.startswith("PRINTIGNOREDFILES="): print_ignored_files = is_true_string(lary[0])
            elif line.startswith("GLOB="):
                for q in my_args:
                    if len(lary) > 2: file_regex[q] = lary[2]
                    else: file_regex[q] = '.'
                    globs[q] = lary[1]
                q = my_args[0]
                temp = glob.glob(globs[q])
                temp1 = [u for u in temp if re.search(file_regex[q], u)]
                if len(temp) == 0:
                    print("WARNING: glob pattern {:s} ~ {:s} at line {:d} of {} does not turn up any files.".format(q, globs[q], line_count, dg_cfg))
                    cfg_edit_line = line_count
                elif len(temp1) == 0:
                    print("WARNING: glob pattern {:s} ~ {:s} at line {:d} turns up files, but none are matched by subsequent regex.".format(q, globs[q], line_count))
                    cfg_edit_line = line_count
                if print_ignored_files and len(temp) != len(temp1):
                    print("IGNORED from {}: {:s}".format(q, ', '.join([u for u in temp if u not in temp1])))
            elif line.startswith("OPENONWARN="):
                open_on_warn = int(lary[0])
            elif line.startswith("SHOWDIFF="): do_diff = is_true_string(lary[0])
            elif line.startswith("MAXPROC="):
                try:
                    max_process = int(lary[0])
                    if max_process < -1:
                        print("Setting default max_process to -1. Maybe fix line", line_count)
                        max_process = -1
                except:
                    print("MAXPROC= went wrong at line", line_count)
                    cfg_edit_line = line_count
            else:
                print("Unrecognized command line", line_count, line.strip())
                cfg_edit_line = line_count
    if cfg_bail:
        print("Fix problems in the CFG file.")
        mt.postopen()
    if cfg_edit_line:
        open_on_warn = False
        if not open_on_warn:
            for q in sys.argv:
                if q == 'e' or q == '-e': open_on_warn = True
        if open_on_warn: mt.npo(dg_cfg, cfg_edit_line)
        else: print("Put in an OPENONWARN in {:s} to open the CFG file, or type e/-e on the command line.".format(dg_cfg))

def done_of(dir_path):
    return os.path.join(dir_path, "done")

def to_proc(dir_path):
    return os.path.join(dir_path, "to-proc")

toproc = proc = to_proc

def is_dir_or_proc(dir_1, dir_list):
    for dir_2 in dir_list:
        temp1 = Path(dir_1)
        temp2 = Path(dir_2)
        if temp2 in temp1.parents or temp2 == temp1:
            return temp2
    return ""
    
def copy_to_done(file_name, dir_path):
    done_path = done_of(dir_path)
    done_from = os.path.join(dir_path, file_name)
    done_target = os.path.join(done_path, file_name)
    if not os.path.exists(done_target):
        print("Copying", done_from, "to", done_target)
        copy(done_from, done_target)

def valid_file(file_name, dir_name):
    base_name = os.path.basename(file_name)
    for d in dir_keywords:
        if d in dir_name.lower():
            return re.search("^20[0-9]{6}\.txt$", base_name.lower())
    print("Bad dir name in", dir_name, "for", base_name)
    return False

