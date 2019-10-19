import sys
import os
import i7
import mytools as my
from filecmp import cmp

copy_over = True
copy_back = True
do_win_merge = True

def usage():
    print("Only co/copy over and cb/copy back defined at this time.")

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'co': copy_over = True
    elif arg == 'cb': copy_back = True
    else: usage()
    cmd_count += 1

x = i7.dir2proj(os.getcwd())

my_gh = i7.gh_src(x)
my_so = i7.main_src(x)

print(i7.main_src(x))
print(i7.gh_src(x))

if not os.path.exists(my_gh): sys.exit("Couldn't locate github story.ni")
if not os.path.exists(my_so): sys.exit("Couldn't locate main story.ni")

if cmp(my_gh, my_so): sys.exit("GitHub and games/inform files are identical.")

if do_win_merge:
    mt.wm(my_gh, my_so)
else:
    if not copy_over and not copy_back:
        sys.exit("Specify copying over or copying back.")
    if copy_over and copy_back:
        sys.exit("Can't both copy over and copy back.")
    if copy_over:
        print("Copying to GitHub")
        copy(my_so, my_gh)
    else:
        print("Copying from GitHub")
        copy(my_gh, my_so)