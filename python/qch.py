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
need_readme_child = 0
need_readme_top = 0
files_need_label = 0
files_have_extra = 0
total_labels = 0
total_extras = 0

perl_global_count = 0
python_global_count = 0
count = 1
rd2 = ""
html_output = False
html_launch = False
ignore_success = True
print_string = ""

topdir_ignore = defaultdict(bool)
alldir_ignore = defaultdict(bool)

def usage():
    print("                    USAGE")
    print("=" * 50)
    print("h         = html output, no launch")
    print("hl, lh, l = html output with launch")
    print("i, is, si = ignore success reporting")
    print("s, sy, ys = show success reporting. Default = success reports {:s}.".format(i7.oo[not ignore_success]))
    print("=         = only look in current GitHub repo mirror")
    print(".         = look in current directory")
    print("?         = this")
    exit()

def read_config():
    with open(config_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            ll = line.strip().lower()
            if '=' not in line:
                print(line.strip(), line_count, "does not have =.")
                continue
            lary = (re.sub(".*[:=]", "", ll)).split(",")
            if ll.startswith('topdir'):
                for q in lary:
                    topdir_ignore[q] = True
                    q2 = os.path.join(root_dir, q)
                    if not os.path.exists(q2): print("WARNING:", q2, "is no longer a valid path. Delete from", config_file)
                continue
            if ll.startswith('alldir'):
                for q in lary: alldir_ignore[q] = True
                continue
            print("Unknown array command = at line", line_count, re.sub("=.*", "", ll))

def readme_process(readme, files_to_see):
    if 'puzzle' not in readme: return
    global files_need_label
    global files_have_extra
    global total_labels
    global total_extras
    global print_string
    f2c = defaultdict(bool)
    fir = defaultdict(bool)
    for q in files_to_see:
        f2c[q] = True
    with open(readme) as file:
        for line in file:
            q = re.findall(r"([a-z0-9-]+\.p[ly])", line)
            if q:
                for j in q: fir[j] = True
    extra_files = list(set(fir.keys()) - set(f2c.keys()))
    missed_files = list(set(f2c.keys()) - set(fir.keys()))
    if len(extra_files):
        files_have_extra += 1
        total_extras += len(extra_files)
        print_string += "{:s} HAS EXTRA FILES {:d}\n        {:s}\n".format(readme, len(extra_files), ' / '.join(sorted(extra_files)))
    if len(missed_files):
        files_need_label += 1
        total_labels += len(missed_files)
        print_string += "{:s} NEEDS TO LABEL {:d}\n        {:s}\n".format(readme, len(missed_files), ' / '.join(sorted(missed_files)))
    elif not ignore_success: print_string += "{:s} up to date.\n".format(readme)

def list_dirs(a, far_down):
    global need_readme
    global need_readme_child
    global need_readme_top
    global print_string
    global perl_global_count
    global python_global_count
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
            perl_global_count += perl_count
            python_global_count += python_count
            need_readme += 1
            if far_down > 1: need_readme_child += 1
            else: need_readme_top += 1
        else:
            readme_process(os.path.join(a, "readme.MD"), any_pl_py)

read_config()

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'h': html_output = True
    elif arg == 'hl' or arg == 'lh' or arg == 'l': html_output = html_launch = True
    elif arg == 'i' or arg == 'is' or arg == 'si': ignore_success = True
    elif arg == 's' or arg == 'ys' or arg == 'sy': ignore_success = False
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
    elif arg == '?': usage()
    else:
        if rd2: sys.exit("Attempted to define two directories. Bailing.")
        rd2 = os.path.join(root_dir, i7.proj_exp(sys.argv[1], True, True))
        if not os.path.exists(rd2): sys.exit(rd2 + " is not a valid directory. Try something else.")
        root_dir = rd2
    count += 1

list_dirs(root_dir, 0)

print_string += "README files needed: {:d} ({:d} root, {:d} child) with {:d} perl and {:d} python files.\n".format(need_readme, need_readme_top, need_readme_child, perl_global_count, python_global_count)
print_string += "README files that need to label more files: {:d}, total files that need labeling: {:d}.\n".format(files_need_label, total_labels)
print_string += "README files that mistakenly label extra files: {:d}, total files that need labeling: {:d}.\n".format(files_have_extra, total_extras)

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