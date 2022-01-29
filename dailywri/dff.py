# dff.py: daily file find
#
# sorts notes from google keep/drive and modifies them a bit if necessary
#

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

DEFAULT_SORT = daily.DAILY

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
    print("The directory gives us a default of", daily_strings[what_to_sort])

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

pop_up_if_clean = False

read_most_recent = False

bail_on_warnings = True

ask_to_copy_back = False

show_stat_numbers = False

last_file_first = True
ignore_limerick_headers_in_stats = True

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

empty_to_protect = defaultdict(bool)
protect_yes_force = False
protect_no_force = False

block_move_from_cfg = defaultdict(set)
local_block_move = set()
local_unblock_move = set()

sect_move = defaultdict(lambda: defaultdict(int))

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
    print("You can also list files you wish to look up.")
    sys.exit()

def blue_print(my_str):
    print(colorama.Fore.CYAN + my_str + colorama.Style.RESET_ALL)

def conditional_bail():
    if bail_on_warnings:
        sys.exit(colorama.Fore.RED + "Bailing on warning. Set -nbw to change this." + colorama.Style.RESET_ALL)

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
        blue_print("    {}SIZES: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))
    elif show_ext_stats == STATS_EXT_BY_SECTION_SIZE:
        ary = sorted(my_sections, key=lambda x:len(my_sections[x]), reverse=True)
        blue_print("    {}SECTION SIZE IN BYTES: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))
    elif show_ext_stats == STATS_EXT_BY_LINES:
        ary = sorted(my_sections, key=lambda x:idea_count(my_sections[x]), reverse=True)
        blue_print("    {}SECTION SIZE BY LINES: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))
    elif show_ext_stats == STATS_EXT_BY_AVERAGE:
        ary = sorted(my_sections, key=lambda x:len(my_sections[x]) / idea_count(my_sections[x]), reverse=True)
        blue_print("    {}SECTION AVG SIZE: {}".format(trailer, ' / '.join(['{} {:.2f}'.format(title_tweak(x), div_results_of(my_sections[x])) for x in ary])))
    else:
        blue_print("    {}SECTION SIZE: {}".format(trailer, ' / '.join(['{} {} {}'.format(title_tweak(x), my_sections[x][0], my_sections[x][1]) for x in ary])))

def short_cfg_prefix(my_line):
    if my_line[1] != ':':
        return False
    return my_line[0].isalpha()

def sanitize(tabbed_names):
    low_case_dict = defaultdict(bool)
    new_ary = []
    for x in re.split("\t+", tabbed_names):
        if x.lower() in low_case_dict:
            blue_print("WARNING deleting duplicate name (case-insensitive) {}".format(x))
        else:
            new_ary.append(x)
            low_case_dict[x.lower()] = True
    return "\t".join(new_ary)

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
            if prefix == 'block':
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
                for x in vals:
                    if x in no_names:
                        print("Duplicate no-name {} line {}".format(x, count))
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
                    suffixes[u] = ary[1]
            elif prefix == "presuf" or prefix == "sufpre":
                for u in entries:
                    if u in suffixes:
                        print("Duplicate suffix", u, "line", line_count)
                        any_warnings = True
                        continue
                    suffixes[u] = ary[1]
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
            if mt.uncommented_length(l) > len(double_digits) * 60:
                print("NOTE: possible but very unlikely spoonerism check for", l)
                return False # this prevents odd cases where I just throw out the number 77
            return True
    return False

def is_risque_spoonerism(l):
    double_digits = re.findall(r'([^0\*]([0\*])\2{1,2}[^0\*])', l)
    for dig in double_digits:
        if probably_numerical(dig[0]): continue
        if re.search("[dfs]\*{3}", dig[0], re.IGNORECASE): continue
        if re.search(r'[1-9]', dig[0]): continue
        if '****' in dig[0]: continue
        return True
    return False

def section_from_suffix(my_line, exact = False):
    if '#' not in my_line and ' zz' not in my_line: return
    ml2 = re.sub(".*(#| zz)", "", my_line).strip().lower()
    for x in suffixes:
        if not exact and ml2.startswith(x):
            return suffixes[x]
        if exact and ml2.startswith(x) and re.search(r'{}\b'.format(x), ml2):
            return suffixes[x]
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
    temp = section_from_suffix(l, exact = True)
    if temp:
        return temp
    if '\t' in l or l.count('  ') > 2:
        if l.count(' ') - l.count('\t') > 2:
            print("LOOK OUT line may have errant tab(s):", l.strip())
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
    temp = section_from_suffix(l, exact = False)
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
    print(" NO BLANKS: {}".format(stats_of(temp_out_file, count_blanks = False)))
    print("NO HEADERS: {}".format(stats_of(temp_out_file, count_blanks = False, count_headings = False)))

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
                    print("EXCLUDE START WITH", x)
                    get_next = False
        if get_next:
            my_lines_2.append(x)
        else:
            print("IGNORING", x)
    my_lines = list(my_lines_2)
    if not count_headings:
        my_lines = [x for x in my_lines if not x.startswith("\\")]
    if not count_blanks:
        my_lines = [x for x in my_lines if x.strip()]
    total_bytes = sum([len(x) for x in my_lines]) + xtra_bytes
    return_string = "{} bytes, {} lines, {:.2f} average.".format(total_bytes, len(my_lines), total_bytes / len(my_lines))
    return return_string

def sort_raw(raw_long):
    overflow = False
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
    if protect_empties:
        for x in empty_to_protect:
            sections[x] = ''
    with open(raw_long, mode='r', encoding='utf-8') as file:
        for (line_count, line) in enumerate(file, 1):
            if '\t' in line:
                line = re.sub("\t+$", "", line) # trivial fix for stuff at end of line
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
                    print("WARNING: may be missing space, reassigning section {} to {} at line {} of {}.".format(current_section, ll[1:], line_count, os.path.basename(raw_long)))
                current_section = ll[1:]
                continue
            if line.strip():
                raw_sections[current_section] += line
            no_punc = mt.strip_punctuation(ll, other_chars_to_zap = '=')
            if no_punc and no_punc in this_file_lines:
                print("WARNING duplicate line", ll, line_count, this_file_lines[no_punc])
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
                    print(colorama.Fore.YELLOW + "NOTE: repeat tab in name line {}.".format(line_count) + colorama.Style.RESET_ALL)
                old_names.extend(re.split("\t+", line.lower().strip()))
            temp = section_from_prefix(ll)
            if temp:
                if temp in prefixes and temp in delete_marker:
                    line = re.sub("^.*?:", "", line).lstrip()
                sections[temp] += line
                if temp != current_section:
                    section_change += 1
                continue
            temp = my_section(line)
            if temp:
                if temp != current_section and (temp not in block_move_from_cfg[current_section] or temp in local_unblock_move) and (current_section not in local_block_move):
                    sect_move[temp][current_section] += 1
                    if verbose >= 2:
                        print("Move from", current_section if current_section else "<none>", "to", temp, ":", line.strip(), block_move_from_cfg[current_section], 'block?', temp in block_move_from_cfg[current_section])
                if temp in block_move_from_cfg[current_section]:
                    sections[current_section] += line
                elif temp == 'nam':
                    line = "\t" + line.strip()
                    sections[temp] += line
                elif temp == 'lim':
                    sections[temp] += mt.slash_to_limerick(line)
                else:
                    if temp in suffixes and temp in delete_marker:
                        sfs = section_from_suffix(line, exact=True)
                        if sfs:
                            line = re.sub(r'( zz| *#).*'.format(sfs), "", line, re.IGNORECASE)
                    sections[temp] += line
                if temp != current_section:
                    if current_section:
                        section_change += 1
                    else:
                        from_blank += 1
                continue
            if one_word_names and is_likely_name(line, current_section) and 'nam' not in local_block_move:
                if current_section:
                    print("    ----> NOTE: moved likely-name from section {} to \\nam at line {}: {}.".format(current_section, line_count, line.strip()))
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
                        if line_count == last_default + 1 and default_streak > 10:
                            overflow = True
                        else:
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
    print("{} section change{}, {} sorted from blank, {} to name-section from blank.".format(section_change, mt.plur(section_change), from_blank, to_names))
    if edit_blank_to_blank and len(blank_edit_lines):
        print("Lines to edit to put in section: {} total, list = {}".format(len(blank_edit_lines), mt.listnums(blank_edit_lines)))
        if overflow:
            print("NOTE: consecutive-line overflow (line not fitting in any section) was detected, so there may be a big chunk that is the result of one extra CR.")
        mt.npo(raw_long, blank_edit_lines[0])
    if len(dupe_edit_lines):
        print("Duplicate lines: {}".format(mt.listnums(dupe_edit_lines)))
        if not ignore_duplicate:
            print("If you are sure this is okay, the igdup option works. But it is hidden for a reason. You probably just want to put a comment after, or change things subtly.")
            mt.npo(raw_long, dupe_edit_lines[0])
    if len(old_names):
        new_names = re.split("\t+", sections['nam'].lower().strip())
        t1 = sorted(list(set(new_names) - set(old_names)))
        t2 = sorted(list(set(old_names) - set(new_names)))
        if len(t1) > 0:
            print(colorama.Fore.GREEN + "New names: {}".format(', '.join(["{}~{}".format(t1, name_line[t1])]) + colorama.Style.RESET_ALL))
        if len(t2) > 0:
            print(colorama.Fore.GREEN + "Old names deleted: {}".format(t2) + colorama.Style.RESET_ALL)
    if 'nam' in sections:
        sections['nam'] = re.sub("\n", "\t", sections['nam'].rstrip())
        sections['nam'] = "\t" + sections['nam'].lstrip()
        sections['nam'] = sanitize(sections['nam'])
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
        sections[x] = sections[x].rstrip()
        fout.write("\\{0}\n".format(x))
        fout.write(sections[x])
        if not sections[x]:
            fout.write("\n")
        elif x != 'nam':
            fout.write("\n\n")
    fout.close()
    mt.compare_alphabetized_lines(raw_long, temp_out_file, verbose = False, max_chars = -300, red_regexp = r"^[^\\\n$]", green_regexp = r"^([\\\n]|$)", show_bytes = True)
    for r in raw_sections:
        raw_sections[r] = raw_sections[r].rstrip()
    no_changes = os.path.exists(raw_long) and cmp(raw_long, temp_out_file)
    if no_changes:
        if verbose or read_most_recent: print(raw_long, "had no sortable changes since last run.")
        if pop_up_if_clean:
            messageBox2 = ctypes.windll.user32.MessageBoxA
            messageBox2(None, "Popup to mention that weekly file is sorted OK.\n\nThis should usually only be run at week's end.".encode('ascii'), "HOORAY!".encode('ascii'), 0x0)
    if show_stat_numbers:
        print("    {}: {}".format('  FULL' if no_changes else 'BEFORE', stats_of(raw_long)))
        without_names = os.stat(temp_out_file).st_size - len(sections['nam'])
        print("  NO NAMES: {}".format(stats_of(temp_out_file, to_exclude = 'nam')))
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
                print(colorama.Fore.YELLOW + "    Got rid of {}/{} characters/line{} from unsectioned.".format(raw_nums[''][0], raw_nums[''][1], mt.plur(raw_nums[''][1])) + colorama.Style.RESET_ALL) # no PLUR for characters since we can assume an idea has more than one character
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
        if test_no_copy:
            print("Not modifying", raw_long, "even though differences were found. Set -co to change this or add a Q to a parameter to get a verification question.")
            if show_differences:
                mt.wm(raw_long, temp_out_file)
            if ask_to_copy_back:
                x = input("Copy back? (Y does, anything else doesn't)")
                if x.strip().lower()[0] == 'y':
                    copy(temp_out_file, raw_long)
            else:
                print("Add q or g to question/get copy-back.")
            if only_one:
                if open_raw:
                    os.system(raw_long)
                print("Bailing, because flag for only one file was set, probably for testing. Again, set with -co to change this.")
                sys.exit()
        if mt.is_npp_modified(raw_long):
            if force_copy:
                print("Force-copying despite {} being unsaved in notepad++. I hope you know what you're doing, but you can always click <NO> and compare.")
                print("Original file saved to {}.".format(force_backup))
                copy(raw_long, force_backup)
            else:
                print("BAILING because {} is unsaved in notepad. You can copy over with -fc.".format(raw_long)) # do not put this option in usage, because I want to make sure I use it sparingly
                sys.exit()
        copy(temp_out_file, raw_long)
        if copy_then_test:
            print("OK, copied one, now testing another.")
            test_no_copy = True
            copy_then_test = False
            open_raw = True
            return 1
    if only_one:
        print("Bailing after first file converted, since only_one is set to True.")
        sys.exit()
    if open_raw:
        print("Opening raw", raw_long)
        os.system(raw_long)
    print("Opening", raw_long)
    os.system(raw_long)
    return 1

def is_outline_text(my_line):
    if my_line == '====':
        return True
    if my_line.startswith("\\"):
        return True
    return False

def deep_duplicate_delete():
    x = glob("c:/writing/daily/20*.txt")
    dupes = 0
    dupe_dict = defaultdict(list)
    for y in x[:-1]:
        bn = os.path.basename(y)
        with open(y) as file:
            for (line_count, line) in enumerate (file, 1):
                line_content = mt.strip_punctuation(line, remove_comments = True)
                if not line_content:
                    continue
                dupe_dict[line_content].append((bn, line_count))
    with open(x[-1]) as file:
        for (line_count, line) in enumerate (file, 1):
            line_content = mt.strip_punctuation(line, remove_comments = True)
            if is_outline_text(line_content):
                continue
            if line_content in dupe_dict:
                dupes += 1
                print(colorama.Fore.GREEN + "DUPLICATE {} {}".format(line_count, line.strip()) + colorama.Style.RESET_ALL)
                print('        ', ', '.join(["{} line {}".format(x[0], x[1]) for x in dupe_dict[line_content]]))
    if not dupes:
        print("no duplicates detected.")
    sys.exit()

files_done = 0
file_list = []
cmd_count = 1
max_files = 1
daily_files_back = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    num_of = mt.end_number_of(arg)
    if arg[0] == 'f' and arg[1:].isdigit():
        max_files = num_of
    elif arg[:2] == 'g=':
        raw_glob = arg[2:]
    elif arg == 'k' or arg == 'dk':
        what_to_sort = daily.KEEP
    elif arg == 'd' or arg == 'dr':
        what_to_sort = daily.DRIVE
    elif arg == 'a' or arg == 'da':
        what_to_sort = daily.DAILY
    elif arg == 'p' or arg == 'sp':
        sort_proc = True
    elif arg == 'ddd':
        deep_duplicate_delete()
    elif arg == 'py' or arg == 'yp':
        protect_yes_force = True
    elif arg == 'pn' or arg == 'np':
        protect_no_force = True
    elif arg == 'o' or arg == 'fo' or arg == 'of' or arg == 'f':
        only_list_files = True
    elif arg == 'puc':
        pop_up_if_clean = True
    elif arg == '1a':
        copy_then_test = True
        test_no_copy = False
        max_files = 2
    elif arg[:2] == 'lb':
        local_block_move.update(arg[3:].split(","))
    elif arg[:2] == 'lu':
        local_unblock_move.update(arg[3:].split(","))
    elif arg == 'c':
        sys.exit("While C is the natural command-line parameter for copy, we want to avoid accidents, so you need to type co.")
    elif arg == 'co':
        test_no_copy = False
    elif arg == 'te':
        test_no_copy = True
    elif arg == 'bu':
        bail_after_unchanged = True
    elif arg == 'n1':
        one_word_names = False
    elif arg == '1w' or arg == 'w1':
        one_word_names = True
    elif arg in ( 'l1', '1l' ):
        last_file_first = True
    elif arg in ( 'f1', '1f' ):
        last_file_first = False
    elif arg == 'vv':
        verbose = 2
    elif arg == 'v':
        verbose = 1
    elif arg == 'q':
        verbose = 0
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
    elif arg in ( 'nv', 'vn' ):
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
    elif arg == 'nbb' or arg == 'bbn':
        show_blank_to_blank = False
        edit_blank_to_blank = False
    elif arg == 'bw' or arg == 'wb':
        bail_on_warning = True
    elif arg == 'nbw' or arg == 'nwb' or arg == 'bwn' or arg == 'wbn':
        bail_on_warning = False
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
    elif mt.alpha_match(arg, 'ldq') or mt.alpha_match(arg, 'ldg') or arg == 'lq' or arg == 'lg':
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
    elif mt.alpha_match(arg, 'rdq') or mt.alpha_match(arg, 'rdg') or arg == 'rq' or arg == 'rg':
        read_most_recent = True
        dir_search_flag = daily.TOPROC
        ask_to_copy_back = True
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
    elif arg[:2] == 'rd' and arg[2:].isdigit():
        read_most_recent = True
        what_to_sort = daily.DAILIES
        dir_search_flag = daily.TOPROC
        daily_files_back = num_of
    elif arg[:2] == 'rf' and arg[2:].isdigit():
        read_most_recent = True
        dir_search_flag = daily.TOPROC
        daily_files_back = num_of
    elif arg == 'fc':
        force_copy = True
    elif arg[:2] == 'm=' or arg[:3] == 'mi=' or arg[:3] == 'mn=' or arg[:4] == 'min=':
        my_min_file = str(num_of)
        print("Minfile is now", my_min_file)
    elif arg[0:2] == 'ma=' or arg[0:2] == 'max=':
        my_max_file = str(num_of)
        print("Maxfile is now", my_max_file)
    elif arg == '?':
        usage()
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

if run_test_file:
    test_file_name = "c:/writing/temp/dff-test-file-{}.txt".format(test_file_index)
    sort_raw(test_file_name)
    sys.exit()

if not len(file_list):
    my_glob = "{}/{}".format(dir_to_scour, dailies_glob)
    file_list = glob(my_glob)
    print("Globbing", my_glob)

if read_most_recent:
    daily_count = 0
    for r in reversed(file_list):
        if not os.stat(r).st_size:
            print("Skipping over zero-byte file {} which we should delete.".format(r))
            continue
        daily_count += 1
        if daily_count == daily_files_back:
            sort_raw(r)
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
    files_done += sort_raw(fi)
    if files_done == max_files: break

if not files_done:
    print("No files sorted.")
