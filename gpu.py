# gpu.py
# pushes all unpushed commits to github
#
# todo: git diff --name-only --cached
#       git ls-files --modified

import sys
import os
import re
import subprocess
import glob
from collections import defaultdict
import mytools as mt

master_to_main = []
note_nongit = False
run_push_command = False
master_main_check = False

check_pushes = check_modified = check_staged = check_uuid = False

x = glob.glob(mt.gitbase + "/*")

ignores_file = "c:/writing/scripts/gpu.txt"
ignores_dict = defaultdict(bool)

valid_git = []

def usage():
    print("a = try all options")
    print("m/p/s = check modified/pushes/staged. R = run don't print. You can combine any or all of these.")
    print("mm = master-to-main check")
    print("special option not in a: u = uuid check if repo has story.ni")
    sys.exit()

def check_master_main(valid_git):
    global master_to_main
    count = 0
    cmd_array_2 = [ 'git', 'rev-list', 'master', '--not', 'origin/master', '--count' ]
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        try:
            x = subprocess.check_output(cmd_array_2, stderr = subprocess.PIPE).strip().decode()
            master_to_main.append(bn)
            count += 1
        except:
            pass
        continue
    return count

def check_story_no_uuid(valid_git):
    count = 0
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        cmd_array = [ 'git', 'ls-files' ]
        try:
            x = subprocess.check_output(cmd_array, stderr = subprocess.PIPE).strip().decode()
            ary = x.split("\n")
            if 'story.ni' in ary and 'uuid.txt' not in x:
                print("Story.ni but no uuid.txt in", bn)
                print("    ----> likely commands:")
                print("        cd \\games\\inform\\{}.inform".format(bn))
                print("        mvl uuid.txt {}".format(bn))
                print("        cd \\users\\andrew\\documents\\github\\{}".format(bn))
                print("        git add -f uuid.txt")
                print("        git commit -m \"Added UUID file\"")
                count += 1
        except:
            pass
    return count

def check_all_pushes(valid_git):
    count = 0
    cmd_array = [ 'git', 'rev-list', 'main', '--not', 'origin/main', '--count' ]
    cmd_array_2 = [ 'git', 'rev-list', 'master', '--not', 'origin/master', '--count' ]
    for d in valid_git:
        bn = os.path.basename(d)
        os.chdir(d)
        try:
            x = subprocess.check_output(cmd_array, stderr = subprocess.PIPE).strip().decode()
            if int(x) > 0:
                print(x, "Unpushed commit{} in".format(mt.plur(int(x))), bn)
                count += 1
                if run_push_command:
                    os.system("git push")
                continue
        except:
            pass
        continue
    return count

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
    return count

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
    return count

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
    if arg == 'a': # do NOT include uuid check, since it rarely needs to be done
        run_push_command = check_modified = check_pushes = check_staged = master_main_check = True
    elif arg == 'mm':
        master_main_check = True
    elif re.match("[mprsu]+$", arg):
        check_modified |= 'm' in arg
        check_pushes |= 'p' in arg
        run_push_command |= 'r' in arg
        check_staged |= 's' in arg
        check_uuid |= 'u' in arg
    else:
        usage()
    cmd_count += 1

get_ignores()

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

if not (check_modified or check_pushes or check_staged or master_main_check or check_uuid):
    sys.exit("Must specify one of modified/pushes/staged/master-main check, or a for all.")

if check_modified:
    temp = check_modified_unadded(valid_git)
    if not temp:
        print("Hooray! No repos with modified/unadded files.")

if check_pushes:
    temp = check_all_pushes(valid_git)
    if not temp:
        print("Hooray! No repos that need a push.")
    elif not run_push_command:
        print("There are changes. Use the R flag to push them.")

if check_staged:
    temp = check_staged_uncommitted(valid_git)
    if not temp:
        print("Hooray! No repos with staged/uncommitted files.")

if check_uuid:
    temp = check_story_no_uuid(valid_git)
    if not temp:
        print("Hooray! No repos with staged/uncommitted files.")

if master_main_check:
    temp = check_master_main(valid_git)
    print(master_to_main)
    if temp:
        print("RENAME MASTER TO MAIN FOR {}:".format(', '.join(master_to_main)))
        print("<FIX ON GITHUB IF NECESSARY: https://github.com/andrewschultz/SAMPLE-REPO-NAME/settings/branches>")
        print("    git branch -m master main")
        print("    git push -u origin main")
        print("    git push origin --delete master")
    else:
        print("Hooray! No master/main changes needed.")