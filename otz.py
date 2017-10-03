# old title zap

from collections import defaultdict

import sys
import re

errs_yet = defaultdict(str)

proj_read = "roiling"
otz = "c:/writing/scripts/otz.txt"

file_dic = {}
regex_dic = {}
incidents_dic = {}
incident_ig = {}
ignore_dic = {}

ignore_dic["##regignore"] = True

only_warnings_or_errors = False
only_errors = False

reading_project = False

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
            for r in regex_dic.keys():
                if re.search(r, line, re.IGNORECASE):
                    ignore = False
                    for id in ignore_dic.keys():
                        if re.search(id, line, re.IGNORECASE):
                            ignore = True
                    if ignore is False:
                        incidents_dic[r] = incidents_dic[r] + 1
                        if not errs_yet[x]:
                            print("======", x, "======")
                            errs_yet[x] = 1
                        print("-->", line_count, r + ": " + line.strip())
                    else:
                        incident_ig[r] = incident_ig[r] + 1

def in_csv(a, b):
    my_csv = a.split(",")
    return b in my_csv

# main program

if len(sys.argv) > 1:
    proj_read = sys.argv[1]
    if proj_read == '?' or proj_read == '-?':
        show_projects()
        exit()
else:
    print("Using default", proj_read)

with open(otz) as file:
    for line in file:
        if line.startswith("#"):
            continue
        if line.startswith(";"):
            break
        if line.lower().startswith("project="):
            reading_project = in_csv(re.sub("^project=", "", line.lower().strip(), re.IGNORECASE), proj_read)
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
        if line.startswith("--"):
            file_dic.pop(re.sub("^--", "", line.strip()), None)
            continue
        if line.startswith("i:"):
            ignore_dic[re.sub("i:", "", line.strip())] = True
            continue
        if line.startswith("i-:"):
            file_dic.pop(re.sub("^i-:", "", line.strip()), None)
            continue
        line = line.strip()
        regex_dic[line] = True
        print("Added",line)
        incidents_dic[line] = 0
        incident_ig[line] = 0

for x in file_dic.keys():
    check_old_matches(x)

my_list = []

if only_warnings_or_errors:
    my_list = [i for i in incidents_dic.keys() if incidents_dic[i] + incident_ig[i] > 0]
elif only_errors:
    my_list = [i for i in incidents_dic.keys() if incidents_dic[i]]

if len(my_list) == 0:
    print("NO INCIDENTS FOR", proj_read.upper(), "YAY")
else:
    print("INCIDENTS (from need most changing to need least):")
    for x in sorted(my_list, key=lambda x:(incidents_dic[x], incident_ig[x], x), reverse=True):
        print("{:<23}: {:<2d} need changing, {:<2d} ignored in otz.py".format(x, incidents_dic[x], incident_ig[x]))
