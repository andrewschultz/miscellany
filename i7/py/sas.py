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

fullname = { 'ab':'abouting',
  'cr':'creditsing',
  've':'verbsing',
  'ta':'table of',
}

default_string = "aqueduct"
my_string = ''

find_regex = False
print_full_rule = True

track_story_files = True
track_extension_files = True

post_open = False

local_max_open = 5
cmd_count = 0

my_sections = []

def usage(msg='General usage'):
    print('=' * 30 + msg)
    print("sas has semantic regex detection for regexes. However, you can force detection in various ways.")
    print("r=(text) means regex, a=(text) means absolute text.")
    print()
    print("re = find regex not text, rn/nr finds text not regex. They can be placed before or after the string.")
    print("To see rarer options, go with ??.")
    print()
    print("To see examples of tricky regexes, go with ?x and x?.")
    sys.exit()

def usage_rarer():
    print('=' * 30 + "rarer options")
    print("r  = print full rule, l = print line.")
    print("s  = track story files only, e/x = track extension files only.")
    print("custom strings: um/use = \\buse max, for detecting deprecated Inform compiler constants.")
    sys.exit()

def usage_examples():
    print("Remember, for exact quotes, if your string has a space, you need to put quotes around it e.g. sas \"shuffling around\"")
    print()
    print("Regexes with the or operator need to be of the form sas.py Andrew^|Schultz for Windows command line. That's the main one, but ^ is the general escape character.")
    sys.exit()

def is_likely_regex(my_string):
    for x in '[].(){{}}*\\|':
        if x in my_string:
            return True
    return False

def print_my_rules(count_start, count_end, the_string, table_name = ''):
    the_string = the_string.rstrip()
    lines_to_write = the_string.split("\n")
    first_rule_line = lines_to_write[0]
    if len(lines_to_write) > 1:
        line_list = "Lines {}-{}".format(count_start, count_end)
        mt.warn("{} CODE CHUNK HEADER {}".format(line_list, first_rule_line))
    elif table_name:
        mt.warn("{} line {}".format(table_name, count_start))
    else:
        mt.warn("Lone line {}".format(count_start))
    mt.okay(the_string)

def matchable(my_line, my_sects):
    if not my_sects:
        return True
    for s in my_sects:
        if s in my_line:
            return True
    return False

def look_for_string(my_string, this_file, sections = []):
    print_this_rule = False
    line_count_to_open = 0
    full_chunk_string = ''
    critical_chunk_string = ''
    first_rule_line_count = 0
    in_table = False
    file_yet = False
    table_name = ''
    if not os.path.exists(this_file):
        mt.warn("WARNING: couldn't access {}. Possible bad symlink. Skipping.".format(this_file))
        return
    with codecs.open(this_file, "r", "utf-8", errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.strip():
                if print_this_rule:
                    if matchable(my_first_line, sections):
                        if not file_yet:
                            print("Matches for", this_file)
                            file_yet = True
                        print_my_rules(first_rule_line_count, line_count - 1, critical_chunk_string if in_table else full_chunk_string, table_name = table_name)
                        mt.add_postopen(this_file, line_count_to_open)
                print_this_rule = False
                full_chunk_string = ''
                critical_chunk_string = ''
                in_table = False
                table_name = ''
                line_count_to_open = 0
                continue
            if not full_chunk_string:
                my_first_line = line.strip()
                first_rule_line_count = line_count
            if not full_chunk_string and line.startswith("table of"):
                in_table = True
                table_name = i7.zap_i7_comments(line)
            elif not full_chunk_string:
                critical_chunk_string += line
            full_chunk_string += line
            if find_regex:
                if re.search(my_string, line.lower()):
                    line_count_to_open = line_count
                    if print_full_rule:
                        print_this_rule = True
                        critical_chunk_string += line
                    else:
                        print(line_count, this_file, line.strip())
                    continue
            else:
                if my_string.lower() in line.lower():
                    line_count_to_open = line_count
                    if print_full_rule:
                        print_this_rule = True
                        critical_chunk_string += line
                    else:
                        print(line_count, this_file, line.strip())
                    continue
    if print_this_rule:
        if not file_yet:
            print("Matches for", this_file)
        print_my_rules(first_rule_line_count, 'END', critical_chunk_string if in_table else full_chunk_string, table_name = table_name)

param_array = sys.argv[1:]

# first, we pull the potential regex string.
# This could be done in the while loop, but it'd potentially cause the is_likely_regex to overwrite user parameters

for x in param_array:
    if len(x) > 2:
        if my_string:
            sys.exit("Can only parse one string at once. {} cannot replace {}.".format(arg, my_string))
        elif x.startswith('r=') or x.startswith('a='):
            pass
        else:
            my_string = x
            print("Looking for", my_string)
            if is_likely_regex(my_string):
                mt.warn("Assuming regex due to special character e.g. [].()* ... if you want to fix things, use r= or a=.")
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
    elif arg.startswith('r='):
        if arg == 'r=':
            mt.bailfail("Need to define a regex after r=.")
        find_regex = True
        my_string = arg[2:]
    elif arg.startswith('a='):
        if arg == 'a=':
            mt.bailfail("Need to define an absolute string after r=.")
        find_regex = True
        my_string = arg[2:]
    elif arg == 's':
        track_story_files = True
        track_extension_files = False
    elif arg in ( 'e', 'x' ):
        track_story_files = False
        track_extension_files = True
    elif arg == 'meta':
        my_sections = [ 'abouting', 'creditsing', 'verbsing' ]
    elif arg.startswith("s="):
        if len(arg) == 2:
            sys.exit("Can't specify blank sections.")
        my_array = [ fullname[x] if x in fullname else x for x in arg[2:].split(',') ]
        my_sections.extend(my_array)
    elif arg in ( 'um', 'use' ):
        my_string = r"\buse max_"
        find_regex = True
    elif arg == '?':
        usage()
    elif arg == '??':
        usage_rarer()
    elif arg in ( '?x', 'x?' ):
        usage_examples()
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
        look_for_string(my_string, my_ni_file, sections=my_sections)

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
        look_for_string(my_string, a, sections=my_sections)

if post_open:
    mt.postopen_files(max_opens = local_max_open)
else:
    to_open = len(mt.file_post_list)
    print("You have {} source file{} to post-open with p/op/po: {}.".format(to_open, mt.plur(to_open), ', '.join([i7.inform_short_name(x) for x in mt.file_post_list])))
