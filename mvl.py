# mvl.py
# move file to its link

import os
import i7
import sys
import glob
import colorama
import mytools as mt

debug_try = False
force_rewrite_link = False

def github_move(file_name, this_proj = ''):
    changing_link = False
    if not os.path.exists(file_name):
        mt.fail("Can't find file", file_name)
        return
    if os.path.islink(file_name):
        mt.warn(file_name, "is already a link.")
        if not force_rewrite_link:
            mt.warn("Use -f to rewrite the link.")
        return
        changing_link = True
    if not this_proj:
        this_proj = i7.dir2proj()
    github_dir = i7.proj2dir(this_proj, to_github=True)
    if not github_dir:
        sys.exit("Can't find a github directory to move to. Check your current directory or modify i7p.txt or force a project with p=.\nNOTE: p= must come first as of 7/23 due to coding laziness.")
    if os.path.islink(file_name):
        mt.warn(file_name, "is already a link!")
        return
    if file_name.startswith('rbr-'):
        github_dir += "/testing/branch"
    if file_name.startswith('reg-'):
        github_dir += "/testing"
        if '-lone-' in file_name and os.path.exists(github_dir + "//standalone"):
            github_dir += "/standalone"
        elif '-thru-' in file_name:
            github_dir += "/generated"
    if file_name.endswith('.py'):
        github_dir += "/utils"
    if not os.path.exists(github_dir):
        normdir = os.path.normpath(github_dir)
        mt.fail(normdir + " does not exist. Create it with ...")
        mt.failbail("mkdir " + normdir)
        sys.exit()
    new_file = os.path.normpath("{}//{}".format(github_dir, file_name))
    file_name = mt.quote_spaced_file(file_name)
    new_file = mt.quote_spaced_file(new_file)
    move_cmd = "move {} {}".format(file_name, new_file)
    link_cmd = "mklink {} {}".format(file_name, new_file)
    if debug_try:
        print(move_cmd)
        print(link_cmd)
    else:
        x = os.system(move_cmd)
        y = os.system(link_cmd)

cmd_count = 1

force_project = ''

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == 'd':
        debug_try = True
    elif arg.startswith('p='):
        force_project = arg[2:]
    elif '*' in arg:
        ary = glob.glob(arg)
        if not len(ary):
            mt.fail("Nothing in glob for", arg)
        else:
            for x in glob.glob(arg):
                github_move(x, force_project)
    else:
        github_move(arg, force_project)
    cmd_count += 1

