#
# ghd.py
# perl github daily checker
#
#

import sys
import os
import mytools as mt
from collections import defaultdict
import subprocess

this_header = "Daily Github commits"
total_count = 0

windows_popup_box = False
only_today = True

projects = defaultdict(list)
final_count = defaultdict(lambda: defaultdict(list))

ghd = "c:/writing/scripts/ghd.txt"
base_dir = mt.gitbase

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

def read_cmd_line():
    cmd_count = 1
    while cmd_count < len(sys.argv):
        arg = mt.nohy(sys.argv[cmd_count])
        if arg =='p':
            windows_popup_box = True
        elif arg == 'pn' or arg == 'np':
            windows_popup_box = False
        else:
            sys.exit("Bad parameter {}.".format(arg))
        cmd_count += 1

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

#################################################

os.chdir(base_dir)

read_cfg_file()
read_cmd_line()

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
            final_count[x][y] = output_array

if not len(final_count):
    mt.win_or_print("NO CHANGES TODAY (yet)", this_header, windows_popup_box, bail = True)

out_string = ""

for f in sorted(final_count):
    proj_ary = []
    local_count = 0
    for g in sorted(final_count[f]):
        my_len = len(final_count[f][g])
        proj_ary.append("{} ~ {}".format(g, my_len))
        total_count += my_len
        local_count += my_len
    out_string += "{}{}: {}\n".format(f.upper(), ' ({})'.format(local_count) if len(final_count) > 1 and len(final_count[f] > 1) else '', ', '.join(proj_ary))

out_string = "TOTALS: {}\n".format(total_count) + out_string
out_string = out_string.rstrip()
mt.win_or_print(out_string, this_header, windows_popup_box, bail = True)
