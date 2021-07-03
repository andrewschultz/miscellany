# gpu.py
# pushes all unpushed commits to github
#
# todo: git diff --name-only --cached
#       git ls-files --modified

import os
import mytools as mt
import subprocess
import glob
from collections import defaultdict

master_to_main = []
note_nongit = False
push_everything = False

check_pushes = check_modified = check_staged = False

x = glob.glob(mt.gitbase + "/*")

ignores_file = "c:/writing/scripts/gpu.txt"
ignores_dict = defaultdict(bool)

valid_git = []

def usage():
    print("a = try all options")
    print("m/p/s = check modified/pushes/staged.")
    sys.exit()

def check_all_pushes(valid_git):
    cmd_array = [ 'git', 'rev-list', 'main', '--not', 'origin/main', '--count' ]
    cmd_array_2 = [ 'git', 'rev-list', 'master', '--not', 'origin/master', '--count' ]
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        try:
            x = subprocess.check_output(cmd_array, stderr = subprocess.PIPE).strip().decode()
            if int(x) > 0:
                print(x, "Unpushed commit{} in".format(mt.plur(int(x))), bn)
                if push_everything:
                    os.system("git push")
                continue
        except:
            pass
        try:
            x = subprocess.check_output(cmd_array_2, stderr = subprocess.PIPE).strip().decode()
            master_to_main.append(bn)
        except:
            pass
        continue

def check_modified_unadded(valid_git):
    count = 0
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        try:
            cmd_array = [ 'git', 'ls-files', '--modified' ]
            cmd_out = subprocess.check_output(cmd_array, stderr = subprocess.PIPE).strip().decode()
            if not cmd_out:
                continue
            ary = cmd_out.split("\n")
            print("Git repo {} has {} modified/unadded file{}.".format(bn, len(ary), mt.plur(len(ary))))
            count += 1
            for x in ary:
                print("    ----> {}".format(x))
        except:
            pass
    return count = 0

def check_staged_uncommitted(valid_git):
    count = 0
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        try:
            cmd_array = [ 'git', 'diff', '--name-only', '--cached']
            cmd_out = subprocess.check_output(cmd_array, stderr = subprocess.PIPE).strip().decode()
            if not cmd_out:
                continue
            ary = cmd_out.split("\n")
            print("Git repo {} has {} staged/uncommitted file{}.".format(bn, len(ary), mt.plur(len(ary))))
            count += 1
            for x in ary:
                print("    ----> {}".format(x))
        except:
            pass
    return count = 0

def get_ignores():
    with open(ignores_file) as file:
        for (line_count, line) in enumerate (file, 1):
            ary = line.split(",")
            for q in ary:
                if q.lower() in ignores_dict:
                    print(q, "already in ignore dict.")
                    continue
                ignores_dict[q] = True

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'a':
        check_modified = check_pushes = check_staged = True
    elif re.match("[mps]+$", arg):
        check_modified |= 'm' in arg
        check_pushes |= 'p' in arg
        check_staged |= 's' in arg
    else:
        usage()        
    cmd_count += 1

for d in x:
    bn = os.path.basename(d)
    if not os.path.isdir(d):
        continue
    if bn.lower() in ignores_dict:
        continue
    if not os.path.isdir(os.path.join(d, ".git")):
        if note_nongit:
            print(bn, "is not a git subdirectory.")
        continue
    valid_git.append(d)

if not (check_modified = check_pushes = check_staged):
    sys.exit("Must specify one of modified/pushes/staged, or a for all.")

if check_modified:
    check_modified_unadded(valid_git)

if check_pushes:
    check_all_pushes(valid_git)

if check_staged:
    check_staged_uncommitted(valid_git)

if len(master_to_main):
    print("RENAME MASTER TO MAIN FOR {}:".format(', '.join(master_to_main)))
    print("<FIX ON GITHUB IF NECESSARY: https://github.com/andrewschultz/SAMPLE-REPO-NAME/settings/branches>")
    print("git branch -m master main")
    print("git push -u origin main")
    print("git push origin --delete master")
