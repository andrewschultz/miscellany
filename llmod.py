# llmod.py: gets rid of lalaland (or other default room) references

from shutil import copy
from collections import defaultdict
from filecmp import cmp
import sys
import os
import re

discard_rooms = defaultdict(str)

f1 = 'story.ni'
f2 = 'story.ni2'

def usage():
    print("-u = unit tests")
    print("-r = new default room")
    print("-b = next arg is banish room, b= current")
    exit()

def mootify(a):
    ll = re.sub(r"move (.*) to " + discard_room, r"moot \1", a, 0, re.IGNORECASE)
    ll = re.sub(r"now (.*) (are|is) in lalaland" + discard_room, r"moot \1", ll, 0, re.IGNORECASE)
    ll = re.sub("not in " + discard_room, "not moot", ll, 0, re.IGNORECASE)
    ll = re.sub("in " + discard_room, "moot", ll, 0, re.IGNORECASE)
    return ll

def read_moot_rooms():
    global discard_room
    cfg_file = "c:/writing/scripts/llmod.txt"
    with open(cfg_file) as file:
        for line in file:
            if line.startswith("#"): continue
            if line.startswith(";"): break
            a = line.strip().split(":")
            discard_rooms[a[0]] = a[1]
    return

def u_trans(a):
    print(a, "/", mootify(a))

def unit_tests(bail = True):
    print("Running unit tests...")
    u_trans("now stuff is in lalaland;")
    u_trans("now stuffs are in lalaland;")
    u_trans("move stuff to lalaland;")
    u_trans("if th is in lalaland, yes; [ic]")
    u_trans("if th are in lalaland, yes; [ic]")
    if bail: exit()
    return

count = 1
discard_room = "lalaland"

difs = 0
line_count = 0
do_unit_tests = False
bail = False
copy_over = False

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-':
        arg = arg[1:]
    if arg == 'u':
        do_unit_tests = True
    elif arg == 'ub':
        do_unit_tests = True
        bail = False
    elif arg == 'b':
        banish_room = sys.argv[count+1].lower()
    elif arg == 'c':
        copy_over = True
    elif arg.startswith('b='):
        banish_room = sys.argv[count][2:]
    elif arg == 'r':
        discard_room = sys.argv[count+1].lower()
        count = count + 1
    else:
        usage()
    count = count + 1

fout = open(f2, "w", newline='\n')

read_moot_rooms()
if 'default' in discard_rooms.keys(): discard_room = discard_rooms['default']

for x in discard_rooms.keys():
    if x + '.inform' in os.getcwd():
        discard_room = discard_rooms[x]
        print(x, "shifts to discard room", discard_rooms[x])

if do_unit_tests: unit_tests(bail)

with open(f1) as file:
    for line in file:
        line_count = line_count + 1
        if discard_room not in line.lower() or '[ic]' in line:
            fout.write(line)
            continue
        ll = mootify(line)
        if ll != line:
            difs = difs + 1
            print("Dif", difs, "at", line_count)
        fout.write(ll)

fout.close()

if cmp(f1, f2):
    print("No changes, no copying over.")
    os.remove(f2)
else:
    print(difs, "total differences.")
    os.system("wm {:s} {:s}".format(f1, f2))
    if copy_over:
        copy(f2, f1)
    else:
        print("-c to copy over")
    os.remove(f2)
