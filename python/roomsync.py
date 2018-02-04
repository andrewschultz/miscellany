#############################
# roomsync.py
#
# compares map text from trizbort to source text from an Inform story.ni file
# also, if invisiclues file is there, compares source text from an Inform story.ni file to invisiclues file
#
# todo: rooms that get ignored in specific projects (conceptville/lalaland everywhere)
# also rooms that map *from* a map *to* a

import os
import i7
import sys
import re
import __main__ as main
import xml.etree.ElementTree as ET

def read_ignore_file():
    with open(ignore_file) as file:
        for line in file:
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if line.startswith('ignore:'):
                ll = re.sub("^ignore:", "", line.strip().lower())
                ignore[ll] = 1

def match_source_invisiclues():
    invisfile = "c:/writing/scripts/invis/{:s}.txt".format(i7.revproj(project))
    print("Checking invisiclues file", invisfile, "...")
    with open(invisfile) as file:
        for line in file:
            if line.startswith(">>"):
                ll = re.sub(">>", "", line.strip().lower())
                invis_rooms[ll] = 1
    b = [x for x in list(set(source.keys()) | set(invis_rooms.keys())) if x not in ignore.keys()]
    count = 0
    print_barrier = True
    for a in b:
        if a not in source.keys():
            if print_barrier:
                print("=" * 40)
                print_barrier = False
            count = count + 1
            print(count, a, "in invisiclues but not source.")
    print_barrier = (count > 0)
    for a in b:
        if a not in invis_rooms.keys():
            if print_barrier:
                print("=" * 40)
                print_barrier = False
            count = count + 1
            print(count, a, "in source but not invisiclues.")

# default dictionaries and such
source = {}
triz = {}
invis_rooms = {}
ignore = {}
project = "buck-the-past"

invisiclues_search = True

ignore_file = re.sub("py$", "txt", main.__file__)

# cmd line looks for project name
if len(sys.argv) > 1 and sys.argv[1]:
    project = sys.argv[1]
    if project in i7.i7x.keys(): project = i7.i7x[project]

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
            source[l1] = l2
        if re.search("^(a|the) (passroom|pushroom|room) called ", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", line, re.IGNORECASE)
            l1 = re.sub(" is .*", "", l1, re.IGNORECASE)
            l2 = re.sub("\".*", "", line, re.IGNORECASE)
            l2 = re.sub(".*is a room in ", "", l2, re.IGNORECASE)
            l2 = re.sub(".*is in ", "", l2, re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, re.IGNORECASE)
            source[l1] = l2
        if re.search("^[^\t].*is a (privately-named )?(passroom|pushroom|room) in ", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub(" is a (privately-named )?(passroom|pushroom|room) in .*", "", line, flags=re.IGNORECASE)
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", l1, flags=re.IGNORECASE)
            l2 = re.sub("\".*", "", line, flags=re.IGNORECASE)
            l2 = re.sub(".*is (a (privately-named )?(passroom|pushroom|room) )?in ", "", l2, flags=re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, flags=re.IGNORECASE)
            source[l1] = l2
        if re.search("^[^\t].*is (above|below|((north|south|east|west|up|down|inside|outside) of)).*it is in", line, re.IGNORECASE):
            line = line.rstrip().lower()
            l1 = re.sub(' is .*', '', line, flags=re.IGNORECASE)
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", l1, flags=re.IGNORECASE)
            l2 = re.sub(".*it is in ", "", line, flags=re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, flags=re.IGNORECASE)
            source[l1] = l2

missmap = 0

maperr = []
sourceerr = []

count = 0

for a in list(set(triz.keys()) | set(source.keys())):
    # if a in triz.keys():
        # print (a,"is in triz and source keys.")
    if a not in triz.keys() and a not in ignore.keys():
        count = count + 1
        print (count, a,"is not in the Trizbort map.")
        maperr.append(a)
        continue
    if a not in source.keys() and a not in ignore.keys():
        count = count + 1
        print(count, a,"is not in the Story.ni source.")
        sourceerr.append(a)
        continue
    if a in ignore.keys():
        continue
    if triz[a] != source[a]:
        print(a, "has different regions for trizbort:", triz[a], " and ", source[a])
        print(a, triz[a], source[a])

print ("TEST RESULTS:triz2source-" + project + ",0,0," + " / ".join(sourceerr))
print ("TEST RESULTS:triz2map-" + project + ",0,0," + "/ ".join(maperr))

if invisiclues_search:
    match_source_invisiclues()

# random note: use 2to3.py