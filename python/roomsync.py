#############################
# roomsync.py
#
# compares map text from trizbort to source text from an Inform story.ni file
# also, if invisiclues file is there, compares source text from an Inform story.ni file to invisiclues file
#
# verified so far on Ailiphilia, Buck the Past and Tragic Mix. Roiling still has minor bugs.
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
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if line.startswith('project:'):
                ll = re.sub("^project:", "", line.strip().lower())
                if not ll or i7.proj_exp(ll) == project: read_this = True
                else: read_this = False
            if not read_this: continue
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
            elif line.startswith("invis-region-rename"):
                ll = re.sub("^invis-region-rename:", "", line.strip().lower())
                ary = ll.split("~")
                if len(ary) != 2:
                    print("Misformed RENAME (needs before/after) at line", line_count, ":", ll)
                if verbose: print("INVIS Renaming", ary[0], "to", ary[1])
                invis_region_rename[ary[0]] = ary[1]
            elif line.startswith("triz-rename:"):
                ll = re.sub("^triz-rename:", "", line.strip().lower())
                ary = ll.split("~")
                if len(ary) != 2:
                    print("Misformed RENAME (needs before/after) at line", line_count, ":", ll)
                triz_renamer[ary[0]] = ary[1]

def region_mismatch(a):
    ir = invis_region[a]
    s = source[a]
    if ir in invis_region_rename: ir = invis_region_rename[ir]
    if s in invis_region_rename: s = invis_region_rename[s]
    return ir != s

def match_source_invisiclues():
    invis_region.clear()
    line_dict = defaultdict(int)
    region_level = 1
    room_level = 2
    cur_region = ""
    room_force = ""
    if not i7.revproj(project): sys.exit("Can't figure out a project for {:s}.".format(project))
    invisfile = "c:/writing/scripts/invis/{:s}.txt".format(i7.revproj(project))
    if not os.path.exists(invisfile):
        print("No file {:s}. Ignoring invisiclues testing.".format(invisfile))
        return
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
    warnings_source = warnings_invis = warnings_clash = 0
    for a in b:
        if a in source.keys() and source[a] in region_ignore.keys(): continue
        if a not in source.keys():
            warnings_source += 1
            print("WARNING: source({:d}) {:s} (invis={:s}) does not have a region in the source.".format(warnings_source, a, invis_region[a]))
        elif a not in invis_region.keys():
            warnings_invis += 1
            print("WARNING: invis({:d}) {:s} (source={:s}) does not have a region in the invisiclues.".format(warnings_invis, a, source[a]))
        elif region_mismatch(a):
            warnings_clash += 1
            print("WARNING {}: region clash for {:s} (line {:d}): {:s} in source but {:s} in invisiclues.".format(warnings_clash, a, line_dict[a], source[a], invis_region[a]))
    print ("TEST RESULTS:triz2invis-" + project + ",0,0, " + ", ".join(sorted(inviserr.keys())))

def match_source_triz():
    source_mod = defaultdict(bool)
    count = 0
    this_count = 0
    for x in source.keys():
        if x in triz_renamer.keys():
            source_mod[triz_renamer[x]] = source[x]
            triz[triz_renamer[x]] = triz[x]
            triz.pop(x)
        else: source_mod[x] = source[x]
    source_and_triz = sorted(list(set(triz.keys()) | set(source_mod.keys())))
    for a in source_and_triz:
        # if a in triz.keys():
            # print (a, "is in triz and source keys.")
        if a not in triz.keys() and a not in ignore.keys():
            if a in source and source[a] in region_ignore: continue
            if not this_count:
                print("IN SOURCE BUT NOT TRIZBORT")
            count += 1
            this_count += 1
            print (count, this_count, a, "/", source[a])
            maperr.append(a)
            continue
    this_count = 0
    for a in source_and_triz:
        if a not in source_mod.keys() and a not in ignore.keys():
            if not this_count:
                print("IN TRIZBORT BUT NOT SOURCE")
            count += 1
            this_count += 1
            print(count, this_count, a)
            sourceerr.append(a)
            continue
    this_count = 0
    for a in source_and_triz:
        if a in ignore.keys() or a not in triz.keys() or a not in ignore.keys():
            continue
        if triz[a] != source[a]:
            if not this_count:
                print("IN DIFFERENT REGIONS")
            count += 1
            this_count += 1
            print(count, this_count, a, "source =", source[a], "and trizbort =", triz[a])
            # print(a, triz[a], source[a])

# default dictionaries and such
source = defaultdict(bool)
triz = defaultdict(bool)
invis_rooms = defaultdict(bool)
ignore = defaultdict(bool) # specific rooms to ignore
region_ignore = defaultdict(bool) # specific regions to ignore
room_renamer = defaultdict(str)
invis_renamer = defaultdict(str)
triz_renamer = defaultdict(str)
invis_region = defaultdict(str)
invis_region_rename = defaultdict(str)

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
    arg = re.sub("^-", "", sys.argv[cmd_count].lower())
    if arg in i7.i7x.keys():
        project = i7.i7x[arg]
        current_as_default = False
    elif os.path.isdir("c:/games/inform/" + arg + ".inform"):
        project = arg
        current_as_default = False
    elif arg == 'v':
        verbose = True
    elif arg == 'f':
        format_help()
    else:
        usage()
    cmd_count += 1

my_proj_dir = i7.dir2proj(os.getcwd())
read_this = True
if not my_proj_dir and not project: sys.exit("Need to be in a valid project directory or define a project on the command line.")
if not project: project = my_proj_dir

trizfile = i7.triz(project)
source_file = i7.src(project)

if not os.path.exists(source_file):
    print(source_file, "does not exist, and there is no expansion for it. Bailing.")
    exit()

read_ignore_file()

triz = i7.get_trizbort_rooms(trizfile, keep_punctuation = False, ignore_regions = list(region_ignore))

def region_name(li):
    li2 = re.sub("\".*?\"", "", li)
    if 'scenery in' in li: sys.exit("Warning not to put scenery in room-defining line: " + li)
    if not re.search("(is|room) +in ", li2): return ""
    li2 = re.sub(".*?(is|room) +in +", "", li2)
    li2 = re.sub("\..*", "", li2)
    return li2

###### below this needs fixing. It is a hack for IFComp 2019

def rooms_from_table(x):
    if x == 'table of bad locs': return "Poorly Penned"
    return ""

def forced_region(tn, pro):
    return "poorly penned" # obviously to be fixed later

def from_table(my_line, my_proj):
    q = my_line.lower().split("\t")
    if len(q) < 2: return ""
    retval = re.sub("^\"", "", q[3])
    return re.sub("\".*", "", retval)

###### above this needs fixing. It is a hack for IFComp 2019

current_table = ""
last_table_line = 0

with open(source_file) as f:
    for (line_count, line) in enumerate(f, 1):
        if line.startswith("table of") and not current_table:
            current_table = re.sub(" *[\(\[].*", "", line.lower().strip())
            last_table_line = line_count
            continue
        if current_table:
            l2 = re.sub(".*[\[\]]", "", line.strip())
            if not l2:
                current_table = ""
                continue
        if current_table and rooms_from_table(current_table):
            if line_count - last_table_line == 1: continue
            source[from_table(line, project)] = forced_region(current_table, project)
            print(line_count, from_table(line, project), forced_region(current_table, project))
            continue
        if "\t" in line or line.startswith("["): continue
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