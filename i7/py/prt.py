import shutil
import os
import glob
import sys
import i7
import filecmp

def bin_not_blorb(x):
    ary = os.path.splitext(x)
    try:
        y = ary[1]
    except:
        return False
    return y.lower() in ('.z5', '.z8', '.ulx')

try:
    my_proj = i7.long_name(sys.argv[1])
except:
    my_proj = i7.dir2proj()

mp = i7.proj2dir(my_proj)

if not my_proj:
    sys.exit("Need a project or valid directory.")

changes = 0
news = 0

for x in glob.glob(os.path.join(mp, "reg-*.txt")):
    x0 = os.path.join(i7.prt, os.path.basename(x))
    if not os.path.exists(x0):
        print("New file", x0)
        news += 1
    if filecmp.cmp(x, x0):
        continue
    else:
        changes += 1
        print(x, "has changed. Copying over.")
        shutil.copy(x, x0)

build_dir = i7.proj2dir(my_proj, my_subdir = "Build")

y0 = glob.glob(os.path.join(build_dir, "output.*"))

y = [x for x in y0 if bin_not_blorb(x)]

if len(y) == 0:
    sys.exit("No non-blorb binary found in {}".format(build_dir))
elif len(y) > 1:
    sys.exit("Multiple non-blorb binaries found in {}: {}".format(build_dir, y))

my_copy_file = y[0]

(_, my_ext) = os.path.splitext(my_copy_file)

file_dest = os.path.join(i7.prt, "debug-{}{}".format(i7.long_name(my_proj), my_ext))

if os.path.exists(file_dest) and filecmp.cmp(my_copy_file, file_dest):
    print("No binary file change.")
else:
    print("New binary file needed! Copying {} to {}.".format(my_copy_file, file_dest))
    shutil.copy(y[0], file_dest)

if not changes:
    print("No test scripts changed--note that RBR.PY may run PRT.PY automatically.")

if not news:
    print("No new test scripts.")
