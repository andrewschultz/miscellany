#
# regver.py: verify that important tests are not commented out in reg-* files
#

import i7
import colorama
import mytools as mt
import os
import sys
import glob
from collections import defaultdict
from shutil import copy

open_after = True
edit_files = False

max_files = 10

temp_regver = "c:/writing/temp/regver-py.txt"

default_wild_card = "reg-*-lone-*.txt"
blanket_wild_card = "reg-*.txt"

my_proj = ''

def usage(header = "usage for ".format(__file__)):
    print('=' * 20, header, '=' * 20)
    print("m# = max files")
    print("o = open after, no/on = don't open after")
    print("e = edit files, can be combined with o")
    print("a = all files, not just -lone-")
    print("You can specify a file or a wild card to test with an asterisk or long (4+ chars) string name.")
    print("Default wild card is {}.".format(default_wild_card))
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
    color_highlight = colorama.Fore.GREEN if edit_the_file else colorama.Fore.RED
    for x in commented_sections:
        if x not in includes:
            if not ret_val:
                mbase = os.path.basename(my_file)
                print("==========================", mbase)
            print(color_highlight + "    {} section {} is commented at line {} but is not in any {{include}}s.".format(mbase, x, commented_sections[x]) + colorama.Style.RESET_ALL)
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
    os.remove(temp_regver)
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
    if arg == 'a':
        default_wild_card = blanket_wild_card
    elif arg == 'e':
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
    elif i7.long_name(arg):
        my_proj = arg
    elif '*' in arg or len(arg) > 4:
        wild_cards.append(to_wild(arg))
    elif arg == '?':
        usage()
    else:
        usage(header = 'invalid argument: {}'.format(arg))
    cmd_count += 1

if my_proj:
    i7.go_proj(my_proj)

if not len(files) and not len(wild_cards):
    print("Going with default {}.".format(default_wild_card))
    wild_cards = [ default_wild_card ]

for this_wild in wild_cards:
    files.extend(glob.glob(this_wild))

if not len(files):
    print("No specific wild cards found. Going with reg-*.txt.")
    files.extend(glob.glob("reg-*.txt"))

files = sorted(set(files))

if not len(files):
    sys.exit("No files were specified.")

running_total = 0 # this is the running total of files to edit

for f in files:
    running_total += check_one_file(f, edit_the_file = edit_files)

if not running_total:
    if len(files) > 1:
        print(len(files), "files {} passed!".format('both' if len(files) == 2 else 'all'))
    else:
        print(files[0], "file passed!")
else:
    print("{} file{} {} of {} total".format(running_total, mt.plur(running_total), 'rewritten' if edit_files else 'failed', len(files)))

if running_total and not edit_files:
    print("-e edits files")

if open_after:
    print("no/on turns opening files off, en/ne edits but does not open files.")
    mt.post_open(bail_after = False)

sys.exit(running_total)
