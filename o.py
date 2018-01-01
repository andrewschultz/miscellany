# o.py
#
# launches or edits various files based on keywords etc
#
# todo: convert the booleans to a dictionary
# have a shortcut of dictionary stuff to look at
# have format strings for each dictionary element if possible

import sys
import os
import re
import i7

from collections import defaultdict

exp_cmd = defaultdict(str)
opt_dict = defaultdict(bool)

exp_cmd = { "tr": "open_trizbort",
    "cg": "open_cantgo",
    "cgl": "launch_cantgo",
    "wa": "open_walkthrough",
    "w": "open_walkthrough",
    "t": "open_source",
    "ta": "open_tables",
    "no": "open_notes",
    "rn": "release_notes",
    "i": "open_raw_invisiclues"
}

conflict = False

for x in exp_cmd.keys():
    if x in i7.i7x.keys():
        conflict = True
        print("Conflict: exp cmd and i7x keys both feature", x, "mapping to", i7.i7x[x], "and", exp_cmd[x])

if conflict:
    print("Fix conflicts before rerunning.")
    exit()

def usage():
    trim = "=" * 30
    print(trim, "usage", trim)
    for x in exp_cmd.keys():
        print(x,"=>", exp_cmd[x])
    exit()

def try_to_open(a):
    if os.path.exists(a):
        print("File found:", a)
        os.system(a)
    else:
        print("File not found:", a)
    return

x = os.getcwd()
# print(x)
proj = ""

notepad = "C:\\Program Files (x86)\\Notepad++\\notepad++.exe"

release_notes = False
open_trizbort = False
open_notes = False
open_source = False
open_tables = False
open_walkthrough = False
open_raw_invisiclues = False

open_cantgo = False
launch_cantgo = False

if ".inform\source" in x.lower():
    proj =  re.sub("\.inform.*", "", x)
    proj = re.sub(".*[\\\/]", "", proj)
    print("Using default project", proj)

count = 0

while (count < len(sys.argv)):
    ca = sys.argv[count]
    if ca == 'tr':
        open_trizbort = True
    if ca == 'cg':
        open_cantgo = True
    if ca == 'cgl':
        launch_cantgo = True
    if ca == 'wa' or ca == 'w':
        open_walkthrough = True
    if ca == 't':
        open_source = True
    if ca == 'ta':
        open_tables = True
    if ca == 'no':
        open_notes = True
    if ca == 'rn':
        release_notes = True
    if ca == 'i':
        open_raw_invisiclues = True
    if ca == '?' or ca == '-?':
        usage()
        exit()
    count = count + 1

sums = release_notes + open_trizbort + open_notes + open_source + open_tables + open_walkthrough + open_raw_invisiclues

proj_space = re.sub("-", " ", proj)
proj_und = re.sub("-", "_", proj)

source = "c:\\games\\inform\\{:s}.inform\\Source\\".format(proj)

if open_raw_invisiclues:
    print("Opening raw invisiclues for", rev)
    try_to_open("c:\\writing\\scripts\\invis\\{:s}.txt".format(rev))

if open_notes:
    print("Opening notes file for", proj)
    try_to_open(source + "notes.txt")

if open_walkthrough:
    print("Opening notes file for", proj)
    if os.path.exists(source + "walkthrough.txt"):
        try_to_open(source + "walkthrough.txt")
    elif os.path.exists(source + "walkthru.txt"):
        try_to_open(source + "walkthru.txt")

if launch_cantgo:
    try_to_open(source + "cantgo.htm")

if open_cantgo:
    if os.path.exists(source + "cantgo.htm"):
        print("Opening cantgo file for", proj)
        os.system("start \"\" \"{:s}\" {:s}cantgo.htm".format(notepad,source))
    else:
        print("No cantgo.htm for", proj)

if open_source:
    print("Opening source file for", proj)
    try_to_open(source + "story.ni")

if open_tables:
    print("Opening tables file for", proj)
    try_to_open("{:s}{:s} tables.i7x".format(i7.i7x, proj_space))

if open_trizbort:
    print("Opening trizbort file for", proj)
    try_to_open("c:\\games\\inform\\triz\\mine\\{:s}.trizbort".format(proj))

if release_notes:
    if proj in i7.i7rn.keys():
        if i7.i7rn[proj].isnumeric():
            rel_file = "{:s}_release_{:s}_notes.txt".format(proj, i7.i7rn[proj])
        else:
            rel_file = i7.i7rn[proj] + "_notes.txt"
    else:
        print("No release notes in i7rn keys. Trying default.")
        rel_file = proj + "_release_1_notes.txt"
    rel_file = re.sub("-", "_", rel_file)
    try_to_open("c:\\users\\andrew\\dropbox\\notes\\{:s}".format(rel_file))

if sums == 0:
    print("Nothing to do.")
