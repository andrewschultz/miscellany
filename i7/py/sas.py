#
# sas.py: search all source for a specific string or regex in story.ni or extension files
#
# created 4/21/2022, put in source control 6/8/2022
#

from collections import defaultdict
import re
import sys
import codecs
import os
import glob
import colorama

import mytools as mt

default_string = "aqueduct"
my_string = ''

find_regex = False
print_full_rule = True

track_story_files = True
track_extension_files = True

cmd_count = 0

def usage(msg='General usage'):
    print('=' * 30 + msg)
    print("sas has semantic regex detection for regexes, so you don't need to specify any options below.")
    print("However, if you do, they will override its semantic detection, so if you want to look for a string with a backslash, rn a\\b and a\\b rn are identical.")
    print("r  = print full rule, l = print line.")
    print("re = find regex not text, rn/nr turns it off.")
    print("s  = track story files only, e/x = track extension files only.")
    print("custom strings: um/use = \\buse max, for detecting deprecated Inform compiler constants.")
    sys.exit()

def is_likely_regex(my_string):
    return '[' in my_string or ']' in my_string or '.' in my_string or '(' in my_string or ')' in my_string or '*' in my_string or '\\' in my_string

def print_my_rules(count_start, count_end, the_string):
    the_string = the_string.rstrip()
    lines_to_write = the_string.split("\n")
    first_rule_line = lines_to_write[0]
    if len(lines_to_write) > 1:
        line_list = "Lines {}-{}".format(count_start, count_end)
        print(colorama.Fore.YELLOW + "{} RULE HEADER {}".format(line_list, first_rule_line) + colorama.Style.RESET_ALL)
    else:
        print(colorama.Fore.YELLOW + "Lone line {}".format(count_start) + colorama.Style.RESET_ALL)
    print(colorama.Fore.GREEN + the_string + colorama.Style.RESET_ALL)

def look_for_string(my_string, this_file):
    print_this_rule = False
    this_rule_string = ''
    first_rule_line_count = 0
    with codecs.open(this_file, "r", "utf-8", errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.strip():
                if print_this_rule:
                    print_my_rules(first_rule_line_count, line_count - 1, this_rule_string)
                print_this_rule = False
                this_rule_string = ''
            else:
                if not this_rule_string:
                    first_rule_line_count = line_count
                this_rule_string += line
            if find_regex:
                if re.search(my_string, line.lower()):
                    if print_full_rule:
                        print_this_rule = True
                    else:
                        print(line_count, this_file, line.strip())
                    continue
            else:
                if my_string.lower() in line.lower():
                    if print_full_rule:
                        print_this_rule = True
                    else:
                        print(line_count, this_file, line.strip())
                    continue
    if print_this_rule:
        print_my_rules(first_rule_line_count, 'END', this_rule_string)

param_array = sys.argv[1:]

# first, we pull the potential regex string.
# This could be done in the while loop, but it'd potentially cause the is_likely_regex to overwrite user parameters

for x in param_array:
    if len(x) > 2:
        if my_string:
            sys.exit("Can only parse one string at once. {} cannot replace {}.".format(arg, my_string))
        else:
            my_string = x
            print("Looking for", my_string)
            if is_likely_regex(my_string):
                print("Assuming regex due to special character e.g. [].()*")
                find_regex = True
            param_array.remove(x)

while cmd_count < len(param_array):
    arg = mt.nohy(param_array[cmd_count])
    if arg == 'r':
        print_full_rule = True
    elif arg == 'l':
        print_full_rule = False
    elif arg == 're':
        find_regex = True
    elif arg in ( 'nr', 'rn' ):
        find_regex = False
    elif arg == 's':
        track_story_files = True
        track_extension_files = False
    elif arg in ( 'e', 'x' ):
        track_story_files = False
        track_extension_files = True
    elif arg in ( 'um', 'use' ):
        my_string = r"\buse max_"
        find_regex = True
    elif arg == '?':
        usage()
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