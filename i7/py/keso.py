# keso.py
#
# sorts notes from google keep/drive and modifies them a bit if necessary
#
#
# todo: MAKE SURE THAT COMMENTS ARE SORTED TOO

TODO: Note if there were any changes if file already exists e.g. rewriting from raw to 2019333
also todo: -keep- files have special notes (?) / notifications. Is this in ld2?

import codecs
import os
import re
import sys
from collections import defaultdict
from fractions import gcd
from functools import reduce
import mytools as mt
from glob import glob

raw_dir = "c:/coding/perl/proj/from_drive"
done_dir = "c:/coding/perl/proj/from_drive/drive_mod"
raw_glob = "raw-*.txt"
important_file = "{0}/important.txt".format(raw_dir)

comment_cfg = "c:/writing/scripts/keso.txt"

cmds = defaultdict(str)
cmds['pal'] = "ni no ai"
cmds['ana'] = "ni an"
cmds['vvff'] = "ni no vv"
cmds['spo'] = "np spopal"

comment_sortable = defaultdict(str)

def in_important_file(x, y):
    with open(y) as file:
        for line in file:
            if x in line.lower(): return True
    return False

def my_section(l):
    if '\t' in l or l.count('  ') > 2: return 'nam'
    if mt.is_palindrome(l): return 'pal'
    if mt.is_anagram(l): return 'ana'
    if mt.is_limerick(l, accept_comments = True): return 'lim'
    if re.search(r'([0-9\*])\1+', l): return 'spo'
    if ' / ' in l: return 'vvff'
    if "#q" in l: return 'qui'
    if "#pc" in l: return 'pc'
    if "#wh" in l: return 'whau'
    if '==' in l: return 'btp'
    if "~" in l: return 'pl'
    if not re.search("[^a-z]", l): return 'nam'
    return ""

def sort_priority(x):
    prio_num = 0
    if x == 'nam': prio_num = 20
    if x == 'vvff': prio_num = 15
    return (prio_num, x)

def is_anagrammy_or_comments(x):
    if x.lower().startswith("anagram") or '#ana' in x.lower(): return True
    return mt.is_anagrammy(x)

def sort_raw(x):
    sections = defaultdict(str)
    if not os.path.exists(x):
        print("Skipping {0} which does not exist.".format(x))
        return
    x0 = os.path.basename(x)
    if not re.search("raw-drive-[0-9]+-[0-9]+-[0-9]+.txt", x0):
        print("Skipping {0} which is not in the raw-drive-##-##-#### format.".format(x))
        return
    y = x0[:-4].split('-')[2:]
    z = [int(q) for q in y]
    daily_file = "{:04d}{:02d}{:02d}.txt".format(z[2], z[0], z[1])
    # print(x0, daily_file)
    print("Parsing", x, "...")
    important = False
    with open(x, mode='r', encoding='utf-8-sig') as file:
        for (line_count, line) in enumerate(file, 1):
            if important:
                sections['important'] += line
                continue
            ll = line.strip().lower()
            if not ll: continue
            if line.startswith('IMPORTANT'):
                important = True
                continue
            temp = my_section(line)
            if temp:
                if temp == 'lim':
                    sections[temp] += mt.slash_to_limerick(line)
                else:
                    sections[temp] += line
                continue
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
    final_out_file = "{0}/{1}".format(done_dir, daily_file)
    temp_out_file = "c:/writing/temp/drive-temp.txt"
    fout = open(temp_out_file, "w")
    for x in sorted(sections, key=lambda x:sort_priority(x)):
        sections[x] = sections[x].rstrip()
        fout.write("\\{0}\n".format(x))
        fout.write(sections[x])
        if x != 'nam': fout.write("\n\n")
    if os.exists(final_out_file) and cmp(final_out_file, temp_out_file):
        print(final_out_file, "was not changed since last run.")
    else:
        copy(temp_out_file, final_out_file)
    fout.close()
    os.system(final_out_file)

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
    else: file_list.append(arg)
    count += 1

if not len(file_list):
    file_list = glob("{0}/{1}".format(raw_dir, raw_glob))
    for fi in file_list:
        if '6-26' not in fi: continue
        sort_raw(fi)
        files_done += 1
        if files_done == max_files: break
