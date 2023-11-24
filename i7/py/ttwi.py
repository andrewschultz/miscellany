# ttwi.py
#
# switch columns as directed for given table and CSV of numbers
#
# usage = ttwi.py <table name or part of it> <2,3,4,5,6,7,8,9,0,1 e.g. array of old columns to new. Names also acceptable.>
#

from collections import Counter
import os
import re
import sys
import pyperclip
import i7
import mytools as mt
from filecmp import cmp

write_for_compare = True
ttwi_temp = "c:/writing/temp/ttwi-after.txt"

switch_array_base = []
table_to_find = ""
table_regex = ""
clipboard_string = ""

header_name = 'ta'
project_name = ''
story_file = False

max_tables = 0

count = 1
to_clipboard = False
in_table = got_table = False
t_start = 0
try_all_tables = False
force_changes = False

detailed_notes = 0

out_newline = '\n'

def print_whats_missing():
    print("Your input was missing something...")
    if not table_to_find:
        print("Need to give me a table to find--that can be any text.")
    if not switch_array_base:
        print("You need a CSV of numbers.")
    sys.exit()

def print_examples():
    print("ttwi.py big stuff -> searches for table of big stuff")
    print("ttwi.py s /level.*stuff -> searches for level one/two/three stuff, in the source file.")
    print("Default is the table file.")
    sys.exit()

def usage():
    print("=" * 40, "USAGE")
    print("A comma separated value denotes the new order of rows. To shift the first 5 over left, it would be 1,2,3,4,0. You can also give column names.")
    print("We also need a for all tables, a table name or a regex. A slash indicates a regex. 'table of' is not needed to start.")
    print("Currently you have to have a permutation of (0, ..., n) as the program does not fill the other numbers in.")
    print("-c/-2c = to clipboard.")
    print("-u/-w toggles newline.")
    print("-f = force changes.")
    print("")
    print("?? gives examples.")
    sys.exit()

def zero_to_n_shuffle(q):
    q2 = list(range(0, len(q)))
    return Counter(q2) == Counter(q)

def least_positive_not_in(my_array):
    ret_val = 0
    while ret_val in my_array:
        ret_val += 1
    return ret_val

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def ordering_of(my_base, this_header):
    int_check = is_integer(my_base[0])
    return_array = []
    for x in range(1, len(my_base)):
        if is_integer(my_base[x]) != int_check:
            mt.warn("I detected mix of integers and strings. Culprit was #{}: {}. Returning.".format(x, this_header[x]))
            return []
    if int_check:
        return_array = [int(x) for x in my_base]
    else:
        my_base = [ re.sub(" *\(.*\)", "", m) for m in my_base ] # get rid of (text) definitions
        print(my_base)
        for m in my_base:
            try:
                return_array.append(this_header.index(m))
            except:
                #print(m, "not in array", this_header)
                return []
    while len(return_array) < len(this_header):
        return_array.append(least_positive_not_in(return_array))
    seen = set()
    dupes = [x for x in return_array if x in seen or seen.add(x)]
    if len(dupes):
        mt.warn("Duplicate{} detected: {}".format(mt.plur(len(dupes)), ', '.join([str(x) for x in sorted(dupes)])))
        return []
    return return_array

if len(sys.argv) == 1:
    print("No command. Printing usage.")
    usage()

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-':
        arg = arg[1:]
    if arg == 'c' or arg == '2c':
        to_clipboard = True
    elif arg == 'a':
        try_all_tables = True
    elif arg == 'd':
        detailed_notes = 1
    elif arg == 'd2':
        detailed_notes = 2
    elif arg == 'f':
        force_changes = True
    elif arg == 'u':
        out_newline = '\n'
    elif arg == 'w':
        out_newline = '\r\n'
    elif arg.startswith('p='):
        project_name = arg[2:]
    elif arg.startswith('h='):
        header_name = arg[2:]
    elif arg == 's':
        story_file = True
    elif arg.startswith("m="):
        try:
            max_tables = int(arg[2:])
        except:
            mt.warn("Need number after m=.")
    elif arg.startswith ('/'):
        table_regex = arg[1:]
    elif ',' in arg:
        if switch_array_base:
            mt.bailfail("Two arrays.")
        switch_array_base = arg.split(',')
    elif re.search("[a-z]", arg):
        if arg.startswith("table-of-"):
            print("No need to start the table name with table-of-.")
            table_to_find = arg
        else:
            table_to_find = ("table of " + arg).lower()
        table_to_find = re.sub("-", " ", table_to_find)
    elif arg == '?':
        usage()
    elif arg == '??':
        print_examples()
    count += 1

if not switch_array_base:
    print_whats_missing()

if try_all_tables:
    if table_to_find or table_regex:
        mt.warn("Try all tables overrides table_to_find/table_regex.")
elif (not table_to_find) == (not table_regex):
    mt.bailfail("You need exactly one of absolute string or a regex.")

if not project_name:
    project_name = i7.dir2proj()
    if not project_name:
        mt.bailfail("You need to go to a project directory or specify one with p=.")

if story_file:
    my_file = i7.main_src(project_name)
    print("Going with main source file", my_file)
else:
    my_file = i7.hdr(project_name, header_name)
    print("Going with header file", my_file)

if not os.path.exists(my_file):
    mt.failbail("Could not locate file {}.".format(my_file))

in_header_row = False

file_out_string = ""
tables_rejigged = 0

with open(my_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith("table of"):
            if table_to_find and try_all_tables or (table_to_find in line.lower()):
                if detailed_notes:
                    print("Got table name", line.strip(), "at line", line_count)
                t_start = line_count
                in_table = got_table = True
                in_header_row = True
            elif table_regex and re.search(table_regex, line.lower(), flags=re.IGNORECASE):
                if detailed_notes:
                    print("Got table regex", table_regex, "at line", line_count)
                t_start = line_count
                in_table = got_table = True
                in_header_row = True
            file_out_string += line
            continue
        if not in_table:
            file_out_string += line
            continue
        if not line.strip() or line.startswith("["):
            if detailed_notes:
                print("Table ends line", line_count)
            file_out_string += line
            in_table = False
            continue
        ll = line.strip()
        cur_row = line_count - t_start - 1
        if cur_row:
            lma = re.sub("( *\[[^\]]*\])*$", "", ll)
        else:
            #ll = re.sub(" ?\([^\)]*\)", "", ll)
            table_headers = [re.sub(" *\(.*", "", x) for x in ll.lower().split("\t")]
            cols = len(table_headers)
            switch_array = ordering_of(switch_array_base, table_headers)
            if not switch_array:
                mt.warn("Line {} table header couldn't be matched up with switch-array. You have either mixed up integers and strings, or the base array has a string the in-file array doesn't.".format(line_count))
                in_table = False
                file_out_string += line
                continue
            if cols < len(switch_array):
                mt.warn("Line {} switch array is too big, {:d} vs {:d}.".format(line_count, len(switch_array), cols))
                in_table = False
                file_out_string += line
                continue
            if cols > len(switch_array):
                ol = len(switch_array)
                for x in range(0, cols):
                    if x not in switch_array:
                        switch_array.append(x)
                if detailed_notes:
                    print("Added", ", ".join([str(q) for q in switch_array[ol:]]))
                    print("New array", switch_array)
            tables_rejigged += 1
            if max_tables and tables_rejigged > max_tables:
                if tables_rejigged == max_tables + 1:
                    mt.warn("Line {} went over maximum # of tables to re-sort.".format(line_count))
                in_table = False
                file_out_string += line
                continue
            lma = str(ll)
        lm = lma.split("\t")
        if in_header_row:
            required_size = len(lm)
            in_header_row = False
        if len(lm) < required_size:
            if detailed_notes >= 2:
                print("Extending line {} by {}.".format(line_count, required_size - len(lm)))
            lm.extend(['--'] * (required_size - len(lm)))
            #print(line_count, lm)
        if cur_row == 0:
            for q in lm:
                if re.search(" [a-z]", q.lower()):
                    print("WARNING space in header", q)
        new_ar = []
        for x in switch_array:
            new_ar.append(lm[x])
        this_row_string = "\t".join(new_ar) + "\n"
        file_out_string += this_row_string
        if to_clipboard:
            clipboard_string += this_row_string + '\n'
        elif not write_for_compare:
            print(this_row_string.rstrip())

if not got_table:
    mt.bailfail("Could not find {} {:s} in story.ni.".format('absolute text' if table_to_find else 'regex', table_to_find if table_to_find else table_regex))

if write_for_compare:
    f = open(ttwi_temp, "w")
    f.write(file_out_string)
    f.close()
    if cmp(my_file, ttwi_temp):
        mt.warn("No changes for all of {}.".format(my_file))
    elif force_changes:
        copy(ttwi_temp, my_file)
        print("Recopied {} over.".format(my_file))
    else:
        mt.wm(my_file, ttwi_temp)
        if cmp(my_file, ttwi_temp):
            mt.warn("Things changed inside WinMerge, no nag to copy over.")
        else:
            x = input("Keep changes? (y to keep, anything else not to. Note -f forces changes.)")
            if x.strip().startswith('y'):
                copy(ttwi_temp, my_file)

if to_clipboard:
    print("String sent to clipboard.")
    pyperclip.copy(clipboard_string)
