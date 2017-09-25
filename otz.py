# old title zap

from collections import defaultdict

import sys
import re

errs_yet = defaultdict(str)

def check_old_matches(x):
    with open(x) as source_file:
        for line in source_file:
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
                        print("-->" + r + ": " + line.strip())
                    else:
                        incident_ig[r] = incident_ig[r] + 1


file_dic = {}
regex_dic = {}
incidents_dic = {}
incident_ig = {}
ignore_dic = {}

ignore_dic["##regignore"] = True

proj_read = "roiling"
otz = "c:/writing/scripts/otz.txt"

if len(sys.argv) > 1:
    proj_read = sys.argv[1]

reading_project = False

proj_read = "PROJECT=" + proj_read

with open(otz) as file:
    for line in file:
        if line.startswith("#"):
            continue
        if line.startswith(";"):
            break
        if re.search(proj_read, line):
            reading_project = True
            continue
        if re.search("PROJEND", line):
            reading_project = False
            continue
        if reading_project is False:
            continue
        if line.startswith("+"):
            file_dic[re.sub("^.", "", line.strip())] = True
            continue
        if line.startswith("-"):
            file_dic.pop(re.sub("^.", "", line.strip()), None)
            continue
        if line.startswith("i:"):
            ignore_dic[re.sub("i:", "", line.strip())] = True
            continue
        regex_dic[line.strip()] = True
        incidents_dic[line.strip()] = 0
        incident_ig[line.strip()] = 0

for x in file_dic.keys():
    check_old_matches(x)

print("INCIDENTS (from need most changing to need least):")
for x in sorted(incidents_dic.keys(), key=lambda x:(incidents_dic[x], incident_ig[x], x), reverse=True):
    print("{:<23}: {:<2d} need changing, {:<2d} ignored in otz.py".format(x, incidents_dic[x], incident_ig[x]))