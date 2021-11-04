import shutil
import os
import glob
import sys
import i7
import filecmp
import mytools as mt

def bin_not_blorb(x):
    ary = os.path.splitext(x)
    try:
        y = ary[1]
    except:
        return False
    return y.lower() in ('.z5', '.z8', '.ulx')

cmd_count = 1
my_proj = ''

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg.startswith("fx"):
        force_extension = arg[2:]
    elif my_proj:
        sys.exit("Duplicate project definition attempt.")
    else:
        my_proj = i7.long_name(arg)
    cmd_count += 1

if not my_proj:
    print("No project on command line. Going with default pulled from directory.")

my_proj = i7.dir2proj()

if not my_proj:
    sys.exit("Need a project or valid directory.")

mp = i7.proj2dir(my_proj)

changes = 0
news = 0

for x in glob.glob(os.path.join(mp, "reg-*.txt")):
    x0 = os.path.join(i7.prt, os.path.basename(x))
    if not os.path.exists(x0):
        print("New file", x0)
        news += 1
        continue
    if filecmp.cmp(x, x0):
        continue
    else:
        changes += 1
        print(x, "has changed. Copying over.")
        shutil.copy(x, x0)

build_dir = i7.proj2dir(my_proj, my_subdir = "Build")

y0 = glob.glob(os.path.join(build_dir, "output.*"))

y = [x for x in y0 if bin_not_blorb(x)]

if force_extension:
    if len(y) > 1:
        print("Initial pass had multiple files. Narrowing them down.")
        y = [x for x in y if x.endswith(force_extension)]
    else:
        print("No need to force extension. Only one file found.")
    

if len(y) == 0:
    sys.exit("No non-blorb binary found in {}".format(build_dir))
elif len(y) > 1:
    print("Multiple non-blorb binaries found in {}. Delete one and try again, or use x(extension).".format(build_dir))
    for y0 in y:
        print("    " + y0)
    sys.exit()

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
