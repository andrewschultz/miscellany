#
# bolds.py
# looks for misplaced bold in story.ni locally
# DEPRECATED FOR THE MORE GENERAL BOLD.PY WHICH HAS A BETTER REGEX AND ERROR-IGNORING
# SO DO NOT RUN THIS

import re
import i7
import os
import sys
import colorama

from collections import defaultdict

bolds_data = "c:/writing/scripts/bolds.txt"

caps = defaultdict(lambda: defaultdict(bool))
ignores = defaultdict(lambda: defaultdict(bool))

line_to_open = defaultdict(str)

cmd_line_proj = ""

def usage():
    print("-f = find caps")
    print("-b = brute_force_bool")
    print("-s = sophisticated_bool")
    print("-c = check_bold_italic_bool")
    print("-nx/-xn negates options above. Only -s is on to start.")
    print("-[fbsc]o/-o[fbsc] = only one option.")
    print("Any project or abbreviation can be used.")
    exit()

def skipit(a):
    if '"' not in a: return True
    if a.startswith("["): return True
    for q in ignores[my_project].keys():
        if q in a: return True
    if re.search(": *print", a): return True
    if a.startswith("USE / GOOD"): return True
    if 'REV OVER doesn\'t think' in a: return True
    return False

def brute_force(my_file = "story.ni"):
    print("Brute force run:")
    count = 0
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            for q in caps:
                if q in line and "[b]{:s}[r]".format(q) not in line:
                    if skipit(line): continue
                    count += 1
                    print(line.rstrip())
    if count == 0: print("NO ERRORS! Yay!")

def sophisticated(my_file = "story.ni"):
    first_line_number = 0
    finerr = defaultdict(str)
    print("Sophisticated run:", my_file)
    count = 0
    countall = 0
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            l2 = i7.in_quotes(line)
            #print(l2.rstrip())
            q = re.findall(r"(?<!(\[b\]))\b({:s})\b(?!(\[r\]))".format(caps_par), l2)
            if q:
                if skipit(line): continue
                if not first_line_number: first_line_number = line_count
                count += 1
                countall += len(q)
                adds = [x[1] for x in q]
                print(count, "/", countall, "Need bold in", line_count, line, ', '.join(adds))
                for j in adds: finerr[j] += " {:05d}".format(line_count)
    if count == 0: print("NO ERRORS! Yay!")
    else:
        for q in sorted(finerr.keys(), key=lambda x: (len(finerr[x]), finerr[x])):
            print("{:10s}".format(q), finerr[q])
    return first_line_number

def find_caps(my_file = "story.ni"):
    retval = 0
    capfind = defaultdict(int)
    print("Find caps:")
    count = 0
    countall = 0
    with open(my_file) as file:
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

def check_bold_italic(my_file = "story.ni"):
    imbalances = 0
    imbalance = 0
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            bolds = line.count("[b]")
            italics = line.count("[i]")
            regs = line.count("[r]")
            imbalance = bolds + italics - regs
            if imbalance:
                print("line", line_count, "has imbalance of", imbalance, ":", line.rstrip())
                imbalances += 1
    if imbalances:
        print(imbalances, "imbalances")
    else:
        print("No bold/italic/regular imbalances found.")

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
find_caps_bool = False
brute_force_bool = False
sophisticated_bool = True
check_bold_italic_bool = False

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'e': i7.npo(bolds_data)
    elif arg == 'f': find_caps_bool = True
    elif arg in ( 'nf', 'fn' ): find_caps_bool = False
    elif arg in ( 'ob', 'bo' ):
        sophisticated_bool = brute_force_bool = check_bold_italic_bool = False
        find_caps_bool = True
    elif arg == 'b': brute_force_bool = True
    elif arg in ( 'nb', 'bn' ): brute_force_bool = False
    elif arg in ( 'ob', 'bo' ):
        sophisticated_bool = brute_force_bool = find_caps_bool = False
        check_bold_italic_bool = True
    elif arg == 's': sophisticated_bool = True
    elif arg in ( 'ns', 'sn' ): sophisticated_bool = False
    elif arg in ( 'os', 'so' ):
        check_bold_italic_bool = brute_force_bool = find_caps_bool = False
        sophisticated_bool = True
    elif arg == 'c': check_bold_italic_bool = True
    elif arg in ( 'nc', 'cn' ): check_bold_italic_bool = False
    elif arg in ( 'oc', 'co' ):
        sophisticated_bool = brute_force_bool = find_caps_bool = False
        check_bold_italic_bool = True
    elif arg == '?': usage()
    else:
        if cmd_line_proj: sys.exit("You tried to define 2 cmd line projects, {:s} then {:s}.".format(cmd_line_proj, arg))
        cmd_line_proj = i7.proj_exp(arg)
    count += 1

if cmd_line_proj:
    print("Changing (or trying to change) dir to", cmd_line_proj)
    try:
        os.chdir(i7.proj2dir(cmd_line_proj))
        my_project = cmd_line_proj
    except:
        sys.exit("Can't map {} to a directory.".format(cmd_line_proj))
else:
    my_project = i7.dir2proj(os.getcwd())
    try:
        os.chdir(i7.proj2dir(my_project))
    except:
        print("Couldn't get project from directory. Going with default.")

if not os.path.exists("story.ni"): sys.exit("Need a directory with story.ni.")

read_data_file()

caps_par = "|".join(set(caps[my_project].keys()) | set(caps["generic"].keys()))

if my_project in i7.i7f:
    file_array = i7.i7f[my_project]
else:
    file_array = [ 'story.ni' ]

for f in file_array:
    if find_caps_bool: find_caps(f)
    if brute_force_bool: brute_force(f)
    if sophisticated_bool: sophisticated(f)
    if check_bold_italic_bool: check_bold_italic(f)

for l in line_to_open:
    i7.npo(l, line_to_open[l], bail = False)

print(colorama.Fore.RED + "WARNING: BOLD.PY is a better, and more recently updated, checker for bold text. You may wish to go with that instead." + colorama.Style.RESET_ALL)
sys.exit()
