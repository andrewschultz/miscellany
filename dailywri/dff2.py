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
from fractions import gcd
from functools import reduce
import mytools as mt
from glob import glob
from filecmp import cmp
from shutil import copy

DAILY = DAILIES = 0
DRIVE = 1
KEEP = 2

what_to_sort = DRIVE
sort_proc = False

# this should go in a config file later if we have time
open_raw = True
only_one = True
see_drive_files = True
test_no_copy = True
only_list_files = False
show_differences = True

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

def usage(my_arg):
    if (my_arg):
        print("Bad argument", my_arg)
    print("=" * 50)
    print("DFF usage:")
    print()
    print("-a/-d/-k specifies dAily, google Drive or google Keep downloads. Default is Google Drive. dAily is useful at the end of each week.")
    print("co/te toggles the test-or-copy flag.")
    print("-o/-fo/-of/-f only lists files.")\
    print("-p/-sp forces sort-proc, meaning we sort a processed file. This is usually done only for daily files.")
    print()
    print("You can also list files you wish to look up.")
    exit()

def read_comment_cfg():
    with open(comment_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            l = line.lower().strip()
            if l.startswith('#'): continue
            if l.startswith(';'): break
            ary = l.split('=')
            if len(ary) != 2:
                print("Bad comment/regex definition line", line_count, l)
                continue
            comment_dict[ary[0]] = ary[1]

def in_important_file(x, y):
    with open(y) as file:
        for line in file:
            if x in line.lower(): return True
    return False

def special_colon_value(l):
    if l.startswith("btp:"): return "btp"
    if l.startswith("mov:") or l.startswith("movie:"): return "mov"
    if l.startswith("song:") or l.startswith("song:"): return "mov"
    return ""

def is_spoonerism_rated(l):
    return re.search(r'\b([0-9])\1\b', l) or ('**' in l and not '***' in l) # we can filter out anything with extra ** in it

def my_section(l):
    if mt.is_limerick(l, accept_comments = True): return 'lim' # this comes first because limericks are limericks
    if l.startswith('wfl'): return 'pc'
    if l.startswith('mov:') or l.startswith('movie:') or l.startswith('movies:'): return 'mov'
    if l.startswith('boo:') or l.startswith('book:') or l.startswith('books:'): return 'boo'
    for x in comment_dict:
        if re.search(r'# *({})\b'.format(comment_dict[x]), l):
            return x
    if '\t' in l or l.count('  ') > 2: return 'nam'
    if mt.is_palindrome(l): return 'pal'
    if '==' in l and not l.startswith('=='): return 'btp'
    if mt.is_anagram(l, accept_comments = True) and not is_spoonerism_rated(l): return 'ana'
    if is_spoonerism_rated(l): return 'spo'
    if "~" in l: return 'ut'
    if not re.search("[^a-z]", l): return 'nam'
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

def is_anagrammy_or_comments(x):
    if x.lower().startswith("anagram") or '#ana' in x.lower(): return True
    return mt.is_anagrammy(x)

def sort_raw(raw_long):
    sections = defaultdict(str)
    if not os.path.exists(raw_long):
        print("Skipping {0} which does not exist.".format(raw_long))
        return 0
    x0 = os.path.basename(raw_long)
    if ".bak" in x0:
        print("Badly named file", x0, "skipped")
    y = x0[:-4].split('-')[2:]
    z = [int(q) for q in y]
    if what_to_sort == DAILIES:
        final_out_file = raw_long
    else:
        daily_file = "{:04d}{:02d}{:02d}.txt".format(z[2], z[0], z[1])
        final_out_file = "{0}/{1}".format(drive_proc_dir, daily_file)
    if is_locked(final_out_file):
        print(final_out_file, "has been locked for writing, skipping.")
        return 0
    print("Parsing", raw_long, "...")
    important = False
    in_header = True
    header_to_write = ""
    current_section = ''
    with open(raw_long, mode='r', encoding='utf-8-sig') as file:
        for (line_count, line) in enumerate(file, 1):
            if in_header:
                if line.startswith("#"):
                    header_to_write += line
                    continue
                in_header = False
                if header_to_write:
                    header_to_write += "\n"
            if important:
                if not line.strip: line = "blank line ---\n"
                sections['important'] += line
                continue
            ll = line.strip().lower()
            if ll.startswith("\\"):
                current_section = ll[1:]
                continue
            if not ll:
                current_section = ''
                continue
            if current_section:
                sections[current_section] += line
                continue
            if line.startswith('IMPORTANT'):
                important = True
                continue
            temp = special_colon_value(ll)
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
            else:
                sections['sh'] += line
    if 'nam' in sections:
        sections['nam'] = re.sub("\n", "\t", sections['nam'].rstrip())
        sections['nam'] = "\t" + sections['nam'].lstrip()
    if 'important' in sections:
        if in_important_file(raw_long, important_file):
            print("Not dumping text to", important_file, "as it's already in there.")
        else:
            fout = open(important_file, "w")
            fout.write("From {0}:\n".format(raw_long))
            fout.write(sections['important'])
            fout.close()
        sections.pop('important')
    temp_out_file = "c:/writing/temp/drive-temp.txt"
    fout = open(temp_out_file, "w")
    fout.write(header_to_write)
    for x in sorted(sections, key=lambda x:sort_priority(x)):
        sections[x] = sections[x].rstrip()
        fout.write("\\{0}\n".format(x))
        fout.write(sections[x])
        if x != 'nam': fout.write("\n\n")
    fout.close()
    mt.compare_alphabetized_lines(raw_long, temp_out_file)
    if os.path.exists(final_out_file) and cmp(final_out_file, temp_out_file):
        print(final_out_file, "was not changed since last run.")
        exit()
        return 0
    else:
        if test_no_copy:
            print("Not copying to", final_out_file, "even though differences were found.")
            if show_differences:
                mt.wm(raw_long, temp_out_file)
            if only_one:
                print("Bailing, because flag for only one file was set, probably for testing.")
                sys.exit()
        copy(temp_out_file, final_out_file)
    if only_one:
        print("Bailing after first file converted, since only_one is set to True.")
        sys.exit()
    print(open_raw, raw_long)
    if open_raw:
        print("Opening raw", raw_long)
        os.system(raw_long)
    print("Opening", final_out_file)
    os.system(final_out_file)
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

os.chdir(dir_to_scour)

read_comment_cfg()

if not len(file_list):
    my_glob = "{}/{}".format(dir_to_scour, dailies_glob if what_to_sort == DAILIES else raw_glob)
    file_list = glob(my_glob)
    print("Globbing", my_glob)

for fi in file_list:
    if only_list_files:
        print(fi)
        continue
    files_done += sort_raw(fi)
    if files_done == max_files: break
