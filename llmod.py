# llmod.py: gets rid of lalaland (or other default room) references

from shutil import copy
from collections import defaultdict
from filecmp import cmp
import sys
import os
import re

discard_rooms = defaultdict(str)

on_off = [ 'off', 'on' ]

f1 = 'story.ni'
f2 = 'story.ni2'

def usage():
    print("-c/-nc = toggle copy, default is", on_off[copy_over])
    print("-d/-nd = run difference file with copy on, default is", on_off[run_dif_on_copy])
    print("-u = unit tests, -unb = unit tests and no bail")
    print("-r = new default banish room, or r= in one argument")
    exit()

def mootify(a):
    ll = re.sub(r"move (.*) to " + discard_room, r"moot \1", a, 0, re.IGNORECASE)
    ll = re.sub(r"now (.*) (are|is) in " + discard_room, r"moot \1", ll, 0, re.IGNORECASE)
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
            discard_rooms[a[0]] = a[1].lower()
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
run_dif_on_copy = True

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-':
        arg = arg[1:]
    if arg == 'u':
        do_unit_tests = True
    elif arg == 'un' or arg == 'unb':
        do_unit_tests = True
        bail = False
    elif arg == 'c':
        copy_over = True
    elif arg == 'd':
        run_dif_on_copy = True
    elif arg == 'dn' or arg == 'nd':
        run_dif_on_copy = False
    elif arg.startswith('r='):
        discard_room = sys.argv[count][2:]
    elif arg == 'r':
        discard_room = sys.argv[count+1].lower()
        count = count + 1
    else:
        print("Bad argument", arg)
        usage()
    count = count + 1

if not os.path.isfile(f1):
    print("No file", f1, "-- bailing.")
    exit()

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
        if discard_room not in line.lower() or '[ic]' in line or ignore_next:
            ignore_next = False
            fout.write(line)
            continue
        if 'definition: a thing is moot:' in line or line.startswith('to moot'): ignore_next = True
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
    if run_dif_on_copy: os.system("wm {:s} {:s}".format(f1, f2))
    if copy_over:
        copy(f2, f1)
    else:
        print("-c to copy over")
    os.remove(f2)
