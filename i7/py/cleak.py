#
# cleak.py:
#
# look for missing instead in check rules
#

import sys
import re
import i7
import os

rules = [ "check pushing", "check pulling" ]
rules = [ "check" ]

f = "story.ni"

in_end_check = False
start_line_num = 0
start_line_text = ""
oops = 0
reignore = 0
last_oops = 0
total_rules = 0

from collections import defaultdict
ignore_rule = defaultdict(bool)
ignored_yet = defaultdict(int)

if os.path.exists("li.txt"):
    with open("li.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            ll = line.strip().lower()
            ignore_rule[ll] = True
            ignored_yet[ll] = False

with open(f) as file:
    for (line_count, line) in enumerate(file, 1):
        ll = line.strip().lower()
        ll = re.sub("\[[^\]]*\]$", "", ll).strip()
        if not ll:
            if in_end_check:
                #if last_line.endswith("instead."):
                if last_line.endswith("instead.") or last_line.endswith("instead"): print("WARNING instead; may be better than instead. Line", line_count - 1, last_line)
                elif "instead;" not in last_line and "continue the action" not in last_line and "the rule succeeds" not in last_line and "the rule fails" not in last_line:
                    print(start_line_num, start_line_text, "may need INSTEAD, ending line", line_count - 1, "(some insteads present)" if any_instead else "")
                    oops += 1
                    last_oops = line_count - 1
            in_end_check = False
            continue
        if in_end_check and "instead" in ll: any_instead = True
        if ll.startswith("check "):
            total_rules += 1
            this_ignore = False
            for r in ignore_rule:
                if ll.startswith(r):
                    this_ignore = True
                    if ignored_yet[r]:
                        print("Line", line_count, "re-ignored rule", r, "originally at line", ignored_yet[r])
                        reignore += 1
                    else: ignored_yet[r] = line_count
            if not this_ignore:
                in_end_check = True
                any_instead = False
                start_line_num = line_count
                start_line_text = ll
        last_line = ll

print(line_count, "lines total,", total_rules, "check rules total")

if not oops: print("SUCCESS! No leaky rules detected.")
else: print("FAILURE! {:d} leaky rules detected.".format(oops))
if reignore: print(reignore, "rules reignored.")

if last_oops: i7.npo("story.ni", last_oops)