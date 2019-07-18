import re
import i7
from collections import defaultdict

boundings = defaultdict(list)
bound_lines = defaultdict(int)

triz_rms = i7.triz_rooms("c:/games/inform/triz/mine/roiling.trizbort")

my_project = "roi"

crit_word = "boring"

my_file = i7.main_src(my_project)

with open(my_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if "\t" in line: continue
        if "scenery" not in line: continue
        if crit_word not in line: continue
        if line.startswith("["): continue
        l = re.sub("\..*", "", line.strip().lower())
        right_part = re.sub(".*scenery in ", "", l)
        left_part = re.sub(" (are|is) .*", "", l)
        left_part = re.sub("^(a|some|the) +", "", left_part)
        #print(right_part, "/", left_part, "/", line_count)
        boundings[right_part].append(left_part)
        if right_part not in bound_lines: bound_lines[right_part] = line_count

total_rooms = 0
total_bounds = 0
for x in sorted(triz_rms, key=lambda z:bound_lines[z] if z in bound_lines else -1):
    if x not in bound_lines:
        continue
        print("Nothing in", x)
    else:
        total_rooms += 1
        total_bounds += len(boundings[x])
        print("{0}/{1} {2} ({3})".format(total_rooms, total_bounds, x, triz_rms[x]), '=', ', '.join(boundings[x]))