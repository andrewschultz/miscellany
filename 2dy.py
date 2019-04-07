#
# 2dy.py: replacement for perl script that went X daily files back.
#

import pendulum
import os
from collections import defaultdict

#init_sect = defaultdict(str)

#d = pendulum.now()
d = pendulum.today()

max_days_new = 7
max_days_back = 1000

os.chdir("c:/writing/daily")
create_or_open = True

daily = "c:/writing/daily/"
daily_done = "c:/writing/daily/done/"

sect_ary = []

files_back_wanted = 1
verbose = False

def get_init_sections():
    global sect_ary
    with open("2dy.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            ary = line.lower().strip().split(",")
            for q in ary:
                ary2 = q.split('=')
                sect_ary += ary2[0]
                # init_sect[ary2[0]] = ary2[1]

def see_back(d, my_dir, days_back):
    my_file = d.subtract(days=days_back).format('YYYYMMDD') + ".txt"
    return os.path.join(my_dir, my_file)

def create_new_file(my_file):
    f = open(my_file)
    f.write("\n")
    f.write("\n\n".join(sect_ary))
    f.close()

#
# main coding block
#
# todo: look on command line

os.chdir("c:/writing/scripts")

get_init_sections()

if create_or_open:
    for x in range(0, max_days_new):
        day_file = see_back(d, daily, x)
        day_done_file = see_back(d, daily_done, x)
        if os.path.exists(day_file):
            print("Found recent daily file {:s}, opening.".format(day_file))
            os.system(day_file)
            exit()
        if os.path.exists(day_done_file): found_done_file = day_done_file
    if found_done_file: sys.exit("Found {:s} in done folder. Not opening new one.")
    print("Looking back", max_days_new, "days, daily file not found. Creating new one.")
    create_new_file(see_back(d, daily, 0))

files_back_in_dir = 0
for x in range(0, max_days_back):
    day_file = see_back(d, daily, x)
    if os.path.exists(day_file):
        files_back_in_dir += 1
        if verbose and files_back_in_dir < files_back_wanted: print("Skipping", day_file)
    if files_back_in_dir == files_back_wanted:
        print("Got daily file", day_file, files_back_wanted, "files back.")
        os.system(day_file)

