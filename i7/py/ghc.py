# ghc.py
# "github copy" copies story.ni from games\inform to github
#

import pathlib
import mytools as mt
import shutil
import filecmp
import os
import i7
import sys

do_diff_after = True
copy_to_blank = False
need_abbreviation = False
cmd_line_proj = ''
trim_before = True

def usage(message = "USAGE"):
    print(message)
    print("a na an = need abbreviation in directory e.g. btp vs buck-the-past")
    print("d nd dn = diff after or not")
    print("c = copy to blank e.g. if there is no story.ni in the destination, do this")
    sys.exit()

def check_valid_git_path():
    path_ary = pathlib.PurePath(os.getcwd()).parts
    if 'github' not in path_ary:
        sys.exit("Not in a github directory.")
    ghi = path_ary.index("github")
    root_path = os.path.normpath(os.path.join('/'.join(path_ary[0:ghi+2]),".git"))
    if not os.path.exists(root_path):
        sys.exit("This github directory does not have a .git subdirectory. You may need to fetch it from somewhere.")

def cmd_line_sniffer(my_proj):
    if not my_proj:
        my_proj = i7.dir2proj(empty_if_unmatched = need_abbreviation)
    if not my_proj:
        sys.exit("Could not find project for the current directory. Bailing.")
    return my_proj

def copy_source_to_github(my_proj, copy_timestamps_misaligned = False):
    if my_proj in i7.i7com and my_proj in i7.i7com[my_proj].split(","): # recursive stuff like Stale Tales Slate
        for x in i7.i7com[my_proj].split(","):
            if x == my_proj:
                continue
            copy_source_to_github(os.path.join(d, x), copy_to_blank, copy_timestamps_misaligned)
        return
    my_main = i7.main_src(my_proj)
    if trim_before:
        os.system("ttrim.py c {}".format(my_main))
    my_gh = i7.gh_src(my_proj)
    if not os.path.exists(my_main):
        print("Cannot find", my_main)
        return
    if not os.path.exists(my_gh):
        if not copy_to_blank:
            print("Cannot find", my_gh)
            print("If this is new, you may wish to copy it manually with c/-c or set copy_to_blank = True in the code.")
        else:
            print("Copying", my_main, "to new file", my_gh)
            shutil.copy(my_main, my_gh)
        return
    if filecmp.cmp(my_main, my_gh):
        print(my_main, "and", my_gh, "are equivalent. Not copying.")
        return
    if os.stat(my_main).st_mtime < os.stat(my_gh).st_mtime:
        print("WARNING timezone for the two files is messed up.")
        if not copy_timestamps_misaligned:
            return
    print("Copying", my_main, "to", my_gh)
    shutil.copy(my_main, my_gh)

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'c':
        copy_to_blank = True
    elif arg in ('a', 'ya', 'ay'):
        need_abbreviation = True
    elif arg in ('na', 'an'):
        need_abbreviation = False
    elif arg == 'd':
        do_diff_after = True
    elif arg in ('dn', 'nd', 'n'):
        do_diff_after = False
    elif arg == '?':
        usage()
    else:
        if cmd_line_proj:
            sys.exit("Duplicate projects specified.")
        cmd_line_proj = i7.proj_exp(arg, return_nonblank = not need_abbreviation, to_github = True)
        if not cmd_line_proj:
            usage(message = "UNRECOGNIZED PARAMETER {}".format(arg))
        else:
            print("Current project is", cmd_line_proj)
    cmd_count += 1

cmd_line_proj = cmd_line_sniffer(cmd_line_proj)
copy_source_to_github(cmd_line_proj)

if do_diff_after:
    from_dir = os.getcwd()
    to_dir = i7.proj2dir(cmd_line_proj, to_github = True)
    if to_dir != from_dir:
        print("Switching to {} in-script. You may wish to do so in your shell.".format(to_dir))
    os.chdir(to_dir)
    os.system("git diff --word-diff")
