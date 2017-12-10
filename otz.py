# otz.py: old text zap
#
# reads otz.txt to work through sections where specific text needs to be deleted
# can also read in exceptions
#
# todo: read in difference between regex searches and text searches

from collections import defaultdict

import os
import sys
import re

errs_yet = defaultdict(str)

specifics = defaultdict(dict)

searches = defaultdict(int)

proj_read = ""
default_project = ""
otz = "c:/writing/scripts/otz.txt"

file_dic = {}
regex_dic = {}
incidents_dic = {}
incident_ig = {}
abbrevs = {}
ignore_dic = {}
match_dic = {}

ignore_dic["##regignore"] = True

current_section = ""

only_warnings_or_errors = False
only_errors = True

got_any_section = False

reading_project = False

read_random_tables = False

def show_projects():
    projs = []
    x = "=" * 10
    print(x + "ALL PROJECTS" + x)
    line_count = 0
    with open(otz) as source_file:
        for line in source_file:
            if line.lower().startswith("project="):
                temp = re.sub("project=", "", line.lower().strip(), re.IGNORECASE)
                if re.search(",", temp):
                    temp = max(temp.split(","), key=len) + " (" + temp + ")"
                projs.append(temp)
    print(", ".join(projs))
    exit()

def check_old_matches(x):
    line_count = 0
    with open(x) as source_file:
        for line in source_file:
            line_count = line_count + 1
            l2 = line.strip().lower()
            if not read_random_tables and l2.startswith("\"") and ("\t" not in l2 or l2.endswith("false") or l2.endswith("true")):
                continue # fix for roiling/shuffling where we want to read the table of megachatter
            if not l2:
                continue
            for m in match_dic.keys():
                if m in l2:
                    ignore = False
                    for id in ignore_dic.keys():
                        if re.search(id, line, re.IGNORECASE):
                            ignore = True
                    if specifics[m]:
                        for j in specifics[m].keys():
                            if re.search(j, line, re.IGNORECASE):
                                ignore = True
                    if ignore is False:
                        incidents_dic[m] = incidents_dic[m] + 1
                        if not errs_yet[x]:
                            print("======", x, "======")
                            errs_yet[x] = 1
                        print("-->", line_count, (abbrevs[m] if r in abbrevs.keys() else m) + ": " + line.strip())
                    else:
                        incident_ig[r] = incident_ig[r] + 1
            for r in regex_dic.keys():
                if re.search(r, line, re.IGNORECASE):
                    ignore = False
                    for id in ignore_dic.keys():
                        if re.search(id, line, re.IGNORECASE):
                            ignore = True
                    if specifics[r]:
                        for j in specifics[r].keys():
                            if re.search(j, line, re.IGNORECASE):
                                ignore = True
                    if ignore is False:
                        incidents_dic[r] = incidents_dic[r] + 1
                        if not errs_yet[x]:
                            print("======", x, "======")
                            errs_yet[x] = 1
                        print("-->", line_count, (abbrevs[r] if r in abbrevs.keys() else r) + ": " + line.strip())
                    else:
                        incident_ig[r] = incident_ig[r] + 1

def in_csv(a, b):
    my_csv = a.split(",")
    return b in my_csv

# main program

read_sections = False
print_sections = False

sections = [ ]

section_check = defaultdict(bool)
full_name = defaultdict(str)

if len(sys.argv) > 1:
    count = 1
    while count < len(sys.argv):
        arg = sys.argv[count]
        count = count + 1
        if arg == 'e' or arg == '-e':
            os.system(otz)
        if arg == '?' or arg == '-?':
            show_projects()
            exit()
        if arg.startswith("as"):
            sections = [ "" ]
            read_sections = True
            print_sections = True
            continue
        if arg.startswith("s=") or arg.startswith("sec="):
            sections = re.sub("^s(ec)?=", "", arg).split(',')
            read_sections = True
            for s in sections:
                section_check[sections[0]] = False
        else:
            proj_read = arg
            print("Going for project", proj_read)

ever_project = False

with open(otz) as file:
    for line in file:
        if line.startswith("#"):
            continue
        if line.startswith(";"):
            break
        l2 = line.lower().strip()
        if line.lower().startswith("default="):
            temp = re.sub("default=", "", line.lower().strip(), re.IGNORECASE)
            default_project = temp
            if proj_read == '':
                proj_read = default_project
                print("Using default project", proj_read)
            continue
        if line.lower().startswith("project="):
            reading_project = in_csv(re.sub("^project=", "", line.lower().strip(), re.IGNORECASE), proj_read)
            ever_project = ever_project or reading_project
            continue
        if line.startswith("sec:") or line.startswith("sec="):
            current_section = re.sub("^sec.", "", line.strip().lower())
            loc_section_names = current_section.split(",")
            any_section_this_line = ""
            for a in loc_section_names:
                if a in sections:
                    print("Found section", a)
                    if any_section_this_line:
                        print("WARNING accessed a section twice", any_section_this_line, "=", a)
                    section_check.pop(a)
                    got_any_section = True
                    any_section_this_line = a
            continue
        if re.search("PROJEND", line):
            reading_project = False
            continue
        if reading_project is False:
            continue
        if line.lower().startswith("f="):
            temp = re.sub("^f=", "", line.strip().lower(), re.IGNORECASE)
            check_old_matches(temp)
            continue
        if read_sections and current_section not in sections:
            if not line.startswith("--") and not line.startswith("i:"):
                searches[current_section] = searches[current_section] + 1
            continue
        if line.startswith("--"):
            file_dic.pop(re.sub("^--", "", line.strip()), None)
            continue
        if line.startswith("i:"): # in the ignore dictionary
            ignore_dic[re.sub("i:", "", line.strip())] = True
            continue
        if line.startswith("m:"): # in the match dictionary
            tr = re.sub("m:", "", line.strip())
            match_dic[tr] = True
            incidents_dic[tr] = 0
            incident_ig[tr] = 0
            continue
        if line.startswith("r:"): # in the regex dictionary
            regex_dic[re.sub("r:", "", line.strip())] = True
            continue
        if line.startswith("s:"): # specific to ignore/see with current regex
            specifics[this_regex][re.sub("s:", "", line.strip())] = True
            continue
        if line.startswith("i-:"): # remove from ignore dictionary
            file_dic.pop(re.sub("^i-:", "", line.strip()), None)
            continue
        line = line.strip()
        if re.search("\t", line):
            tabs = line.strip().split('\t')
            abbrevs[tabs[0]] = tabs[1]
            this_regex = tabs[0]
        else:
            this_regex = line
            regex_dic[line] = True
        # print("Added", line)
        regex_dic[this_regex] = True
        incidents_dic[this_regex] = 0
        incident_ig[this_regex] = 0

if print_sections:
    for x in sorted(searches.keys(), key=searches.get):
        print("Section", x, "has", searches[x], "keys.")

if proj_read == '' and default_project == '':
    print("Need to define DEFAULT= in otz.txt or write in your project on the command line.")

for x in file_dic.keys():
    check_old_matches(x)

my_list = []

if only_warnings_or_errors:
    my_list = [i for i in incidents_dic.keys() if incidents_dic[i] + incident_ig[i] > 0]
elif only_errors:
    my_list = [i for i in incidents_dic.keys() if incidents_dic[i]]
else:
    my_list = [i for i in incidents_dic.keys()]

if not ever_project:
    print("WARNING never found project", proj_read, "in", otz + "--for sections use s=" + proj_read)
    exit()

for s in section_check.keys():
    print ("WARNING Didn't find section", s)

if len(sections) > 0 and not got_any_section:
    print ('Warning: No text found for', 'section' + ['', 's'][len(sections)> 1], ', '.join(sections))

if len(my_list) == 0:
    if got_any_section == False and read_sections == True:
        print("No incidents, but I might not have read anything. Check what sections you wrote in.")
    else:
        print("NO INCIDENTS FOR", proj_read.upper(), "YAY")
else:
    print("INCIDENTS (from need most changing to need least):")
    for x in sorted(my_list, key=lambda x:(incidents_dic[x], incident_ig[x], x), reverse=True):
        print("{:<23}: {:<2d} need changing, {:<2d} ignored in otz.py".format(abbrevs[x] if x in abbrevs.keys() else x, incidents_dic[x], incident_ig[x]))
