# sas.py: search all source for a specific string or regex

import re
import sys
import codecs
import os
import glob

my_string = "aqueduct"

find_regex = False
print_full_rule = False

track_story_files = True
track_extension_files = True

try:
    my_string = sys.argv[1]
    if my_string.startswith('r:'):
        my_string = my_string[2:]
        print_full_rule = True
    if my_string.startswith('/'):
        find_regex = True
        my_string = my_string[1:]
except:
    pass

def look_for_string(my_string, this_file):
    in_rule = False
    with codecs.open(this_file, "r", "utf-8", errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.strip():
                in_rule = False
            if find_regex:
                if re.search(my_string, line.lower()):
                    print(line_count, this_file, line.strip())
                    in_rule = True
                    continue
            else:
                if my_string.lower() in line.lower():
                    print(line_count, this_file, line.strip())
                    in_rule = True
                    continue
            if in_rule and print_full_rule:
                print(line_count, this_file, line.strip())

if track_story_files:
    ary = glob.glob("c:/games/inform/*.inform")
    for d in ary:
        if not os.path.isdir(d):
            continue
        my_ni_file = os.path.join(d, "source", "story.ni")
        if not os.path.exists(my_ni_file):
            print("WARNING no story file", my_ni_file)
            continue
        look_for_string(my_string, my_ni_file)

if track_extension_files:
    ary = glob.glob("C:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/*.i7x")
    for a in ary:
        look_for_string(my_string, a)