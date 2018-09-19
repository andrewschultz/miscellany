# tent.py
#
# brute force searching for potential "if x entry" without checking if there is an x entry
#

import sys
import re
from collections import defaultdict
import os

cc = 0

globals = defaultdict(bool)
ignores = defaultdict(bool)
entry_checks = defaultdict(int)

if os.path.exists("tent-ignore.txt"):
    with open("tent-ignore.txt") as file:
        for line in file:
            ll = line.lower().strip()
            if ll.startswith("#"): continue
            if ll.startswith(";"): break
            l0 = ll.split(",")
            for l1 in l0: ignores[l1] = True
else:
    print("No tent-ignore.txt file. Reading all entry names.")

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        if not line.strip(): entry_checks.clear()
        ll = line.lower().rstrip()
        if "\t" not in ll: continue
        if 'if there is' in line:
            fa = re.findall(r'if there is (a |an |)([a-z0-9-]+)? entry', ll)
            if len(fa):
                # print(line_count, fa)
                for f in fa: entry_checks[f[1]] = line_count
        if ' entry' in line and 'there is no' not in line:
            fa = re.findall(r'([a-z0-9-]+)? entry', ll)
            if len(fa):
                for f in fa:
                    if f not in entry_checks.keys() and f not in ignores.keys():
                        globals[f] = True
                        cc += 1
                        print(cc, f, "at line", line_count, "may need 'if there is'")

outwrite = "{:d}/{:d}: {:s}".format(cc, len(globals.keys()), ', '.join(sorted(globals.keys())))
sys.stderr.write(outwrite + "\n")
print(outwrite)
