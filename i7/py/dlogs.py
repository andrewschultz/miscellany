from collections import defaultdict
import sys
import re
import i7
import os

word_count_hash = defaultdict(int)

ignore = [ "random text" ]

my_name = 'Andrew Schultz'
my_projs = []
default_proj = 'roi'
count = 1
sort_by_size = False

def word_count(x):
    x2 = re.sub(".*, which is ", "", x.lower().strip())
    x2 = re.sub(" words.*", "", x2)
    return int(x2)

def read_one_log(lfi):
    total_lines = 0
    with open(lfi) as file:
        for line in file:
            if 'words long' not in line: continue
            accept_it = False
            if 'your source text' in line: accept_it = True
            if my_name in line: accept_it = True
            for q in ignore:
                if q in line.lower():
                    if accept_it: print(q.upper(), "disqualifies", '"' + line.strip() + '"')
                    accept_it = False
            if accept_it:
                tl = word_count(line)
                print(tl, "from", '"' + line.strip() + '"')
                total_lines += tl
        word_count_hash[debug_log] = total_lines

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg == '-s':
        sort_by_size = True
    else:
        arga = arg.split(",")
        for arg in arga:
            if arg in my_projs:
                print(arg, "/", i7.pex(arg), "already in project array!")
            else:
                my_projs.append(i7.pex(arg))
    count += 1

if not my_projs:
    print("Using default project", default_proj)
    my_projs = [ default_proj ]

for x in my_projs:
    debug_log = i7.bl(x)
    print("Checking", x)
    if os.path.exists(debug_log):
        read_one_log(debug_log)
    else:
        print ("Build file for {:s} ({:s}) does not exist, so I can't check word count.".format(x, debug_log))
        continue

if word_count_hash.keys(): print('=' * 60)

for q in sorted(word_count_hash.keys(), key=(word_count_hash.get if sort_by_size else str.lower), reverse=sort_by_size):
    print (q, "has total word count of", word_count_hash[q])
