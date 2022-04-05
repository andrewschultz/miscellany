#
# regver.py: verify that important tests are not commented out in reg-* files
#

import mytools as mt
import os
import sys
import glob
from collections import defaultdict

open_after = True

max_files = 10

def usage(header = "usage for ".format(__file__)):
    print('=' * 20, header, '=' * 20)
    print("m# = max files")
    print("o = open after, no/on = don't open after")
    print("You can specify a file or a wild card to test.")
    sys.exit()

def to_wild(my_text):
    if '*' in my_text:
        return my_text
    return '*' + my_text + '*'

def check_one_file(my_file):
    commented_sections = defaultdict(int)
    includes = defaultdict(int)
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
            if open_after:
                mt.add_post_open(my_file, commented_sections[x])

files = []
wild_cards = []
cmd_count = 1

while cmd_count < len(sys.argv):
    (arg, num, valid) = mt.let_num(sys.argv[cmd_count])
    if arg == 'o':
        open_after = True
    elif arg in ( 'no', 'on' ):
        open_after = False
    elif arg == 'm' and valid:
        max_files = num
    elif os.path.exists(arg):
        check_one_file(arg)
        files.append(arg)
    elif '*' in arg or len(arg) > 4:
        wild_cards.append(to_wild(arg))
    elif arg == '?':
        usage()
    else:
        usage(header = 'invalid argument: {}'.format(arg))
    cmd_count += 1

if not len(files) and not len(wild_cards):
    print("Going with default reg-*.txt.")
    wild_cards = [ "reg-*.txt" ]

for this_wild in wild_cards:
    files.extend(glob.glob(this_wild))

for f in files:
    check_one_file(f)

if open_after:
    mt.post_open()
