#
# 2dy.py: replacement for perl script that went X daily files back.
#

import sys
import pendulum
import os
from collections import defaultdict
import mytools as mt

#init_sect = defaultdict(str)

#d = pendulum.now()
d = pendulum.today()

#these are covered in the config file, but keep them here to make sure
max_days_new = 7
max_days_back = 1000

os.chdir("c:/writing/daily")
latest_daily = True

daily = "c:/writing/daily/"
daily_done = "c:/writing/daily/done/"

file_header = ""

sect_ary = []

files_back_wanted = 1
verbose = False

my_sections_file = "c:/writing/scripts/2dy.txt"

def usage(param = 'Cmd line usage'):
    print(param)
    print('=' * 50)
    print("(-?)f (#) = # files back")
    print("(-?)m (#) = # max days back")
    print("(-?)mn/n/nm (#) = # max new days back")
    print("(-?)l or ln/nl = latest-daily (or not)")
    print("(-?)v or vn/nv = toggle verbosity")
    print("(-)e = edit 2dy.txt to add sections or usage or adjust days_new")
    exit()

def get_init_sections():
    global sect_ary
    global file_header
    with open(my_sections_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            if line.startswith("maxnew="):
                max_days_new = int(line[7:])
                continue
            if line.startswith("maxback="):
                min_days_new = int(line[8:])
                continue
            if line.startswith("file_header="):
                file_header = line[12:].replace("\\", "\n")
                continue
            ary = line.lower().strip().split(",")
            for q in ary:
                ary2 = q.split('=')
                sect_ary.append(ary2[0])
                # init_sect[ary2[0]] = ary2[1]

def see_back(d, my_dir, days_back):
    my_file = d.subtract(days=days_back).format('YYYYMMDD') + ".txt"
    return os.path.join(my_dir, my_file)

def create_new_file(my_file, launch = True):
    print("Creating new daily file", my_file)
    f = open(my_file, "w")
    if file_header:
        f.write(file_header)
    for s in sect_ary: f.write("\n\\{:s}\n".format(s))
    f.close()
    if launch: os.system(my_file)

#
# main coding block
#
# todo: look on command line

os.chdir("c:/writing/scripts")

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg[0] == 'f' and arg[1:].isdigit():
        files_back_wanted = int(arg[1:])
        latest_daily = False
    elif arg[0] == 'm' and arg[1:].isdigit():
        max_days_back = int(arg[1:])
        latest_daily = False
    elif (arg[:2] == 'mn' or arg[:2] == 'nm') and arg[2:].isdigit():
        max_days_new = int(arg[2:])
        latest_daily = False
    elif arg == 'l': latest_daily = True
    elif arg == 'nl' or arg == 'ln': latest_daily = False
    elif arg == 'v': verbose = True
    elif arg == 'nv' or arg == 'vn': verbose = False
    elif arg == 'e': mt.npo(my_sections_file)
    elif arg == '?': usage()
    else: usage("Bad parameter {:s}".format(arg))
    cmd_count += 1

if latest_daily:
    get_init_sections()
    found_done_file = False
    for x in range(0, max_days_new):
        day_file = see_back(d, daily, x)
        day_done_file = see_back(d, daily_done, x)
        if os.path.exists(day_file):
            print("Found recent daily file {:s}, opening.".format(day_file))
            os.system(day_file)
            exit()
        if os.path.exists(day_done_file): found_done_file = day_done_file
    if found_done_file: sys.exit("Found {:s} in done folder. Not opening new one.")
    print("Looking back", max_days_new, "days, daily file not found.")
    create_new_file(see_back(d, daily, 0))
    exit()

files_back_in_dir = 0
for x in range(0, max_days_back):
    day_file = see_back(d, daily, x)
    if os.path.exists(day_file):
        files_back_in_dir += 1
        if verbose and files_back_in_dir <= files_back_wanted: print("Skipping", day_file)
    if files_back_in_dir > files_back_wanted:
        print("Got daily file", day_file, files_back_wanted, "files back.")
        os.system(day_file)
        exit()

