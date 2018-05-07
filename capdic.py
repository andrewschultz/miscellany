# capdic.py
#
# capitaliation dictionary
# checks the different ways words are capitalized within a source file

from collections import defaultdict
import re

# struct definitions
capfinds = defaultdict(int)
cap_sets = defaultdict(lambda: defaultdict(int))

# variables
print_singletons = False

def capsample():
    xxx = "ufo tofu or maybe UFO TOFU or UFO tofu could be right. UFO tofu is what I want, maybe UFO Tofu."
    m = re.findall("ufo tofu", xxx, re.IGNORECASE)
    for x in m:
        print(x)

line_count = 0

with open("zr.txt") as file:
    for line in file:
        line_count += 1
        if line.startswith('#'): continue
        if line.startswith(';'): break
        ll = line.strip().lower()
        if ll in capfinds.keys():
            print(ll, "is a duplicate key, line", line_count, "vs", capfinds[ll])
        capfinds[ll] = line_count

with open("story.ni") as file:
    for line in file:
        ll = line.strip().lower()
        for x in capfinds.keys():
            if x in ll:
                m = re.findall(x, line, re.IGNORECASE)
                for q in m:
                    cap_sets[x][q] += 1

for j in sorted(capfinds.keys()):
    if j not in cap_sets.keys():
        print("WARNING", j, "not in cap_sets")
        continue
    if len(cap_sets[j].keys()) == 1:
        if print_singletons: print("Only capitalization for", j, "is", ''.join(cap_sets[j].keys()))
    else:
        print('/'.join('{:s}={:d}'.format(y, cap_sets[j][y]) for y in cap_sets[j].keys()))