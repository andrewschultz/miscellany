# defs.py
#
# pulls out the definitions from a source file in the user's directory

import os
import sys

count = 0
in_def = False
file_name = "story.ni"

def start_def(my_line):
    ll = my_line.lower()
    starties = [ "definition:", "to determine ", "to decide " ]
    for q in starties:
        if ll.startswith(q): return True
    return False

if not os.path.exists(file_name): sys.exit("Need a {:s} in the directory.".format(file_name))

with open(file_name) as file:
    for (line_count, line) in enumerate(file, 1):
        if in_def and not line.startswith("\t"):
            print()
            in_def = False
            continue
        if start_def(line):
            in_def = True
            count += 1
            print(count, line_count, line.rstrip())
            continue
        if not in_def: continue
        print(line.rstrip())

print("Finished parsing", file_name)