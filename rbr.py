import sys
import re
import os
import i7
from collections import defaultdict

def_file = defaultdict(str)
times = defaultdict(int)

edit_main_branch = False

in_file = ""
in_dir = os.getcwd()

def usage():
    print("-er = edit branch file (default = for directory you are in)")
    print("-e = edit rbr.txt")
    print("-c = edit rbr.py")
    print("shorthand or longterm project names accepted")
    exit()

def get_file(fname):
    dupe_val = 1
    last_cmd = ""
    file_list = []
    file_array = []
    line_count = 0
    dupe_file_name = ""
    temp_diverge = False
    try:
        dupe_file = open("hello.txt", "r")
        dupe_file.close()
    except:
        pass
    print("Poking at", fname)
    with open(fname) as file:
        for line in file:
            line_count = line_count + 1
            if temp_diverge and not line.strip():
                temp_diverge = False
                actives = old_actives
            if line.startswith("dupefile="):
                dupe_file_name = re.sub(".*=", "", line.lower().strip())
                dupe_file = open(dupe_file_name, "w")
                continue
            if line.startswith("files="):
                file_array = re.sub(".*=", "", line.lower().strip()).split(',')
                actives = [False] * len(file_array)
                for x in file_array:
                    f = open(x, 'w')
                    file_list.append(f)
                continue
            if len(actives) == 0: continue
            if line.startswith(">"):
                last_cmd = line.lower().strip()
            if line.startswith("===a"):
                actives = [True] * len(actives)
                continue
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
            if re.search("^=+t", line):
                old_actives = list(actives)
                temp_diverge = True
                ll = re.sub("^=+t", "", line.lower().strip()).split(',')
                actives = [False] * len(file_array)
                for x in ll:
                    if x.isdigit(): actives[int(x)] = True
                continue
            if line.startswith("==="):
                ll = re.sub("^=+", "", line.lower().strip()).split(',')
                actives = [False] * len(file_array)
                for x in ll:
                    if x.isdigit(): actives[int(x)] = True
                continue
            for ct in range(0, len(file_list)):
                if actives[ct]:
                    file_list[ct].write(line)
            if actives[dupe_val]:
                dupe_file.write(line)
                if 'by one point' in line:
                    reps = 1
                    if times[last_cmd[1:]] > 1: reps = times[last_cmd[1:]]
                    for x in range(0, reps):
                        dupe_file.write("\n" + last_cmd + "\n")
                        dupe_file.write("/by one point\n")
    for ct in range(0, len(file_array)):
        file_list[ct].close()
    dupe_file.close()
    print("Wrote files:", ', '.join(file_array), 'from', fname)

with open('c:/writing/scripts/rbr.txt') as file:
    for line in file:
        if line.startswith(';'): break
        if line.lower().startswith('dupe'):
            j = re.sub(r'^dupe([:=])?', "", line.strip().lower())
            ja = j.split("\t")
            times[ja[0]] = int(ja[1])
            continue
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
    if arg == 'c':
        i7.open_source()
        exit()
    elif arg == 'e':
        os.system("rbr.txt")
        exit()
    elif arg == 'er':
        edit_main_branch = True
    elif arg in i7.i7x.keys():
        in_proj = i7.i7x[arg]
        in_file = i7.sdir(arg) + "\\" + def_file[in_proj]
    elif os.path.exists(arg):
        in_file = arg
    elif arg == '?':
        usage()
    else:
        print("Bad argument", count, arg)
        print("Possible projects: ", ', '.join(sorted(def_file.keys())))
        usage()
        exit()
    count = count + 1

if not in_file:
    myd = os.getcwd()
    if i7.dir2proj(myd):
        in_file = os.path.join(myd, def_file[i7.dir2proj(myd)])
    if not in_file:
        in_file = os.path.join(sdir(def_proj), def_file(def_proj))
        print("Going with default", def_proj, "to", in_file)
    else:
        print("Getting file from current directory", in_file)

if edit_main_branch:
    print("Opening branch file", in_file)
    os.system(in_file)
else:
    get_file(in_file)