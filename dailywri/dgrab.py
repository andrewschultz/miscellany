# dgrab.py
#
# daily grab file: grab section from daily files (or other) and pipe it directly to notes files
#
# for instand #whau would go to welp-haunted file
#
# this looks at files in the to-proc directory
#
# usage: dgrab.py -da s=wh
#
# question: search for starting tabs in non-.ni files. What script for that?
#
# daily.py has the main engine details
# dgrab.txt has what maps where
# todo: utf8 to ascii, open first nonblank, open first bad header

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
import mytools as mt
from pathlib import Path

delete_empties = True

my_sect = ""
default_by_dir = i7.dir2proj(to_abbrev = True)
my_globs = []

dg_temp = "c:/writing/temp/dgrab-temp.txt"
dg_temp_2 = "c:/writing/temp/dgrab-temp-2.txt"
flat_temp = os.path.basename(dg_temp)

notes_to_open = defaultdict(int)

file_list = defaultdict(list)
sect_lines = defaultdict(int)

max_process = 0
open_notes = 0
days_before_ignore = 0 # this used to make sure we didn't hack into a current daily file, but now we have a processing subdirectory, we don't need that
min_for_list = 0

open_cluttered = False
just_analyze = False
look_for_lines = False
bail_without_copying = False
do_diff = True
verbose = False
open_notes_after = True
change_list = []
print_ignored_files = False
list_it = False

daily_dir = "c:/writing/daily"
daily_proc = daily.to_proc(daily_dir)
gdrive_dir = "c:/coding/perl/proj/from_drive"
gdrive_proc = daily.to_proc(gdrive_dir)
kdrive_dir = "c:/coding/perl/proj/from_keep"
kdrive_proc = daily.to_proc(kdrive_dir)

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
    print("sample usage:")
    print("  dgrab.py -da s=ut for processing Under They Thunder sections in daily files")
    print("  dgrab.py -dr s=vvff for processing VVFF sections in Google Drive files")
    print("  dgrab.py -dk s=ai for processing Ailihphilia sections in Google Keep files")
    exit()

def look_for_section(sec_to_find, the_files):
    if sec_to_find not in daily.mapping:
        print(sec_to_find, "not in mapping file dgrab.txt")
    else:
        print(sec_to_find, "in", daily.mapping[sec_to_find], daily.where_to_insert[sec_to_find])
    got_one = False
    my_token = "\\" + sec_to_find.lower()
    for f in sorted(the_files):
        with open(f) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.strip() == my_token:
                    mt.npo(f, line_count, bail=False)
                    got_one = True
                    break
    if not got_one:
        print("Found nothing.")
        exit()
    if sec_to_find not in daily.mapping:
        print(sec_to_find, "is not visible in the daily mapping. You may wish to open dgrab.txt.")
        sys.exit()
    with open(daily.mapping[sec_to_find]) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(daily.where_to_insert[sec_to_find]):
                mt.npo(daily.mapping[sec_to_find], line_count)
    print("Did not find", daily.where_to_insert[sec_to_find], "in", daily.mapping[sec_to_find])
    exit()

def orig_vs_proc(file_to_compare, ask_before = False):
    file_to_compare = os.path.basename(file_to_compare)
    if not file_to_compare.endswith(".txt"):
        file_to_compare += ".txt"
    global dir_to_proc
    if not dir_to_proc:
        print("Assuming daily_proc directory")
        dir_to_proc = daily_proc
    dir_to_orig = Path(dir_to_proc).parent
    proc_file = os.path.join(dir_to_proc, file_to_compare)
    orig_file = os.path.join(dir_to_orig, file_to_compare)
    if not ask_before or 'y' in input("Compare after editing?").lower().strip():
        mt.wm(orig_file, proc_file)
    else:
        print("OK, but if you want, wm", orig_file, proc_file)
    exit()

def attempt_line(poss_header):
    otls = glob.glob("c:/writing/*.otl")
    poss_matches = 0
    for f in otls:
        fb = os.path.basename(f)
        with open(f) as file:
            for (line_count, line) in enumerate (file, 1):
                if line.startswith("\\" + poss_header + '='):
                    poss_matches += 1
                    print("  possible match {} for {} at line {} of file {}: {}".format(poss_matches, poss_header, line_count, fb, line.strip()))
                    print("  suggested configuration line for dgrab.txt: MAPPING={},{},{}".format(poss_header, f, line.strip()))
    return poss_matches

def analyze_to_proc():
    sections_left = defaultdict(int)
    first_file_with_section = defaultdict(str)
    files_to_verify = glob.glob(daily_proc + "/*.*")
    err_flagged = defaultdict(int)
    bad_header_count = 0
    file_to_open = ""
    lines_to_open = []
    last_line = -1
    for this_daily in files_to_verify:
        if this_daily.endswith(".bak"):
            print("Backup file", this_daily, "should probably be deleted.")
            continue
        with open(this_daily) as file:
            in_section = False
            daily_basename = os.path.basename(this_daily)
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("#"): continue
                if line.startswith("\\"):
                    in_section = True
                    ll = line.lower().strip()[1:]
                    if ll not in daily.mapping and ll not in err_flagged:
                        bad_header_count += 1
                        print("Bad header #{:2d}:".format(bad_header_count), ll, "line", line_count, daily_basename)
                        if look_for_lines:
                            if not attempt_line(ll):
                                print("Could not find suggestions.")
                        err_flagged[ll] = True
                    sections_left[ll] += 1
                    if ll not in first_file_with_section:
                        first_file_with_section[ll] = daily_basename
                elif not line.strip():
                    in_section = False
                elif not in_section:
                    if not file_to_open or file_to_open == this_daily:
                        file_to_open = this_daily
                        if line_count - last_line > 1:
                            lines_to_open.append(line_count)
                            print("Potential cleanup at file {} line {}: {}".format(this_daily, line_count, line.strip()))
                        last_line = line_count
    if not bad_header_count: print("Hooray! You have no bad headers.")
    sections_to_sort = 0
    for x in sorted(sections_left, key=lambda x: (-sections_left[x], x), reverse=True):
        sections_to_sort += 1
        print("{:2d}: {:15s} {:2d} time{} 1st file={}".format(sections_to_sort, x, sections_left[x], "s" if sections_left[x] > 1 else " ", first_file_with_section[x]))
    if not sections_to_sort: print("Hooray! You have no sections to shuffle.")
    if open_cluttered and lines_to_open:
        print("Look to clean up {} line{}: {}".format(len(lines_to_open), 's' if len(lines_to_open) != 1 else '', ','.join([str(x) for x in lines_to_open[::-1]])))
        mt.npo(file_to_open, lines_to_open[-1], bail=False)
        orig_vs_proc(file_to_open, ask_before = True)
    elif open_cluttered:
        print("No files to de-clutter. Nice going.")
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

def file_len(fname):
    with open(fname) as f:
        for (i, l) in enumerate(f, 1):
            pass
    return i

def send_mapping(sect_name, file_name, change_files = False):
    temp_time = os.stat(file_name)
    fn = os.path.basename(file_name)
    time_delta = time.time() - temp_time.st_mtime
    my_reg = daily.regex_sect[sect_name]
    my_reg_comment = daily.regex_comment[sect_name]
    found_sect_name = False
    in_sect = False
    file_remain_text = ""
    sect_text = ""
    if sect_name not in daily.mapping: sys.exit("No section name {:s} in the general mappings file dgrab.txt. Bailing on file {:s} before even running. Run with (-)e to open config.".format(sect_name, file_name))
    # print(sect_name, "looking for", my_reg, "in", file_name)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            lls = line.lower().strip()
            if re.search(r"{}\b".format(my_reg), line):
                if found_sect_name:
                    print("WARNING -- (no information lost) 2 section types similar to", sect_name, "from", my_reg, "line", found_sect_name, line_count, file_name)
                if verbose: print(file_name, "line", line_count, "has {:s} section".format("extra" if found_sect_name else "a"), sect_name)
                if not re.search(r'^\\{}\n'.format(sect_name), lls): print("    NOTE: alternate section name from {:s} is {:s} line {} in {}".format(sect_name, line.strip(), line_count, file_name))
                found_sect_name = line_count
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
    if not found_sect_name:
        if verbose:
            print("No section text was found in", fn, "for", sect_name)
        return False
    if not sect_text:
        if delete_empties:
            print("Empty section found. Deleting.")
        else:
            print("Empty section found but not deleting.")
            return
    if not change_files:
        global change_list
        change_list.append(fn)
        return False
    f = open(dg_temp, "w")
    f.write(file_remain_text)
    f.close()
    to_file = daily.mapping[sect_name]
    remain_written = False
    if sect_text:
        print("Found", sect_name, "in", file_name, "to add to", to_file)
    else:
        print("Not adding to", to_file, "but deleting from", file_name)
        if bail_without_copying:
            print("Actually, I would, if I didn't bail without copying.")
        else:
            copy(dg_temp, file_name)
        sys.exit()
    if to_file not in notes_to_open:
        notes_to_open[to_file] = file_len(to_file)
    if daily.where_to_insert[sect_name]:
        print("Specific insert token found for {:s}, inserting there in {:s}.".format(sect_name, to_file))
        write_next_blank = False
        w2i = daily.where_to_insert[sect_name]
        f = open(dg_temp_2, "w")
        with open(to_file) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.lower().strip() == w2i.lower():
                    f.write(line)
                    if line.startswith("\\"):
                        print("Section to append starts at line", line_count)
                        write_next_blank = True
                    else:
                        f.write("<from daily/keep file {:s}>\n".format(file_name) + sect_text)
                        remain_written = True
                    continue
                if write_next_blank and not line.strip():
                    print("Will start writing at line", line_count)
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
        if not remain_written: sys.exit("Text chunk for {:s} ~ {:s} not written to {:s}. Bailing.".format(sect_name, w2i, to_file))
        f.close()
        #sys.exit("Ok done with test")
    else:
        print("Appending to", to_file)
        f = open(to_file, "a")
        f.write("\n<from daily/keep file {:s}>\n".format(file_name) + sect_text)
        f.close()
    if do_diff:
        if os.path.exists(dg_temp_2): mt.wm(to_file, dg_temp_2)
        mt.wm(file_name, dg_temp)
    if bail_without_copying:
        print("Bailing before copying back over")
        print(dg_temp, file_name)
        print(dg_temp_2, to_file)
        sys.exit()
    if not filecmp.cmp(dg_temp, file_name): copy(dg_temp, file_name)
    if os.path.exists(dg_temp_2) and not filecmp.cmp(dg_temp_2, to_file):
        copy(dg_temp_2, to_file)
        os.remove(dg_temp_2)
    if os.path.exists(dg_temp): os.remove(dg_temp)
    return True

#
# start main program
#

daily.read_section_sort_cfg()
daily.read_main_daily_config()
dir_to_proc = ""

section_to_find = ''

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg.isdigit():
        max_process = int(arg)
    elif re.search("^d(b)?[0-9]+$", arg):
        temp = re.sub("^d(b)?", "", arg)
        days_before_ignore = int(temp)
    elif arg[:2] == 'o:' or arg[:2] == 'o=':
        section_to_find = arg[2:]
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
    elif arg[:3] == 'l20': daily.lower_bound = arg[1:]
    elif arg[:3] == 'u20': daily.upper_bound = arg[1:]
    elif re.search(r'^m20[0-9]{6}$', arg):
        orig_vs_proc(arg[1:])
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
    elif re.search('^a[lc]+', arg):
        just_analyze = True
        look_for_lines = 'l' in arg
        open_cluttered = 'c' in arg
    elif arg == '?': usage()
    else:
        usage("BAD PARAMETER {:s}".format(sys.argv[cmd_count]))
    cmd_count += 1

if just_analyze:
    analyze_to_proc()
    exit()

if not dir_to_proc:
    my_cwd = os.getcwd()
    temp = daily.is_dir_or_proc(my_cwd, [daily_dir, gdrive_dir, kdrive_dir])
    print(temp)
    if temp:
        print("Trying current directory", my_cwd)
        dir_to_proc = my_cwd
    else:
        sys.exit("Need to specify a directory with -da (daily) or -dr (drive) or go to either writing-daily or google drive dir.")

if "to-proc" not in dir_to_proc:
    dir_to_proc = os.path.join(dir_to_proc, "to-proc")

os.chdir(dir_to_proc)

the_glob = glob.glob(dir_to_proc + "/20*.txt")
my_file_list = [u for u in the_glob if daily.valid_file(os.path.basename(u), dir_to_proc)]

if section_to_find:
    look_for_section(section_to_find, the_glob)
    exit()

if not my_sect:
    if not default_by_dir or default_by_dir not in daily.mapping:
        print("Going with default section defined in {:s}: {:s}.{:s}".format(daily.flat_cfg, daily.default_sect, (" {:s} is defined by the PWD but is not in the {:s} mapping.".format(default_by_dir, daily.flat_cfg) if default_by_dir else "")))
        my_sect = daily.default_sect
    else:
        print("Going with default section defined by directory you're in {:s}.".format(default_by_dir))
        my_sect = default_by_dir

processed = 0

max_warning = False
if max_process == -1: print("Running test to cull all eligible files.")

for q in my_file_list:
    qbase = os.path.basename(q)
    temp_file = os.path.join(daily.wri_temp, qbase)
    if q.endswith(".bak"):
        print("WARNING backup file", q)
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

if processed == 0:
    print("Could not find anything to process for {:s}.".format(my_sect))
else:
    print("Processed", processed, "total file(s)")

if len(change_list):
    print("Files still to process:", ', '.join(change_list))
if max_process > 0: print("Got {:d} of {:d} files.".format(processed, max_process))

if open_notes_after:
    for q in notes_to_open: mt.npo(q, notes_to_open[q], False, False)
