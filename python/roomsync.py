#############################
# roomsync.py
#
# compares map text from trizbort to source text from an Inform story.ni file
# also, if invisiclues file is there, compares source text from an Inform story.ni file to invisiclues file
#
# verified so far on Ailiphilia, Buck the Past and Tragic Mix
#
# also rooms that map *from* a map *to* a
#
# this is not perfect. In the future we will want to divide roomsync by projects
#

#import traceback
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
    if x in room_renamer.keys():
        return room_renamer[x]
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
            elif line.startswith("regignore:"):
                ll = re.sub("^regignore:", "", line.strip().lower())
                region_ignore[ll] = True
            elif line.startswith("room-rename:"):
                ll = re.sub("^room-rename:", "", line.strip().lower())
                ary = ll.split("~")
                if len(ary) != 2:
                    print("Misformed RENAME (needs before/after) at line", line_count, ":", ll)
                if verbose: print("Renaming", ary[0], "to", ary[1])
                room_renamer[ary[0]] = ary[1]
            elif line.startswith("invis-rename:"):
                ll = re.sub("^invis-rename:", "", line.strip().lower())
                ary = ll.split("~")
                if len(ary) != 2:
                    print("Misformed RENAME (needs before/after) at line", line_count, ":", ll)
                if verbose: print("INVIS Renaming", ary[0], "to", ary[1])
                invis_renamer[ary[0]] = ary[1]
            elif line.startswith("triz-rename:"):
                ll = re.sub("^triz-rename:", "", line.strip().lower())
                ary = ll.split("~")
                if len(ary) != 2:
                    print("Misformed RENAME (needs before/after) at line", line_count, ":", ll)
                triz_renamer[ary[0]] = ary[1]

def match_source_invisiclues():
    invis_region = defaultdict(str)
    line_dict = defaultdict(int)
    region_level = 1
    room_level = 2
    cur_region = ""
    room_force = ""
    if not i7.revproj(project): sys.exit("Can't figure out a project for {:s}.".format(project))
    invisfile = "c:/writing/scripts/invis/{:s}.txt".format(i7.revproj(project))
    if not os.path.exists(invisfile): sys.exit("No file {:s}. Bailing.".format(invisfile))
    print("Checking invisiclues file", invisfile, "...")
    with open(invisfile) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("##roomlevel="):
                room_level = int(re.sub("^##roomlevel=", "", line.strip().lower()))
                continue
            if line.startswith("##reglevel="):
                region_level = int(re.sub("^##reglevel=", "", line.strip().lower()))
                continue
            if line.startswith("##roomforce="):
                room_force = int(re.sub("^##roomforce=", "", line.strip().lower()))
                continue
            if line.startswith("##region="):
                cur_region = re.sub("^##region=", "", line.strip().lower())
                continue
            if region_level and line.startswith(">" * region_level) and not line.startswith(">" * (region_level + 1)):
                ll = re.sub(">>", "", line.strip().lower())
                ll = re.sub(", ?", " ", ll)
                cur_region = re.sub("^>*", "", ll)
            if room_level and line.startswith(">" * room_level) and not line.startswith(">" * (room_level + 1)):
                if room_force:
                    this_room = room_force
                    room_force = ""
                else:
                    this_room = re.sub(">>", "", line.strip().lower())
                    this_room = re.sub(", ?", " ", this_room)
                invis_rooms[this_room] = 1
                if not cur_region: sys.exit("Need region for room " + this_room)
                line_dict[this_room] = line_count
                invis_region[this_room] = cur_region
    modsource = defaultdict(bool)
    for q in source.keys(): modsource[invis_renamer[q] if q in invis_renamer.keys() else q] = True # this is if we don't want to spoil room names
    b = [x for x in list(set(modsource.keys()) | set(invis_rooms.keys())) if x not in ignore.keys()]
    count = 0
    print_barrier = True
    inviserr = defaultdict(bool)
    for a in b:
        if a not in invis_rooms.keys() and a not in region_ignore.keys():
            if print_barrier:
                print("=" * 40)
                print_barrier = False
            count += 1
            print(count, a, "in source but not invisiclues.")
            inviserr['>' + a] = True
    print_barrier = (count > 0)
    for a in b:
        if a not in modsource.keys():
            if print_barrier:
                print("=" * 40)
                print_barrier = False
            count += 1
            print(count, a, "in invisiclues but not source.")
            inviserr['<' + a] = True
    warnings_source = warnings_invis = 0
    for a in b:
        if a in source.keys() and source[a] in region_ignore.keys(): continue
        if a not in source.keys():
            warnings_source += 1
            print("WARNING: source({:d}) {:s} (invis={:s}) does not have a region in the source.".format(warnings_source, a, invis_region[a]))
        elif a not in invis_region.keys():
            warnings_invis += 1
            print("WARNING: invis({:d}) {:s} (source={:s}) does not have a region in the invisiclues.".format(warnings_invis, a, source[a]))
        elif invis_region[a] != source[a]:
            print("WARNING: region clash for {:s} (line {:d}): {:s} in source but {:s} in invisiclues.".format(a, line_dict[a], source[a], invis_region[a]))
    print ("TEST RESULTS:triz2invis-" + project + ",0,0, " + ", ".join(sorted(inviserr.keys())))

def match_source_triz():
    source_mod = defaultdict(bool)
    count = 0
    for x in source.keys():
        if x in triz_renamer.keys():
            source_mod[triz_renamer[x]] = source[x]
            triz[triz_renamer[x]] = triz[x]
            triz.pop(x)
        else: source_mod[x] = source[x]

    for a in list(set(triz.keys()) | set(source_mod.keys())):
        # if a in triz.keys():
            # print (a, "is in triz and source keys.")
        if a not in triz.keys() and a not in ignore.keys():
            count += 1
            print (count, a, "is in the source but not in the Trizbort map.")
            maperr.append(a)
            continue
        if a not in source_mod.keys() and a not in ignore.keys():
            count += 1
            print(count, a, "is in the Trizbort map but not in the source.")
            sourceerr.append(a)
            continue
        if a in ignore.keys():
            continue
        if triz[a] != source[a]:
            print(a, "has different regions: source =", source[a], "and trizbort =", triz[a])
            # print(a, triz[a], source[a])

# default dictionaries and such
source = defaultdict(bool)
triz = defaultdict(bool)
invis_rooms = defaultdict(bool)
ignore = defaultdict(bool) # specific rooms to ignore
room_renamer = defaultdict(str)
invis_renamer = defaultdict(str)
triz_renamer = defaultdict(str)

region_ignore = defaultdict(bool)

default_project = "buck-the-past"
project = ""

invisiclues_search = True
triz_search = True
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
        x = re.sub(" *\(.*\)", "", x) # get rid of parenthetical/alternate name
        x = re.sub(",", "", x) # get rid of commas Inform source doesn't like
        stuf_ary = re.split(" */ *", x) # optional for if a room name changes
        for q in stuf_ary:
            triz[q] = str(elem.get('region')).lower()
    # print (x,triz[x])
    # triz[atype.get('name')] = 1;

def region_name(li):
    li2 = re.sub("\".*?\"", "", li)
    if not re.search("(is|room) +in ", li2): return ""
    li2 = re.sub(".*?(is|room) +in +", "", li2)
    li2 = re.sub("\..*", "", li2)
    return li2

with open(source_file) as f:
    for (line_count, line) in enumerate(f, 1):
        if "\t" in line: continue
        if line.lower().startswith("index map with"): continue
        line = line.rstrip().lower()
        if re.search("^there is a (passroom|pushroom|room) called ", line, flags=re.IGNORECASE):
            l1 = re.sub("^there is a (passroom|pushroom|room) called ", "", line, flags=re.IGNORECASE)
            l1 = re.sub("\..*", "", l1, re.IGNORECASE)
            l2 = re.sub(".*is in ", "", line, re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, re.IGNORECASE)
            source[if_rename(l1)] = l2
        elif re.search("^(a|the) (passroom|pushroom|room) called ", line, flags=re.IGNORECASE):
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", line, flags=re.IGNORECASE)
            l1 = re.sub(" is .*", "", l1, re.IGNORECASE)
            l2 = re.sub("\".*", "", line, re.IGNORECASE)
            l2 = re.sub(".*is a room in ", "", l2, re.IGNORECASE)
            l2 = re.sub(".*is in ", "", l2, re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, re.IGNORECASE)
            source[if_rename(l1)] = l2
        elif re.search(" is a room\.", line, flags=re.IGNORECASE):
            l1 = re.sub(" is a room.*", "", line)
            source[l1] = "NONE"
        elif re.search("^[^\t\"\[\.]*is (above|below|((north|south|east|west|up|down|inside|outside) of))", line, flags=re.IGNORECASE):
            l1 = re.sub(' is .*', '', line, flags=re.IGNORECASE)
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", l1, flags=re.IGNORECASE)
            l2 = region_name(line)
            if l2:
                source[if_rename(l1)] = l2
            elif if_rename(l1) not in source.keys():
                print("WARNING no region name for", l1, line_count)
        elif re.search("^[^\t\"\[]* is (an innie|an outie|a|a privately-named) (passroom|pushroom|room) in ", line, flags=re.IGNORECASE):
            l1 = re.sub(" is (an innie|an outie|a|a privately-named) (passroom|pushroom|room) in .*", "", line, flags=re.IGNORECASE)
            l1 = re.sub("^(a|the) (passroom|pushroom|room) called ", "", l1, flags=re.IGNORECASE)
            l2 = re.sub("\".*", "", line, flags=re.IGNORECASE)
            l2 = re.sub(".*is (a|a privately-named|an innie) (passroom|pushroom|room) in ", "", l2, flags=re.IGNORECASE)
            l2 = re.sub("\..*", "", l2, flags=re.IGNORECASE)
            if 'idle deli' in l2: print("!!", l1, "/", l2)
            source[if_rename(l1)] = l2

missmap = 0

maperr = []
sourceerr = []

count = 0

if not project:
    print ("No project. Defining default project", default_project)
    project = default_project

if invisiclues_search: match_source_invisiclues()

if triz_search: match_source_triz()

print ("TEST RESULTS:triz2source-" + project + ",0,0," + " / ".join(sourceerr))
print ("TEST RESULTS:triz2map-" + project + ",0,0," + "/ ".join(maperr))

# random note: use 2to3.py