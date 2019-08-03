#
# ttrim.py: this trims ending tabs from a script
#
# we can have a set of files or a directory or just one file
#
# we can also specify a glob
#
# bad_extensions and good_extensions are the main files to tinker with
#   (with which to tinker)
#

from collections import defaultdict
from shutil import copy
import mytools as mt
import re
import sys
import os
from glob import glob
from pathlib import Path
import i7

quiet_mode = False
win_merge_show = False
verbose = False
copy_back = False
flag_neutral = True
tab_space_search = True

exclude = [ '.git' ]
tabtemp = "c:/users/andrew/documents/github/tabtemp.txt"

bad_extensions = [ "pdf", "blorb", "png", "odt", "jpg" ]
good_extensions = [ "txt", "ni", "i7x", "py", "pl" ]

total_changes = 0

def usage():
    print("c = copy back, nc/cn = don't copy back")
    print("nw/wn = no win merge show, w shows")
    print("q = quiet mode")
    print("f flags neutral file extensions, nfn/fn/nf does not.")
    print("ts = tab-space together search, nts/tsn = none")
    print("* puts in a glob argument.")
    exit()

def is_unix(f):
    with open(f) as file:
        for line in file:
            if line.endswith("\r\n"): return False
            return True

def is_okay(f):
    for q in bad_extensions:
        if f.endswith(q): return False
    if do_perl_tidy:
        return f.endswith("pl") or f.endswith("pm")
    if flag_neutral:
        for q in good_extensions:
            if f.endswith(q): return True
        return False
        print("Flagged neutral file", q)
    return True

def check_file(my_f):
    ''' runs the expected test on the file
    the return tuple has (# of files fixed) / (# of files looked at), usually (0/1, 1) '''
    if not is_okay(my_f):
        if verbose: print(my_f, "ignored")
        return (0, 0)
    if not quiet_mode: print("Checking", my_f)
    lines_stripped = 0
    if do_perl_tidy:
        tidy_out = "c:/writing/temp/tidy.tdy"
        os.system("perltidy.bat -i=2 {0} -o {1}".format(my_f, tidy_out))
        temp = not cmp(my_f, tidy_out)
        if copy_back and temp:
            copy(tidy_out, my_f)
        os.delete(tidy_out)
        return (temp, 1)
    else:
        with open(tabtemp, "w") as out_file:
            with open(my_f, "U") as in_file:
                for line in in_file:
                    ls = 0
                    if re.search("[\t ]$", line):
                        # print(text.endswith(" "), text.endswith("\t"), text.endswith(")"), "!" + text[-1] + "!")
                        line = re.sub("[ \t]+$", "", line)
                        ls = 1
                    if tab_space_search and re.search("( \t|\t )", line):
                        line = re.sub("( +\t|\t +)", "\t", line)
                        ls = 1
                    lines_stripped += ls
                    out_file.write(line)
        # print(my_f, os.path.getsize(my_f), tabtemp, os.path.getsize(tabtemp))
    if win_merge_show: i7.wm(my_f, tabtemp)
    if lines_stripped:
        print("Rstripping/copying" if copy_back else "flagging (use -c to copy back)", my_f, "of", lines_stripped, "rstrips")
        if copy_back: copy(tabtemp, my_f)
        return (1, 1)
    else:
        if verbose: print("Nothing to strip in", my_f)
        return (0, 1)

def check_directory(my_dir):
    total_changes = 0
    total_files = 0
    for root, dirs, files in os.walk(my_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            f_f = os.path.join(root, f)
            x = check_file(f_f)
            total_changes += x[0]
            total_files += x[1]
    sys.exit("Total changes = {:d} of {:d}.".format(total_changes, total_files))

do_perl_tidy = False
test_type = "tab strip"

to_edit = []
cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohyp(sys.argv[cmd_count])
    if arg == 'c': copy_back = True
    elif arg == 'nc' or arg == 'cn': copy_back = False
    elif arg == 'w': win_merge_show = True
    elif arg == 'nw' or arg == 'wn': win_merge_show = False
    elif arg == 'q': quiet_mode = True
    elif arg == 'ts': tab_space_search = True
    elif arg == 'pt':
        do_perl_tidy = True
        test_type = "perl tidy"
    elif arg == 'nts' or arg == 'tsn': tab_space_search = False
    elif arg == 'f': flag_neutral = True
    elif arg == 'nfn' or arg == 'fn' or arg == 'nf': flag_neutral = False
    elif '*' in arg: to_edit += glob(arg)
    elif arg == '?': usage()
    else: to_edit.append(arg)
    cmd_count += 1

if len(to_edit) == 0: sys.exit("You need an argument -- directory, file or glob -- to trim.")

done_yet = defaultdict(bool)

total_tweaks = 0

for my_f in to_edit:
    if my_f in done_yet:
        print(my_f, "done already.")
        continue
    done_yet[my_f] = True
    if os.path.isdir(my_f): check_directory(my_f)
    elif os.path.isfile(my_f):
        cf = check_file(my_f)[0]
        if cf:
            print(my_f, "needed {0}s.".format(test_type))
            total_tweaks += 1
        elif not quiet_mode:
            print(my_f, "needed no {0}s.".format(test_type))
    else:
        print(my_f, " is neither a directory nor a file.")

sys.exit(total_tweaks)