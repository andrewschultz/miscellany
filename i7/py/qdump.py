#
# qdump.py: quoted text dump from inform game source.
#
# alternate names: quick text dump, quick quote dump.
#
# arguments: qdump.py (project or abbreviation)
#
# to do: optionally get rid of line count?

import sys
import os
import re
import i7
import mytools as mt

global_ignore = set()
already_parsed = set()

show_lines = False

def print_quotes_of(my_file):
    print("Printing quotes for", my_file)
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if '"' not in line:
                continue
            x = line.lower().split('"')
            text_raw = ' '.join(x[1::2])
            text_raw = re.sub("\[.*.]", " ", text_raw)
            if show_lines:
                print(line_count, text_raw)
            else:
                print(text_raw)

def file_from_source(my_line):
    #print("Sourcing", my_line)
    a = my_line.split(' ')
    try:
        b = a.index('by')
    except:
        print("WARNING {} not parseable for file.".format(my_line))
        return ''
    start_title = ' '.join(a[1:b])
    author = ' '.join(a[b+1:])
    author = re.sub("\..*", "", author)
    try_1 = "c:/program files (x86)/Inform 7/Inform7/Extensions/{}/{}.i7x".format(author, start_title)
    try_2 = "C:/Users/Andrew/Documents/inform/Extensions/{}/{}.i7x".format(author, start_title)
    if os.path.exists(try_1):
        return try_1
    if os.path.exists(try_2):
        return try_2
    return ''

def short_look(file_name):
    return os.path.basename(file_name.lower()).replace('.i7x', '')

def headers_of(my_file):
    print("Headers in", my_file)
    base_match = short_look(my_file)
    if base_match in global_ignore:
        return set()
    if base_match in already_parsed:
        return set()
    already_parsed.add(base_match)
    this_set = set()
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            lls = line.lower().strip()
            if not lls.startswith("include"):
                continue
            if ' by ' not in lls:
                continue
            x = file_from_source(lls)
            if not x:
                mt.fail("Skipping line", lls)
                continue
            x_match = short_look(x)
            if x not in global_ignore and x_match not in already_parsed:
                this_set.add(x)
                this_set = this_set | headers_of(x)
    return this_set

def main_and_headers(file_names):
    new_set = set()
    for f in file_names:
        new_set = new_set | headers_of(f)
    return new_set

def get_cfg():
    qdump_cfg = "c:/writing/scripts/qdump.txt"
    if not os.path.exists(qdump_cfg):
        mt.warn("Could not open {} ... you may get more header files than you want.")
    with open(qdump_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('#'):
                continue
            if line.startswith(';'):
                break
            if not '=' in line:
                mt.warn("Line {} in {} needs =.".format(line_count, qdump_cfg))
            ary = line.lower().strip().split('=')
            myopt = ary[0]
            a2 = ary[1].split(',')
            if myopt in ('ignore', 'ignored'):
                global_ignore.add(set(a2))

project_specified = ''


cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg in ( 's', 'l', 'sl', 'ls' ):
        show_lines = True
    elif mt.alfmatch('nl', arg) or mt.alfmatch('ns', arg) or mt.alfmatch('nsl', arg):
        show_lines = False
    else:
        project_specified = arg
    cmd_count += 1

if project_specified:
    print("Going to", project_specified)
    i7.go_proj(project_specified)
    print(os.getcwd())

files_to_find = main_and_headers(["story.ni"])

for f in files_to_find:
    print_quotes_of(f)