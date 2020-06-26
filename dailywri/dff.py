# dff.py: daily file find
#
# sorts notes from google keep/drive and modifies them a bit if necessary
#
#
# todo: MAKE SURE THAT COMMENTS ARE SORTED TOO

#TODO: Note if there were any changes if file already exists e.g. rewriting from raw to 2019333
#also todo: -keep- files have special notes (?) / notifications. Is this in ld2?

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
open_raw = True
only_one = True
bail_after_unchanged = False
see_drive_files = True
test_no_copy = True
only_list_files = False
show_differences = True
my_min_file = "20170000.txt"
my_max_file = "21000000.txt"

raw_drive_dir = "c:/coding/perl/proj/from_drive"
drive_proc_dir = "c:/coding/perl/proj/from_drive/to-proc"
raw_keep_dir = "c:/coding/perl/proj/from_keep"
keep_proc_dir = "c:/coding/perl/proj/from_keep/to-proc"
daily_proc_dir = "c:/writing/daily/to-proc"
raw_glob = "raw-*.txt"
dailies_glob = "20*.txt"
important_file = "{0}/important.txt".format(raw_drive_dir)

comment_cfg = "c:/writing/scripts/keso.txt"

cmds = defaultdict(str)
cmds['pal'] = "ni no ai"
cmds['ana'] = "ni an"
cmds['vvff'] = "ni no vv"
cmds['spo'] = "np spopal"

comment_dict = defaultdict(str)
section_words = defaultdict(str)
prefixes = defaultdict(str)

def usage(my_arg):
    if (my_arg):
        print("Bad argument", my_arg)
    print("=" * 50)
    print("DFF usage:")
    print()
    print("-a/-d/-k specifies dAily, google Drive or google Keep downloads. Default is Google Drive. dAily is useful at the end of each week.")
    print("co/te toggles the test-or-copy flag.")
    print("-o/-fo/-of/-f only lists files.")
    print("-p/-sp forces sort-proc, meaning we sort a processed file. This is usually done only for daily files.")
    print("-bu bails after unchanged. Used for testing.")
    print()
    print("You can also list files you wish to look up.")
    exit()

def read_comment_cfg():
    with open(comment_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            l = line.lower().strip()
            if l.startswith('#'): continue
            if l.startswith(';'): break
            if ':' not in l:
                print("Line", l, "needs colon prefix.")
                continue
            ary = mt.cfgary(l, delimiter='=')
            if len(ary) != 2:
                print("Bad comment/regex definition line", line_count, l)
                continue
            if l.startswith("keyword:"):
                section_words[ary[0]] = ary[1]
            elif l.startswith("prefix:"):
                for u in ary[0].split(','):
                    if u in prefixes:
                        print("Duplicate", u, "line", line_count)
                        continue
                    prefixes[u] = ary[1]
            elif l.startswith("suffix:"):
                comment_dict[ary[0]] = ary[1]
            else:
                print("ERROR bad colon/cfg definition line", line_count, ary[0])

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
    double_digits = re.findall(r'\b([1-9])\1\b', l)
    if not len(double_digits): return False
    if mt.uncommented_length(l) > len(double_digits) * 60: return False # this prevents odd cases where I just throw out the number 77
    return True

def is_risque_spoonerism(l):
    return '**' in l and '***' not in l

def comment_section(my_line, exact = False):
    for x in comment_dict:
        if re.search(r'# *({}){}'.format(comment_dict[x], r'\b' if exact else ''), my_line, re.IGNORECASE):
            return x
    return ""

def smart_section(my_line):
    for sw in section_words:
        search_string = r'\b{}\b'.format(sw)
        if re.search(search_string, my_line, re.IGNORECASE):
            return section_words[sw]
    return ""

def my_section(l):
    if mt.is_limerick(l, accept_comments = True): return 'lim' # this comes first because limericks are limericks
    if l.startswith('wfl'): return 'pc'
    if l.startswith('mov:') or l.startswith('movie:') or l.startswith('movies:'): return 'mov'
    if l.startswith('boo:') or l.startswith('book:') or l.startswith('books:'): return 'boo'
    temp = comment_section(l, exact = True)
    if temp:
        return temp
    if '\t' in l or l.count('  ') > 2: return 'nam'
    if mt.is_palindrome(l): return 'pal'
    if '==' in l and not l.startswith('=='): return 'btp'
    if is_risque_spoonerism(l): return 'sw'
    if is_spoonerism_rated(l): return 'spo'
    temp = smart_section(l)
    if temp:
        return temp
    if mt.is_anagram(l, accept_comments = True): return 'ana'
    if "~" in l: return 'ut'
    if not re.search("[^a-z]", l): return 'nam'
    temp = comment_section(l, exact = False)
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
    sections = defaultdict(str)
    if is_locked(raw_long):
        print(raw_long, "has been locked for writing, skipping.")
        return 0
    print("Parsing", raw_long, "...")
    important = False
    in_header = True
    header_to_write = ""
    current_section = ''
    with open(raw_long, mode='r', encoding='utf-8') as file:
        for (line_count, line) in enumerate(file, 1):
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
            if not resort_already_sorted:
                if current_section:
                    sections[current_section] += line
                    continue
            temp = section_from_prefix(ll)
            if temp:
                sections[temp] += line
                continue
            temp = my_section(line)
            if temp:
                if temp == 'lim':
                    sections[temp] += mt.slash_to_limerick(line)
                else:
                    sections[temp] += line
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
            print("Not dumping text to", important_file, "as it's already in there.")
        else:
            fout = open(important_file, "a")
            fout.write("From {0}:\n".format(raw_long))
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
        print(raw_long, "was not changed since last run.")
        if bail_after_unchanged:
            exit()
        return 0
    else:
        if test_no_copy:
            print("Not modifying", raw_long, "even though differences were found. Set -co to change this.")
            if show_differences:
                mt.wm(raw_long, temp_out_file)
            if only_one:
                print("Bailing, because flag for only one file was set, probably for testing. Again, set with -co to change this.")
                sys.exit()
        copy(temp_out_file, raw_long)
    if only_one:
        print("Bailing after first file converted, since only_one is set to True.")
        sys.exit()
    print(open_raw, raw_long)
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
    elif arg == 'k':
        what_to_sort = KEEP
    elif arg == 'd':
        what_to_sort = DRIVE
    elif arg == 'a':
        what_to_sort = DAILY
    elif arg == 'p' or arg == 'sp':
        sort_proc = True
    elif arg == 'o' or arg == 'fo' or arg == 'of' or arg == 'f':
        only_list_files = True
    elif arg == 'co':
        test_no_copy = False
    elif arg == 'te':
        test_no_copy = True
    elif arg == 'bu':
        bail_after_unchanged = True
    elif arg[0:2] == 'm=':
        my_min_file = arg[2:]
        print("minfile", my_min_file)
    elif arg == '?':
        usage()
    elif len(arg) < 2:
        usage(arg)
    else:
        if not os.path.exists(arg) and not os.path.exists(os.path.join(raw_drive_dir, arg)):
            print("WARNING", arg, "is not a valid file")
        else:
            file_list.append(arg)
    cmd_count += 1

if what_to_sort == DAILIES:
    dir_to_scour = daily_proc_dir
    sort_proc = True
elif what_to_sort == DRIVE:
    dir_to_scour = raw_drive_dir
elif what_to_sort == KEEP:
    dir_to_scour = raw_keep_dir
else:
    sys.exit("Unknown sorting type.")

dir_to_scour += "/to-proc"

os.chdir(dir_to_scour)

read_comment_cfg()

if not len(file_list):
    my_glob = "{}/{}".format(dir_to_scour, dailies_glob)
    file_list = glob(my_glob)
    print("Globbing", my_glob)

for fi in file_list:
    fbn = os.path.basename(fi)
    if fbn < my_min_file:
        continue
    if fbn > my_max_file:
        continue
    if only_list_files:
        print(fi)
        continue
    files_done += sort_raw(fi)
    if files_done == max_files: break

if not files_done:
    print("No files sorted.")
