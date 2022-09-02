#
# ifarg.py: this combs through PYTHON paths to look for
#   if x == 'a' or x == -b
# and replaces it with
#   if x in ( 'a', 'b' )
#

import codecs
import os
import sys
import re
import mytools as mt
import glob
import pyperclip

debug = True
ignores = []

temp_file = "c:\\writing\\temp\\ifarg-from-old.txt"

max_to_list = 10

max_needed = 1
total_so_far = 0

def try_line_open(my_file):
    global total_so_far
    if total_so_far >= max_needed:
        if debug:
            print("Since we're at max_needed, ignoring", my_file)
        return
    if debug:
        print("Checking", my_file)
    any_bugs = False
    my_line = 0
    f2 = open(temp_file, "w")
    with codecs.open(my_file, encoding='utf8', errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            new_line = line
            if re.search("if arg == .* or ", line):
                if not any_bugs:
                    print(my_file)
                    any_bugs = True
                    my_line = line_count
                x = re.findall("== ('.*?')", line)
                x_list = ', '.join(x)
                new_line = re.sub("if arg ==.*?:", "if arg in ( {} ):".format(x_list), line)
                print(line_count, line.rstrip())
                print(line_count, new_line.rstrip())
            new_line = new_line.rstrip() + "\n"
            f2.write(new_line)
    f2.close()
    if any_bugs:
        paste_string = "copy {} {}".format(temp_file, my_file)
        pyperclip.copy(paste_string)
        mt.wm(my_file, temp_file)
        total_so_far += 1
        if total_so_far == max_needed:
            print("Max of {} reached.".format(max_needed))
        else:
            print("{} of {} reached so far.".format(total_so_far, max_needed))

g = []

try:
    temp = sys.argv[1]
    if temp.isdigit():
        max_needed = int(temp)
    else:
        g = [ sys.argv[1] ]
except:
    print("You can put in an integer as an argument to open multiple files.")

if not g:
    my_dir = "c:\\writing\\scripts"
    g = glob.glob(my_dir + "\\*.py")

for f in g:
    if os.path.basename(f) in ignores:
        continue
    try_line_open(f)

if not total_so_far:
    print("Found nothing to adjust from {}.".format(', '.join(g) if len(g) < max_to_list else '{} items'.format(len(g))))
