# qch.py
#
# no usage necessary
# quick check of all README.MD in my github dirs
#

import i7
import sys
import re
import os
from collections import defaultdict

qch_out = "c:/writing/scripts/qch-out.htm"
config_file = "c:/writing/scripts/qch.txt"
root_dir = "c:/users/andrew/documents/github"

need_readme = 0
files_need_label = 0
total_labels = 0

topdir_ignore = defaultdict(bool)
alldir_ignore = defaultdict(bool)

def read_config():
    with open(config_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            ll = line.strip().lower()
            if '=' not in line:
                print(line.strip(), line_count, "does not have =.")
                continue
            lary = (re.sub(".*:", "", ll)).split(",")
            if ll.startswith('topdir'):
                for q in lary: topdir_ignore[q] = True
                continue
            if ll.startswith('alldir'):
                for q in lary: alldir_ignore[q] = True
                continue
            print("Unknown array command = at line", line_count, re.sub("=.*", "", ll))

def readme_process(readme, files_to_see):
    global files_need_label
    global total_labels
    global print_string
    f2c = defaultdict(bool)
    for q in files_to_see:
        f2c[q] = True
    with open(readme) as file:
        for line in file:
            for q in list(f2c):
                if q in line: f2c.pop(q, None)
    if len(f2c):
        files_need_label += 1
        total_labels += len(f2c.keys())
        print_string += "{:s} NEEDS TO LABEL {:d}\n        {:s}\n".format(readme, len(f2c.keys()), ' / '.join(f2c.keys()))
    else:
        print_string += "{:s} up to date.\n".format(readme)

def list_dirs(a, far_down):
    global need_readme
    global print_string
    if far_down == 0: print_string += "Listing directories for {:s}\n{:s}\n".format(a, '=' * 80)
    any_pl_py = []
    got_readme = False
    perl_count = 0
    python_count = 0
    for x in os.listdir(a):
        if far_down == 0 and x in topdir_ignore.keys(): continue
        if x in alldir_ignore.keys(): continue
        x2 = os.path.join(a, x)
        if os.path.isdir(x2):
            #print("Recursing to", x2)
            list_dirs(x2, far_down + 1)
        if x.endswith("pl") or x.endswith("py"):
            if x.endswith("pl"): perl_count += 1
            else: python_count += 1
            any_pl_py.append(x)
        if x.lower() == 'readme.md': got_readme = True
    if len(any_pl_py):
        if got_readme == False:
            print_string += "{:s} may need readme for {:s} as it has {:d} perl and {:d} python file(s).\n".format(a, ' / '.join(any_pl_py), perl_count, python_count)
            need_readme += 1
        else:
            readme_process(os.path.join(a, "readme.MD"), any_pl_py)

read_config()

count = 1
rd2 = ""
html_output = False
html_launch = False
print_string = ""

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'h': html_output = True
    elif arg == 'hl' or arg == 'lh' or arg == 'l': html_output = html_launch = True
    elif arg == '.':
        rd2 = os.getcwd()
        root_dir = rd2
    elif arg == '=':
        if rd2: sys.exit("Attempted to define two directories. Bailing.")
        ary = re.split("[\\\/]", os.getcwd())
        for x in range(0, len(ary) - 1):
            if ary[x].lower() == 'github':
                rd2 = '/'.join(ary[0:x+2])
                root_dir = rd2
        if not rd2: sys.exit("= needs you to be in a github project.")
    else:
        if rd2: sys.exit("Attempted to define two directories. Bailing.")
        rd2 = os.path.join(root_dir, i7.proj_exp(sys.argv[1]))
        if not os.path.exists(rd2): sys.exit(rd2 + " is not a valid directory. Try something else.")
        root_dir = rd2
    count += 1

list_dirs(root_dir, 0)

print_string += "Need readme: {:d}\n".format(need_readme)
print_string += "Need labels: {:d}, total labels {:d}.".format(files_need_label, total_labels)

if html_output:
    f = open(qch_out, "w")
    f.write("<html><title>QCH quick check output file</title><body><pre>\n")
    f.write(print_string)
    f.write("</pre></body></html>\n")
    f.close()
    if html_launch:
        print("Launched", qch_out)
        os.system(qch_out)
    else: print("Written to", qch_out, "but not launched. Use -l for that.")
else:
    print(print_string)