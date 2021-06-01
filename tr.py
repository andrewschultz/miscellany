#
# tr.py: opens up a trizbort file or gets its name with -c
#

import os
import sys
import i7
import mytools as mt
from pathlib import Path
import subprocess
from collections import defaultdict
import pyperclip

to_clipboard = False
orig_name = False
link_name = False

my_triz = defaultdict(str)

def usage():
    print("Use a project name as an argument. You can also use a sub-map, such as roi-h, for a sub-map. In this case the 'others' area of A Roiling Original.")
    print("e = text editor")
    print("c = to clipboard")
    sys.exit()

cmd_count = 1
my_editor = 'gui'

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'e':
        my_editor = 'txt'
    elif arg == 'en' or arg == 'ne':
        my_editor = 'gui'
    elif arg == 'c':
        to_clipboard = True
    elif arg == 'cl' or arg == 'lc':
        to_clipboard = link_name = True
        orig_name = False
    elif arg == 'co' or arg == 'oc':
        to_clipboard = orig_name = True
        link_name = False
    elif arg in i7.i7x:
        if arg in my_triz:
            print("SKIP redefining", arg)
        my_triz[arg] = my_editor
    elif arg == '?':
        usage()
    elif '?' in arg:
        a = arg.replace('?', '')
        if a in i7.i7trizmaps:
            for x in i7.i7trizmaps[a]:
                print(x, "=>", i7.i7trizmaps[a][x])
        sys.exit()
    else:
        got_one = False
        for x in i7.i7trizmaps:
            if arg in i7.i7trizmaps[x]:
                if arg in my_triz:
                    print("SKIP redefining", arg)
                    continue
                my_triz[(x, arg)] = my_editor
                got_one = True
        if not got_one:
            usage()
    cmd_count += 1

if len(my_triz) == 0:
    my_triz = [ i7.curdef ]
    print("Going with default", i7.curdef)

clip_text = ""

for x in my_triz:
    exe = "c:/tech/trizbort/trizbort.exe"
    if type(x) == str:
        tf = i7.triz(x)
        if x == 'txt':
            exe = mt.npnq
    else:
        tf = i7.i7trizmaps[x[0]][x[1]]
    if not os.path.exists(tf):
        print("Uh oh. {0} is not a valid path for {1}.".format(tf, x))
        continue
    tf2 = os.path.realpath(tf)
    if to_clipboard:
        if tf == tf2 or orig_name:
            clip_text += tf
        elif link_name:
            clip_text += tf2
        else:
            clip_text += "{} <=> {}".format(tf, tf2)
        continue
    if tf2 != tf:
        print("Followed link from", tf, "to", tf2)
    if exe == 'txt':
        mt.npo(u)
    else:
        subprocess.Popen([exe, tf2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Launching file", tf2)

if to_clipboard:
    pyperclip.copy(clip_text)
    print(clip_text.strip())