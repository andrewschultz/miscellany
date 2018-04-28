import sys
import re
import os
import i7
from collections import defaultdict

def_file = defaultdict(str)

in_file = ""
in_dir = os.getcwd()

def get_file(x):
    file_list = []
    file_array = []
    line_count = 0
    print("Poking at", x)
    with open(x) as file:
        for line in file:
            line_count = line_count + 1
            if len(file_array) == 0:
                file_array = line.lower().strip().split(',')
                actives = [False] * len(file_array)
                for x in file_array:
                    f = open(x, 'w')
                    file_list.append(f)
                continue
            if len(actives) == 0: continue
            if line.startswith("==+"):
                ll = line.lower().strip()[3:]
                for x in ll.split(','):
                    if x.isdigit():
                        actives[int(x)] = True
            if line.startswith("==-"):
                ll = line.lower().strip()[3:]
                for x in ll.split(','):
                    if x.isdigit():
                        actives[int(x)] = False
            if line.startswith("==="):
                ll = re.sub("^=+", "", line.lower().strip())
                la = ll.split(',')
                actives = [False] * len(file_array)
                for x in la:
                    if x.isdigit(): actives[int(x)] = True
                continue
            for ct in range(0, len(file_list)):
                if actives[ct]:
                    file_list[ct].write(line)
    for ct in range(0, len(file_array)):
        file_list[ct].close()
    print("Wrote files:", ', '.join(file_array), 'from', x)

with open('c:/writing/scripts/rbr.txt') as file:
    for line in file:
        if line.startswith(';'): break
        if line.lower().startswith('default'):
            j = re.sub(r'^default([:=])?', "", line.strip().lower())
            def_proj = j
            continue
        j = line.strip().lower().split("\t")
        if len(j) < 2:
            print("Need tab in", line.strip())
        hk = i7.lpro(j[0])
        if hk:
            def_file[hk] = j[1]
        else:
            print(j[0], hk, "not recognized as project or shortcut")

count = 1

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    print(arg, i7.i7x[arg])
    if arg in i7.i7x.keys():
        in_proj = i7.i7x[arg]
        in_file = i7.sdir(arg) + "/" + def_file[in_proj]
    elif os.path.exists(arg):
        in_file = arg
    count = count + 1

if not in_file:
    myd = os.getcwd()
    if i7.dir2proj(myd):
        in_file = myd + "/" + def_file[i7.dir2proj(myd)]
    if not in_file:
        in_file = sdir(def_proj) + "/" + def_file(def_proj)
        print("Going with default", def_proj, "to", in_file)
    else:
        print("Getting file from current directory", in_file)

get_file(in_file)