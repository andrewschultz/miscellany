import re
from collections import defaultdict

table_start = defaultdict(bool)
table_end = defaultdict(bool)
in_outline = defaultdict(bool)

now_xx = False
ever_xx = False
in_table = False

line_count = 0

with open("story.ni") as file:
    for line in file:
        line_count = line_count + 1
        ll1 = line.lower()
        if ll1.startswith("xx start") or ll1.startswith("start xx"):
            ever_xx = True
            now_xx = True
            continue
        if now_xx:
            if not line.strip():
                now_xx = False
                continue
            ll = re.sub(" .*", "", line.lower().strip())
            in_outline[ll] = line_count
        if '[xx' in line:
            ll = re.sub(".*\[xx", "", line.lower().strip())
            ll = re.sub("\].*", "", ll)
            table_start[ll] = True
            in_table = True
            continue
        if '[zz' in line:
            in_table = False
            ll = re.sub("\].*", "", line.strip()[3:])
            table_end[ll] = True

if not ever_xx:
    print("Never got a ToC of xx-text. Put XX START at the start of an early line.")

for x in sorted(list(set(table_start.keys()) | set(table_end.keys()) | set(in_outline.keys()))):
    if x not in table_start.keys():
        print("Need table start [xx for ", x)
    if x not in table_end.keys():
        print("Need table end [zz for ", x)
    if x not in in_outline.keys():
        print("Need outline mention at top for ", x.upper())
