#
# ghd.py
# perl github daily checker
#
#

import os
import mytools as mt
from collections import defaultdict
import subprocess

totals = 0

only_today = True

projects = defaultdict(list)
final_count = defaultdict(lambda: defaultdict(list))

ghd = "c:/writing/scripts/ghd.txt"

def read_cfg_file():
    with open(ghd) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix == 'base':
                global base_dir
                base_dir = data
                continue
            projects[prefix] = data.split(",")

def process_result(output_text):
    lines = output_text.splitlines()
    output_array = []
    read_next_line = False
    for x in lines:
        if x.startswith("Date"):
            read_next_line = True
            continue
        if read_next_line and x.strip():
            read_next_line = False
            output_array.append(x.strip())
    return output_array
    
read_cfg_file()

os.chdir(mt.gitbase)

for x in projects:
    for y in projects[x]:
        try:
            os.chdir(os.path.join(mt.gitbase, y))
        except:
            print("Bad github subdir", y, "in", x)
            continue
        proc_array = [ 'git', 'log' ]
        if only_today:
            proc_array.append('--since="00:00:00"')
        else:
            proc_array.append('--since="23 days ago"')
        result = subprocess.check_output(proc_array)
        if not result:
            continue
        output_array = process_result(result.decode())
        if output_array:
            print("!", x, y, output_array)
            final_count[x][y] = output_array

if not len(final_count):
    print("No changes today")
    sys.exit()

for f in final_count:
    proj_ary = []
    for g in final_count[f]:
        proj_ary.append("{} {}".format(g, len(final_count[f][g])))
        totals += len(final_count[f][g])
    print(f.upper(), ', '.join(proj_ary))

print("TOTALS:", totals)