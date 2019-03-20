# question: search for starting tabs in non-.ni files. What script for that?

from shutil import copy
from collections import defaultdict
import i7
import glob
import re
import os
import sys

default_sect = ""
my_sect = ""

mapping = defaultdict(str)

def send_mapping(sect_name, file_name):
    dgtemp = "c:/writing/temp/dgrab-temp.txt"
    sect_alt = "\\" + sect_name
    found_sect_name = False
    in_sect = False
    file_remain_text = ""
    sect_text = ""
    if sect_name not in mapping: sys.exit("No section name {:s}, bailing on file {:s}.".format(sect_name, file_name))
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(sect_alt):
                print(file_name, "line", line_count, "has {:s} section".format("extra" if found_sect_name else "a"), sect_name)
                found_sect_name = True
                in_sect = True
                continue
            if in_sect:
                if line.startswith("\\"): sys.exit("Being pedantic that " + file_name + " has bad sectioning. Bailing.")
                if not line.strip():
                    in_sect = False
                    continue
                sect_text += line
            else:
                file_remain_text += line
    if not found_sect_name: return False
    print("Found", sect_name, "in", file_name, "appending to", mapping[sect_name])
    f = open(dgtemp, "w")
    f.write(file_remain_text)
    f.close()
    i7.wm(file_name, dgtemp)
    copy(dgtemp, file_name)
    os.remove(dgtemp)
    f = open(mapping[sect_name], "a")
    f.write("\n<from daily/keep file {:s}>\n".format(file_name) + sect_text)
    return True

os.chdir("c:/writing/scripts")

with open("dgrab.txt") as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith("#"): continue
        if line.startswith(";"): continue
        l0 = re.sub("^.*?=", "", line.strip())
        lary = l0.split(",")
        if line.startswith("MAPPING="): mapping[lary[0]] = lary[1]
        elif line.startswith("DEFAULT="): default_sect = lary[0]
        else: print("Unrecognized command line", line_count, line.strip())

x = glob.glob("c:/writing/daily/20*.txt")

my_sect = default_sect
processed = 0
max_process = 1

for q in x:
    processed += send_mapping(my_sect, q)
    if processed == max_process: sys.exit("Stopped at file " + q)

if max_process > 0: sys.exit("Got {:d} of {:d} files.".format(processed, max_process))
