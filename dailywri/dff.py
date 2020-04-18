# dff.py
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

only_one = False
see_drive_files = True

raw_drive_dir = "c:/coding/perl/proj/from_drive"
drive_proc_dir = "c:/coding/perl/proj/from_drive/to-proc"
raw_keep_dir = "c:/coding/perl/proj/from_keep"
keep_proc_dir = "c:/coding/perl/proj/from_keep/to-proc"
raw_glob = "raw-*.txt"
important_file = "{0}/important.txt".format(raw_drive_dir)

comment_cfg = "c:/writing/scripts/keso.txt"

cmds = defaultdict(str)
cmds['pal'] = "ni no ai"
cmds['ana'] = "ni an"
cmds['vvff'] = "ni no vv"
cmds['spo'] = "np spopal"

comment_dict = defaultdict(str)

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
    return re.search(r'([0-9\*])\1+ ', l)

def my_section(l):
    for x in comment_dict:
        if re.search(r'#( )?{}\b'.format(comment_dict[x]), l):
            return x
    if '\t' in l or l.count('  ') > 2: return 'nam'
    if mt.is_palindrome(l): return 'pal'
    if '==' in l and not l.startswith('=='): return 'btp'
    if mt.is_anagram(l, accept_comments = True) and not is_spoonerism_rated(l): return 'ana'
    if mt.is_limerick(l, accept_comments = True): return 'lim'
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

def sort_raw(x):
    sections = defaultdict(str)
    if not os.path.exists(x):
        print("Skipping {0} which does not exist.".format(x))
        return
    x0 = os.path.basename(x)
    if not re.search("raw-(drive|keep)-[0-9]+-[0-9]+-[0-9]+.txt", x0):
        print("Skipping {0} which is not in the raw-drive/keep-##-##-#### format.".format(x))
        return
    y = x0[:-4].split('-')[2:]
    z = [int(q) for q in y]
    daily_file = "{:04d}{:02d}{:02d}.txt".format(z[2], z[0], z[1])
    # print(x0, daily_file)
    final_out_file = "{0}/{1}".format(drive_proc_dir, daily_file)
    if is_locked(final_out_file):
        print(final_out_file, "has been locked for writing, skipping.")
        return 0
    return 0
    print("Parsing", x, "...")
    important = False
    with open(x, mode='r', encoding='utf-8-sig') as file:
        for (line_count, line) in enumerate(file, 1):
            if important:
                if not line.strip: line = "blank line ---\n"
                sections['important'] += line
                continue
            ll = line.strip().lower()
            if ll.startswith("\\"):
                mt.npo(x, line_count)
                print("Uh oh. You can't start with a backslash. Change to something else. {0} line {1}".format(os.path.basename(x), line_count))
            if not ll: continue
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
        sections['nam'] = "\t" + sections['nam']
    if 'important' in sections:
        if in_important_file(x, important_file):
            print("Not dumping text to", important_file, "as it's already in there.")
        else:
            fout = open(important_file, "w")
            fout.write("From {0}:\n".format(x))
            fout.write(sections['important'])
            fout.close()
        sections.pop('important')
    temp_out_file = "c:/writing/temp/drive-temp.txt"
    fout = open(temp_out_file, "w")
    for x in sorted(sections, key=lambda x:sort_priority(x)):
        sections[x] = sections[x].rstrip()
        fout.write("\\{0}\n".format(x))
        fout.write(sections[x])
        if x != 'nam': fout.write("\n\n")
    fout.close()
    if os.path.exists(final_out_file) and cmp(final_out_file, temp_out_file):
        print(final_out_file, "was not changed since last run.")
        return 0
    else:
        copy(temp_out_file, final_out_file)
    if only_one:
        print("Bailing after first file converted, since only_one is set to True.")
        sys.exit()
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
        see_drive_files = False
    elif arg == 'd':
        see_drive_files = True
    else:
        if not os.path.exists(arg) and not os.path.exists(os.path.join(raw_drive_dir, arg)):
            print("WARNING", arg, "is not a valid file")
        else:
            file_list.append(arg)
    cmd_count += 1

if see_drive_files:
    os.chdir(raw_drive_dir)
else:
    os.chdir(raw_keep_dir)

read_comment_cfg()

if not len(file_list):
    file_list = glob("{0}/{1}".format(raw_drive_dir, raw_glob))
    for fi in file_list:
        files_done += sort_raw(fi)
        if files_done == max_files: break
