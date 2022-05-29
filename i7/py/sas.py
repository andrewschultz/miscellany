# sas.py: search all source for a specific string

import sys
import codecs
import os
import glob

my_string = "aqueduct"

try:
    my_string = sys.argv[1]
except:
    pass

def look_for_string(my_string, this_file):
    with codecs.open(this_file, "r", "utf-8", errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if my_string.lower() in line.lower():
                print(line_count, this_file, line.strip())

ary = glob.glob("c:/games/inform/*.inform")

for d in ary:
    if not os.path.isdir(d):
        continue
    my_ni_file = os.path.join(d, "source", "story.ni")
    if not os.path.exists(my_ni_file):
        print("WARNING no story file", my_ni_file)
        continue
    look_for_string(my_string, my_ni_file)

