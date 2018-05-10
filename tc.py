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

launch_after = False
write_edit_files = False
write_over = False

def out_name(x):
    if x.endswith('.txt'):
        return re.sub("\.txt$", "-comments.txt", x)
    else:
        return "comments-" + x

def edit_name(x):
    if x.startswith("edit"): return ''
    return os.path.dirname(x) + "edit-" + os.path.basename(x)

def to_output(f_i, f_o):
    f2 = open(f_o, "w")
    count = 0
    comments = 0
    lines_in_out_file = 0
    lines = []
    so_far = ""
    with open(f_i) as file:
        for (lc,line) in enumerate(file):
            if line.startswith('>'):
                if re.search("^> *[\*;]", line):
                    f2.write("=" * 50 + "Line " + str(lc) + "\n")
                    f2.write(so_far + line)
                    lines_in_out_file = lines_in_out_file + so_far.count('\n') + 2
                    lines.append(lines_in_out_file)
                    so_far = ""
                    comments = comments + 1
                else:
                    so_far = "(prev) " + line
                    if line != line.lower():
                        print(f_i, lc, line.strip(), "may be a comment.")
                continue
            so_far = so_far + line
    if so_far != "":
        f2.write("ENDING TEXT")
        f2.write(so_far)
    if comments:
        comwri = "{:d} total comments found ({:s}).".format(comments, ', '.join(map(str, lines)))
        print(comwri)
        f2.write("\n" + comwri + "\n")
    f2.close()

so_far = ""

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
    if 'comments' in mf:
        print("COMMENTS is probably a file output by tc. Change", os.path.basename(mf))
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
            ona = out_name(mf)
            print(os.path.basename(mf), "to", os.path.basename(ona))
            to_output(mf, ona)
        if launch_after and len(my_files) == 1:
            os.system(ona)

if launch_after and len(my_files) > 1:
    print("Too many files to launch.")
