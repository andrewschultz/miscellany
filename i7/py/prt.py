#
# prt.py : python regression test copy-over script
# supplants prt.pl (old copy-over script) -- more portable, faster
#
# usage: no arguments or, if there are 2 binary files,
#     prt.py fxz8 to pull a z8 file
#

import shutil
import os
import glob
import sys
import i7
import filecmp
import mytools as mt
import colorama

def bin_not_blorb(x):
    ary = os.path.splitext(x)
    try:
        y = ary[1]
    except:
        return False
    return y.lower() in ('.z5', '.z8', '.ulx')

cmd_count = 1
my_proj = ''
force_extension = ''

write_current_project = False
read_i7_default_project = False

copy_all = False

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg.startswith("fx"):
        force_extension = arg[2:]
    elif my_proj:
        sys.exit(colorama.Fore.RED + "Duplicate project definition attempt." + colorama.Style.RESET_ALL)
    elif arg in ( 'wp', 'pw' ):
        write_current_project = True
    elif arg == 'a':
        copy_all = True
    else:
        my_proj = i7.long_name(arg)
    cmd_count += 1

if not my_proj:
    my_proj = i7.main_abb(i7.dir2proj())
    if not my_proj:
        my_proj = mt.val_from_cfg(i7.rbr_config, "default")
        if my_proj:
            mt.warn("Going with default from RBR file, {}.".format(my_proj))
        else:
            my_proj = i7.curdef
            if not my_proj:
                mt.bailfail("No project from CWD, and no project is defined in rbr.txt or i7p.txt. Bailing.")
            mt.warn("Going with default from i7p.txt file, {}.".format(my_proj))
            read_i7_default_project = True
    else:
        print(colorama.Fore.YELLOW + "No project on command line. Going with default pulled from directory." + colorama.Style.RESET_ALL)

mp = i7.proj2dir(my_proj)

changes = 0
news = 0

for x in glob.glob(os.path.join(mp, "reg-*.txt")):
    x0 = os.path.join(i7.prt, os.path.basename(x))
    if not os.path.exists(x0):
        print(colorama.Fore.GREEN + "Copying over new file {}.".format(x0) + colorama.Style.RESET_ALL)
        news += 1
        shutil.copy(x, x0)
        continue
    try:
        temp = filecmp.cmp(x, x0)
    except Exception as p:
        any_yet = False
        if not os.path.exists(x):
            print(x, "source may be a stale symlink.")
            any_yet = True
        if not os.path.exists(x0):
            print(x0, "target may be a stale symlink.")
            any_yet = True
        if not any_yet:
            print(os.path.basename(x), "Official error:", p)
        continue
    if not temp:
        changes += 1
        print(colorama.Fore.GREEN + "File {} has changed. Copying over.".format(x) + colorama.Style.RESET_ALL)
        shutil.copy(x, x0)

build_dir = i7.proj2dir(my_proj, my_subdir = "Build")

y0 = glob.glob(os.path.join(build_dir, "output.*"))

y = [x for x in y0 if bin_not_blorb(x)]

if force_extension:
    if len(y) > 1:
        print(colorama.Fore.YELLOW + "Initial pass had multiple files. Narrowing them down." + colorama.Style.RESET_ALL)
        y = [x for x in y if x.endswith(force_extension)]
    else:
        print(colorama.Fore.YELLOW + "No need to force extension. Only one file found." + colorama.Style.RESET_ALL)

if len(y) == 0:
    sys.exit("No non-blorb binary found in {}".format(build_dir))
elif len(y) > 1 and copy_all is False:
    print(colorama.Fore.YELLOW + "Multiple non-blorb binaries found in {}. Delete one and try again, or use fx(extension) to force extension.".format(build_dir) + colorama.Style.RESET_ALL)
    for y0 in y:
        print("    " + y0)
    sys.exit()

for my_copy_file in y:
    (_, my_ext) = os.path.splitext(my_copy_file)

    file_dest = os.path.normpath(os.path.join(i7.prt, "debug-{}{}".format(i7.long_name(my_proj), my_ext)))

    binary_change = False

    if os.path.exists(file_dest) and filecmp.cmp(my_copy_file, file_dest):
        print("No binary file change.")
    else:
        print(colorama.Fore.GREEN + "New binary file needed! Copying {} to {}.".format(my_copy_file, file_dest) + colorama.Style.RESET_ALL)
        shutil.copy(my_copy_file, file_dest)
        binary_change = True

if not changes:
    print("No test scripts changed--note that RBR.PY may run PRT.PY automatically.")

if not news:
    print("No new test scripts.")

if not (binary_change or changes or news):
    print(colorama.Fore.RED + "    WARNING: nothing was actually copied over." + colorama.Style.RESET_ALL)

if write_current_project:
    i7.write_latest_project(my_proj, give_success_feedback = True)
elif read_i7_default_project:
    print("Note we can write a new default project with -wp or -pw.")
