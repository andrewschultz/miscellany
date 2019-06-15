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
warnings = 0
all_dupe = 0

from collections import defaultdict
ignore_rule = defaultdict(int)
ignored_yet = defaultdict(int)
all_check = defaultdict(int)

check_all_dupe_rules = False

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg == 'e': os.system("li.txt")
    elif arg == 'ac' or arg == 'ca': check_all_dupe_rules = True
    else: print("Unrecognized parameter", arg)
    cmd_count += 1

if os.path.exists("li.txt"):
    bail_after = False
    fix_line = 0
    with open("li.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            ll = line.strip().lower()
            if not ll: continue
            if ll in ignore_rule:
                bail_after = True
                print(ll, "listed twice, first at line", ignore_rule[ll], "then at line", line_count)
                fix_line = line_count
            ignore_rule[ll] = line_count
            ignored_yet[ll] = False
    if bail_after:
        print("Fix duplicates in li.txt before continuing.")
        i7.npo("li.txt", fix_line)

with open(f) as file:
    for (line_count, line) in enumerate(file, 1):
        ll = line.strip().lower()
        ll = re.sub("\[[^\]]*\]$", "", ll).strip()
        if not ll:
            if in_end_check:
                #if last_line.endswith("instead."):
                if last_line.endswith("instead.") or last_line.endswith("instead"):
                    print("WARNING instead; may be better than instead. Line", line_count - 1, last_line)
                    warnings += 1
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
                if check_all_dupe_rules:
                    all_dupe_found = False
                    for r in all_check:
                        if ll.startswith(r):
                            print("All-check duplicate rule", "<{:s}>".format(r), "original line", all_check[r], "duplicate", line_count)
                            all_dupe += 1
                            all_dupe_found = True
                    if not all_dupe_found:
                        x = re.sub(" *:.*", "", ll)
                        all_check[x] = line_count
        last_line = ll

print(line_count, "lines total,", total_rules, "check rules total")

if not oops: print("SUCCESS! No leaky rules detected.")
else: print("FAILURE! {:d} leaky rules detected.".format(oops))
if reignore: print(reignore, "rules reignored.")
if warnings: print(warnings, "dumb syntax warnings.")
if all_dupe: print(all_dupe, "duplicate check rules.")

if last_oops: i7.npo("story.ni", last_oops)