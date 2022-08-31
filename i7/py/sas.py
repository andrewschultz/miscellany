#
# sas.py: search all source for a specific string or regex in story.ni or extension files
#
# created 4/21/2022, put in source control 6/8/2022
#
# todo: search for more than just "table" if necessary for only_critical_lines
# todo: 'use' and 'um' can both be put in a preformed_regex dictionary
# todo: have a list of ignorable directories (probably in i7)
# todo: force only-critical-lines with option
# todo: verbose/debug

from collections import defaultdict
import re
import sys
import codecs
import os
import glob
import colorama

import mytools as mt
import i7

default_string = "aqueduct"
my_string = ''

find_regex = False
print_full_rule = True

track_story_files = True
track_extension_files = True

post_open = False

local_max_open = 5
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
        print(colorama.Fore.YELLOW + "{} CODE CHUNK HEADER {}".format(line_list, first_rule_line) + colorama.Style.RESET_ALL)
    else:
        print(colorama.Fore.YELLOW + "Lone line {}".format(count_start) + colorama.Style.RESET_ALL)
    print(colorama.Fore.GREEN + the_string + colorama.Style.RESET_ALL)

def look_for_string(my_string, this_file):
    print_this_rule = False
    full_chunk_string = ''
    critical_chunk_string = ''
    first_rule_line_count = 0
    in_table = False
    file_yet = False
    with codecs.open(this_file, "r", "utf-8", errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.strip():
                if print_this_rule:
                    if not file_yet:
                        print("Matches for", this_file)
                        file_yet = True
                    print_my_rules(first_rule_line_count, line_count - 1, critical_chunk_string if in_table else full_chunk_string)
                print_this_rule = False
                full_chunk_string = ''
                critical_chunk_string = ''
                in_table = False
            else:
                if not full_chunk_string:
                    first_rule_line_count = line_count
                if not full_chunk_string and line.startswith("table of"):
                    in_table = True
                elif not full_chunk_string:
                    critical_chunk_string += line
                full_chunk_string += line
            if find_regex:
                if re.search(my_string, line.lower()):
                    mt.add_postopen(this_file, line_count)
                    if print_full_rule:
                        print_this_rule = True
                        critical_chunk_string += line
                    else:
                        print(line_count, this_file, line.strip())
                    continue
            else:
                if my_string.lower() in line.lower():
                    mt.add_postopen(this_file, line_count)
                    if print_full_rule:
                        print_this_rule = True
                        critical_chunk_string += line
                    else:
                        print(line_count, this_file, line.strip())
                    continue
    if print_this_rule:
        if not file_yet:
            print("Matches for", this_file)
        print_my_rules(first_rule_line_count, 'END', critical_chunk_string if in_table else full_chunk_string)

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
    elif arg in ('p', 'op', 'po'):
        post_open = True
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
        db = os.path.basename(d)
        if db.lower() in i7.i7ignore or re.sub("\..*", "", db.lower()) in i7.i7ignore:
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

if post_open:
    mt.postopen_files(max_opens = local_max_open)
else:
    print("There are source files you could post-open with p/op/po.")
