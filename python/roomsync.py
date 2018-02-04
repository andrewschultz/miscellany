#############################
# roomsync.py
#
# compares map text from trizbort to source text from an Inform story.ni file
# also, if invisiclues file is there, compares source text from an Inform story.ni file to invisiclues file
#
# todo: rooms that get ignored in specific projects (conceptville/lalaland everywhere)
# also rooms that map *from* a map *to* a 

import i7
import sys
import re
import xml.etree.ElementTree as ET
source = {}
triz = {}

ignore = {}

ignore["conceptville"] = 1
ignore["lalaland"] = 1
ignore["tempmet"] = 1
ignore["zerorez"] = 1

project = "buck-the-past"

if len(sys.argv) > 1 and sys.argv[1]:
    project = sys.argv[1]
    if project in i7.i7x.keys(): project = i7.i7x[project]

trizfile = "c:\\games\\inform\\triz\\mine\\{:s}.trizbort".format(project)

try:
    e = ET.parse(trizfile)
except:
    print("Couldn't find", trizfile)
    exit()

root = e.getroot()

for elem in e.iter('room'):
    if elem.get('name'):
        x = str(elem.get('name')).lower()
        x = re.sub(" ?[\/\(].*", "", x, flags=re.IGNORECASE)
        triz[x] = str(elem.get('region')).lower()
    # print (x,triz[x])
    # triz[atype.get('name')] = 1;

with open("c:\\games\\inform\\" + project + ".inform\\source\\story.ni") as f:
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

full = {}

for a in source:
    full[a] = 1

for a in triz:
    full[a] = 1

for a in sorted(full):
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


# random note: use 2to3.py