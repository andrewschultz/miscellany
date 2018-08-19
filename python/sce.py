# sce.py
#
# detects scenery and backdrops to check
#
# cmd line args: any project
# also create/launch sce.txt file post processing
#

import i7
import re
import sys

count = 0

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if i7.proj_exp(arg): my_proj = i7.proj_exp(arg)
    count += 1

sce = {}
tot = {}
bak = []

nuthin = "zzzz scenery with no location"

with open("story.ni") as file:
    for line in file:
        if not re.search("^[a-z]", line, re.IGNORECASE): continue
        if re.search("is a ([ -a-z]*)?backdrop", line, re.IGNORECASE):
            line2 = re.sub(" is a .*backdrop.*", "", line, re.IGNORECASE)
            bak.append(line2.strip())
        if re.search("is scenery\.", line, re.IGNORECASE):
            line = re.sub(" is scenery.*", "", line.strip().lower(), re.IGNORECASE)
            line = i7.no_lead_art(line)
            if nuthin not in sce.keys():
                sce[nuthin] = []
                tot[nuthin] = 0
            sce[nuthin].append(line)
            tot[nuthin] += 1
            continue
        if not re.search("\.", line, re.IGNORECASE): continue
        line = re.sub("\..*", "", line.strip())
        if not re.search("scenery in ", line, re.IGNORECASE): continue
        line2 = line.strip().lower()
        line2 = re.sub(" (is|are) ([-a-z ]*)?scenery.*", "", line2, re.IGNORECASE)
        line2 = i7.no_lead_art(line2)
        line3 = line.strip().lower()
        line3 = re.sub(".*scenery in ", "", line3, re.IGNORECASE)
        if line3 not in sce.keys():
            tot[line3] = 0
            sce[line3] = []
        sce[line3].append(line2)
        tot[line3] += 1

for x in sorted(sce.keys()):
    print('{:s} ({:d}): {:s}'.format(re.sub("^Z+ ?", "", x.upper()), tot[x], ', '.join(sorted(sce[x]))))
    # print(x.upper() + ":",tot[x], sce[x])

if len(bak) > 0:
    print('=' * 40)
    print('BACKDROPS:', ', '.join(bak))
else:
    print("No backdrops.")