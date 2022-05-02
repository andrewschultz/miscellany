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

detailed_notes = False

out_newline = '\n'

def print_whats_missing():
    print("Your input was missing something...")
    if not table_to_find: print("Need to give me a table to find--that can be any text.")
    if not switch_array: print("You need a CSV of numbers.")
    exit()

def usage():
    print("=" * 40, "USAGE")
    print("A comma separated value denotes the new order of rows. To shift the first 5 over left, it would be 1,2,3,4,0.")
    print("We also need a table name. 'table of' is not needed to start.")
    print("Currently you have to have a permutation of (0, ..., n) as the program does not fill the other numbers in.")
    print("-c/-2c = to clipboard")
    print("-u/-w toggles newline")
    exit()

def increasing(q):
    q2 = list(range(0, len(q)))
    return Counter(q2) == Counter(q)

if len(sys.argv) == 1:
    print("No command. Printing usage.")
    usage()

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c' or arg == '2c': to_clipboard = True
    elif arg == 'd': detailed_notes = True
    elif arg == 'u': out_newline = '\n'
    elif arg == 'w': out_newline = '\r\n'
    elif re.search("[a-z]", arg):
        if arg.startswith("table-of-"):
            print("No need to start the table name with table-of-.")
            table_to_find = arg
        else:
            table_to_find = ("table of " + arg).lower()
        table_to_find = re.sub("-", " ", table_to_find)
    elif re.search("[0-9]", arg):
        switch_array = [int(x) for x in arg.split(",")]
    elif '?' in arg: usage()
    count += 1

if not table_to_find or not switch_array: print_whats_missing()

if not increasing(switch_array): sys.exit("You need the switch-array to be a permutation of 0, ..., n.")

if not os.path.exists("story.ni"): sys.exit("Need to move to a directory with story.ni.")

in_header_row = False

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith(table_to_find):
            print("Got", table_to_find, "at line", line_count)
            t_start = line_count
            in_table = got_table = True
            in_header_row = True
            continue
        if not in_table: continue
        if not line.strip() or line.startswith("["):
            print("Table ends line", line_count)
            break
        ll = line.strip()
        cur_row = line_count - t_start - 1
        if cur_row:
            lma = re.sub("( *\[[^\]]*\])*$", "", ll)
        else:
            #ll = re.sub(" ?\([^\)]*\)", "", ll)
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
        if in_header_row:
            required_size = len(lm)
            in_header_row = False
        if len(lm) < required_size:
            if detailed_notes:
                print("Extending line {} by {}.".format(line_count, required_size - len(lm)))
            lm.extend(['--'] * (required_size - len(lm)))
            #print(line_count, lm)
        if cur_row == 0:
            for q in lm:
                if re.search(" [a-z]", q.lower()): print("WARNING space in header", q)
        new_ar = []
        for x in switch_array: new_ar.append(lm[x])
        this_row_string = "\t".join(new_ar)
        if to_clipboard:
            clipboard_string += this_row_string + '\n'
        else:
            print(this_row_string)

if not got_table: sys.exit("Could not find {:s} in story.ni.".format(table_to_find))

if to_clipboard:
    print("String sent to clipboard.")
    pyperclip.copy(clipboard_string)
