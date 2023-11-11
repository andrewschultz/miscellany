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

bail_on_error = True
do_diff_after = True
copy_to_blank = False
need_abbreviation = False
cmd_line_proj = ''
trim_before = True
ignore_misaligned_timestamps = False
reverse_copy = False

NO_DIFFS = 0
MAIN_DIFFS = 1
ALL_DIFFS = 2

show_diff_after = MAIN_DIFFS

def usage(message = "USAGE"):
    print(message)
    print("a na an = need abbreviation in directory e.g. btp vs buck-the-past")
    print("b nb bn = toggles bail")
    print("d nd dn = diff after or not")
    print("c = copy to blank e.g. if there is no story.ni in the destination, do this")
    print("r = reverse-copy (useful for branches)")
    print("s/sa/as = show all, sn/ns = show none, sm/ms = show main story.ni")
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
            copy_source_to_github(x, copy_timestamps_misaligned)
        return
    my_main = i7.main_src(my_proj)
    if trim_before:
        os.system("ttrim.py c {}".format(my_main))
    my_gh = i7.gh_src(my_proj)
    if not os.path.exists(my_main):
        print("Cannot find main source", my_main)
        if bail_on_error:
            sys.exit()
        else:
            return
    if not os.path.exists(my_gh):
        if not copy_to_blank:
            print("Cannot find GitHub file", my_gh)
            print("If this is new, you may wish to copy it manually with c/-c or set copy_to_blank = True in the code.")
        else:
            if reverse_copy:
                sys.exit("Can't reverse copy if {} doesn't exist.".format(my_gh))
            print("Copying", my_main, "to new file", my_gh)
            shutil.copy(my_main, my_gh)
        if bail_on_error:
            sys.exit()
        else:
            return
    if filecmp.cmp(my_main, my_gh):
        mt.warn(my_main, "and", my_gh, "are equivalent. Not copying.")
        return # not an error, so no bail-on-error
    if reverse_copy:
        (my_main, my_gh) = (my_gh, my_main)
    if os.stat(my_main).st_mtime < os.stat(my_gh).st_mtime:
        mt.warn("WARNING timestamp for from-file is after timestamp for to-file. Ignore with -i or reverse with -r.")
        mt.warn("    ----> from: {}".format(my_main))
        mt.warn("    ---->   to: {}".format(my_gh))
        if not copy_timestamps_misaligned:
            if bail_on_error:
                sys.exit()
            else:
                return
    mt.okay("Copying", my_main, "to", my_gh)
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
    elif arg == 'b':
        bail_on_error = True
    elif arg in ('bn', 'nb'):
        bail_on_error = False
    elif arg == 'd':
        do_diff_after = True
    elif arg in ('dn', 'nd', 'n'):
        do_diff_after = False
    elif arg == 'i':
        ignore_misaligned_timestamps = True
    elif arg == 'r':
        reverse_copy = True
    elif arg in ( 's', 'sa', 'as' ):
        show_diff_after = ALL_DIFFS
    elif arg in ( 'ms', 'sm' ):
        show_diff_after = MAIN_DIFFS
    elif arg in ( 'sn', 'ns' ):
        show_diff_after = NO_DIFFS
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
copy_source_to_github(cmd_line_proj, ignore_misaligned_timestamps)

if do_diff_after:
    from_dir = os.getcwd()
    to_dir = i7.proj2dir(cmd_line_proj, to_github = True, bail_if_nothing = True)
    if to_dir != from_dir:
        print("Switching to {} in-script. You may wish to do so in your shell.".format(to_dir))
    os.chdir(to_dir)
    if show_diff_after == ALL_DIFFS:
        os.system("git diff --word-diff")
    elif show_diff_after == MAIN_DIFFS:
        os.system("git diff --word-diff **story.ni")
        print("-s to show all difference(s) after, -sn for none")
    else:
        print("-s to show all difference(s) after, -sm for main")
