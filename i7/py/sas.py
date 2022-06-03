# sas.py: search all source for a specific string or regex

from collections import defaultdict
import re
import sys
import codecs
import os
import glob

import mytools as mt

default_string = "aqueduct"
my_string = ''

find_regex = False
print_full_rule = False

track_story_files = True
track_extension_files = True

cmd_count = 1

def usage(msg='General usage'):
    print('=' * 30 + msg)
    print("r  = print full rule")
    print("re = find regex not text")
    print("s  = track story files only, e/x = track extension files only")
    sys.exit()

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

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'r':
        print_full_rule = True
    elif arg == 're':
        find_regex = True
    elif arg == 's':
        track_story_files = True
        track_extension_files = False
    elif arg == ( 'e', 'x' ):
        track_story_files = False
        track_extension_files = True
    elif arg == '?':
        usage()
    elif len(arg) > 2:
        if my_string:
            sys.exit("Can only parse one string at once. {} cannot replace {}.".format(arg, my_string))
        else:
            my_string = arg
    else:
        usage('Bad command {}'.format(arg))
    cmd_count += 1

if not my_string:
    print("Using default string", default_string)
    my_string = default_string

done_dict = defaultdict(bool)

if track_story_files:
    ary = glob.glob("c:/games/inform/*.inform")
    done_dict.clear()
    for d in ary:
        if not os.path.isdir(d):
            continue
        temp = os.path.realpath(d)
        if temp in done_dict:
            print(temp, "already covered by another symlink")
            continue
        my_ni_file = os.path.join(d, "source", "story.ni")
        if not os.path.exists(my_ni_file):
            print("WARNING no story file", my_ni_file)
            continue
        look_for_string(my_string, my_ni_file)

if track_extension_files:
    ary = glob.glob("C:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/*.i7x")
    done_dict.clear()
    for a in ary:
        temp = os.path.realpath(a)
        if temp in done_dict:
            print(temp, "already covered by another symlink")
            continue
        else:
            done_dict[temp] = True
        look_for_string(my_string, a)