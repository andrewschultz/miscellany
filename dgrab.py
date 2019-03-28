# question: search for starting tabs in non-.ni files. What script for that?

from shutil import copy
from collections import defaultdict
import i7
import glob
import re
import os
import sys
import time

default_sect = ""
my_sect = ""
default_by_dir = i7.dir2proj(to_abbrev = True)

dg_cfg = "c:/writing/scripts/dgrab.txt"
flat_cfg = os.path.basename(dg_cfg)
dg_temp = "c:/writing/temp/dgrab-temp.txt"
flat_temp = os.path.basename(dg_temp)

mapping = defaultdict(str)
regex_to = defaultdict(str)
notes_to_open = defaultdict(int)

max_process = 0
open_notes = 0
days_before_ignore = 7

verbose = False
open_notes_after = True
change_list = []

def usage(header="GENERAL USAGE"):
    print(header)
    print('=' * 50)
    print("# = maximum number of files to process")
    print("d/db(#) = days before to ignore")
    print("o = open notes after, no/on = don't")
    print("e = edit cfg file")
    exit()

def file_len(fname):
    with open(fname) as f:
        for (i, l) in enumerate(f, 1):
            pass
    return i

def send_mapping(sect_name, file_name, change_files = False):
    temp_time = os.stat(file_name)
    fn = os.path.basename(file_name)
    time_delta = time.time() - temp_time.st_ctime
    my_reg = regex_to[sect_name]
    found_sect_name = False
    in_sect = False
    file_remain_text = ""
    sect_text = ""
    x = r'^\\(vvff)'
    if sect_name not in mapping: sys.exit("No section name {:s}, bailing on file {:s}.".format(sect_name, file_name))
    # print(sect_name, "looking for", my_reg, "in", file_name)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if re.search(my_reg, line):
                if verbose: print(file_name, "line", line_count, "has {:s} section".format("extra" if found_sect_name else "a"), sect_name)
                if not line.startswith("\\" + sect_name): print("    NOTE: alternate section name from {:s} is {:s}".format(sect_name, line.strip()))
                found_sect_name = True
                in_sect = True
                continue
            if in_sect:
                if line.startswith("\\"): sys.exit("Being pedantic that " + file_name + " has bad sectioning. Bailing.")
                if not line.strip():
                    in_sect = False
                    continue
                sect_text += line
            else:
                file_remain_text += line
    if time_delta < days_before_ignore * 86400 and found_sect_name:
        print("Something was found, but time delta was not long enough for {:s}. It is {:d} and needs to be at least {:d}. Set with d(b)#.".format(file_name, int(time_delta), days_before_ignore * 86400))
        return 0
    if not found_sect_name: return False
    if not change_files:
        global change_list
        change_list.append(fn)
        return False
    nfi = mapping[sect_name]
    print("Found", sect_name, "in", file_name, "appending to", )
    if nfi not in notes_to_open:
        notes_to_open[nfi] = file_len(nfi)
    f = open(nfi, "a")
    f.write("\n<from daily/keep file {:s}>\n".format(file_name) + sect_text)
    f.close()
    f = open(dgtemp, "w")
    f.write(file_remain_text)
    f.close()
    i7.wm(file_name, dgtemp)
    copy(dgtemp, file_name)
    os.remove(dgtemp)
    return True

#
# start main program
#

#
# need to read CFG file first as defaults may be in there
#

cfg_edit_line = 0

with open(dg_cfg) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith("#"): continue
        if line.startswith(";"): break
        l0 = re.sub("^.*?=", "", line.strip())
        lary = l0.split(",")
        if line.startswith("MAPPING="):
            my_regex = r'^\\({:s})'.format(lary[0])
            for q in lary[0].split("|"):
                mapping[q] = lary[1]
                regex_to[q] = my_regex
        elif line.startswith("DEFAULT="): default_sect = lary[0]
        elif line.startswith("OPENONWARN="):
            open_on_warn = int(lary[0])
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

if cfg_edit_line:
    if not open_on_warn:
        for q in sys.argv:
            if q == 'e' or q == '-e': open_on_warn = True
    if open_on_warn: i7.npo(dg_cfg, cfg_edit_line)
    else: print("Put in an OPENONWARN in {:s} to open the CFG file, or type e/-e on the command line.")

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg.isdigit(): max_process = arg
    elif re.search("^d(b)?[0-9]+$", arg):
        temp = re.sub("^d(b)?", "", arg)
        days_before_ignore = int(temp)
    elif arg == 'd' or arg == 'db': days_before_ignore = 0
    elif arg == 'dt' or arg == 't': max_process = -1
    elif arg == 'e':
        os.system(dg_cfg)
        exit()
    elif arg == 'o': open_notes_after = True
    elif arg == 'no' or arg == 'on': open_notes_after = False
    elif arg == '?': usage()
    else:
        usage("BAD PARAMETER {:s}".format(sys.argv[cmd_count]))
    cmd_count += 1

x = glob.glob("c:/writing/daily/20*.txt")

if not my_sect:
    if not default_by_dir or default_by_dir not in mapping:
        print("Going with default section defined in {:s}: {:s}.{:s}".format(flat_cfg, default_sect, (" {:s} is defined by the PWD but is not in the {:s} mapping.".format(default_by_dir, flat_cfg) if default_by_dir else "")))
        my_sect = default_sect
    else:
        print("Going with default section defined by directory you're in {:s}.".format(default_by_dir))
        my_sect = default_by_dir

processed = 0

max_warning = False
if max_process == -1: print("Running test to cull all eligible files.")

for q in x:
    processed += send_mapping(my_sect, q, processed < max_process or max_process == 0)
    if max_process and processed == max_process and not max_warning:
        max_warning = True
        if max_process > 1: print("Reached maximum. Stopped at file " + q)

if processed == 0 and max_process >= 0: print("Could not find anything to process for {:s}.".format(my_sect))

if len(change_list):
    print("Files still to process:", ', '.join(change_list))
if max_process > 0: print("Got {:d} of {:d} files.".format(processed, max_process))

if open_notes_after:
    for q in notes_to_open: i7.npo(q, notes_to_open[q], False, False)
