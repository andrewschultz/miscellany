# dff.py: daily file find
#
# sorts notes in daily files e.g. moves #RoL to RoL
# todo: pull COMMENTS from DDD
# todo: in a = b lines, flag both a and b and get all the comments. Have actual_info array along with my_comment_list
#
# todo: ignore spacing e.g. if there are only blanks added/subtracted, we just search arrays [x for x in f.readlines if x.strip()] then compare

import daily
import codecs
import os
import re
import sys
from collections import defaultdict
from math import gcd
from functools import reduce
import mytools as mt
from glob import glob
from filecmp import cmp
from shutil import copy
import colorama
import pathlib
import ctypes
import pendulum
import pyperclip

DEFAULT_SORT = daily.DAILY

max_consecutive_blank_section_lines = 10
max_adjustment_summary = 100

dff_clipboard = "c:/writing/temp/dff-clipboard.txt"

force_backup = "c:/writing/temp/dff-forcecopy-backup.txt"
test_file_index = 0
daily_strings = ['daily', 'drive', 'keep']

what_to_sort = DEFAULT_SORT

my_cwd = os.getcwd()
colorama.init()

dir_search_flag = daily.TOPROC

cwd_parts = [ x.lower() for x in pathlib.PurePath(my_cwd).parts ]

if 'daily' in cwd_parts:
    print("Sorting DAILY stuff")
    what_to_sort = daily.DAILY
elif 'keep' in cwd_parts:
    print("Sorting KEEP stuff")
    what_to_sort = daily.KEEP
elif 'drive' in cwd_parts:
    print("Sorting DRIVE stuff")
    what_to_sort = daily.DRIVE
else:
    what_to_sort = DEFAULT_SORT
    print("The current working directory gave no information what to sort, so we are reverting to a default of", daily_strings[what_to_sort])

force_copy = False

resort_already_sorted = True

sort_proc = False

# this should go in a config file later
edit_blank_to_blank = True
one_word_names = True
open_raw = False
only_one = True
bail_after_unchanged = False
see_drive_files = True
test_no_copy = True
copy_then_test = False
only_list_files = False
show_differences = True
my_min_file = "20170000.txt"
my_max_file = "21000000.txt"
verbose = False
show_blank_to_blank = True
edit_blank_to_blank = True
run_test_file = False
ignore_duplicate = False
header_verify = False

force_speech_to_text = False

show_total_jumps = False

pop_up_if_clean = False

read_most_recent = False

bail_on_warnings = True

ask_to_copy_back = False

show_stat_numbers = False

space_to_tab_conversion = False
clipboard_file = False

last_file_first = True
ignore_limerick_headers_in_stats = True

keep_directive_text = False

RUN_NO_APOSTROPHE = 0
RUN_LATEST_APOSTROPHE = 1
RUN_ALL_APOSTROPHE = 2

run_apostrophe_check = RUN_NO_APOSTROPHE

STATS_EXT_OFF = 0
STATS_EXT_ALPHABETICALLY = 1
STATS_EXT_BY_SECTION_SIZE = 2
STATS_EXT_BY_LINES = 3
STATS_EXT_BY_AVERAGE = 4
show_ext_stats = STATS_EXT_OFF

raw_drive_dir = "c:/coding/perl/proj/from_drive"
proc_drive_dir = "c:/coding/perl/proj/from_drive/to-proc"
raw_keep_dir = "c:/coding/perl/proj/from_keep"
proc_keep_dir = "c:/coding/perl/proj/from_keep/to-proc"
raw_daily_dir = "c:/writing/daily"
proc_daily_dir = "c:/writing/daily/to-proc"
raw_glob = "raw-*.txt"
dailies_glob = "20*.txt"
important_file = "{0}/important.txt".format(raw_drive_dir)

valid_procs = [proc_drive_dir, proc_keep_dir, proc_daily_dir]

comment_cfg = "c:/writing/scripts/dff.txt"

cmds = defaultdict(str)
cmds['pal'] = "ni no ai"
cmds['ana'] = "ni an"
cmds['vvff'] = "ni no vv"
cmds['spo'] = "np spopal"

suffixes = defaultdict(str)
section_words = defaultdict(str)
prefixes = defaultdict(str)
delete_marker = defaultdict(str)
fixed_marker = defaultdict(str)
prority_sort = defaultdict(int)
header_tweak = defaultdict(str)
no_names = defaultdict(bool)
apostrophe_check = defaultdict(str)

empty_to_protect = defaultdict(bool)
protect_yes_force = False
protect_no_force = False

block_move_from_cfg = defaultdict(set)
local_block_move = set()
local_unblock_move = set()

sect_move = defaultdict(lambda: defaultdict(int))

class suffix_search:
    def __init__(self, name, out_section):
        search_type_cue = out_section[-1]
        self.text_to_search = name
        self.search_type = SUFFIX_EXACT
        self.out_section = out_section[:-1]
        if search_type_cue == '!':
            self.search_type = SUFFIX_EXACT
        elif search_type_cue == '@':
            self.search_type = SUFFIX_ANYWHERE
        elif search_type_cue == '&':
            self.search_type = SUFFIX_START
        else:
            self.out_section = out_section

def examples():
    print("dgrab.py s=pbn would actually sort things afterwards.")
    print("dff.py sr/st force sorting in regular or to-proc directory.")
    print("dff.py ld/rd sorts first file back in regular/to-proc directory but doesn't copy. Adding a q verifies changes.")
    print("dff.py cq/qc copies back.")
    print("dff.py fb specifies maximum files back.")
    print("dff.py ddq or kdq copies back when looking ad drive or keep files.")
    print("dff.py ver/verc = verify headers, dff.py apo fixes apostrophes.")
    sys.exit()

def usage(my_arg = ''):
    if (my_arg):
        print("Bad argument", my_arg)
    print("=" * 50)
    print("DFF usage:")
    print()
    print("-a/da, -d/dr, -k/-dk specifies d<A>ily, Google D<R>ive or Google <K>eep downloads. Default is daily. D<A>ily is useful at the end of each week.")
    print("co/te toggles the test-or-copy flag. 1a copies, then tests the next file in the directory.")
    print("-o/-fo/-of/-f only lists files.")
    print("-p/-sp forces sort-proc, meaning we sort a processed file. This is usually done only for daily files.")
    print("-bu bails after unchanged. Used for testing.")
    print("m(in)= and ma(x)= set min and max ranges.")
    print("-n1/1w toggles one-word names in lines.")
    print("-v/-q is verbose/quiet.")
    print("-rd# means go back # daily files, default is 1, -rf looks at files in current directory.")
    print("  adding Q to rd/ld allows you to say YES to changes.")
    print()
    print("?? lists examples or sibling scripts for tinkering with files once sorted, as well as most po[ular/used commands.")
    print("You can also list files you wish to look up.")
    sys.exit()

def have_first_comment(file_name):
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"):
                return line.strip()
            if line.startswith("\\"):
                return ''
    return 'COMPLETED'

def convert_apos_case(x):
    apos = apostrophe_check[x.lower()]
    if x == x.lower():
        return apos
    if x == x.title():
        if apos.startswith("'"):
            return apos[0] + apos[1].upper() + apos[2:].lower()
        return apos[0].upper() + apos[1:].lower()
    if x == x.upper():
        return apos.upper()
    return_value = ''
    count = 0
    for y in range(0, len(apos)):
        if not apos[y].isalpha():
            return_value += apos[y]
            continue
        if x[count] == x[count].lower():
            return_value += x[count]
        else:
            return_value += x[count].upper()
        count += 1
    return return_value

def relevant_daily_glob(my_dir):
    gwarning = [x for x in glob(my_dir + "/20*.txt") if not re.search("[0-9]{8}\.txt$", x)]
    if len(gwarning):
        mt.warn("WARNING: nonrelevant daily files {} found in {}.".format(', '.join(gwarning), my_dir))
    gbase = [x for x in glob(my_dir + "/20*.txt") if re.search("[0-9]{8}\.txt$", x)]
    if 'to-proc' in my_dir:
        return gbase
    return gbase[-1:]

def add_apostrophe(match):
    return match.group(1) + convert_apos_case(match.group(2)) + match.group(3)

def verify_header(my_file, must_have_mod_daily = False):
    need_name_next = False
    need_modify_next = False
    retval = True
    name_section = False
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('\\'):
                if line.strip() == '\\nam':
                    need_name_next = True
                    continue
                need_modify_next = True
                continue
            if need_name_next:
                name_section = True
                need_modify_next = True
                need_name_next = False
                continue
            if need_modify_next:
                if not line.startswith(mt.daily_warning_bumper):
                    mt.warn("{} line {} needs to be a daily warning bumper.".format(my_file, line_count))
                    retval = False
                need_modify_next = False
                continue
            if name_section:
                mt.warn("Name section with tabs should have ended {} but did not.".format(my_file))
                return False
    return retval

def check_apostrophes_in_file(my_file, first_find_message = ''):
    #apostrophe_regex = r"[^a-z']({})[^a-z']".format("|".join(list(apostrophe_check)))
    apostrophe_regex = r"(^|[^a-z'])({})($|[^a-z'])".format("|".join(list(apostrophe_check)))
    temp_apostrophe_file = "c:/writing/temp/dff-apostrophe.txt"
    change_lines = []
    apos_out = open(temp_apostrophe_file, "w")
    subcount = 0
    stt_lines = []
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            for x in set(re.findall(apostrophe_regex, line, re.IGNORECASE)):
                if subcount == 0 and first_find_message:
                    print(first_find_message)
                subcount += 1
                print("    ", subcount, line_count, x[1], "->", convert_apos_case(x[1]))
                line = re.sub(r"(^|[^a-z'])({})($|[^a-z'])".format(x[1]), add_apostrophe, line)
                change_lines.append(line_count)
            if force_speech_to_text and line != speech_to_text_minor_tweaks(line):
                if subcount == 0 and first_find_message:
                    print(first_find_message)
                subcount += 1
                stt_lines.append(str(line_count))
                line = speech_to_text_minor_tweaks(line)
            apos_out.write(line)
    apos_out.close()
    if cmp(my_file, temp_apostrophe_file):
        return 0
    mt.wm(my_file, temp_apostrophe_file)
    old_size = os.stat(my_file).st_size
    new_size = os.stat(temp_apostrophe_file).st_size
    size_delta = new_size - old_size
    print("Size delta: {} vs {} = {}.".format(old_size, new_size, size_delta))
    if len(change_lines):
        print('APOSTROPHES FLAGGED FOR CHANGE:', ', '.join(["{}: {}".format(change_lines.index(x) + 1, x) for x in change_lines]))
    if len(stt_lines):
        print('LINES WITH STT SPACING: {}'.format(', '.join(stt_lines)))
    x = input("Copy back? (Y does, O doesn't but opens, Q quits, E edits = opens and quits, #/E# opens at a specific line, anything else is ignored)")
    xl = x.strip().lower()
    if not xl:
        return len(change_lines)
    if xl[0] == 'e':
        if xl == 'e':
            mt.npo(my_file, change_lines[0])
        if xl.isdigit():
            xl = xl[1:]
    if xl.isdigit():
        xd = int(x)
        if xd in change_lines:
            mt.npo(my_file, xd)
        elif xd <= len(change_lines) and xd >= 0:
            if xd > 0:
                xd -= 1
            mt.npo(my_file, change_lines[xd])
    elif xl[0] == 'y':
        copy(temp_apostrophe_file, my_file)
    elif xl[0] == 'e':
        if xl[1:].isdigit():
            mt.npo(my_file, int(x1[1:]))
    elif xl[0] == 'q':
        sys.exit()
    elif xl[0] == 'o':
        mt.npo(my_file, change_lines[0], bail=False)
    else:
        mt.warn(xl + "ignored.")
    return len(change_lines)

def check_apostrophes_in_dir(dir_list = [ raw_daily_dir + "/to-proc", raw_drive_dir + "/to-proc", raw_keep_dir + "/to-proc", raw_daily_dir ]):
    for di in dir_list:
        count = 0
        globdir = relevant_daily_glob(di)
        lgd = len(globdir)
        print("Checking directory", di)
        for f in globdir:
            if not re.search("[0-9]{8}\.txt$", f):
                mt.warn("SKIPPING possible backup file {}.".format(f))
                continue
            count += 1
            check_apostrophes_in_file(f, first_find_message = "File {} of {} in glob found apostrophe/space tweak(s): {}".format(count, lgd, f))
    sys.exit()

def verify_weekly_headers_in_dirs(dir_list = [ raw_daily_dir + "/to-proc", raw_drive_dir + "/to-proc", raw_keep_dir + "/to-proc" ], clipboard_msg = ''):
    start_comments = defaultdict(int)
    for di in dir_list:
        smallest_file_list = []
        this_dir_file = ''
        this_dir_to_fix = 0
        for f in glob(di + "/20*.txt"):
            temp = have_first_comment(f)
            start_comments[temp] += 1
            if not temp:
                this_dir_file = f
                this_dir_to_fix += 1
                smallest_file_list.append(this_dir_file)
        if this_dir_to_fix:
            smallest_file_list = sorted(smallest_file_list, key=lambda x: os.stat(x).st_size)
            mt.warn("{} to add headers to in {}".format(this_dir_to_fix, di))
            print(smallest_file_list[0], "has size", os.stat(smallest_file_list[0]).st_size, "with maximum size", os.stat(smallest_file_list[-1]).st_size)
            mt.add_open(smallest_file_list[0])
    for com in sorted(start_comments, key=start_comments.get, reverse = True):
        print("{} instance{} of {}".format(start_comments[com], mt.plur(start_comments[com]), com if com else 'no comment'))
    if clipboard_msg:
        mt.cyan("Copying header to clipboard: {}".format(clipboard_msg.strip()))
        pyperclip.copy(clipboard_msg)
    mt.post_open(full_file_paths = True)
    sys.exit()

def conditional_bail():
    if bail_on_warnings:
        mt.bailfail("Bailing on warning. Set -nbw to change this.")

def div_results_of(a_tuple):
    try:
        return a_tuple[0] / a_tuple[1]
    except:
        return 0

def idea_count(text_chunk):
    if '\n' in text_chunk:
        return text_chunk.count('\n') + 1 # sections' CRs cut off at end
    elif '\t' in text_chunk:
        return text_chunk.count('\t') + 1
    elif text_chunk.startswith("====") and ignore_limerick_headers_in_stats:
        return 0
    else:
        return 1

def title_tweak(my_title):
    if my_title.isdigit():
        return colorama.Fore.GREEN + '#' + my_title + colorama.Fore.CYAN
    if not my_title:
        return colorama.Fore.RED + '<NONE>' + my_title + colorama.Fore.CYAN
    return my_title

def color_of(my_num):
    if my_num == 0:
        return colorama.Fore.WHITE
    if my_num < 0:
        return colorama.Fore.RED
    if my_num > 0:
        return colorama.Fore.GREEN

def change_string_of(my_val, change_dict):
    return_string = colorama.Fore.CYAN + title_tweak(my_val)
    return_string += ' ' + color_of(change_dict[my_val][0]) + str(change_dict[my_val][0]) + ' ' + color_of(change_dict[my_val][1]) + str(change_dict[my_val][1])
    return_string += colorama.Style.RESET_ALL
    return return_string

def show_size_stats(my_sections, trailer = ''):
    if show_ext_stats == STATS_EXT_OFF:
        return
    if len(my_sections) == 0:
        return
    if trailer:
        trailer = trailer.strip() + ' '
    if show_ext_stats == STATS_EXT_ALPHABETICALLY:
        ary = sorted(my_sections)
        mt.cyan("    {}SIZES: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))
    elif show_ext_stats == STATS_EXT_BY_SECTION_SIZE:
        ary = sorted(my_sections, key=lambda x:len(my_sections[x]), reverse=True)
        mt.cyan("    {}SECTION SIZE IN BYTES: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))
    elif show_ext_stats == STATS_EXT_BY_LINES:
        ary = sorted(my_sections, key=lambda x:idea_count(my_sections[x]), reverse=True)
        mt.cyan("    {}SECTION SIZE BY LINES: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))
    elif show_ext_stats == STATS_EXT_BY_AVERAGE:
        ary = sorted(my_sections, key=lambda x:len(my_sections[x]) / idea_count(my_sections[x]), reverse=True)
        mt.cyan("    {}SECTION AVG SIZE: {}".format(trailer, ' / '.join(['{} {:.2f}'.format(title_tweak(x), div_results_of(my_sections[x])) for x in ary])))
    else:
        mt.cyan("    {}SECTION SIZE: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))

def short_cfg_prefix(my_line):
    if my_line[1] != ':':
        return False
    return my_line[0].isalpha()

def tab_split(x):
    return re.split("\t+", x.strip())

def sanitize(tabbed_names, start_tab = False):
    low_case_dict = defaultdict(bool)
    new_ary = []
    for x in tab_split(tabbed_names):
        if x.lower() in low_case_dict:
            mt.cyan("WARNING deleting duplicate name (case-insensitive) {}".format(x))
        else:
            new_ary.append(x)
            low_case_dict[x.lower()] = True
    return_val = "\t".join(new_ary)
    if not return_val.startswith("\t"):
        return_val = "\t" + return_val
    return return_val

def read_daily_cfg():
    with open("c:/writing/scripts/2dy.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("defaults:"):
                global empty_to_protect
                empty_to_protect = mt.quick_dict_from_line(line)
                return
    print("WARNING: failed to read protected sections in daily cfg.")

def read_comment_cfg():
    any_warnings = False
    with open(comment_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            l = line.lower().strip()
            if l.startswith('#'): continue
            if l.startswith(';'): break
            delete_next = fix_next = False
            while short_cfg_prefix(l):
                if l[0] == 'd':
                    delete_next = True
                elif l[0] == 'f':
                    fix_next = True
                else:
                    print("Bad short-prefix {} line {}.".format(l[0], line_count))
                l = l[2:]
            (prefix, data) = mt.cfg_data_split(l)
            if not prefix or not data:
                print("Line", l, "needs main colon prefix.")
                any_warnings = True
                continue
            ary = data.split('=')
            entries = ary[0].split(",")
            try:
                vals = ary[1].split(",")
            except:
                vals = []
            if fix_next:
                for y in entries:
                    if y in fixed_marker:
                        print("doubly fixed marker", y, "line", line_count)
                        any_warnings = True
                    else:
                        fixed_marker[y] = True
            if delete_next:
                for y in entries:
                    if y in delete_marker:
                        print("doubly deleted marker", y, "line", line_count)
                        any_warnings = True
                    else:
                        delete_marker[y] = True
            if prefix in ( 'apostrophe', 'apostrophes' ):
                for e in entries:
                    if "'" not in e:
                        mt.warn("WARNING line {} in config file has {} for apostrophe-checking, but it does not have an apostrophe: {}".format(line_count, e, line[:50].strip()))
                        continue
                    er = e.replace("'", '')
                    if er in apostrophe_check:
                        print("WARNING line {} has duplicate apostrophe entry {}.".format(er))
                        continue
                    apostrophe_check[er] = e
            elif prefix == 'block':
                for my_from in entries:
                    for my_to in vals:
                        block_move_from_cfg[my_from].add(my_to)
            elif prefix == "delmar":
                for u in entries:
                    if u in delete_marker:
                        print("Duplicate delete-marker", u, "line", line_count)
                        any_warnings = True
                        continue
                    delete_marker[u] = ary[1]
            elif prefix == 'edit-blank-to-blank':
                edit_blank_to_blank = mt.truth_state_of(data)
                if edit_blank_to_blank:
                    show_blank_to_blank = edit_blank_to_blank
            elif prefix == "fixmar":
                for u in entries:
                    if u in fixed_marker:
                        print("Duplicate save-marker", u, "line", line_count)
                        any_warnings = True
                        continue
                    fixed_marker[u] = ary[1]
            elif prefix == 'keyword':
                section_words[ary[0]] = ary[1]
            elif prefix in ( 'noname', 'nonames' ):
                for x in entries:
                    if x in no_names:
                        print("Duplicate no-name {} line {}".format(x, line_count))
                    no_names[x] = True
            elif prefix == "prefix":
                for u in entries:
                    if u in prefixes:
                        print("Duplicate prefix", u, "line", line_count)
                        any_warnings = True
                        continue
                    prefixes[u] = ary[1]
            elif prefix == 'prio' or prefix == 'priority':
                global priority_sort
                priority_sort = mt.quick_dict_from_line(line, use_ints = True)
                continue
            elif prefix == "suffix":
                for u in entries:
                    if u in suffixes:
                        print("Duplicate suffix", u, "line", line_count)
                        any_warnings = True
                        continue
                    suffixes[u] = suffix_search(u, ary[1])
            elif prefix == "presuf" or prefix == "sufpre":
                for u in entries:
                    if u in suffixes:
                        print("Duplicate suffix", u, "line", line_count)
                        any_warnings = True
                        continue
                    suffixes[u] = suffix_search(u, ary[1])
                for u in entries:
                    if u in prefixes:
                        print("Duplicate prefix", u, "line", line_count)
                        any_warnings = True
                        continue
                    prefixes[u] = ary[1]
            elif prefix == 'show-blank-to-blank':
                show_blank_to_blank = mt.truth_state_of(data)
            elif prefix == 'tweak':
                for e in entries:
                    if '~' not in e:
                        print("We need a tilde for similarities in TWEAK.")
                        continue
                    eary = e.split("~")
                    if e.count("~") > 1:
                        print("WARNING line {} has more than one tilde in", e)
                        any_warnings = True
                    if eary[0] in header_tweak:
                        print(eary[0], "already in header tweak keys, line", line_count)
                        continue
                    if eary[1] in header_tweak.values():
                        print(eary[1], "already in header tweak values, line", line_count)
                        continue
                    header_tweak[eary[0]] = eary[1]
            else:
                print("ERROR bad colon/cfg definition line", line_count, ary[0])
                any_warnings = True
    for d in delete_marker:
        if d not in prefixes and d not in suffixes:
            print("WARNING: we have a delete-marker for something not in prefixes or suffixes:", d)
            any_warnings = True
    if any_warnings:
        conditional_bail()

def is_valid_limerick(this_limerick):
    if not '====' in this_limerick:
        return False
    if this_limerick.count("\n") == 6:
        return True
    slashes = this_limerick.count("/")
    if len(this_limerick) > 20 * (slashes + 1) and slashes + this_limerick.count("\n") == 6:
        return True
    return False

def limerick_flip(complete_section, incomplete_section):
    d1 = complete_section.strip().split("\n")
    d2 = incomplete_section.strip().split("\n")
    add_bumpers = False
    if d1[0] == mt.daily_warning_bumper.strip():
        d1 = d1[1:]
        add_bumpers = True
    if len(d2) and d2[0] == mt.daily_warning_bumper.strip():
        d2 = d2[1:]
        add_bumpers = True
    done_limericks = ''
    undone_limericks = ''
    daily_modify_lines = 0
    for d in [ d1, d2 ]:
        current_limerick = ''
        for x in d:
            if x.startswith('==='):
                if current_limerick:
                    if is_valid_limerick(current_limerick):
                        done_limericks += current_limerick
                    else:
                        undone_limericks += current_limerick
                current_limerick = ''
            current_limerick += x + "\n"
        if is_valid_limerick(current_limerick):
            done_limericks += current_limerick
        else:
            undone_limericks += current_limerick.lstrip()
    if add_bumpers:
        if done_limericks:
            done_limericks = mt.daily_warning_bumper + done_limericks
        if undone_limericks:
            undone_limericks = mt.daily_warning_bumper + undone_limericks
    return(done_limericks, undone_limericks)

def is_in_procs(my_file):
    fbn = os.path.normpath(my_file)
    for vp in valid_procs:
        this_file = os.path.join(vp, fbn)
        if os.path.exists(this_file):
            return this_file
    if ".txt" not in fbn:
        temp_val = is_in_procs(fbn + ".txt")
        if temp_val:
            return temp_val
    return ""

def is_match_monthdate(my_date):
    for x in range(mt.this_year, mt.this_year - 5, -1):
        this_check = "{}{}".format(x, my_date)
        print("Checking", this_check)
        temp = is_in_procs(this_check)
        if temp:
            return temp
    return ""

def is_likely_name(my_line, my_sec):
    if ' ' in my_line or '=' in my_line: return False
    if '/' in my_line and '(' not in my_line: return False
    if ':' in my_line: return False
    if my_sec in no_names: return False
    return True

def in_important_file(x, y):
    with open(y) as file:
        for line in file:
            if x in line.lower(): return True
    return False

def section_from_prefix(l):
    for p in prefixes:
        if l.startswith(p + ":"):
            return prefixes[p]
    return ""

def probably_numerical(my_text):
    if ':' in my_text or '/' in my_text or ',' in my_text or '%' in my_text: return True
    return False

def is_spoonerism_rated(l):
    if "#" in l and "nospoon" in l:
        return False
    double_digits = re.findall(r'([^0-9]([1-9])\2[^0-9])', l)
    for dig in double_digits:
        if probably_numerical(dig[0]):
            return False
        if ' ' in dig[0]:
            if mt.uncommented_length(l) > len(double_digits) * 60 and '#nospoon' not in l:
                mt.warn("NOTE: possible but very unlikely spoonerism check for", l)
                mt.warn("Get rid of this warning with #nospoon")
                return False # this prevents odd cases where I just throw out the number 77
            return True
    return False

def is_risque_spoonerism(l):
    double_digits = re.findall(r'([^0-9\*]([0\*])\2{1,2}[^0\*])', l)
    for dig in double_digits:
        if probably_numerical(dig[0]): continue
        if re.search("[dfs]\*{3}", dig[0], re.IGNORECASE): continue
        if re.search(r'[1-9]\.', dig[0]): continue # this isn't perfect! If we type 99 then 2 spaces, a period will appear on the phone. But we can check that by hand.
        if '****' in dig[0]: continue
        return True
    return False

SUFFIX_ANYWHERE = 0
SUFFIX_START = 1
SUFFIX_EXACT = 2

def section_from_suffix(my_line):
    if '#' not in my_line and ' zz' not in my_line: return
    ml2 = re.sub(".*(#| zz)", "", my_line).strip().lower()
    for x in suffixes:
        this_search = suffixes[x]
        if this_search.search_type == SUFFIX_EXACT and ml2 == this_search.text_to_search:
            return this_search.out_section
        if this_search.search_type == SUFFIX_START and ml2.startswith(this_search.text_to_search):
            return this_search.out_section
        if this_search.search_type == SUFFIX_ANYWHERE and re.search(r'\b{}\b'.format(this_search.text_to_search), ml2):
            return this_search.out_section
    return ""

def smart_section(my_line):
    for sw in section_words:
        search_string = r'\b({})\b'.format(sw)
        if re.search(search_string, my_line, re.IGNORECASE):
            return section_words[sw]
    return ""

def all_nums(l):
    if '/' in l:
        l = re.sub("[0-9]+/[0-9]+", "", l)
    return re.findall(r'[0-9]+', l)

def is_one_two_punch(l):
    if '1' not in l:
        return ''
    l = l.replace('1st ', 'first')
    l = l.replace('1 of 2', 'one of two')
    ret_string = ''
    for x in all_nums(l):
        if x == '1' and ret_string == '':
            ret_string += '1'
        elif x == '2' and ret_string == '1':
            ret_string += '2'
        elif x == '3' and ret_string == '12':
            ret_string += '3'
    if '#no12' in l:
        return ''
    if ret_string == '1':
        return ''
    return ret_string

def is_repeated_text(l):
    l = l.lower()
    l = re.sub("[^a-z]", "", l, 0, re.IGNORECASE)
    if not len(l):
        return False
    y = len(l) // 2
    return l[:y] == l[y:]

def my_section(l):
    l = l.strip()
    if mt.is_limerick(l, accept_comments = True): return 'lim' # this comes first because limericks are limericks
    if l.startswith('wfl'): return 'pc'
    if '\t' in l or l.count('  ') > 2:
        if l.count('\t') == 0:
            if not space_to_tab_conversion:
                mt.warn("LOOK OUT name section may require space-to-tab conversion with -tc")
        elif l.count(' ') - l.count('\t') > 2:
            mt.warn("LOOK OUT name section may have errant tab(s): {}".format(l.strip()))
        return 'nam'
    if mt.is_palindrome(l): return 'pal'
    if '==' in l and not l.startswith('=='): return 'btp'
    if '=' in l and re.search('=[0-9]+=', l): return 'btp'
    if is_risque_spoonerism(l): return 'cw'
    if is_spoonerism_rated(l): return 'spo'
    temp = smart_section(l)
    if temp:
        return temp
    if l.lower().startswith("if ") and "what a story" in l: return 'roo-was'
    otp = is_one_two_punch(l)
    if otp: return otp
    if is_repeated_text(l): return 'py'
    if mt.is_anagram(l, accept_comments = True): return 'ana'
    # if "~" in l: return 'ut'
    if not re.search("[^a-z]", l): return 'nam'
    temp = section_from_suffix(l)
    if temp:
        return temp
    return ""

def is_locked(proc_file):
    if not os.path.exists(proc_file): return False
    with open(proc_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#locked"):
                return True
            if not line.startswith("#"):
                return False
    return False

def lock_it(proc_file):
    if not os.path.exists(proc_file):
        print("Could not find", proc_file)
    if is_locked(proc_file):
        print(proc_file, "is already locked.")
        return
    f = open(proc_file, "r")
    my_lines = f.readlines()
    f.close()
    f = open(proc_file, "w")
    f.write("#locked\n")
    if my_lines[0].strip():
        f.write("\n")
    for m in my_lines:
        f.write(m)
    f.close()

def process_blank_details(temp_out_file):
    mt.warn(" NO BLANKS: {}".format(stats_of(temp_out_file, count_blanks = False)))
    mt.warn("NO HEADERS: {}".format(stats_of(temp_out_file, count_blanks = False, count_headings = False)))

def stats_of(text_file, count_blanks = True, count_headings = True, to_exclude = []):
    f = open(text_file, "r")
    my_lines = f.readlines()
    xtra_bytes = len(my_lines) - 1
    f.close()
    my_lines_2 = []
    get_next = True
    if type(to_exclude) == str:
        to_exclude = [to_exclude]
    for x in my_lines:
        if not x.strip():
            get_next = True
        if x.startswith("\\"):
            for y in to_exclude:
                if x.startswith("\\" + y):
                    if verbose:
                        print("EXCLUDE START WITH", x)
                    get_next = False
        if get_next:
            my_lines_2.append(x)
        else:
            if verbose:
                print("IGNORING", x)
    my_lines = list(my_lines_2)
    if not count_headings:
        my_lines = [x for x in my_lines if not x.startswith("\\")]
    if not count_blanks:
        my_lines = [x for x in my_lines if x.strip()]
    total_bytes = sum([len(x) for x in my_lines]) + xtra_bytes
    return_string = "{} bytes, {} lines, {:.2f} average.".format(total_bytes, len(my_lines), total_bytes / len(my_lines))
    return return_string

def worthwhile_line(line):
    if not line.strip():
        return False
    if line.startswith('#') or line.startswith('\\') or line.startswith('='):
        return False
    return True

def sanitized_readlines_of(file_1, file_2):
    f1 = open(file_1, 'r')
    ary_1 = [x.lower().strip() for x in f1.readlines() if worthwhile_line(x)]
    f2 = open(file_2, 'r')
    ary_2 = [x.lower().strip() for x in f2.readlines() if worthwhile_line(x)]
    ary_1a = [ x for x in ary_1 if x in ary_2 ]
    ary_2a = [ x for x in ary_2 if x in ary_1 ]
    return (ary_1a, ary_2a)

def show_adjustments(before_file, after_file):
    total_adjustments = 0
    total_places = 0
    (before_ary, after_ary) = sanitized_readlines_of(before_file, after_file)
    sorting_to_do = True
    total_delta = 0
    total_changes = 0
    print("    (NOTE: some line numbers may be identical due to reshuffling/deleting. But the net values are right.)")
    while sorting_to_do:
        max_delta = 0
        to_fix = 0
        sorting_to_do = False
        for x in range(0, len(before_ary)):
            if before_ary[x] != after_ary[x]:
                this_delta = abs(x - after_ary.index(before_ary[x]))
                if this_delta > max_delta:
                    max_delta = this_delta
                    to_fix = x
                    sorting_to_do = True
        if not sorting_to_do:
            break
        to_delete = before_ary.pop(to_fix)
        after_fix = after_ary.index(to_delete)
        after_ary.remove(to_delete)
        if len(to_delete) > max_adjustment_summary:
            try:
                space_index = to_delete.index(' ', max_adjustment_summary)
            except:
                pass
            to_delete = to_delete[:max_adjustment_summary] + " ..."
        print(to_delete, to_fix, "->", after_fix, "shifted", abs(after_fix - to_fix))
        total_delta += max_delta
        total_changes += 1
    print("Total changes and delta", total_changes, total_delta)

def spaces_to_tabs(name_sect):
    if '  ' in name_sect:
        if '\t' in name_sect.strip():
            print("WARNING mixing tabs and extra spaces in NAM section. Open manually to fix this.")
            xspace = re.findall(" {2,}", name_sect)
            print("To be precise, {} tabs and {} extra spaces.".format(name_sect.count('\t'), len(xspace)))
            return name_sect
    else:
        return name_sect
    return re.sub(" {2,}", "\t", name_sect)

def speech_to_text_minor_tweaks(my_str):
    if 'sttok' in my_str and '#' in my_str:
        return my_str
    if ' .' in my_str or ' ,' in my_str: # this changes x ,y to x, y. The if-statement is to save regex time
        my_str = re.sub(r" ([,.])([a-zA-Z])", r'\1 \2', my_str)
    my_str = re.sub(r" +(,|\.[^.0-9]|$)", r'\1', my_str)
    if my_str.startswith("#1") or my_str.lower().startswith("number one"):
        my_str = re.sub(r'#([0-9]+)', r'\1', my_str)
        my_str = re.sub(r'^number one', '1', my_str, flags=re.IGNORECASE)
    return my_str

def dupe_ignorable(x, force_lower = False):
    if force_lower:
        x = x.lower()
    if x.startswith("**modify daily instead"):
        return True
    return False

def bumper_at_start(section_name):
    if section_name == 'nam':
        return False
    return True

def sort_raw(raw_long, open_temp_out = False):
    overflow = 0
    raw_long = os.path.normpath(raw_long)
    global test_no_copy
    global copy_then_test
    global open_raw
    sections = defaultdict(str)
    raw_sections = defaultdict(str)
    blank_dict = defaultdict(str)
    name_line = defaultdict(int)
    if is_locked(raw_long):
        print(raw_long, "has been locked for writing, skipping.")
        return 0
    section_change = from_blank = to_names = 0
    important = False
    in_header = True
    header_to_write = ""
    current_section = ''
    blank_edit_lines = []
    dupe_edit_lines = []
    old_names = []
    this_file_lines = defaultdict(int)
    default_streak = last_default = 0
    found_speech_to_text = 0
    if protect_empties:
        for x in empty_to_protect:
            sections[x] = '' # protected empty sections are defined as ones that pop up in 2dy.txt, the file that creates a section outline to start the week
    mt.wait_until_npp_saved(raw_long)
    odd_tab_found = False
    rbase = os.path.basename(raw_long)
    in_to_proc = 'to-proc' in raw_long or 'to_proc' in raw_long
    with open(raw_long, mode='r', encoding='utf-8', errors='ignore') as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(mt.daily_warning_bumper_short):
                continue
            if '\t' in line:
                line = re.sub("\t+$", "", line) # trivial fix for stuff at end of line
            if line != speech_to_text_minor_tweaks(line):
                if force_speech_to_text:
                    line = speech_to_text_minor_tweaks(line)
                print(colorama.Fore.MAGENTA + "WARNING: Line {} {}{} may have been speechtotexted. Unexpected spaces were found.".format(line_count, line.strip()[:40], '...' if len(line.strip()) > 40 else '') + mt.WTXT)
                mt.add_post(raw_long, line_count, priority=4)
                found_speech_to_text += 1
            if in_header:
                if line.startswith("#"):
                    header_to_write += line
                    continue
                if line.startswith("\\"):
                    in_header = False
                    if header_to_write:
                        header_to_write += "\n"
            if important:
                sections['important'] += line
                continue
            if line.startswith('IMPORTANT'):
                important = True
                continue
            if line.startswith('UNIMPORTANT'):
                important = False
                continue
            ll = line.strip().lower()
            if ll.startswith("\\"):
                if current_section:
                    print("WARNING: may be missing space, reassigning section {} to {} at line {} of {}.".format(current_section, ll[1:], line_count, rbase))
                current_section = ll[1:]
                continue
            if line.strip():
                raw_sections[current_section] += line
            no_punc = mt.strip_punctuation(ll, other_chars_to_zap = '=', ignore_after = ['===='])
            if no_punc and no_punc in this_file_lines and not dupe_ignorable(no_punc):
                mt.warn("WARNING duplicate line {} in {} copies {}: {}".format(line_count, rbase, this_file_lines[no_punc], ll))
                dupe_edit_lines.append(line_count)
            else:
                this_file_lines[no_punc] = line_count
            if not ll:
                current_section = ''
                important = False
                continue
            if current_section in fixed_marker:
                sections[current_section] += line
                continue
            if not resort_already_sorted:
                if current_section:
                    sections[current_section] += line
                    continue
            if current_section == 'nam':
                if "\t\t" in line:
                    offsets = [str(m.start()) for m in re.finditer('\t{2,}', line)]
                    mt.warn("NOTE: repeat tab in NAME section in line {}, offset{} {} of {}.".format(line_count, mt.plur(len(offsets)), ', '.join(offsets), len(line)))
            elif current_section and '\t' in line:
                mt.fail("NOTE: tab in non-name section in line {}.".format(line_count))
                odd_tab_found = True
                mt.add_post(raw_long, line_count)
            temp = section_from_prefix(ll)
            if temp:
                if (temp in prefixes and temp in delete_marker) or not keep_directive_text:
                    line = re.sub("^.*?:", "", line).lstrip()
                sections[temp] += line
                if temp != current_section:
                    section_change += 1
                continue
            temp = section_from_suffix(line)
            if temp and temp not in block_move_from_cfg[current_section]:
                if not keep_directive_text and section_from_suffix(line):
                    line = re.sub(" *#.*", "", line)
                sections[temp] += line
                continue
            temp = my_section(line)
            if temp:
                if temp != current_section and (temp not in block_move_from_cfg[current_section] or temp in local_unblock_move) and (current_section not in local_block_move):
                    sect_move[temp][current_section] += 1
                    if verbose >= 2:
                        print("Move from", current_section if current_section else "<none>", "to", temp, ":", line.strip(), block_move_from_cfg[current_section], 'block?', temp in block_move_from_cfg[current_section])
                if temp in block_move_from_cfg[current_section]:
                    sections[current_section] += line
                    continue
                elif temp == 'nam':
                    line = "\t" + line.strip()
                    sections[temp] += line.replace('`', '') # the "replace" is for stuff done at the library
                elif temp == 'lim':
                    sections[temp] += mt.slash_to_limerick(line)
                else:
                    if temp in suffixes and temp in delete_marker:
                        sfs = section_from_suffix(line, search_type = True)
                        if sfs:
                            line = re.sub(r'( zz| *#).*'.format(sfs), "", line, re.IGNORECASE)
                    sections[temp] += line
                if temp != current_section:
                    if current_section:
                        section_change += 1
                    else:
                        from_blank += 1
                continue
            if one_word_names and is_likely_name(line, current_section) and 'nam' not in local_block_move and current_section != 'nam':
                mt.cyan("    ----> NOTE: moved likely-name from section {} to \\nam at line {}: {}.".format(current_section if current_section else '<none>', line_count, line.strip()))
                sections['nam'] += "\t" + line.strip()
                name_line[line.strip()] = line_count
                to_names += 1
                continue
            if resort_already_sorted:
                if current_section:
                    sections[current_section] += line
                    continue
            if current_section == '':
                if not line.startswith('#'):
                    if show_blank_to_blank:
                        if line_count == last_default + 1 and default_streak > max_consecutive_blank_section_lines:
                            if not overflow:
                                mt.fail("    <note: lines-in-a-row (x, x+1) exceeded max_consecutive_blank_section_lines at line {}.>".format(line_count))
                            overflow += 1
                        elif not dupe_ignorable(line, force_lower = True):
                            print("BLANK-TO-DEFAULT: {} = {}".format(line_count, line.strip()))
                            blank_edit_lines.append(line_count)
                        default_streak += 1
                        last_default = line_count
            else:
                default_streak = 0
            if temp != current_section:
                if current_section:
                    section_change += 1
                else:
                    from_blank += 1
            sections['sh'] += line
    if odd_tab_found:
        print("Tabs need fixing. Opening document.")
        mt.post_open()
    if space_to_tab_conversion:
        sections['nam'] = spaces_to_tabs(sections['nam'])
    if len(dupe_edit_lines):
        if not ignore_duplicate:
            print("If you are sure the duplication ({}) is okay, the igdup option will bypass this bail. But the option is hidden for a reason. You probably just want to put a comment after, or change things subtly.".format(mt.listnums(dupe_edit_lines)))
            mt.npo(raw_long, dupe_edit_lines[0])
    if verbose or section_change:
        print((colorama.Fore.CYAN if section_change > 0 else '') + "{} section change{}, {} sorted from blank, {} to name-section from blank.".format(section_change, mt.plur(section_change), from_blank, to_names), colorama.Style.RESET_ALL)
    if overflow:
        print("NOTE: consecutive-line overflow (line not fitting in any section) was detected. Inspection showed a total of {} overflow line{}.".format(overflow, mt.plur(overflow)))
    if edit_blank_to_blank and len(blank_edit_lines) and not clipboard_file:
        print("Lines to edit to put in section: {} total, list = {}".format(len(blank_edit_lines), mt.listnums(blank_edit_lines)))
        mt.npo(raw_long, blank_edit_lines[0])
    if len(old_names):
        new_names = tab_split(sections['nam'].lower().strip())
        t1 = sorted(list(set(new_names) - set(old_names)))
        t2 = sorted(list(set(old_names) - set(new_names)))
        if len(t1) > 0:
            mt.okay("New names: {}".format(', '.join(["{}~{}".format(x, name_line[x]) for x in t1])))
        if len(t2) > 0:
            mt.okay("Old names deleted: {}".format(t2))
    if 'nam' in sections:
        sections['nam'] = re.sub("\n", "\t", sections['nam'].rstrip())
        sections['nam'] = "\t" + sections['nam'].lstrip()
        sections['nam'] = sanitize(sections['nam'], start_tab = True)
    if 'lim' in sections or 'lip' in sections:
        ( sections['lim'], sections['lip'] ) = limerick_flip(sections['lim'], sections['lip'])
        if not sections['lip'].strip(): # don't pop LIM, as it is one of our default sections, and if we sort things early in the week, we'll want to keep LIM. However, if LIP's part-limericks are fixed, pop them, as it can be deleted/created at will.
            sections.pop('lip')
    if 'important' in sections:
        if in_important_file(raw_long, important_file):
            print("Not dumping text to", important_file, "as the text", raw_long, "is already in there.")
        else:
            fout = open(important_file, "a")
            fout.write("\nIMPORTANT STUFF from {0}:\n".format(raw_long))
            fout.write(sections['important'])
            fout.close()
        sections.pop('important')
    temp_out_file = "c:/writing/temp/dff-temp.txt"
    for x in daily_strings:
        if x in raw_long:
            temp_out_file = "c:/writing/temp/{}-temp.txt".format(x)
    fout = open(temp_out_file, "w")
    fout.write(header_to_write)
    if verbose:
        for x in sorted(sect_move):
            print("To {}: {}".format(x, ', '.join(["{} {}".format(a if a else '<blank>', sect_move[x][a]) for a in sect_move[x]])))
    for x in sorted(sections, key=lambda x:(priority_sort[x], header_tweak[x] if x in header_tweak else x)): # note this is a tuple that's used to push current hot projects to the bottom
        if in_to_proc:
            if bumper_at_start(x):
                sections[x] = mt.daily_warning_bumper + sections[x]
            else:
                if not sections[x].endswith('\n'):
                    sections[x] += '\n'
                sections[x] += mt.daily_warning_bumper
        sections[x] = sections[x].rstrip()
        fout.write("\\{0}\n".format(x))
        fout.write(sections[x])
        if not sections[x]:
            fout.write("\n")
        elif x != 'nam':
            fout.write("\n\n")
    fout.close()
    if found_speech_to_text:
        mt.warn("You may want to run STT/apostrophe checking with -stt/-apo or add #sttok at the end. There were {} prespaces found.".format(found_speech_to_text))
    mt.compare_alphabetized_lines(raw_long, temp_out_file, verbose = False, max_chars = -300, red_regexp = r"^[^\\\n$]", green_regexp = r"^([\\\n]|$)", show_bytes = True, compare_tabbed = True, verify_alphabetized_true = read_most_recent, case_insensitive = True, comment_note_level = mt.CAL_PASS_COMMENTS)
    for r in raw_sections:
        raw_sections[r] = raw_sections[r].rstrip()
    no_changes = os.path.exists(raw_long) and cmp(raw_long, temp_out_file)
    if no_changes:
        if verbose or read_most_recent: print(raw_long, "had no sortable changes since last run.")
        if pop_up_if_clean:
            messageBox2 = ctypes.windll.user32.MessageBoxA
            messageBox2(None, "Popup to mention that weekly file is sorted OK.\n\nThis should usually only be run at week's end.".encode('ascii'), "HOORAY!".encode('ascii'), 0x0)
    if show_stat_numbers:
        mt.okay("    {}: {}".format('  FULL' if no_changes else 'BEFORE', stats_of(raw_long)))
        without_names = os.stat(temp_out_file).st_size - len(sections['nam'])
        mt.cyan("  NO NAMES: {}".format(stats_of(temp_out_file, to_exclude = 'nam')))
        if not no_changes:
            print("     AFTER: {}".format(stats_of(temp_out_file)))
        process_blank_details(temp_out_file)
    if no_changes:
        if bail_after_unchanged:
            if not verbose: print("Bailing after unchanged.")
            sys.exit()
        return 0
    else:
        if show_stat_numbers:
            sectdif = defaultdict(tuple)
            sectnew = defaultdict(tuple)
            raw_nums = defaultdict(tuple)
            for x in raw_sections:
                raw_nums[x] = ( len(raw_sections[x]), idea_count(raw_sections[x]) )
            if '' in raw_nums:
                mt.warn("    Got rid of {}/{} characters/line{} from unsectioned.".format(raw_nums[''][0], raw_nums[''][1], mt.plur(raw_nums[''][1]))) # no PLUR for characters since we can assume an idea has more than one character
            for x in sections:
                if x in raw_sections and raw_sections[x].strip() == sections[x].strip():
                    continue
                if x in raw_sections:
                    sectdif[x] = (len(sections[x]), idea_count(sections[x]))
                else:
                    sectnew[x] = (len(sections[x]), idea_count(sections[x]))
            show_size_stats(sectdif, "CHANGED SECT")
            show_size_stats(sectnew, "NEW")
            change_amounts = defaultdict(tuple)
            for x in sectdif:
                change_amounts[x] = ( sectdif[x][0] - raw_nums[x][0], sectdif[x][1] - raw_nums[x][1] )
            show_size_stats(change_amounts, "NET SECTION DELTAS")
        if show_total_jumps:
            show_adjustments(raw_long, temp_out_file)
        if test_no_copy:
            if not ask_to_copy_back:
                print("Not modifying", raw_long, "even though differences were found. Set -co force changes with no question or add a Q to a parameter to get a verification question.")
                mt.post_open(bail_after=False)
            if show_differences:
                mt.wm(raw_long, temp_out_file)
            if ask_to_copy_back:
                x = input("Copy back? (Y does, anything else doesn't)")
                if not x.strip():
                    pass
                elif x.strip().lower()[0] == 'y':
                    copy(temp_out_file, raw_long)
            else:
                print("Add q or g to question/get copy-back, or use cq/qc as a separate argument, or co to force copying back.")
        if mt.is_npp_modified(raw_long):
            if force_copy:
                print("Force-copying despite {} being unsaved in notepad++. I hope you know what you're doing, but you can always click <NO> and compare.")
                print("Original file saved to {}.".format(force_backup))
                copy(raw_long, force_backup)
            else:
                print("BAILING because {} is unsaved in notepad. You can copy over with -fc.".format(raw_long)) # do not put this option in usage, because I want to make sure I use it sparingly
                sys.exit()
        if not test_no_copy:
            copy(temp_out_file, raw_long)
        if copy_then_test:
            print("OK, copied one, now testing another.")
            test_no_copy = True
            copy_then_test = False
            open_raw = True
            return 1
    if clipboard_file:
        os.system(temp_out_file)
    if open_raw:
        print("Opening raw", raw_long)
        os.system(raw_long)
    if open_temp_out:
        print("Opening tempfile", temp_out_file)
        os.system(temp_out_file)
    if only_one:
        mt.warn("Bailing after first file converted, since only_one is set to True. Change this with -fb or -f or cap number of files changed with -f# or -fb#.")
        sys.exit()
    return 1

def is_outline_text(my_line):
    if my_line.startswith('===='):
        return True
    if my_line.startswith("\\"):
        return True
    return False

def dff_normalize(my_line):
    my_line = mt.strip_punctuation(my_line, remove_comments = True)
    if re.search(r' ([0-9=])\1 ', my_line):
        rexp = re.compile(r' *(?:([0-9=])\1) *')
        line_list = rexp.split(my_line)[0::2]
        if '==' in my_line:
            my_line = "<BTP> " + ', '.join(sorted(line_list))
        else:
            my_line = "<SPOONERISM> " + ', '.join(sorted(line_list))
    return my_line

def deep_duplicate_delete(last_file = "3000.txt"):
    if not last_file.lower().endswith('txt'):
        last_file += '.txt'
    dailies = [x for x in glob("c:/writing/daily/20*.txt") if re.sub(".*[\\\/]", "", x) <= last_file]
    name_dupes = dupes = 0
    name_bytes_i_got = bytes_i_got = 0
    dupe_dict = defaultdict(list)
    dupe_name_dict = defaultdict(list)
    this_sect = '<none>'
    to_print = []
    for y in dailies[:-1]:
        bn = os.path.basename(y)
        with open(y) as file:
            for (line_count, line) in enumerate (file, 1):
                line_content = dff_normalize(line)
                if not line_content:
                    continue
                if '\t' in line_content:
                    for a_name in tab_split(line.lower()):
                        dupe_name_dict[a_name].append(bn)
                dupe_dict[line_content].append((bn, line_count))
    with open(dailies[-1]) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("\\"):
                this_sect = line.strip()[1:]
                continue
            elif not line.strip():
                this_sect = '<none>'
                continue
            if '\t' in line:
                for a_name in tab_split(line.lower()):
                    if a_name in dupe_name_dict:
                        name_dupes += 1
                        to_print.append(colorama.Fore.GREEN + "DUPLICATE NAME {}:{} {}{}".format(a_name, colorama.Fore.YELLOW, ', '.join(dupe_name_dict[a_name]), colorama.Style.RESET_ALL))
                        name_bytes_i_got += len(a_name)
            line_content = dff_normalize(line)
            if is_outline_text(line_content):
                continue
            if line_content in dupe_dict:
                dupes += 1
                to_print.append(colorama.Fore.GREEN + "DUPLICATE LINE {} {} {}:{} {}{}".format(line_count, this_sect, line.strip(), colorama.Fore.YELLOW, ', '.join(["{} line {}".format(x[0], x[1]) for x in dupe_dict[line_content]]), colorama.Style.RESET_ALL))
                bytes_i_got += len(line) + 1
    head_foot_string = colorama.Fore.CYAN + "{} duplicate lines for a total of {} bytes. {} duplicate names for a total of {} bytes.".format(dupes, bytes_i_got, name_dupes, name_bytes_i_got) + colorama.Style.RESET_ALL
    if not dupes:
        print("no duplicates detected.")
    else:
        mt.center(head_foot_string)
    for tp in to_print:
        print(tp)
    if dupes:
        mt.center(head_foot_string)
    sys.exit()

files_done = 0
file_list = []
cmd_count = 1
max_files = 1
daily_files_back = 1

while cmd_count < len(sys.argv):
    (arg, num, value_found) = mt.parameter_with_number(sys.argv[cmd_count], default_value = 1)
    if arg in ( 'f', 'fb'):
        max_files = num
        only_one = False
    elif arg[:2] == 'g=': # there may be a letter here so we can't rely on num
        raw_glob = num if num else arg[2:]
    elif arg in ( 'k', 'dk' ):
        what_to_sort = daily.KEEP
    elif arg in ( 'd', 'dr' ):
        what_to_sort = daily.DRIVE
    elif arg in ( 'a', 'da' ):
        what_to_sort = daily.DAILY
    elif arg in ( 'p', 'sp' ):
        sort_proc = True
    elif arg in ( 'cq', 'qc' ):
        ask_to_copy_back = True
    elif arg == 'ddd':
        deep_duplicate_delete()
    elif arg[:3] == 'ddd' and arg[3:].isdigit():
        deep_duplicate_delete(arg[3:])
    elif arg in ( 'py', 'yp' ):
        protect_yes_force = True
    elif arg in ( 'pn', 'np' ):
        protect_no_force = True
    elif arg in ( 'o', 'fo', 'of', 'f' ):
        only_list_files = True
    elif arg == 'puc':
        pop_up_if_clean = True
    elif arg == '1a':
        copy_then_test = True
        test_no_copy = False
        max_files = 2
    elif arg in ('cly', 'ycl'):
        clipboard_file = True
        open_raw = True
    elif arg in ( 'clo', 'ocl'):
        clipboard_file = True
        open_raw = False
    elif arg[:2] == 'lb':
        local_block_move.update(arg[3:].split(","))
    elif arg[:2] == 'lu':
        local_unblock_move.update(arg[3:].split(","))
    elif arg == 'c':
        sys.exit("While C is the natural command-line parameter for copy, we want to avoid accidents, so you need to type co.")
    elif arg == 'mu':
        max_files = -1
        only_one = False
    elif arg == 'oo':
        only_one = True
    elif arg == 'co':
        test_no_copy = False
    elif arg == 'te':
        test_no_copy = True
    elif arg == 'bu':
        bail_after_unchanged = True
    elif arg == 'n1':
        one_word_names = False
    elif arg in ( '1w', 'w1' ):
        one_word_names = True
    elif arg in ( 'l1', '1l' ):
        last_file_first = True
    elif arg in ( 'f1', '1f' ):
        last_file_first = False
    elif arg in ( 've', 'ver' ):
        verify_weekly_headers_in_dirs(clipboard_msg = '')
    elif arg in ( 'vc', 'vec', 'verc' ):
        verify_weekly_headers_in_dirs(clipboard_msg = "#verified sorted for final dgrab\n\n")
    elif arg == 'vv':
        verbose = 2
    elif arg == 'v':
        verbose = 1
    elif arg == 'q':
        verbose = 0
    elif arg == 'stt':
        force_speech_to_text = True
    elif arg == 'tf':
        run_test_file = True
    elif arg == 'igdup':
        ignore_duplicate = True
    elif arg == 'n':
        show_stat_numbers = True
    elif arg in ( 'na', 'an' ):
        show_stat_numbers = True
        show_ext_stats = STATS_EXT_ALPHABETICALLY
    elif arg in ( 'ns', 'sn' ):
        show_stat_numbers = True
        show_ext_stats = STATS_EXT_BY_SECTION_SIZE
    elif arg in ( 'nl', 'ln' ):
        show_stat_numbers = True
        show_ext_stats = STATS_EXT_BY_LINES
    elif arg in ( 'nv', 'vn', 'ny', 'yn' ):
        show_stat_numbers = True
        show_ext_stats = STATS_EXT_BY_AVERAGE
    elif arg[:2] == 'tf':
        run_test_file = True
        if arg[2:].isdigit():
            test_file_index = int(arg[2:])
        elif len(arg) > 2:
            print("Test file index must be a digit, so I couldn't translate {}. Going with default of 0.".format(arg[2:]))
    elif arg == 'bbe':
        show_blank_to_blank = True
        edit_blank_to_blank = True
    elif arg == 'bb':
        show_blank_to_blank = True
        edit_blank_to_blank = False
    elif arg in ( 'nbb', 'bbn' ):
        show_blank_to_blank = False
        edit_blank_to_blank = False
    elif arg in ( 'bw', 'wb' ):
        bail_on_warning = True
    elif arg in ( 'nbw', 'nwb', 'bwn', 'wbn' ):
        bail_on_warning = False
    elif arg in ( 'tj', 'jt' ):
        show_total_jumps = True
    elif arg == 'sb':
        dir_search_flag = daily.BACKUP
    elif arg == 'sr':
        dir_search_flag = daily.ROOT
    elif arg == 'st':
        dir_search_flag = daily.TOPROC
    elif arg == 'ld':
        read_most_recent = True
        dir_search_flag = daily.ROOT
    elif mt.alpha_match(arg, 'ldc'):
        read_most_recent = True
        dir_search_flag = daily.ROOT
        test_no_copy = False
    elif mt.alpha_match(arg, 'ldq') or mt.alpha_match(arg, 'ldg') or arg in ( 'lq', 'lg' ):
        read_most_recent = True
        dir_search_flag = daily.ROOT
        ask_to_copy_back = True
    elif arg == 'rd':
        read_most_recent = True
        dir_search_flag = daily.TOPROC
    elif mt.alpha_match(arg, 'rdc'):
        read_most_recent = True
        dir_search_flag = daily.TOPROC
        test_no_copy = False
    elif mt.alpha_match(arg, 'rdq') or mt.alpha_match(arg, 'rdg') or arg in ( 'rq', 'rg' ):
        read_most_recent = True
        dir_search_flag = daily.TOPROC
        ask_to_copy_back = True
        daily_files_back = num
    elif mt.alpha_match(arg, 'dd'):
        what_to_sort = daily.DRIVE
        dir_search_flag = daily.TOPROC
    elif mt.alpha_match(arg, 'ddc'):
        what_to_sort = daily.DRIVE
        dir_search_flag = daily.TOPROC
        test_no_copy = False
    elif mt.alpha_match(arg, 'ddq'):
        what_to_sort = daily.DRIVE
        dir_search_flag = daily.TOPROC
        ask_to_copy_back = True
        daily_files_back = num
    elif mt.alpha_match(arg, 'kd'):
        what_to_sort = daily.KEEP
        dir_search_flag = daily.TOPROC
    elif mt.alpha_match(arg, 'kdc'):
        what_to_sort = daily.KEEP
        read_most_recent = False
        dir_search_flag = daily.TOPROC
        test_no_copy = False
    elif mt.alpha_match(arg, 'kdq'):
        what_to_sort = daily.KEEP
        dir_search_flag = daily.TOPROC
        ask_to_copy_back = True
        daily_files_back = num
    elif mt.alpha_match(arg, 'lwd'):
        read_most_recent = True
        dir_search_flag = daily.ROOT
        what_to_sort = daily.DAILIES
    elif mt.alpha_match(arg, 'rwd'):
        read_most_recent = True
        dir_search_flag = daily.ROOT
        what_to_sort = daily.DAILIES
    elif arg == 'rf':
        read_most_recent = True
    elif arg[:2] == 'rd':
        read_most_recent = True
        what_to_sort = daily.DAILIES
        dir_search_flag = daily.TOPROC
        daily_files_back = num
    elif arg[:2] == 'rf':
        read_most_recent = True
        dir_search_flag = daily.TOPROC
        daily_files_back = num_of
    elif arg == 'fc':
        force_copy = True
    elif arg in ( 'hv', 'vh' ):
        header_verify = True
    elif arg in ( 'hvn', 'vhn', 'nhv', 'nvh' ):
        header_verify = False
    elif arg in ( 'm=', 'mi=', 'mn=', 'min=' ):
        my_min_file = str(num)
        print("Minfile is now", my_min_file)
    elif arg in ( 'ma=', 'max=' ):
        my_max_file = str(num)
        print("Maxfile is now", my_max_file)
    elif arg in ( 'kd', 'dk') or mt.alfmatch('kdt', arg):
        keep_directive_text = True
    elif arg == 'tc':
        space_to_tab_conversion = True
    elif arg in ( 'ap', 'apo', 'apa', 'apoa' ):
        run_apostrophe_check = RUN_ALL_APOSTROPHE
        print("APL runs latest apostrophe check.")
    elif arg in ( 'ap1', 'apo1', 'apl', 'apol' ):
        run_apostrophe_check = RUN_LATEST_APOSTROPHE
        print("APO runs all apostrophe checks.")
    elif arg == '?':
        usage()
    elif arg == '??':
        examples()
    elif len(arg) <= 2:
        usage(arg)
    else:
        if arg.startswith("20"):
            if ".txt" not in arg:
                arg += ".txt"
            file_list.append(arg)
        elif re.search("^(0)?[0-9]{3}$", arg):
            temp = is_match_monthdate(arg)
            if temp:
                file_list.append(temp)
            else:
                sys.exit("WARNING: {} is not a readable file in any to-proc directory. Treating as command and bailing. Use ? to see usage.".format(arg))
        elif is_in_procs(arg):
            file_list.append(arg)
        else:
            sys.exit("WARNING: {} is not a readable file in any to-proc directory. Treating as command and bailing. Use ? to see usage.".format(arg))
    cmd_count += 1

temp_set = local_block_move.intersection(local_unblock_move)
if len(temp_set) > 0:
    sys.exit("User-enforced block/unblock arrays share element{} {}. Bailing.".format(mt.plur(len(temp_set)), ', '.join(temp_set)))

if protect_yes_force and protect_no_force:
    sys.exit("Forced all protections on and off with the py/pn parameters. You can only choose one. Bailing.")

if my_min_file > my_max_file: sys.exit("Min file specified >> max file specified. Bailing.")

if what_to_sort == daily.DAILIES:
    dir_to_scour = raw_daily_dir
    sort_proc = True
elif what_to_sort == daily.DRIVE:
    dir_to_scour = raw_drive_dir
elif what_to_sort == daily.KEEP:
    dir_to_scour = raw_keep_dir
else:
    sys.exit("Unknown sorting type/directory.")

if not os.path.exists(dir_to_scour):
    sys.exit("Can't open scour-directory {}.".format(dir_to_scour))

if dir_search_flag == daily.TOPROC:
    dir_to_scour = os.path.join(dir_to_scour, "to-proc")
elif dir_search_flag == daily.BACKUP:
    dir_to_scour = os.path.normpath(os.path.join(dir_to_scour, "backup"))
elif dir_search_flag == daily.ROOT:
    dir_to_scour = os.path.normpath(os.path.join(dir_to_scour, "."))

if protect_yes_force:
    protect_empties = True
elif protect_no_force:
    protect_empties = False
else:
    protect_empties = (dir_search_flag != daily.TOPROC)

if not os.path.exists(dir_to_scour):
    sys.exit("Something went wrong after changing directories according to the dir-search-flags.\n\nI am bailing as I could not find {}.".format(dir_to_scour))

os.chdir(dir_to_scour)

read_daily_cfg()
read_comment_cfg()

if run_apostrophe_check == RUN_ALL_APOSTROPHE:
    check_apostrophes_in_dir()
elif run_apostrophe_check == RUN_LATEST_APOSTROPHE:
    check_apostrophes_in_dir(dir_list = [ 'c:/writing/daily' ])

if clipboard_file:
    f = open(dff_clipboard, "w")
    f.write(pyperclip.paste().replace('\r\n', '\n'))
    f.close()
    sort_raw(dff_clipboard, open_temp_out = True)
    mt.okay("REMEMBER: cly/ycl = open raw and final files, cln/ncl=only open final file.")
    sys.exit()

if run_test_file:
    test_file_name = "c:/writing/temp/dff-test-file-{}.txt".format(test_file_index)
    sort_raw(test_file_name)
    sys.exit()

if not len(file_list):
    my_glob = "{}/{}".format(dir_to_scour, dailies_glob)
    file_list = mt.dailies_of(dir_to_scour, full_file_path = True)
    if verbose:
        print("Finding dailies in", dir_to_scour)

if read_most_recent:
    daily_count = 0
    for r in reversed(file_list):
        if not os.stat(r).st_size:
            print("Skipping over zero-byte file {} which we should delete.".format(r))
            continue
        daily_count += 1
        if daily_count == daily_files_back:
            sort_raw(r)
            if read_most_recent and ask_to_copy_back:
                mt.warn("REMINDER: use APL and not APO to adjust apostrophes/spaces on latest file.")
            print("Got to back of daily files! Exiting.")
            sys.exit()
    if daily_count == 0:
        print("No recent daily to read.")
    else:
        print("Could only go {} of {} back.".format(daily_count, daily_files_back))
    sys.exit()

list_count = 0

if last_file_first:
    file_list.reverse()

for fi in file_list:
    list_count += 1
    fbn = os.path.basename(fi)
    if not os.path.exists(fi):
        print("WARNING: {} does not exist.".format(fbn), dir_to_scour)
        continue
    if fbn < my_min_file:
        continue
    if fbn > my_max_file:
        continue
    if only_list_files:
        print(fi)
        continue
    print("Parsing file {} of {}: {}".format(list_count, len(file_list), fbn))
    if header_verify:
        verify_header(fi)
    files_done += sort_raw(fi)
    if files_done == max_files:
        print("Hit max_files of {}. You can change this with -f# or -fb#.".format(max_files))
        break

if not files_done:
    print("No files sorted.")
