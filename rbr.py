import sys
import re
import os
import i7
from collections import defaultdict

def_file = defaultdict(str)
times = defaultdict(int)

always_be_writing = False
edit_main_branch = False
debug = False

in_file = ""
in_dir = os.getcwd()

def examples():
    print("===1,2,4 changes the active file list to #1, 2, 4 for example.")
    print("==t5 means only use file 5 until next empty line. Then it switches back to what was there before. A second ==t wipes out the first saved array.")
    print("==- inverts the active file list")
    print("== ! - ^ 1,2,4 = all but numbers 1, 2, 4")
    print("*FILE is replaced by the file name.")
    print("#-- is a comment only for the branch file.")
    exit()

def usage():
    print("-er = edit branch file (default = for directory you are in)")
    print("-e = edit rbr.txt")
    print("-c = edit rbr.py")
    print("-d = debug on")
    print("-x = list examples")
    print("shorthand or longterm project names accepted")
    exit()

def all_false(a):
    for x in a:
        if x: return False
    return True

def act(a):
    trues = []
    for x in range(len(a)):
        if a[x]: trues.append(str(x))
    return '/'.join(trues)

def get_file(fname):
    dupe_val = 1
    warns = 0
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
    actives = []
    with open(fname) as file:
        for line in file:
            line_count += 1
            if line.startswith('#--'): continue
            if temp_diverge and not line.strip():
                temp_diverge = False
                for x in actives: file_list[x].write("\n") # only actives get a CR
                actives = list(old_actives)
                continue
            if line.strip() == "\\\\": line = "\n"
            if line.startswith("'") or line.strip().endswith("'"): print("Possible apostrophe-to-quote change needed line", line_count, ":", line.strip())
            if '[\']' in line or '[line break]' in line or '[paragraph break]' in line: print("CR artifact in line", line_count, ":", line.strip())
            if '##location' in line or '##condition' in line: print("Excess generated text from mist.py in line", line_count, ":", line.strip())
            if '[if' in line or '[one of]' in line: print("Control statement artifact in line", line_count, ":", line.strip())
            if line.startswith("dupefile="):
                dupe_file_name = re.sub(".*=", "", line.lower().strip())
                dupe_file = open(dupe_file_name, "w")
                continue
            if re.search("^TSV(I)?[=:]", line): #tab separated values
                ignore_too_short = line.lower().startswith("tsvi")
                l2 = re.sub("TSV(I)?.", "", line.lower(), 0, re.IGNORECASE).strip().split("\t")
                if len(l2) > len(actives):
                    print("WARNING line", line_count, "has too many TSV values, ignoring")
                    print("TEXT:", line.strip())
                    continue
                elif ignore_too_short and len(l2) < len(actives):
                    print("WARNING line", line_count, "doesn't cover all files. Change TSV to TSVI to ignore this.")
                    print("TEXT:", line.strip())
                for x in range(len(l2)):
                    file_list[x].write(l2[x] + "\n")
                continue
            if line.startswith("files="):
                file_array = re.sub(".*=", "", line.lower().strip()).split(',')
                actives = [True] * len(file_array)
                for x in file_array:
                    f = open(x, 'w')
                    file_list.append(f)
                continue
            if all_false(actives):
                if always_be_writing and len(actives):
                    sys.exit("No files written to at line " + line_count + ": " + line.strip())
            if line.startswith(">"):
                last_cmd = line.lower().strip()
            if line.startswith("===a"):
                actives = [True] * len(actives)
                continue
            if line.strip() == "==!":
                actives = [not x for x in actives]
                continue
            if line.startswith("==!") or line.startswith("==-") or line.startswith("==^"):
                actives = [True] * len(actives)
                try:
                    for x in line.lower().strip()[3:].split(','):
                        actives[int(x)] = False
                except:
                    sys.exit("Failed at line " + line_count + ": " + line.strip())
                continue
            if line.startswith("==+"):
                ll = line.lower().strip()[3:]
                for x in ll.split(','):
                    if x.isdigit():
                        actives[int(x)] = True
                continue
            if re.search("^=+t", line):
                if temp_diverge:
                    print("Oops, bailing due to second temporary divergence ==t at line", line_count, ":", line.strip())
                    exit()
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
            if line.startswith("=="):
                print("Uh oh line", line_count, "may be a bad command.")
                warns += 1
            if debug and line.startswith(">"): print(act(actives), line.strip())
            for ct in range(0, len(file_list)):
                if actives[ct]:
                    line_write = re.sub("\*file", file_list[ct].name, line, 0, re.IGNORECASE)
                    file_list[ct].write(line_write)
            if actives[dupe_val]:
                dupe_file.write(line)
                if 'by one point' in line:
                    reps = 1
                    if times[last_cmd[1:]] > 1: reps = times[last_cmd[1:]]
                    for x in range(0, reps):
                        dupe_file.write("\n" + last_cmd + "\n")
                        dupe_file.write("!by one point\n")
    for ct in range(0, len(file_array)):
        file_list[ct].close()
    dupe_file.close()
    if warns > 0: print(warns, "potential bad commands.")
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
        def_file[j[0]] = j[1]
        if hk:
            print(hk, j[1])
            def_file[hk] = j[1]
        else:
            print(j[0], hk, "not recognized as project or shortcut")

count = 1

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c':
        i7.open_source()
        exit()
    elif arg == 'e':
        os.system("rbr.txt")
        exit()
    elif arg == 'er':
        edit_main_branch = True
    elif arg == 'd':
        debug = True
    elif arg in i7.i7x.keys():
        in_proj = i7.i7x[arg]
        in_file = i7.sdir(arg) + "\\" + def_file[in_proj]
    elif os.path.exists(arg):
        in_file = arg
    elif arg == 'x':
        examples()
    elif arg == '?':
        usage()
    else:
        print("Bad argument", count, arg)
        print("Possible projects: ", ', '.join(sorted(def_file.keys())))
        usage()
        exit()
    count += 1

if not in_file:
    myd = os.getcwd()
    if i7.dir2proj(myd):
        in_file = os.path.join(myd, def_file[i7.dir2proj(myd)])
    if not in_file:
        in_file = os.path.join(i7.sdir(def_proj), def_file[def_proj])
        print("Going with default", def_proj, "to", in_file)
    else:
        print("Getting file from current directory", in_file)

os.chdir(os.path.dirname(in_file))

if edit_main_branch:
    print("Opening branch file", in_file)
    os.system(in_file)
else:
    get_file(in_file)