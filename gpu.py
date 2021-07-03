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

x = glob.glob(mt.gitbase + "/*")

ignores_file = "c:/writing/scripts/gpu.txt"
ignores_dict = defaultdict(bool)

valid_git = []

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

def check_staged_uncommitted(valid_git):
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        try:
            cmd_array = [ 'git', 'ls-files', '--modified' ]
            cmd_out = subprocess.check_output(cmd_array, stderr = subprocess.PIPE).strip().decode()
            if not cmd_out:
                continue
            ary = cmd_out.split("\n")
            print("Git repo {} has {} staged/uncommitted file{}.".format(bn, len(ary), mt.plur(len(ary))))
            for x in ary:
                print("    ----> {}".format(x))
        except:
            pass

def get_ignores():
    with open(ignores_file) as file:
        for (line_count, line) in enumerate (file, 1):
            ary = line.split(",")
            for q in ary:
                if q.lower() in ignores_dict:
                    print(q, "already in ignore dict.")
                    continue
                ignores_dict[q] = True

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

check_all_pushes(valid_git)
check_staged_uncommitted(valid_git)

if len(master_to_main):
    print("RENAME MASTER TO MAIN FOR {}:".format(', '.join(master_to_main)))
    print("<FIX ON GITHUB IF NECESSARY: https://github.com/andrewschultz/SAMPLE-REPO-NAME/settings/branches>")
    print("git branch -m master main")
    print("git push -u origin main")
    print("git push origin --delete master")
