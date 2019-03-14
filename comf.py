#
# comf.py
# comment find
#
# in any order: we need directories and words behind comments, then we search everything
#

import glob
import sys
import re
from collections import defaultdict
import i7

fetch_word = defaultdict(bool)
fetch_dir = defaultdict(str)

get_this_word = defaultdict(bool)
get_this_dir = defaultdict(str)

config_file = "c:/writing/scripts/comf.txt"

open_file = True

def launch_it(x, lc):
    print(x)
    if open_file: i7.npo(config_file, lc)
    exit()

def get_file_comment(fi, these_words):
    file_yet = False
    search_string = r'# *({:s})\b'.format("|".join(these_words))
    #sys.exit(search_string)
    with open(fi) as file:
        for (line_count, line) in enumerate(file, 1):
            if '#' not in line: continue
            if re.search(search_string, line):
                if not file_yet:
                    print("=====For file", fi)
                    file_yet = True
                print("    {:04d} {:s}".format(line_count, line.rstrip()))

def get_comments(this_dir, these_words):
    g = glob.glob(this_dir + "/*.txt")
    for fi in g:
        get_file_comment(fi, these_words)

def read_cfg():
    overlap_line = 0
    with open(config_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            l0 = re.sub("^[a-zA-Z]+:", "", line.strip())
            if line.startswith("DIR:"):
                l1 = l0.split("~")
                if len(l1) != 2: launch_it("Need just one tilde at line {:d}: {:s}".format(line_count, line.strip()), line_count)
                fetch_dir[l1[0]] = l1[1]
            if line.startswith("WORDGROUP:"):
                l1 = l0.split(",")
                for lx in l1:
                    if lx in fetch_dir:
                        print("OVERLAP: {:s} has DIR {:s} WORDGROUP {:s}".format(lx, fetch_dir[lx], fetch_word[lx]))
                        if not overlap_line: overlap_line = line_count

                    fetch_word[lx] = l0
    if overlap_line: launch_it(config_file, overlap_line)

read_cfg()

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg in fetch_word:
        print(arg, fetch_word[arg])
        for q in fetch_word[arg].split(","): get_this_word[q] = True
    elif arg in fetch_dir:
        print(arg, fetch_dir[arg])
        for q in fetch_dir[arg].split(","): get_this_dir[q] = True
    else: sys.exit("Didn't recognize " + arg)
    cmd_count += 1

my_dirs = list(get_this_dir)
my_words = list(get_this_word)

for md in my_dirs: get_comments(md, my_words)