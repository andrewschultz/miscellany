import sys
import os
import re

def try_to_open(a):
    if os.path.exists(a):
        os.system(a)
    else:
        print("File not found:", a)
    print("File found:", a)
    os.system(a)
    return

x = os.getcwd()
print(x)
proj = ""

notepad = "C:\\Program Files (x86)\\Notepad++\\notepad++.exe"

release_notes = False
open_trizbort = False
open_notes = False
open_source = False
open_tables = False
open_walkthrough = False

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
    count = count + 1

sums = open_trizbort + open_notes + open_source + open_tables

proj_space = re.sub("-", " ", proj)
proj_und = re.sub("-", "_", proj)

i7 = "C:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\"

source = "c:\\games\\inform\\{:s}.inform\\Source\\".format(proj)

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
    try_to_open("{:s}{:s} tables.i7x".format(i7, proj_space))

if open_trizbort:
    print("Opening trizbort file for", proj)
    os.system("c:\\games\\inform\\triz\\mine\\{:s}.trizbort".format(proj))

if release_notes:
    print("Opening release notes for", proj)
    os.system("c:\\users\\andrew\\dropbox\\notes\\{:s}.txt".format(proj))

if sums == 0:
    print("Nothing to do.")
