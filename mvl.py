#
# mvl.py
# move non-github file to a github subdirectory
#

import os
import i7
import sys
import glob
import colorama
import mytools as mt
from shutil import copy

mt.check_for_admin()

debug_try = False
force_rewrite_link = False

def usage():
    mt.warn("USAGE for mvl.py")
    mt.warn('=' * 50)
    print("d  : force debug/only show what commands to run")
    print("s= : force subdir")
    print("p= : force project")
    sys.exit()

def glob_it(my_glob):
    ary = glob.glob(my_glob)
    if not len(ary):
        mt.fail("Nothing in glob for", arg)
    else:
        for x in ary:
            github_move(x, force_project, force_subdir)

def best_subdir_of(file_name, github_dir):
    if file_name.startswith('rbr-'):
        return "/testing/branch"
    if file_name.startswith('reg-'):
        ret_val = "/testing"
        if '-lone-' in file_name and os.path.exists(github_dir + "/testing/standalone"):
            ret_val += "/standalone"
        elif '-thru-' in file_name:
            ret_val += "/generated"
        return ret_val
    if file_name.endswith('.py'):
        return "/utils"
    return ""

def github_move(file_name, this_proj = '', subdir = ''):
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
    if not subdir:
        subdir = best_subdir_of(file_name, github_dir)
    if not os.path.exists(github_dir):
        normdir = os.path.normpath(github_dir)
        mt.fail(normdir + " does not exist. Create it with ...")
        mt.failbail("mkdir " + normdir)
        sys.exit()
    github_dir += subdir
    if not os.path.exists(github_dir):
        mt.bailfail("Couldn't make directory", github_dir)
    new_file = os.path.normpath("{}//{}".format(github_dir, file_name))
    file_name = mt.quote_spaced_file(file_name)
    new_file = mt.quote_spaced_file(new_file)
    move_cmd = "move {} {} > NUL 2>&1".format(file_name, new_file)
    link_cmd = "mklink {} {} > NUL 2>&1".format(file_name, new_file)
    if debug_try:
        mt.warn("COMMANDS THAT WOULD BE RUN")
        mt.warn(move_cmd)
        mt.warn(link_cmd)
    else:
        x = os.system(move_cmd)
        y = os.system(link_cmd)
        if os.path.islink(file_name):
            mt.okay("Created link {} successfully.".format(file_name))
        else:
            mt.fail("Failed to create link {}.".format(file_name))
        if os.path.exists(file_name):
            mt.okay("Created file {} successfully.".format(new_file))
        else:
            mt.fail("Failed to create file {}.".format(new_file))

cmd_count = 1

force_project = ''
force_subdir = ''

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == 'd':
        debug_try = True
    elif arg.startswith('p='):
        force_project = arg[2:]
    elif arg.startswith('s='):
        force_subdir = arg[2:]
    elif arg == 'l':
        glob_it("reg-*lone*.txt")
    elif arg == '?':
        usage()
    elif '*' in arg:
        glob_it(arg)
    else:
        github_move(arg, force_project, force_subdir)
    cmd_count += 1

