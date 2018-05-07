#############################
# roomsync.py
#
# compares map text from trizbort to source text from an Inform story.ni file
# also, if invisiclues file is there, compares source text from an Inform story.ni file to invisiclues file
#
# verified so far on UP, BTP
#
# also rooms that map *from* a map *to* a

import os
import i7
import sys
import re
import __main__ as main
import xml.etree.ElementTree as ET
from collections import defaultdict

def usage():
    print("Use a project directory or its abbreviation.")
    print("-v = verbose output")
    print("-f = format help for roomsync.txt file")
    exit()

def format_help():
    print("ignore: = ignore rooms labeled X")
    print("rename: = rename (source name) to (trizbort name)")
    exit()

def if_rename(x):
    if x in renamer.keys():
        return renamer[x]
    return x

def read_ignore_file():
    line_count = 0
    with open(ignore_file) as file:
        for line in file:
            line_count += 1
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if line.startswith('ignore:'):
                ll = re.sub("^ignore:", "", line.strip().lower())
                ignore[ll] = 1
            elif line.startswith("rename:"):
                ll = re.sub("^rename:", "", line.strip().lower())
                ary = ll.split("/")
                if len(ary) != 2:
                    print("Misformed RENAME (needs before/after) at line", line_count, ":", ll)
                if verbose: print("Renaming", ary[0], "to", ary[1])
                renamer[ary[0]] = ary[1]

def match_source_invisiclues():
    invisfile = "c:/writing/scripts/invis/{:s}.txt".format(i7.revproj(project))
    print("Checking invisiclues file", invisfile, "...")
    with open(invisfile) as file:
        for line in file:
            if line.startswith(">>"):
                ll = re.sub(">>", "", line.strip().lower())
                ll = re.sub(", ?", " ", ll)
                invis_rooms[ll] = 1
    b = [x for x in list(set(source.keys()) | set(invis_rooms.keys())) if x not in ignore.keys()]
    count = 0
    print_barrier = True
    inviserr = defaultdict(bool)
    for a in b:
        if a not in invis_rooms.keys():
            if print_barrier:
                print("=" * 40)
                print_barrier = False
            count += 1
            print(count, a, "in source but not invisiclues.")
            inviserr['>' + a] = True
    print_barrier = (count > 0)
    for a in b:
        if a not in source.keys():
            if print_barrier:
                print("=" * 40)
                print_barrier = False
            count += 1
            print(count, a, "in invisiclues but not source.")
            inviserr['<' + a] = True
    print ("TEST RESULTS:triz2invis-" + project + ",0,0, " + ", ".join(sorted(inviserr.keys())))

# default dictionaries and such
source = defaultdict(bool)
triz = defaultdict(bool)
invis_rooms = defaultdict(bool)
ignore = defaultdict(bool)
renamer = defaultdict(str)
project = "buck-the-past"

invisiclues_search = True
verbose = False

ignore_file = re.sub("py$", "txt", main.__file__)

current_as_default = False

if i7.dir2proj():
    project = i7.dir2proj()
    current_as_default = True

cmd_count = 1
while cmd_count < len(sys.argv):
    j = re.sub("^-", "", sys.argv[cmd_count].lower())
    if j in i7.i7x.keys():
        project = i7.i7x[j]
        current_as_default = False
    elif os.path.isdir("c:/games/inform/" + j + ".inform"):
        project = j
        current_as_default = False
    elif j == 'v':
        verbose = True
    elif j == 'f':
        format_help()
    else:
        usage()
    cmd_count += 1

trizfile = i7.triz(project)
source_file = i7.src(project)

if not os.path.exists(source_file):
    print(source_file, "does not exist, and there is no expansion for it. Bailing.")
    exit()

try:
    e = ET.parse(trizfile)
except:
    print("Couldn't find", trizfile)
    exit()

read_ignore_file()

root = e.getroot()

for elem in e.iter('room'):
    if elem.get('name'):
        x = str(elem.get('name')).lower()
        x = re.sub(" ?[\/\(].*", "", x, flags=re.IGNORECASE)
        x = re.sub(", ?", " ", x)
        triz[x] = str(elem.get('region')).lower()
    # print (x,triz[x])
    # triz[atype.get('name')] = 1;

with open(source_file) as f:
    for line in f:
        if re.search("^there is a (passroom|pushroom|room) called ", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub("^there is a (passroom|pushroom|room) called ", "", line, re.IGNORECASE)
            l1 = re.sub("\..*", "", l1, re.IGNORECASE)
            l2 = re.sub(".*is in ", "", line, re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, re.IGNORECASE)
            source[if_rename(l1)] = l2
        if re.search("^(a|the) (passroom|pushroom|room) called ", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", line, re.IGNORECASE)
            l1 = re.sub(" is .*", "", l1, re.IGNORECASE)
            l2 = re.sub("\".*", "", line, re.IGNORECASE)
            l2 = re.sub(".*is a room in ", "", l2, re.IGNORECASE)
            l2 = re.sub(".*is in ", "", l2, re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, re.IGNORECASE)
            source[if_rename(l1)] = l2
            print(ll, l2)
        if re.search("^[^\t].*is a (privately-named )?(passroom|pushroom|room) in ", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub(" is a (privately-named )?(passroom|pushroom|room) in .*", "", line, flags=re.IGNORECASE)
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", l1, flags=re.IGNORECASE)
            l2 = re.sub("\".*", "", line, flags=re.IGNORECASE)
            l2 = re.sub(".*is (a (privately-named )?(passroom|pushroom|room) )?in ", "", l2, flags=re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, flags=re.IGNORECASE)
            source[if_rename(l1)] = l2
        if re.search("^[^\t].*is (above|below|((north|south|east|west|up|down|inside|outside) of)).*it is in", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub(' is .*', '', line, flags=re.IGNORECASE)
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", l1, flags=re.IGNORECASE)
            l2 = re.sub(".*it is in ", "", line, flags=re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, flags=re.IGNORECASE)
            source[if_rename(l1)] = l2

missmap = 0

maperr = []
sourceerr = []

count = 0

for a in list(set(triz.keys()) | set(source.keys())):
    # if a in triz.keys():
        # print (a, "is in triz and source keys.")
    if a not in triz.keys() and a not in ignore.keys():
        count += 1
        print (count, a, "is in the source but not in the Trizbort map.")
        maperr.append(a)
        continue
    if a not in source.keys() and a not in ignore.keys():
        count += 1
        print(count, a, "is in the Trizbort map but not in the source.")
        sourceerr.append(a)
        continue
    if a in ignore.keys():
        continue
    if triz[a] != source[a]:
        print(a, "has different regions: source =", source[a], "and trizbort =", triz[a])
        # print(a, triz[a], source[a])

print ("TEST RESULTS:triz2source-" + project + ",0,0," + " / ".join(sourceerr))
print ("TEST RESULTS:triz2map-" + project + ",0,0," + "/ ".join(maperr))

if invisiclues_search:
    match_source_invisiclues()

# random note: use 2to3.py