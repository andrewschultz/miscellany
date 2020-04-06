# dgrab.py
#
# daily grab file: grab section from daily files (or other) and pipe it directly to notes files
#
# for instand #whau would go to welp-haunted file
#
# usage: dgrab.py -da s=wh
#
# question: search for starting tabs in non-.ni files. What script for that?
#

import datetime
from shutil import copy
from collections import defaultdict
import i7
import glob
import re
import os
import sys
import time
import filecmp
import daily

glob_default = "da"
default_sect = ""
my_sect = ""
default_by_dir = i7.dir2proj(to_abbrev = True)
my_globs = []

dg_cfg = "c:/writing/scripts/dgrab.txt"
flat_cfg = os.path.basename(dg_cfg)
dg_temp = "c:/writing/temp/dgrab-temp.txt"
dg_temp_2 = "c:/writing/temp/dgrab-temp-2.txt"
flat_temp = os.path.basename(dg_temp)

mapping = defaultdict(str)
preferred_header = defaultdict(str)
regex_sect = defaultdict(str)
regex_comment = defaultdict(str)
file_regex = defaultdict(str)
notes_to_open = defaultdict(int)
globs = defaultdict(str)

where_to_insert = defaultdict(str)
file_list = defaultdict(list)
sect_lines = defaultdict(int)

max_process = 0
open_notes = 0
days_before_ignore = 0 # this used to make sure we didn't hack into a current daily file, but now we have a processing subdirectory, we don't need that
min_for_list = 0

just_analyze = False
bail_without_copying = False
open_on_warn = False
do_diff = True
verbose = False
open_notes_after = True
change_list = []
print_ignored_files = False
list_it = False

daily_dir = "c:/writing/daily"
daily_proc = daily.to_proc(daily_dir)
gdrive_dir = "c:/coding/perl/proj/from_drive/drive_mod"
gdrive_proc = daily.to_proc(gdrive_dir)

def usage(header="GENERAL USAGE"):
    print(header)
    print('=' * 50)
    print("# = maximum number of files to process")
    print("d/db(#) = days before to ignore")
    print("o = open notes after, no/on = don't")
    print("e = edit cfg file")
    print("di = do windiff, ndi/din/nd/dn = don't do windiff")
    print("pi = print ignore, npi/pin = don't print ignore")
    print("l = list headers, l# = list headers with # or more entries")
    print("s= = section to look for")
    print("a= analyze what is left")
    print("")
    print("sample usage: dgrab.py -da s=ut for Under processing")
    exit()

def analyze_to_proc():
    sections_left = defaultdict(int)
    first_file_with_section = defaultdict(str)
    files_to_verify = glob.glob(daily_proc + "/*.*")
    err_flagged = defaultdict(int)
    count = 0
    for this_daily in files_to_verify:
        with open(this_daily) as file:
            daily_basename = os.path.basename(this_daily)
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("\\"):
                    ll = line.lower().strip()[1:]
                    if ll not in mapping and ll not in err_flagged:
                        count += 1
                        print("Bad header #{:2d}:".format(count), ll, "line", line_count, daily_basename)
                        err_flagged[ll] = True
                    sections_left[ll] += 1
                    if ll not in first_file_with_section:
                        first_file_with_section[ll] = daily_basename
    count = 0
    for x in sorted(sections_left, key=lambda x: (-sections_left[x], x)):
        count += 1
        print("{:2d}: {:15s} {:2d} time{} 1st file={}".format(count, x, sections_left[x], "s" if sections_left[x] > 1 else " ", first_file_with_section[x]))
    exit()

def append_one_important(my_file):
    important_file = os.path.join(gdrive_dir, "important.txt")
    my_file_back = os.path.join(gdrive_dir, "my-file-backup.txt")
    if not os.path.exists(important_file):
        print("Create", important_file, "before continuing.")
        sys.exit()
    important_string = "\n\nIMPORTANT STRING FOR FILE {0} at {1}====\n".format(os.path.basename(my_file), datetime.datetime.now())
    in_important = False
    important_start = 0
    fb = os.path.basename(my_file)
    f = open(my_file_back, "w")
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            write_main = True
            if in_important:
                important_string += line
                write_main = False
                if not line.strip():
                    in_important = False
                    continue
            if line.startswith("\\important"):
                write_main = False
                if important_start:
                    print("Uh oh, extra important start at line", line_count, "after", important_start)
                    continue
                print("Started important section in {0} at line {1}".format(fb, line_count))
                important_start = line_count
                in_important = True
                continue
            if write_main: f.write(line)
    f.close()
    if important_start:
        copy(my_file_back, my_file)
        f = open(important_file, "a")
        f.write(important_string)
        f.close()
    else:
        print("Nothing important for", fb)
    os.remove(my_file_back)
    return important_start > 0

def append_all_important():
    os.chdir(gdrive_dir)
    appended = 0
    for a in glob.glob(gdrive_dir + "/20*"):
        ap = re.sub("\..*", "", os.path.basename(a))
        if invalid_year(ap): continue
        appended += append_one_important(a)
    print(appended, "total important sections appended")
    exit()

def get_list_data(this_fi):
    bn = os.path.basename(this_fi)
    in_sect = False
    my_section = ""
    with open(this_fi) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("\\"):
                if in_sect:
                    print("Died reading \\ inside \\ at line {:d}, starting line {:d}, file {:s}.".format(line_count, sect_start, bn))
                    i7.npo(this_fi, line_count)
                my_section = re.sub("^.", "", line.lower().strip())
                file_list[my_section].append(bn)
                sect_start = line_count
                in_sect = True
            if in_sect and not line.strip():
                sect_lines[my_section] += line_count - sect_start
                in_sect = False

def is_true_string(x):
    if x == '0' or x == 'false': return False
    return True

def file_len(fname):
    with open(fname) as f:
        for (i, l) in enumerate(f, 1):
            pass
    return i

def send_mapping(sect_name, file_name, change_files = False):
    temp_time = os.stat(file_name)
    fn = os.path.basename(file_name)
    time_delta = time.time() - temp_time.st_mtime
    my_reg = regex_sect[sect_name]
    my_reg_comment = regex_comment[sect_name]
    found_sect_name = False
    in_sect = False
    file_remain_text = ""
    sect_text = ""
    if sect_name not in mapping: sys.exit("No section name {:s} in the general mappings. Bailing on file {:s} before even running. Run with (-)e to open config.".format(sect_name, file_name))
    # print(sect_name, "looking for", my_reg, "in", file_name)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            lls = line.lower().strip()
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
            elif re.search(my_reg_comment, lls):
                sect_text += line
            else:
                file_remain_text += line
    if time_delta < days_before_ignore * 86400 and found_sect_name:
        print("Something was found, but time delta was not long enough for {:s}. It is {:d} and needs to be at least {:d}. Set with d(b)#.".format(file_name, int(time_delta), days_before_ignore * 86400))
        return 0
    if not sect_text:
        if verbose:
            print("No section text was found in", fn, "for", sect_name)
        return False
    if not change_files:
        global change_list
        change_list.append(fn)
        return False
    f = open(dg_temp, "w")
    f.write(file_remain_text)
    f.close()
    nfi = mapping[sect_name]
    remain_written=False
    print("Found", sect_name, "in", file_name, "to add to", nfi)
    if nfi not in notes_to_open:
        notes_to_open[nfi] = file_len(nfi)
    if where_to_insert[sect_name]:
        print("Specific insert token found for {:s}, inserting there in {:s}.".format(sect_name, nfi))
        write_next_blank = False
        w2i = where_to_insert[sect_name]
        f = open(dg_temp_2, "w")
        with open(nfi) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.lower().strip() == w2i:
                    f.write(line)
                    if line.startswith("\\"):
                        print("Will start writing at line", line_count)
                        write_next_blank = True
                    else:
                        f.write("<from daily/keep file {:s}>\n".format(file_name) + sect_text)
                        remain_written = True
                    continue
                if write_next_blank and not line.strip():
                    f.write(sect_text)
                    f.write("\n")
                    write_next_blank = False
                    remain_written = True
                    continue
                f.write(line)
        if write_next_blank:
            print("Need CR at end of section for {:s}. Writing at end of file anyway.".format(sect_name))
            f.write("\n<from daily/keep file {:s}>\n".format(file_name) + sect_text)
            f.write(sect_text)
            remain_written = True
        if not remain_written: sys.exit("Text chunk for {:s}/{:s} not written to {:s}. Bailing".format(sect_name, w2i, nif))
        f.close()
        sys.exit("Ok done with test")
    else:
        print("Appending to", nfi)
        f = open(nfi, "a")
        f.write("\n<from daily/keep file {:s}>\n".format(file_name) + sect_text)
        f.close()
    if do_diff:
        if os.path.exists(dg_temp_2): i7.wm(nfi, dg_temp_2)
        i7.wm(file_name, dg_temp)
    if bail_without_copying:
        print("Bailing before copying back over")
        print(dg_temp, file_name)
        print(dg_temp_2, nfi)
        sys.exit()
    if not filecmp.cmp(dg_temp, file_name): copy(dg_temp, file_name)
    if os.path.exists(dg_temp_2) and not filecmp.cmp(dg_temp_2, nfi):
        copy(dg_temp_2, nfi)
        os.remove(dg_temp_2)
    if os.path.exists(dg_temp): os.remove(dg_temp)
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
        my_args = lary[0].split("|")
        if line.startswith("MAPPING="):
            my_regex_1 = r'^\\({:s})'.format(lary[0])
            my_regex_2 = r' *#({:s})\b'.format(lary[0])
            if len(lary) < 3:
                print("You need to have 3 arguments in a MAPPING: headers, file, and headers-in-file to insert after (empty is ok).")
                i7.npo(dg_cfg, line_count)
            for q in my_args:
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
                temp = glob.glob(globs[q])
                temp1 = [u for u in temp if re.search(file_regex[q], u)]
                if len(temp) == 0:
                    print("WARNING: glob pattern {:s}/{:s} at line {:d} does not turn up any files.".format(q, globs[q], line_count))
                    cfg_edit_line = line_count
                elif len(temp1) == 0:
                    print("WARNING: glob pattern {:s}/{:s} at line {:d} turns up files, but none are matched by subsequent regex.".format(q, globs[q], line_count))
                    cfg_edit_line = line_count
                if print_ignored_files and len(temp) != len(temp1):
                    print("IGNORED: {:s}".format(', '.join([u for u in temp if u not in temp1])))
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

if cfg_edit_line:
    if not open_on_warn:
        for q in sys.argv:
            if q == 'e' or q == '-e': open_on_warn = True
    if open_on_warn: i7.npo(dg_cfg, cfg_edit_line)
    else: print("Put in an OPENONWARN in {:s} to open the CFG file, or type e/-e on the command line.".format(dg_cfg))

daily.read_main_daily_config()
dir_to_proc = ""

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg.isdigit():
        max_process = int(arg)
    elif re.search("^d(b)?[0-9]+$", arg):
        temp = re.sub("^d(b)?", "", arg)
        days_before_ignore = int(temp)
    elif arg == 'd' or arg == 'db': days_before_ignore = 0
    elif arg == 'dt' or arg == 't': max_process = -1
    elif arg == 'i':
        append_all_important()
        exit()
    elif arg == 'l': list_it = True
    elif arg[:2] == 's=': my_sect = arg[2:]
    elif arg[0] == 'l' and arg[1:].isdigit():
        list_it = True
        min_for_list = int(arg[1:])
    elif arg == 'da': dir_to_proc = daily_proc
    elif arg == 'dr': dir_to_proc = gdrive_proc
    elif arg[:3] == 's20': daily.lower_bound = arg[1:]
    elif arg[:3] == 'e20': daily.upper_bound = arg[1:]
    elif arg == 'e':
        os.system(dg_cfg)
        exit()
    elif arg == 'o': open_notes_after = True
    elif arg == 'pi': print_ignored_files = True
    elif arg == 'npi' or arg == 'pin': print_ignored_files = False
    elif arg == 'di': do_diff = True
    elif arg == 'ndi' or arg == 'din' or arg == 'dn' or arg == 'nd': do_diff = False
    elif arg == 'no' or arg == 'on': open_notes_after = False
    elif arg == 'v': verbose = True
    elif arg == 'q': verbose = False
    elif arg == 'a': just_analyze = True
    elif arg == '?': usage()
    else:
        usage("BAD PARAMETER {:s}".format(sys.argv[cmd_count]))
    cmd_count += 1

if just_analyze:
    analyze_to_proc()

if not dir_to_proc:
    my_cwd = os.getcwd()
    temp = daily.slashy_equals(my_cwd, [daily_dir, gdrive_dir])
    print(gdrive_dir)
    if temp:
        print("Trying current directory", my_cwd)
        dir_to_proc = my_cwd
    else:
        sys.exit("Need to specify a directory with -da or -dr or go to either writing-daily or google drive dir.")

os.chdir(dir_to_proc)

the_glob = glob.glob(dir_to_proc + "/20*.txt")
my_file_list = [u for u in the_glob if daily.valid_file(os.path.basename(u), dir_to_proc)]

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

for q in my_file_list:
    qbase = os.path.basename(q)
    temp_file = os.path.join(daily.wri_temp, qbase)
    if qbase < daily.lower_bound: continue
    if qbase > daily.upper_bound: continue
    if verbose: print("Processing", qbase)
    if list_it:
        get_list_data(q)
        continue
    processed += send_mapping(my_sect, q, processed < max_process or max_process == 0)
    if max_process and processed == max_process and not max_warning:
        max_warning = True
        if max_process > 1: print("Reached maximum. Stopped at file " + q)

if list_it:
    mins_ignored = 0
    for x in sorted(file_list, key=lambda y: len(file_list[y]), reverse=True):
        if len(file_list[x]) < min_for_list:
            mins_ignored += 1
            continue
        fl2 = [re.sub(".txt", "", x0) for x0 in file_list[x]]
        print("{:s} ({:d}) = {:s}".format(x, len(file_list[x]), ", ".join(fl2)))
    if mins_ignored: print(mins_ignored, "list entries below minimum ignored.")
    print(", ".join("{:s}={:d}".format(x, sect_lines[x]) for x in sorted(sect_lines, key=sect_lines.get, reverse=True)))
    exit()

if processed == 0 and max_process >= 0: print("Could not find anything to process for {:s}.".format(my_sect))

if len(change_list):
    print("Files still to process:", ', '.join(change_list))
if max_process > 0: print("Got {:d} of {:d} files.".format(processed, max_process))

if open_notes_after:
    for q in notes_to_open: i7.npo(q, notes_to_open[q], False, False)
