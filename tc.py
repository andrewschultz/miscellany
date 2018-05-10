# tc.py
#
# inform transcript cutter
#
# tc.py (optional file name) (output file name)
#

from shutil import copy
import glob
import os
import sys
import re

write_edit_files = False
write_over = False

def out_name(x):
    if x.endswith('.txt'):
        return re.sub("\.txt$", "-comments.txt", file_name)
    else:
        return "comments-" + x

def edit_name(x):
    if x.startswith("edit"): return ''
    return os.path.dirname(x) + "edit-" + os.path.basename(x)

def to_output(fn):
    f2 = open(fn, "w")
    count = 0
    comments = 0
    lines_in_out_file = 0
    lines = []
    so_far = ""
    with open(fn) as file:
        for f in file:
            count = count + 1
            if f.startswith('>'):
                if re.search("^> *[\*;]", f):
                    f2.write("=" * 50 + "Line " + str(count) + "\n")
                    f2.write(so_far + f)
                    lines_in_out_file = lines_in_out_file + so_far.count('\n') + 2
                    lines.append(lines_in_out_file)
                    so_far = f
                    comments = comments + 1
                else:
                    so_far = f
                continue
            so_far = so_far + f
    if so_far != "":
        f2.write("ENDING TEXT")
        f2.write(so_far)
    if comments:
        f2.write("\n{:d} total comments found ({:s}).\n".format(comments, ', '.join(map(str, lines))))
    f2.close()

so_far = ""

file_name = "abca.txt"
out_file_name = "comments.txt"
the_glob = ""

count = 1

my_files = []

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg.startswith('-'): arg = arg[1:]
    if '*' in arg:
        the_glob = arg
    elif arg == 'w': write_edit_files = True
    elif arg == 'wo': write_over = write_edit_files = True
    else:
        my_files.append(arg)
    count = count + 1

if the_glob:
    my_files = my_files + glob.glob(the_glob)

if not len(my_files):
    sys.exit("No files specified. Use * to add them all, or specify them in the arguments.")

for mf in my_files:
    if not os.path.exists(mf):
        print(mf, "does not exist, skipping.")
        if the_glob: print("Not sure what happened, since this was from a glob.")
    else:
        if write_edit_files:
            ef = edit_name(mf)
            if ef:
                if os.path.exists(ef) and not write_over:
                    print(ef, "exists. Use (-)wo to write over.")
                    continue
                print(mf, 'to', ef)
                copy(mf, ef)
                os.system("attrib -r " + ef)
        else:
            to_output(mf)
