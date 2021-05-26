import shutil
import filecmp
import os
import i7
import sys

def copy_source_to_github(d = os.getcwd(), copy_to_blank = False, copy_timestamps_misaligned = False):
    my_proj = i7.dir2proj(d)
    my_main = i7.main_src(my_proj)
    my_gh = i7.gh_src(my_proj)
    if filecmp.cmp(my_main, my_gh):
        print(my_main, "and", my_gh, "are equivalent. Not copying.")
        return
    if not os.path.exists(my_main):
        print("Cannot find", my_main)
        return
    if not os.path.exists(my_gh) and not copy_to_blank:
        print("Cannot find", gh)
        print("If this is new, you may wish to copy it manually or set copy_to_blank = True.")
        return
    if os.stat(my_main).st_mtime < os.stat(my_gh).st_mtime:
        print("WARNING timezone for the two files is messed up.")
        if not copy_timestamps_misaligned:
            return
    print("Copying", my_main, "to", my_gh)
    shutil.copy(my_main, my_gh)

if len(sys.argv) > 1:
    copy_source_to_github(sys.argv[1])
else:
    copy_source_to_github()
