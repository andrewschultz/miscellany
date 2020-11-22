# dff.py: daily file find
#
# sorts notes from google keep/drive and modifies them a bit if necessary
#
#
# todo: MAKE SURE THAT COMMENTS ARE SORTED TOO

#TODO: Note if there were any changes if file already exists e.g. rewriting from raw to 2019333
#also todo: -keep- files have special notes (?) / notifications. Is this in ld2?

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

DEFAULT_SORT = 0

DAILY = DAILIES = 0
DRIVE = 1
KEEP = 2

daily_strings = ['daily', 'drive', 'keep']

what_to_sort = DEFAULT_SORT

my_cwd = os.getcwd()

dir_search_flag = daily.TOPROC

if 'daily' in my_cwd:
    print("Sorting DAILY stuff")
    what_to_sort = DAILY
elif 'keep' in my_cwd:
    print("Sorting KEEP stuff")
    what_to_sort = KEEP
elif 'drive' in my_cwd:
    print("Sorting DRIVE stuff")
    what_to_sort = DRIVE
else:
    what_to_sort = DEFAULT_SORT
    print("Default sorting", daily_strings[what_to_sort])

resort_already_sorted = True

sort_proc = False

# this should go in a config file later
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
verbose = True

bail_on_warnings = True

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

def usage(my_arg):
    if (my_arg):
        print("Bad argument", my_arg)
    print("=" * 50)
    print("DFF usage:")
    print()
    print("-a/da, -d/dr, -k/-dk specifies dAily, google Drive or google Keep downloads. Default is daily. dAily is useful at the end of each week.")
    print("co/te toggles the test-or-copy flag. 1a copies, then tests the next file in the directory.")
    print("-o/-fo/-of/-f only lists files.")
    print("-p/-sp forces sort-proc, meaning we sort a processed file. This is usually done only for daily files.")
    print("-bu bails after unchanged. Used for testing.")
    print("-n1/1w toggles one-word names in lines.")
    print("-v/-q is verbose/quiet")
    print()
    print("You can also list files you wish to look up.")
    exit()

def conditional_bail():
    if bail_on_warnings:
        sys.exit("Bailing on warning. Set -nbw to change this.")

def read_comment_cfg():
    any_warnings = False
    with open(comment_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            l = line.lower().strip()
            if l.startswith('#'): continue
            if l.startswith(';'): break
            if ':' not in l:
                print("Line", l, "needs colon prefix.")
                any_warnings = True
            if l[:2] == 'd:':
                delete_next = True
                l = l[2:]
            else:
                delete_next = False
            ary = mt.cfgary(l, delimiter='=')
            if len(ary) != 2:
                print("Bad comment/regex definition line", line_count, l)
                any_warnings = True
                continue
            entries = ary[0].split(",")
            if delete_next:
                for y in ary[0].split(','):
                    if y in delete_marker:
                        print("doubly deleted marker", y, "line", line_count)
                        any_warnings = True
                    else:
                        delete_marker[y] = True
            if l.startswith("keyword:"):
                section_words[ary[0]] = ary[1]
            elif l.startswith("delmar:"):
                for u in entries:
                    if u in delete_marker:
                        print("Duplicate delete-marker", u, "line", line_count)
                        any_warnings = True
                        continue
                    delete_marker[u] = ary[1]
            elif l.startswith("prefix:"):
                for u in entries:
                    if u in prefixes:
                        print("Duplicate prefix", u, "line", line_count)
                        any_warnings = True
                        continue
                    prefixes[u] = ary[1]
            elif l.startswith("suffix:"):
                for u in entries:
                    if u in suffixes:
                        print("Duplicate suffix", u, "line", line_count)
                        any_warnings = True
                        continue
                    suffixes[u] = ary[1]
            elif l.startswith("presuf") or l.startswith("sufpre"):
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
            elif l.startswith("fixmar:"):
                for u in entries:
                    if u in fixed_marker:
                        print("Duplicate save-marker", u, "line", line_count)
                        any_warnings = True
                        continue
                    fixed_marker[u] = ary[1]
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
        if os.path.exists(os.path.join(vp, fbn)): return True
    retval = False
    if ".txt" not in fbn:
        retval |= is_in_procs(fbn + ".txt")
    return retval

def is_likely_name(my_line, my_sec):
    if ' ' in my_line or '=' in my_line: return False
    if '/' in my_line and '(' not in my_line: return False
    if my_sec == 'por' or my_sec == 'oro' or my_sec == 'q': return False
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

def is_spoonerism_rated(l):
    double_digits = re.findall(r'([^0-9]([1-9])\2[^0-9])', l)
    for dig in double_digits:
        if ':' in dig[0] or '/' in dig[0]: return False
        if ' ' in dig[0]:
            if mt.uncommented_length(l) > len(double_digits) * 40:
                return False # this prevents odd cases where I just throw out the number 77
            return True
    return False

def is_risque_spoonerism(l):
    double_digits = re.findall(r'([^0-9]([0\*])(\2+)[^0-9])', l)
    for dig in double_digits:
        if ':' in dig[0] or '/' in dig[0]: continue
        if re.search("[fs]\*\*\*", dig[0], re.IGNORECASE): continue
        if '****' in dig: continue
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

def is_one_two_punch(l):
    if l.startswith("1") and (("2 " in l) or (" 2" in l)) and not l.startswith('12'): return True
    if " 1 " in l and " 2 " in l: return True
    return False

def is_repeated_text(l):
    l = l.lower()
    if not l[0].isalpha(): return False
    y = len(l) // 2
    return l[:y] == l[y:]

def my_section(l):
    l = l.strip()
    if mt.is_limerick(l, accept_comments = True): return 'lim' # this comes first because limericks are limericks
    if l.startswith('wfl'): return 'pc'
    if l.startswith('mov:') or l.startswith('movie:') or l.startswith('movies:'): return 'mov'
    if l.startswith('boo:') or l.startswith('book:') or l.startswith('books:'): return 'boo'
    temp = section_from_suffix(l, exact = True)
    if temp:
        return temp
    if '\t' in l or l.count('  ') > 2:
        if l.count(' ') - l.count('\t') > 2:
            print("LOOK OUT line may have errant tab(s):", l.strip())
        return 'nam'
    if mt.is_palindrome(l): return 'pal'
    if '==' in l and not l.startswith('=='): return 'btp'
    if is_risque_spoonerism(l): return 'sw'
    if is_spoonerism_rated(l): return 'spo'
    temp = smart_section(l)
    if temp:
        return temp
    if l.lower().startswith("if ") and "what a story" in l: return 'roo-was'
    if is_one_two_punch(l): return '12'
    if is_repeated_text(l): return 'py'
    if mt.is_anagram(l, accept_comments = True): return 'ana'
    # if "~" in l: return 'ut'
    if not re.search("[^a-z]", l): return 'nam'
    temp = section_from_suffix(l, exact = False)
    if temp:
        return temp
    return ""

def sort_priority(x):
    prio_num = 0
    if x == 'nam': prio_num = 20
    if x == 'vvff': prio_num = 15
    return (prio_num, x)

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

def sort_raw(raw_long):
    raw_long = os.path.normpath(raw_long)
    global test_no_copy
    global copy_then_test
    global open_raw
    sections = defaultdict(str)
    if is_locked(raw_long):
        print(raw_long, "has been locked for writing, skipping.")
        return 0
    important = False
    in_header = True
    header_to_write = ""
    current_section = ''
    with open(raw_long, mode='r', encoding='utf-8') as file:
        for (line_count, line) in enumerate(file, 1):
            if '\t' in line:
                line = re.sub("\t+$", "", line) # trivial fix for stuff at end of line
            if in_header:
                if line.startswith("#"):
                    header_to_write += line
                    continue
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
                current_section = ll[1:]
                continue
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
            temp = section_from_prefix(ll)
            if temp:
                if temp in prefixes and temp in delete_marker:
                    line = re.sub("^.*?:", "", line).lstrip()
                sections[temp] += line
                continue
            temp = my_section(line)
            if temp:
                if temp == 'nam':
                    line = "\t" + line.strip()
                    sections[temp] += line
                elif temp == 'lim':
                    sections[temp] += mt.slash_to_limerick(line)
                else:
                    if temp in suffixes and temp in delete_marker:
                        sfs = section_from_suffix(line, exact=True)
                        if sfs:
                            line = re.sub(r'( zz|#){}.*'.format(sfs), "", line, re.IGNORECASE)
                    sections[temp] += line
                continue
            if one_word_names and is_likely_name(line, current_section):
                sections['nam'] += "\t" + line.strip()
                continue
            if resort_already_sorted:
                if current_section:
                    sections[current_section] += line
                    continue
            sections['sh'] += line
    if 'nam' in sections:
        sections['nam'] = re.sub("\n", "\t", sections['nam'].rstrip())
        sections['nam'] = "\t" + sections['nam'].lstrip()
    if 'important' in sections:
        if in_important_file(raw_long, important_file):
            print("Not dumping text to", important_file, "as the text", raw_long, "is already in there.")
        else:
            fout = open(important_file, "a")
            fout.write("\nIMPORTANT STUFF from {0}:\n".format(raw_long))
            fout.write(sections['important'])
            fout.close()
        sections.pop('important')
    temp_out_file = "c:/writing/temp/drive-temp.txt"
    fout = open(temp_out_file, "w")
    fout.write(header_to_write)
    for x in sorted(sections, key=lambda x:sort_priority(x)): # note this is a tuple that's used to push current hot projects to the bottom
        sections[x] = sections[x].rstrip()
        fout.write("\\{0}\n".format(x))
        fout.write(sections[x])
        if x != 'nam': fout.write("\n\n")
    fout.close()
    mt.compare_alphabetized_lines(raw_long, temp_out_file, verbose = False)
    if os.path.exists(raw_long) and cmp(raw_long, temp_out_file):
        if verbose: print(raw_long, "was not changed since last run.")
        if bail_after_unchanged:
            if not verbose: print("Bailing after unchanged.")
            exit()
        return 0
    else:
        if test_no_copy:
            print("Not modifying", raw_long, "even though differences were found. Set -co to change this.")
            if show_differences:
                mt.wm(raw_long, temp_out_file)
            if only_one:
                if open_raw:
                    os.system(raw_long)
                print("Bailing, because flag for only one file was set, probably for testing. Again, set with -co to change this.")
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

files_done = 0
file_list = []
cmd_count = 1
max_files = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg[0] == 'f' and arg[1:].isdigit():
        max_files = int(arg[1:])
    elif arg[:2] == 'g=':
        raw_glob = arg[2:]
    elif arg == 'k' or arg == 'dk':
        what_to_sort = KEEP
    elif arg == 'd' or arg == 'dr':
        what_to_sort = DRIVE
    elif arg == 'a' or arg == 'da':
        what_to_sort = DAILY
    elif arg == 'p' or arg == 'sp':
        sort_proc = True
    elif arg == 'o' or arg == 'fo' or arg == 'of' or arg == 'f':
        only_list_files = True
    elif arg == '1a':
        copy_then_test = True
        test_no_copy = False
        max_files = 2
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
    elif arg == 'v':
        verbose = True
    elif arg == 'q':
        verbose = False
    elif arg == 'bw' or arg == 'wb':
        bail_on_warning = True
    elif arg == 'nbw' or arg == 'nwb' or arg == 'bwn' or arg == 'wbn':
        bail_on_warning = False
    elif arg == 'sb':
        dir_search_flag = daily.BACKUP
    elif arg == 'sr':
        dir_search_flag = daily.ROOT
    elif arg == 'st':
        dir_search_flag = daily.TOSORT
    elif arg == 'rd':
        read_recent_daily = True
        dir_search_flag = daily.ROOT        
    elif arg[0:2] == 'm=':
        my_min_file = arg[2:]
        print("Minfile is now", my_min_file)
    elif arg[0:2] == 'ma=':
        my_max_file = arg[2:]
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
        elif is_in_procs(arg):
            file_list.append(arg)
        else:
            print("WARNING", arg, "is not a readable file in any to-proc directory. Ignoring.")
    cmd_count += 1

if my_min_file > my_max_file: sys.exit("Min file specified >> max file specified. Bailing.")

if what_to_sort == DAILIES:
    dir_to_scour = raw_daily_dir
    sort_proc = True
elif what_to_sort == DRIVE:
    dir_to_scour = raw_drive_dir
elif what_to_sort == KEEP:
    dir_to_scour = raw_keep_dir
else:
    sys.exit("Unknown sorting type.")

if not os.path.exists(dir_to_scour):
    sys.exit("Can't open scour-directory {}.".format(dir_to_scour))

if "to-proc" not in dir_to_scour:
    print("Something happened that should not have. I am tacking on to-proc.")
    new_proc = os.path.join(dir_to_scour, "to-proc")
    if not os.path.exists(new_proc):
        sys.exit("Can't open scour-directory after tacking on to-proc: {}.".format(new_proc))
    dir_to_scour = new_proc

if dir_search_flag == daily.BACKUP:
    dir_to_scour = os.path.normpath(os.path.join(dir_to_scour, "../backup"))
elif dir_search_flag == daily.ROOT:
    dir_to_scour = os.path.normpath(os.path.join(dir_to_scour, ".."))

os.chdir(dir_to_scour)

read_comment_cfg()


if not len(file_list):
    my_glob = "{}/{}".format(dir_to_scour, dailies_glob)
    file_list = glob(my_glob)
    print("Globbing", my_glob)

if read_recent_daily:
    sort_raw(file_list[-1])
    exit()

list_count = 0
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
