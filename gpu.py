# gpu.py
# pushes all unpushed commits to github
#
# todo: git diff --name-only --cached
#       git ls-files --modified

import os
import mytools as mt
import subprocess
import glob

master_to_main = []
note_nongit = False

cmd_array = [ 'git', 'rev-list', 'main', '--not', 'origin/main', '--count' ]
cmd_array_2 = [ 'git', 'rev-list', 'master', '--not', 'origin/master', '--count' ]

x = glob.glob(mt.gitbase + "/*")

ignores = [ 'kerkerkruip', 'pendulum', 'perlmaven', 'plotex', 'NA', 'frotz', 'glulxe', 'lawless-legends', 'merge-practice' ]

for d in x:
    bn = os.path.basename(d)
    if os.path.isdir(d):
        if bn in ignores:
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
                print(x, "Commit{} in".format(mt.plur(int(x)), bn, "so pushing.")
                print("git push")
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
    print("<FIX ON GITHUB IF NECESSARY: https://github.com/andrewschultz/{}/settings/branches>".format(bn))
    print("git branch -m master main")
    print("git push -u origin main")
    print("git push origin --delete master")
