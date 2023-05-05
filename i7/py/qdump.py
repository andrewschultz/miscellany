# qdump.py: quoted text dump from inform game source.

import sys
import os
import re
import i7

ignored = [ 'trivial niceties', 'intro restore skip', 'old school verb total carnage', 'basic screen effects' ]

global_include = set()

def print_quotes_of(my_file):
    print("Printing quotes for", my_file)
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if '"' not in line:
                continue
            x = line.lower().split('"')
            text_raw = ' '.join(x[1::2])
            text_raw = re.sub("\[.*.]", " ", text_raw)
            print(line_count, text_raw)

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
    return "c:/program files (x86)/Inform 7/Inform7/Extensions/{}/{}.i7x".format(author, start_title)

def headers_of(my_file, already_counted):
    bname = os.path.basename(my_file)
    if my_file in global_include:
        return set()
    if bname in ignored:
        return set()
    global_include.add(my_file)
    this_set = set()
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            lls = line.lower().strip()
            if not lls.startswith("include"):
                continue
            if ' by ' not in lls:
                continue
            x = file_from_source(lls)
            if x not in already_counted and x not in ignored:
                this_set.add(x)
                this_set = this_set | headers_of(x, already_counted)
    return this_set

def main_and_headers(file_names):
    new_set = set()
    for f in file_names:
        new_set = new_set | (headers_of(f, new_set))
    return new_set

project_specified = ''

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    project_specified = arg
    cmd_count += 1

if project_specified:
    print("Going to", project_specified)
    i7.go_proj(project_specified)
    print(os.getcwd())

files_to_find = main_and_headers(["story.ni"])

for f in files_to_find:
    print_quotes_of(f)