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
            print(x, "is commented at line", commented_sections[x], "but is not in {include}s.")
            if open_after:
                mt.add_post_open(my_file, commented_sections[x])

file = ''
wild_card = "reg-*.txt"
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
        wild_card = ''
    elif '*' in arg:
        wild_card = arg
    elif arg == '?':
        usage()
    else:
        usage(header = 'invalid argument: {}'.format(arg))
    cmd_count += 1

if wild_card:
    reg_glob = glob.glob(wild_card)
    for f in reg_glob:
        check_one_file(f)

if open_after:
    mt.post_open()
