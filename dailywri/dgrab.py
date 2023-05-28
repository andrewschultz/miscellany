# dgrab.py
#
# daily grab file: grab section from daily files (or other) and pipe it directly to notes files
#
# for instand #whau would go to welp-haunted file
#
# this looks at files in the to-proc directory
#
# usage: dgrab.py -da -nd s=wh
# usage: dgrab.py a # just analyzes
# usage: dgrab.py ld s=critical pulls critical section from latest daily (lf from latest file in other directories)
#
# (don't show differences)
#
# question: search for starting tabs in non-.ni files. What script for that?
#
# daily.py has the main engine details
# dgrab.txt has what maps where
# todo: utf8 to ascii, open first nonorphan, open first bad header
#
# note: dga.bat (section name) copies the section name over
#
# todo: insert stuff at start or end of output file/section

import codecs
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
import pendulum
import colorama

delete_empties = True

my_sect = ""
default_by_dir = i7.dir2proj(to_abbrev = True)
my_globs = []

dg_temp = "c:/writing/temp/dgrab-temp.txt"
dg_temp_2 = "c:/writing/temp/dgrab-temp-2.txt"
dg_preview = "c:/writing/temp/dgrab-preview.txt"
flat_temp = os.path.basename(dg_temp)
move_log = "c:/writing/temp/dgrab-move-log.txt"

file_list = defaultdict(list)
sect_lines = defaultdict(int)
blank_sect = defaultdict(int) # not orphan_sect since this is literally the blank stuff we want to dump elsewhere, and the section name may change
bad_bumpers = set()

max_process = 0
open_notes = 0
days_before_ignore = 0 # this used to make sure we didn't hack into a current daily file, but now we have a processing subdirectory, we don't need that
min_for_list = 0
total_lines_moved = 0

force_timestamp = False
open_cluttered = False
just_analyze = False
look_for_lines = False
bail_without_copying = False
do_diff = False
verbose = False
open_notes_after = True
change_list = []
print_ignored_files = False
list_it = False
print_commands = False
open_to_after = False

analyze_orphans = False
look_for_orphan = False
append_importants = False
important_test = True
latest_file_only = False
preview_moved_text = False
preview_any_yet = False
launch_backup_log = True
section_dump_yet = False
duplicate_bumpers = False

dir_search_flag = daily.TOPROC

search_ary = ""

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
    print("1o/ao = first orphan or analyze orphans")
    print("noa = no open after")
    print("pc = print suggested commands")
    print("ld = latest daily only (not to-proc), lf = latest file from this/chosen directory")
    print("pre = preview only")
    print("")
    print("sample usage:")
    print("  dgrab.py -da s=ut 5 for processing 5 Under They Thunder sections in daily files")
    print("  dgrab.py -dr s=vvff for processing VVFF sections in Google Drive files")
    print("  dgrab.py -dk s=ai for processing Ailihphilia sections in Google Keep files")
    print("  dga.bat s=my processes all sections labeled my for daily/drive/keep.")
    sys.exit()

def cmd_param_of(my_dir):
    if 'daily' in my_dir: return "-da"
    if 'keep' in my_dir: return "-dk"
    if 'drive' in my_dir: return "-dr"
    return "-?"

def find_section_in_daily(sec_to_find, the_files):
    print("NOTE: if you want to open the original big list document, use o= instead.")
    if sec_to_find not in daily.mapping:
        print(sec_to_find, "not in mapping file dgrab.txt")
    else:
        print(sec_to_find, "in", daily.mapping[sec_to_find], daily.where_to_insert[sec_to_find])
    got_one = False
    my_token = "\\" + sec_to_find.lower()
    for f in sorted(the_files):
        if got_one: break
        with open(f) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.strip() == my_token:
                    mt.npo(f, line_count, bail=False)
                    got_one = True
                    break
    if not got_one:
        print("Found nothing.")
        sys.exit()
    if sec_to_find not in daily.mapping:
        print(sec_to_find, "is not visible in the daily mapping. You may wish to open dgrab.txt.")
        sys.exit()
    with open(daily.mapping[sec_to_find]) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(daily.where_to_insert[sec_to_find]):
                mt.npo(daily.mapping[sec_to_find], line_count)
    print("Did not find", daily.where_to_insert[sec_to_find], "in", daily.mapping[sec_to_find])
    sys.exit()

def find_first_orphan(the_files):
    for f in sorted(the_files):
        should_start_outline = False
        with open(f) as file:
            for (line_count, line) in enumerate(file, 1):
                if not line.strip():
                    should_start_outline = True
                    continue
                if should_start_outline and not line.startswith("\\"):
                    mt.npo(f, line_count)
                should_start_outline = False
    print("No orphaned/orphan lines! Yay!")
    sys.exit()

def find_all_orphans(the_files):
    if not len(the_files):
        sys.exit("No files to look through!")
    total_orphans = total_sections = orphan_files = okay_files = 0
    for f in sorted(the_files):
        in_section = in_orphan_section = False
        orphan_lines = orphan_sections = 0
        with open(f) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("\\"):
                    in_section = True
                    continue
                if not line.strip():
                    in_section = in_orphan_section = False
                    continue
                if in_section:
                    continue
                orphan_lines += 1
                if not in_orphan_section:
                    orphan_sections += 1
                    in_orphan_section = True
        if orphan_lines:
            print("{} has {} orphan lines in {} sections.".format(f, orphan_lines, orphan_sections))
            orphan_files += 1
            total_sections += orphan_sections
            total_orphans += orphan_lines
        else:
            okay_files += 1
    if not orphan_files:
        print("No files with orphan lines. All {} are sorted. Well done!".format(len(the_files)))
        sys.exit()
    if okay_files:
        print(okay_files, "files had no orphans.")
    print("{} total files with {} lines in {} sections. Open the first with -1b.".format(orphan_files, total_orphans, total_sections))
    sys.exit()

def open_destination_doc(sec_to_find, look_for_end = True):
    print("NOTE: if you want to open in dailies, use od= instead.")
    if sec_to_find not in daily.mapping:
        print(sec_to_find, "is not visible in the daily mapping. You may wish to open dgrab.txt.")
        sys.exit()
    if sec_to_find not in daily.where_to_insert:
        sys.exit("Could not find section for {} in daily mapping file. Open dgrab.txt to check.".format(my_section))
    print(sec_to_find, "in", daily.mapping[sec_to_find], daily.where_to_insert[sec_to_find])
    got_one = False
    temp_open_line = 0
    with open(daily.mapping[sec_to_find]) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(daily.where_to_insert[sec_to_find]):
                if not look_for_end:
                    mt.npo(daily.mapping[sec_to_find], line_count)
                temp_open_line = line_count
                continue
            if temp_open_line:
                temp_open_line += 1
                if not line.strip():
                    mt.npo(daily.mapping[sec_to_find], line_count)
    if temp_open_line:
        print("Section {} ended the file.".format(daily.where_to_insert[sec_to_find]) if sec_to_find in daily.where_to_insert and daily.where_to_insert[sec_to_find] else "This may be a file without sections.", "We will open at the end.")
        mt.npo(daily.mapping[sec_to_find], temp_open_line)
    print("Did not find", daily.where_to_insert[sec_to_find], "in", daily.mapping[sec_to_find])
    sys.exit()

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
    sys.exit()

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

def analyze_to_proc(my_dir):
    sections_left = defaultdict(int)
    first_file_with_section = defaultdict(str)
    os.chdir(my_dir)
    files_to_verify = mt.dailies_of(my_dir)
    err_flagged = defaultdict(int)
    bad_header_count = 0
    file_to_open = ""
    lines_to_open = []
    last_line = -1
    last_header = ""
    section_start = False
    print("Analyzing section headers in", my_dir)
    for this_daily in files_to_verify:
        if this_daily.endswith(".bak"):
            print("Backup file", this_daily, "should probably be deleted.")
            continue
        with open(this_daily) as file:
            in_section = False
            daily_basename = os.path.basename(this_daily)
            if verbose: print(daily_basename)
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("#"): continue
                if section_start:
                    if not line.strip():
                        blank_sect[last_header] += 1
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
                    last_header = ll
                    section_start = True
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
        blanks_string = "" if x not in blank_sect else "{} blank{} ".format(blank_sect[x], "s" if blank_sect[x] > 1 else "")
        print("{:2d}: {:15s} {:2d} time{} {}1st file={}".format(sections_to_sort, x, sections_left[x], "s" if sections_left[x] > 1 else " ", blanks_string, first_file_with_section[x]))
    if print_commands:
        for x in sorted(sections_left, key=lambda x: (-sections_left[x], x), reverse=True):
            print("dgrab.py {} s={}".format(cmd_param_of(my_dir), x))
    if not sections_to_sort: print("Hooray! You have no sections to shuffle.")
    if open_cluttered and lines_to_open:
        print("Look to clean up {} line{}: {}".format(len(lines_to_open), 's' if len(lines_to_open) != 1 else '', ','.join([str(x) for x in lines_to_open[::-1]])))
        mt.npo(file_to_open, lines_to_open[-1], bail=False)
        orig_vs_proc(file_to_open, ask_before = True)
    elif open_cluttered:
        print("No files to de-clutter. Nice going.")
    sys.exit()

def append_one_important(my_file, my_dir):
    important_file = os.path.join(my_dir, "important.txt")
    important_file_2 = os.path.join(my_dir, "important2.txt")
    my_file_back = os.path.join(my_dir, "my-file-backup.txt")
    if not os.path.exists(important_file):
        print("Create", important_file, "before continuing.")
        sys.exit()
    important_string = "\n\nIMPORTANT STRING FOR FILE {0}...====\n".format(os.path.join(my_dir, my_file))
    f = open(my_file_back, "w")
    with open(important_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.strip() == important_string.strip():
                print("Important stuff from", my_file, "already copied over.")
                return 0
    in_important = False
    ever_important = False
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("IMPORTANT") and len(line) < 20:
                ever_important = True
                in_important = True
                continue
            if line.startswith("UNIMPORTANT") and len(line) < 20:
                in_important = False
                continue
            if in_important:
                important_string += line
            else:
                f.write(line)
    f.close()
    copy(important_file, important_file_2)
    f = open(important_file_2, "a")
    f.write(important_string)
    f.close()
    if not ever_important:
        os.remove(my_file_back)
        print("Nothing important in", my_file)
        return 0
    if important_test:
        print("Testing important. Run with -i to actually do stuff.")
        mt.wm(my_file, my_file_back)
        mt.wm(important_file, important_file_2)
        os.remove(my_file_back)
        os.remove(important_file_2)
        sys.exit()
    mt.wm(my_file, my_file_back)
    mt.wm(important_file, important_file_2)
    copy(my_file_back, my_file)
    copy(important_file_2, important_file)
    os.remove(my_file_back)
    os.remove(important_file_2)
    return 1

def search_regex_in_section(section_name, regex, my_dir):
    got_one = False
    for a in mt.dailies_of(my_dir):
        my_section = ""
        with codecs.open(a, mode='r', encoding='utf-8', errors='replace') as file:
            for (line_count, line) in enumerate (file, 1):
                if line.startswith("\\"):
                    my_section = line[1:].strip()
                    continue
                if not line.strip():
                    my_section = ""
                if section_name == my_section:
                    if re.search(r'{}'.format(regex), line, re.IGNORECASE):
                        got_one = True
                        print(a, line_count, line.strip())
    if not got_one:
        print("Found no regex ({})".format(regex), "in section", "\\" + section_name, "in dir", my_dir)
    sys.exit()

def append_all_important(my_dir):
    appended = 0
    for a in mt.dailies_of(my_dir):
        appended += append_one_important(a, my_dir)
    print(appended, "total important sections appended")
    sys.exit()

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
    global section_dump_yet
    if sect_name == 'lim':
        alt_section = ''
        alt_section_reject = True
    else:
        alt_section = ''
        alt_section_reject = False
    last_line = ''
    alt_section_found = in_alt_section = False
    alt_lines = 0
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
                if verbose:
                    print(file_name, "line", line_count, "has {:s} section".format("extra" if found_sect_name else "a"), sect_name)
                if not re.search(r"^\\{}$".format(sect_name), lls):
                    print("    NOTE: alternate section name from {:s} is {:s} line {} in {}".format(sect_name, line.strip(), line_count, file_name))
                found_sect_name = line_count
                in_sect = True
                if change_files:
                    print(sect_name, "section found in {}, parsing begins...".format(fn))
                continue
            if not line.strip():
                in_alt_section = False
                in_sect = False
            if in_alt_section:
                alt_lines += 1
            if not alt_section_found:
                if line.strip() == '\\' + alt_section:
                    alt_section_found = True
                    in_alt_section = True
            if in_sect:
                if line.startswith("\\"):
                    sys.exit("Being pedantic that " + file_name + " has bad sectioning. Bailing.")
                if line == mt.daily_warning_bumper:
                    pass
                else:
                    sect_text += line
            elif re.search(my_reg_comment, lls):
                sect_text += line
            else:
                if line.strip() or last_line.strip():
                    file_remain_text += line
                last_line = line
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
            return True
        else:
            print("Empty section found but not deleting.")
            return False
    if not change_files:
        global change_list
        change_list.append(fn)
        return False
    f = open(move_log, "a")
    f.write("Moving over {} lines in section {} for file {} on {}.\n".format(sect_text.count("\n"), sect_name, file_name, my_date))
    f.close()
    if alt_section_reject and alt_section_found:
        print("Alt section of {} ({}) found. Not copying over ... yet.".format(sect_name, alt_section))
        print("Lines in {}: {}.".format(sect_name, sect_text.count('\n')))
        print("Lines in {}: {}.".format(alt_section, alt_lines))
        return False
    if preview_moved_text:
        if sect_text:
            global preview_any_yet
            if preview_any_yet:
                f = open(dg_preview, "a")
            else:
                f = open(dg_preview, "w")
                preview_any_yet = True
            f.write("======================={}\n".format(file_name))
            f.write(sect_text)
            f.close()
            return True
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
    if open_to_after:
        mt.add_post_open(to_file, file_len(to_file))
    if not section_dump_yet:
        g = open(dg_backup_log, "w")
        g.write("BACKUP LOG (disable with -bln)\n\nResults of dump for section {} on {}:\n\n".format(my_sect, my_date))
        g.close()
        section_dump_yet = True
    g = open(dg_backup_log, "a")
    g.write("Results of {} section dump from {} to {}:\n".format(sect_name, file_name, to_file))
    g.write(sect_text + "\n")
    g.close()
    global total_lines_moved
    total_lines_moved += sect_text.count("\n")
    if sect_text.startswith("**"):
        total_lines_moved -= 1
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
                        duplicate_bumpers = False
                    else:
                        f.write("<from daily/keep file {:s}>\n".format(file_name) + sect_text)
                        remain_written = True
                    continue
                if write_next_blank and not line.strip():
                    print("Will start writing at line", line_count)
                    if sect_name in daily.timestamps or force_timestamp:
                        f.write('# start {} {}\n'.format(fn, my_date_for_file))
                    f.write(sect_text)
                    f.write("\n")
                    write_next_blank = False
                    remain_written = True
                    continue
                if not line.startswith(mt.daily_warning_bumper):
                    f.write(line)
                    if line.startswith("**") and (duplicate_bumpers or line.strip() not in bad_bumpers):
                        print(colorama.Fore.RED + "WARNING: unusual daily warning bumper {} line {}: {}".format(fn, line_count, line.strip()) + colorama.Style.RESET_ALL)
                        bad_bumpers.add(line.strip())
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
    elif arg[:3] == 'do:' or arg[:3] == 'od:' or arg[:3] == 'od=' or arg[:3] == 'do=':
        section_to_find = arg[3:] #find_section_in_daily
    elif arg[:2] == 'o:' or arg[:2] == 'o=':
        section_to_find = arg[2:]
        open_destination_doc(section_to_find)
    elif arg == 'd' or arg == 'db': days_before_ignore = 0
    elif arg == 'dt' or arg == 't': max_process = -1
    elif arg == 'i':
        append_importants = True
        important_test = False
    elif arg == 'it' or arg == 'ti':
        append_importants = True
        important_test = True
    elif arg == 'l': list_it = True
    elif arg in ( 'bl', 'lb' ):
        launch_backup_log = True
    elif mt.alpha_match(arg, 'bln'):
        launch_backup_log = False
    elif arg == 'ld':
        latest_file_only = True
        dir_to_proc = daily_proc
    elif arg == 'lf': latest_file_only = True
    elif arg == 'pre': preview_moved_text = True
    elif arg[:2] == 's=': my_sect = arg[2:]
    elif arg[0] == 'l' and arg[1:].isdigit():
        list_it = True
        min_for_list = int(arg[1:])
    elif arg == 'da': dir_to_proc = daily_proc
    elif arg == 'dr' or arg == 'dd': dir_to_proc = gdrive_proc
    elif arg == 'dk': dir_to_proc = kdrive_proc
    elif arg[:3] == 'l20': daily.lower_bound = arg[1:]
    elif arg[:3] == 'u20': daily.upper_bound = arg[1:]
    elif re.search(r'^m20[0-9]{6}$', arg):
        orig_vs_proc(arg[1:])
    elif arg == 'e':
        os.system(daily.dg_cfg)
        sys.exit()
    elif arg in ( 'fts', 'ts', 'ft' ):
        force_timestamp = True
    elif arg in ( 'ftn', 'nft', 'ntf' ):
        force_timestamp = False
    elif arg == 'o': open_notes_after = True
    elif arg == 'pi': print_ignored_files = True
    elif arg == 'npi' or arg == 'pin': print_ignored_files = False
    elif arg == 'di': do_diff = True
    elif arg == 'ndi' or arg == 'din' or arg == 'dn' or arg == 'nd': do_diff = False
    elif arg == 'no' or arg == 'on': open_notes_after = False
    elif arg == 'v': verbose = True
    elif arg == 'q': verbose = False
    elif arg == '1o': look_for_orphan = True
    elif arg == 'ao': analyze_orphans = True
    elif arg == 'a': just_analyze = True
    elif arg == 'pc': print_commands = True
    elif arg == 'oa': open_to_after = True
    elif arg == 'noa': open_to_after = False
    elif arg[0:3] == 'ss:' or arg[0:3] == 'ss=':
        dir_search_flag = daily.TOPROC
        search_ary = arg[3:].split(",")
        if len(search_ary) != 2:
            sys.exit("Searching must have a section and a regex separated by a comma.")
    elif arg[0:3] == 'sr:' or arg[0:3] == 'sr=':
        dir_search_flag = daily.ROOT
        search_ary = arg[3:].split(",")
        if len(search_ary) != 2:
            sys.exit("Searching must have a section and a regex separated by a comma.")
    elif arg[0:3] == 'sb:' or arg[0:3] == 'sb=':
        dir_search_flag = daily.BACKUP
        search_ary = arg[3:].split(",")
        if len(search_ary) != 2:
            sys.exit("Searching must have a section and a regex separated by a comma.")
    elif re.search('^a[lc]+', arg):
        just_analyze = True
        look_for_lines = 'l' in arg
        open_cluttered = 'c' in arg
    elif arg == 'dub':
        duplicate_bumpers = True
    elif arg == '?': usage()
    else:
        usage("BAD PARAMETER {:s}".format(sys.argv[cmd_count]))
    cmd_count += 1

if not dir_to_proc:
    my_cwd = os.getcwd()
    temp = daily.is_dir_or_proc(my_cwd, [daily_dir, gdrive_dir, kdrive_dir])
    print(temp)
    if temp:
        print("Trying current directory", my_cwd)
        dir_to_proc = my_cwd
    else:
        if latest_file_only:
            print("Forcing to", daily_proc, "for last daily file")
            dir_to_proc = daily_proc
        else:
            sys.exit("Need to specify a directory with -da (daily) or -dr (drive) or go to either writing-daily or google drive dir.")

if "to-proc" not in dir_to_proc:
    dir_to_proc = os.path.join(dir_to_proc, "to-proc")

dir_to_proc = os.path.normpath(dir_to_proc)

if dir_search_flag == daily.ROOT:
    dir_to_proc = os.path.join(dir_to_proc, '..')
    print("Switching to", dir_to_proc)
elif dir_search_flag == daily.BACKUP:
    dir_to_proc = os.path.join(dir_to_proc, '..', 'backup')
    print("Switching to", dir_to_proc)

os.chdir(dir_to_proc)

if append_importants:
    append_all_important(dir_to_proc)
    sys.exit()

if just_analyze:
    analyze_to_proc(dir_to_proc)
    sys.exit()

the_glob = glob.glob(dir_to_proc + "/20*.txt")
my_file_list = [u for u in the_glob if daily.valid_file(os.path.basename(u), dir_to_proc)]

if latest_file_only:
    parent_dir = Path(dir_to_proc).parent.absolute()
    print("ORIG:", parent_dir)
    the_glob = glob.glob(str(parent_dir) + "/20*.txt")
    if not len(my_file_list):
        sys.exit("No valid files found in {}.".format(parent_dir))
    my_file_list = [the_glob[-1]]


if analyze_orphans:
    find_all_blanks(the_glob)
    sys.exit()

if look_for_orphan:
    find_first_blank(the_glob)
    sys.exit()

if section_to_find:
    find_section_in_daily(section_to_find, the_glob)
    sys.exit()

if len(search_ary):
    search_regex_in_section(search_ary[0],search_ary[1], dir_to_proc)
    sys.exit()

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

print("REMINDER: -di means to do diff. -ndi means not to. The default is not to do differences. You can break during differences after seeing stuff is added.")

my_date = pendulum.now().format("YYYY/MM/DD HH:mm:ss")
my_date_for_file = pendulum.now().format("YYYY-MM-DD-HH-mm-ss")
dg_backup_log = "c:/writing/temp/dgrab-backup-log-{}-{}.txt".format(my_sect, my_date_for_file)

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
        continue

if preview_moved_text:
    mt.npo(dg_preview)

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
    sys.exit()

if processed == 0:
    print("Could not find anything to process for {} in {}.".format(my_sect, dir_to_proc))
else:
    print("Processed", processed, "total file{}{}".format(mt.plur(processed), '' if processed == 1 else ", {} lines".format(total_lines_moved)))

if len(change_list):
    print("{} File{} still to process, probably since we had a ceiling on the number to generate:".format(len(change_list), 's' if len(change_list) > 1 else ''), ', '.join(change_list))

if max_process > 0: print("Got {:d} of {:d} files.".format(processed, max_process))

if launch_backup_log:
    if section_dump_yet:
        mt.file_in_browser(dg_backup_log)
    else:
        print("No backup log file written, since nothing was extracted from daily files.")

if open_to_after:
    mt.postopen_files()
