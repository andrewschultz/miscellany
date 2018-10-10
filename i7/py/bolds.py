# bolds.py
# looks for misplaced bold in story.ni locally

import re
import i7
import os
import sys

from collections import defaultdict

bolds_data = "c:/writing/scripts/bolds.txt"

caps = defaultdict(lambda: defaultdict(bool))
ignores = defaultdict(lambda: defaultdict(bool))

my_project = "ailihphilia"
cmd_line_proj = ""

def skipit(a):
    if '"' not in a: return True
    if a.startswith("["): return True
    for q in ignores[my_project].keys():
        if q in a: return True
    if re.search(": *print", a): return True
    if a.startswith("USE / GOOD"): return True
    if 'REV OVER doesn\'t think' in a: return True
    return False

def bruteforce():
    print("Brute force run:")
    count = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            for q in caps:
                if q in line and "[b]{:s}[r]".format(q) not in line:
                    if skipit(line): continue
                    count += 1
                    print(line.rstrip())
    if count == 0: print("NO ERRORS! Yay!")

def sophisticated():
    retval = 0
    finerr = defaultdict(str)
    print("Sophisticated run:")
    count = 0
    countall = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            l2 = i7.in_quotes(line)
            #print(l2.rstrip())
            q = re.findall(r"(?<!(\[b\]))\b({:s})\b(?!(\[r\]))".format(caps_par), l2)
            if q:
                if skipit(line): continue
                if not retval: retval = line_count
                count += 1
                countall += len(q)
                adds = [x[1] for x in q]
                print(count, "/", countall, "Need bold in", line_count, line, ', '.join(adds))
                for j in adds: finerr[j] += " {:05d}".format(line_count)
    if count == 0: print("NO ERRORS! Yay!")
    else:
        for q in sorted(finerr.keys(), key=lambda x: (len(finerr[x]), finerr[x])):
            print("{:10s}".format(q), finerr[q])
    return retval

def find_caps():
    retval = 0
    capfind = defaultdict(int)
    print("Find caps:")
    count = 0
    countall = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            if skipit(line): continue
            l2 = i7.in_quotes(line)
            q = re.findall(r"([A-Z])([A-Z ]*[A-Z])".format(caps_par), l2)
            if q: retval = line_count
            for l in q:
                capfind[l[0]+l[1]] += 1
    for q in sorted(capfind.keys(), key=capfind.get):
        print(q, capfind[q])
    return retval

def check_bold_italic():
    imbalances = 0
    imbalance = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            bolds = line.count("[b]")
            italics = line.count("[i]")
            regs = line.count("[r]")
            imbalance = bolds + italics - regs
            if imbalance:
                print("line", line_count, "has imbalance of", imbalance, ":", line.rstrip())
                imbalances += 1
    if imbalances: print(imbalances, "imbalances")
    else: print("No bold/italic/regular imbalances found.")

def read_data_file():
    if not os.path.exists(bolds_data): sys.exit("Need file " + bolds_data)
    cur_proj = "generic"
    with open(bolds_data) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if re.search("^IGNORE[:=]", line):
                l2 = re.sub("^IGNORE[:=]", "", line.rstrip())
                ignores[cur_proj][l2] = True
                continue
            if re.search("^(PROJ|PROJECT)=", line):
                l2 = re.sub("^(PROJ|PROJECT)=", "", line.rstrip()).lower()
                cur_proj = l2
                continue
            l2 = line.rstrip()
            if l2 in caps["generic"].keys():
                print("WARNING", l2, "in generic caps keys as well as", cur_proj, "at line", line_count)
            caps[cur_proj][l2] = True

count = 1
while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    elif arg == 'e': i7.npo(bolds_data)
    else:
        if cmd_line_proj: sys.exit("You tried to define 2 cmd line projects, {:s} then {:s}.".format(cmd_line_proj, arg))
        cmd_line_proj = i7.proj_exp(arg)
    count += 1

if cmd_line_proj:
    print("Changing dir to", cmd_line_proj)
    try:
        os.chdir(to_proj(cmd_line_project))
    except:
        sys.exit("Can't map", cmd_line_proj, "to a directory.")

my_proj = i7.dir2proj(os.getcwd())

if not os.path.exists("story.ni"): sys.exit("Need a directory with story.ni.")

read_data_file()

caps_par = "|".join(set(caps[my_project].keys()) | set(caps["generic"].keys()))

#find_caps()
#bruteforce()
line_to_open = sophisticated()
check_bold_italic()

if line_to_open: i7.npo("story.ni", line_to_open)