# ttwi.py
#
# switch columns as directed for given table and CSV of numbers
#
# usage = ttwi.py table-of-goodacts 2,3,4,5,6,7,8,9,0,1
#

from collections import Counter
import os
import re
import sys
import pyperclip

switch_array = []
table_to_find = ""
clipboard_string = ""

count = 1
to_clipboard = False
in_table = got_table = False
t_start = 0

out_newline = '\n'

def increasing(q):
    q2 = list(range(0, len(q)))
    return Counter(q2) == Counter(q)

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c' or arg == '2c': to_clipboard = True
    elif arg == 'u': out_newline = '\n'
    elif arg == 'w': out_newline = '\r\n'
    elif re.search("[a-z]", arg.lower()):
        if arg.startswith("table-of-"):
            print("No need to put table-of- to start.")
            table_to_find = arg
        else:
            table_to_find = ("table of " + arg).lower()
        table_to_find = re.sub("-", " ", table_to_find)
    elif re.search("[0-9]", arg.lower()):
        switch_array = [int(x) for x in arg.split(",")]
    count += 1

if not table_to_find or not switch_array: sys.exit("Need to define CSV array and table to find.")

if not increasing(switch_array): sys.exit("You need the switch-array to be a permutation of 0, ..., n.")

if not os.path.exists("story.ni"): sys.exit("Need to move to a directory with story.ni.")

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith(table_to_find):
            print("Got", table_to_find, "at line", line_count)
            t_start = line_count
            in_table = got_table = True
            continue
        if not in_table: continue
        if not line.strip() or line.startswith("["):
            print("Table ends line", line_count)
            break
        ll = line.strip()
        if line_count - t_start > 1:
            lma = re.sub("( *\[[^\]]*\])*$", "", ll)
        else:
            ll = re.sub("\([^\)]*\)", "", ll)
            cols = len(line.split("\t"))
            if cols < len(switch_array): sys.exit("Switch array is too big, {:d} vs {:d}.".format(len(switch_array), cols))
            if cols > len(switch_array):
                ol = len(switch_array)
                for x in range(0, cols):
                    if x not in switch_array: switch_array.append(x)
                print("Added", ", ".join([str(q) for q in switch_array[ol:]]))
                print("New array", switch_array)
            lma = str(ll)
        lm = lma.split("\t")
        if "\"" in ll:
            lx = re.sub(".*\"", "", ll)
        else:
            lx = ""
        new_ar = []
        for x in switch_array: new_ar.append(lm[x])
        this_row_string = "\t".join(new_ar) + lx
        if to_clipboard: clipboard_string += this_row_string + '\n'
        else: print(this_row_string)

if not got_table: sys.exit("Could not find {:s} in story.ni.".format(table_to_find))

if to_clipboard:
    print("String sent to clipboard.")
    pyperclip.copy(clipboard_string)
