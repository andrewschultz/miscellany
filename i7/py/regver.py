#
# regver.py: verify that important tests are not commented out in reg-* files
#

import mytools as mt
import os
import sys
import glob
from collections import defaultdict

open_after = True
edit_files = False

max_files = 10

temp_regver = "c:/writing/temp/regver-py.txt"

default_wild_card = "reg-*-lone-*.txt"

def usage(header = "usage for ".format(__file__)):
    print('=' * 20, header, '=' * 20)
    print("m# = max files")
    print("o = open after, no/on = don't open after")
    print("You can specify a file or a wild card to test with an asterisk. Default wild card is {}.".format(default_wild_card))
    sys.exit()

def to_wild(my_text):
    if '*' in my_text:
        return my_text
    return '*' + my_text + '*'

def check_one_file(my_file, edit_the_file = True):
    commented_sections = defaultdict(int)
    includes = defaultdict(int)
    lines_to_edit = []
    ret_val = False
    if not os.path.exists(my_file):
        print("IGNORNG", my_file)
        return 0
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("* _"):
                commented_sections[line[2:].strip()] = line_count
                continue
            if line.startswith(">{include}"):
                my_entry = line[10:].strip()
                includes[line[10:].strip()] = line_count
    for x in commented_sections:
        if x not in includes:
            print("{}: {} is commented at line {} of but is not in {{include}}s.".format(my_file, x, commented_sections[x]))
            ret_val = True
            lines_to_edit.append(commented_sections[x])
            if open_after:
                mt.add_post_open(my_file, commented_sections[x])
    if not edit_the_file or not len(lines_to_edit):
        return ret_val
    f = open(temp_regver, "w")
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line_count in lines_to_edit:
                line = line.replace("* _", "* ")
            f.write(line)
    f.close()
    copy(temp_regver, my_file)
    os.path.delete(temp_regver)
    return ret_val

files = []
wild_cards = []
cmd_count = 1

while cmd_count < len(sys.argv):
    (arg, num, valid) = mt.let_num(sys.argv[cmd_count])
    if arg == 'o':
        open_after = True
    elif arg in ( 'no', 'on' ):
        open_after = False
    if arg == 'e':
        edit_files = True
        open_after = False
    elif arg in ( 'ne', 'en' ):
        edit_files = False
    elif arg in ( 'oe', 'eo' ):
        edit_files = True
        open_after = True
    elif arg == 'm' and valid:
        max_files = num
    elif os.path.exists(arg):
        files.append(arg)
    elif '*' in arg or len(arg) > 4:
        wild_cards.append(to_wild(arg))
    elif arg == '?':
        usage()
    else:
        usage(header = 'invalid argument: {}'.format(arg))
    cmd_count += 1

if not len(files) and not len(wild_cards):
    print("Going with default {}.".format(default_wild_card))
    wild_cards = [ default_wild_card ]

for this_wild in wild_cards:
    files.extend(glob.glob(this_wild))

files = sorted(set(files))

for f in files:
    check_one_file(f)

if open_after:
    mt.post_open()
