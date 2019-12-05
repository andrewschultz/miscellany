#
# source file copy/compare sfc.py
#
# co = copy over, cb = copy back
# can run from a source/github directory or specify project
#

import sys
import os
import i7
import mytools as mt
from filecmp import cmp
from shutil import copy

copy_over = False
copy_back = False
do_win_merge = True
force_win_merge = False

my_proj = ""

def usage(arg=""):
    if arg: print("BAD ARGUMENT", arg)
    print("=" * 60)
    print("co = copy over")
    print("cb = copy back")
    print("wm = force winmerge (on by default but switched off with co/cb)")
    print("You can also specify a project if you are not in a github or games/inform source directory.")
    exit()

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'co':
        copy_over = True
        do_win_merge = False
    elif arg == 'cb':
        copy_back = True
        do_win_merge = False
    elif arg == 'wm':
        force_win_merge = True
    elif arg == '?': usage()
    elif arg in i7.i7x:
        if my_proj: sys.exit("Cannot define two projects.")
        my_proj = arg
    else: usage(arg)
    cmd_count += 1

do_win_merge |= force_win_merge

if not my_proj:
    my_proj = i7.dir2proj(os.getcwd())
    if not my_proj: sys.exit("Could not get valid project from command parameters or CWD. Bailing.")
    print("Taking project from command line:", my_proj)

my_gh = i7.gh_src(my_proj)
my_so = i7.main_src(my_proj)

print(i7.main_src(my_proj))
print(i7.gh_src(my_proj))

if not os.path.exists(my_gh): sys.exit("Couldn't locate github story.ni")
if not os.path.exists(my_so): sys.exit("Couldn't locate main story.ni")

if cmp(my_gh, my_so): sys.exit("GitHub and games/inform files are identical.")

if do_win_merge:
    mt.wm(my_gh, my_so)
    if not copy_over and not copy_back: sys.exit()


if not copy_over and not copy_back:
    sys.exit("We shouldn't have hid this code, but you need to specify copying over or copying back.")

if cmp(my_gh, my_so): sys.exit("After you modified one or both of them, GitHub and games/inform files are identical. No need to copy.")

if copy_over and copy_back:
    sys.exit("Can't both copy over and copy back.")
if copy_over:
    print("Copying to GitHub")
    copy(my_so, my_gh)
else:
    print("Copying from GitHub")
    copy(my_gh, my_so)