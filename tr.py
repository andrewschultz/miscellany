import os
import sys
import i7
import mytools as mt
from pathlib import Path
import subprocess
from collections import defaultdict

my_triz = defaultdict(str)

def usage():
    print("Use a project name as an argument.")
    exit()

cmd_count = 1
my_editor = 'gui'

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'e':
        my_editor = 'txt'
    elif arg == 'en' or arg == 'ne':
        my_editor = 'gui'
    elif arg in i7.i7x:
        if arg in my_triz:
            print("SKIP redefining", arg)
        my_triz[arg] = my_editor
    else:
        got_one = False
        for x in i7.i7trizmaps:
            if arg in i7.i7trizmaps[x]:
                if arg in my_triz:
                    print("SKIP redefining", arg)
                    continue
                my_triz[arg] = my_editor
                got_one = True
        if not got_one:
            usage()
    cmd_count += 1

if len(my_triz) == 0:
    my_triz = [ i7.curdef ]
    print("Going with default", i7.curdef)

for x in my_triz:
    if type(x) == str:
        tf = i7.triz(x)
    else:
        tf = i7.i7trizmaps[x[0]][x[1]]
    if not os.path.exists(tf):
        print("Uh oh. {0} is not a valid path for {1}.".format(tf, x))
        continue
    exe = mt.npnq if my_triz[x] == 'txt' else "c:/tech/trizbort/trizbort.exe"
    print(exe)
    tf2 = mt.follow_link(tf)
    if tf2 != tf:
        print("Followed link from", tf, "to", tf2)
    if exe == 'txt':
        mt.npo(u)
    else:
        subprocess.Popen([exe, tf2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Launching file", tf2)