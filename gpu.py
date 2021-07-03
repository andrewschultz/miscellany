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

cmd_array = [ 'git', 'rev-list', 'main', '--not', 'origin/main', '--count' ]
cmd_array_2 = [ 'git', 'rev-list', 'master', '--not', 'origin/master', '--count' ]

x = glob.glob(mt.gitbase + "/*")

ignores_file = "c:/writing/scripts/gpu.txt"
ignores_dict = defaultdict(bool)

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
    if os.path.isdir(d):
        if bn.lower() in ignores_dict:
            continue
        if not os.path.isdir(os.path.join(d, ".git")):
            if note_nongit:
                print(bn, "is not a git subdirectory.")
            continue
        #print("Trying", bn)
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

if len(master_to_main):
    print("RENAME MASTER TO MAIN FOR {}:".format(', '.join(master_to_main)))
    print("<FIX ON GITHUB IF NECESSARY: https://github.com/andrewschultz/SAMPLE-REPO-NAME/settings/branches>")
    print("git branch -m master main")
    print("git push -u origin main")
    print("git push origin --delete master")
