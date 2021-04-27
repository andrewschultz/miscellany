#
# 2dy.py: replacement for perl script that went X daily files back.
#
# 2dy.txt is the CFG file
#
# note that this is a misnomer as I in fact only create a file once a week
#
# but it still creates the latest daily file, and the "daily" directory name is kept for posterity
#

import glob
import xml.etree.ElementTree as ET
import sys
import pendulum
import os
from collections import defaultdict
from shutil import copy
import mytools as mt
from stat import S_IREAD, S_IRGRP, S_IROTH
import matplotlib.pyplot as plt
import numpy as np

#init_sect = defaultdict(str)

#d = pendulum.now()
d = pendulum.today()

#these are covered in the config file, but keep them here to make sure
max_days_new = 7
max_days_back = 1000

os.chdir("c:/writing/daily")
latest_daily = True

daily = "c:/writing/daily"
daily_proc = "c:/writing/daily/to-proc"
daily_done = "c:/writing/daily/done"

stats_file = "c:/writing/temp/daily-stats.txt"

file_header = ""

sect_ary = []

files_back_wanted = 1
verbose = False

my_sections_file = "c:/writing/scripts/2dy.txt"

def see_back(this_file = d, my_dir = "", days_back = 7):
    my_file = this_file.subtract(days=days_back).format('YYYYMMDD') + ".txt"
    return os.path.join(my_dir, my_file)

def check_unsaved():
    open_array = []
    e = ET.parse(mt.np_xml)
    root = e.getroot()
    for elem in e.iter('File'):
        itersize += 1
        t = elem.get('filename')
        if 'daily' in t and re.search("[\\\/][0-9]{8}\.txt", t):
            bfp = elem.get("backupFilePath")
            if bfp:
                if not os.path.exists(bfp):
                    print("No backup file for", t, "exists. It should be", bfp)
                    continue
                print(t, "has backup/needs re-saving")
                open_array.append(t)
    if not len(open_array): return
    for x in open_array:
        mt.npo(x, bail = False)

def get_stats():
    os.chdir("c:/writing/daily")
    f = open(stats_file, "r")
    stat_lines = f.readlines()
    stat_lines.reverse()
    first_array = stat_lines[0].split("\t")
    this_file = first_array[0]
    this_idx = 0
    while this_idx < len(stat_lines) and stat_lines[this_idx].split("\t")[0] == this_file:
        this_idx += 1
    relevant_stats = stat_lines[:this_idx]
    relevant_stats.reverse()
    f.close()

    init_time = stat_lines[-1].split("\t")[1]
    itp = pendulum.parse(init_time)

    times = []
    sizes = []

    current_size = os.stat(this_file).st_size
    last_size = int(first_array[2])

    for r in relevant_stats:
        ary = r.split("\t")
        my_time = pendulum.parse(ary[1])
        times.append((my_time - itp).seconds / 86400)
        sizes.append(int(ary[2]))
    times = np.array(times)
    sizes = np.array(sizes)

    (a, b) = np.polyfit(times, sizes, 1)
    my_label = "bytes={:.2f}*days{}{:.2f}".format(a, '+' if b > 0 else '', b)

    if current_size > last_size:
        my_label += "\n{} bytes since last data check".format(current_size - last_size)

    plt.scatter(times, sizes, label=my_label)
    plt.xlabel("days")
    plt.ylabel("bytes")
    plt.plot(times, a*times+b)
    plt.legend(loc='upper left')
    plt.show()
    sys.exit()

def put_stats(bail = True):
    os.chdir("c:/writing/daily")
    f = open(stats_file, "a")
    ld = mt.last_daily_of()
    pn = pendulum.now()
    out_string = "{}\t{}\t{}".format(ld, pendulum.now(), os.stat(ld).st_size)
    f.write(out_string + "\n")
    print(out_string)
    f.close()
    if bail:
        sys.exit()

def move_to_proc(my_dir = "c:/writing/daily"):
    import win32ui
    import win32con

    os.chdir(my_dir)
    print("Moving", my_dir, "to to-proc.")
    g1 = mt.dailies_of(my_dir)
    g2 = mt.dailies_of(my_dir + "/to-proc")

    threshold = see_back(d, '', 7)
    temp_save_string = ""

    for q in g1:
        if q > threshold:
            print(q, "above threshold of", threshold, "so ignoring. Set mn=0 to harvest/read-only all files.") # this should only happen once per run
            continue
        if mt.is_daily(q):
            abs_q = os.path.abspath(q)
            if mt.is_npp_modified(abs_q):
                temp = win32ui.MessageBox("{} is open in notepad. Save and click OK, or CANCEL.".format(abs_q), "Save {} first!".format(q), win32con.MB_OKCANCEL)
                if temp == win32con.IDCANCEL:
                    temp_save_string += "\n" + q
                    continue
            if q not in g2:
                print(q, "needs to be moved to to-proc and set read-only. Let's do that now!")
                copy(q, "to-proc/{}".format(q))
                os.chmod(q, S_IREAD|S_IRGRP|S_IROTH)
            else:
                if os.access(q, os.W_OK):
                    print(q, "needs to be set read-only in the base directory. Let's do that now!")
                    os.chmod(q, S_IREAD|S_IRGRP|S_IROTH)

    if temp_save_string:
        to_save = "c:/writing/temp/daily-to-save.htm"
        f = open(to_save, "w")
        f.write("Daily file(s) that need saving:")
        f.write(temp_save_string)
        f.close()
        mt.text_in_browser(to_save)

    if 'daily' not in my_dir:
        sys.exit("Bailing since we're using non-daily directory.")

def usage(param = 'Cmd line usage'):
    print(param)
    print('=' * 50)
    print("(-?)f (#) = # files back (or # without f)")
    print("(-?)m (#) = # max days back")
    print("(-?)mn/n/nm (#) = # max new days back")
    print("(-?)l or ln/nl = latest-daily (or not)")
    print("(-?)v or vn/nv = toggle verbosity")
    print("(-?)p/tp = move to to_proc, tk/kt and dt/td to keep/drive")
    print("(-?)ps = put stats, (-?)gs = get stats, (-?)es = edit stats, (-?)ss = sift stats")
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
                file_header += line[12:].replace("\\", "\n")
                continue
            if "," not in line:
                print("WARNING: unidentified line (no valid header or CSV of sections {}".format(line_count))
                continue
            ary = line.lower().strip().split(",")
            if len(sect_ary):
                print("Adding to array of blank sections on line {}".format(line_count))
            for q in ary:
                ary2 = q.split('=')
                sect_ary.append(ary2[0])
                # init_sect[ary2[0]] = ary2[1]
    sect_ary_2 = sorted(sect_ary, key=lambda x:(x == 'nam', x))
    if sect_ary_2 != sect_ary:
        print("WARNING wobbly unsorted sections:")
        print("    is: {}".format(', '.join(sect_ary)))
        print("    best order: {}".format(', '.join(sect_ary_2)))
        sect_ary = sect_ary_2

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
    elif arg.isdigit():
        files_back_wanted = int(arg)
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
    elif arg == 'p' or arg == 'tp' or arg == 't': move_to_proc()
    elif arg == 'gs': get_stats()
    elif arg == 'ps': put_stats()
    elif arg == 'es': mt.npo(stats_file)
    elif arg == 'tk' or arg == 'kt': move_to_proc("c:/coding/perl/proj/from_keep")
    elif arg == 'td' or arg == 'dt': move_to_proc("c:/coding/perl/proj/from_drive")
    elif arg == '?': usage()
    else: usage("Bad parameter {:s}".format(arg))
    cmd_count += 1

if latest_daily:
    found_done_file = False
    for x in range(0, max_days_new):
        day_file = see_back(d, daily, x)
        day_done_file = see_back(d, daily_done, x)
        if os.path.exists(day_file):
            if os.stat(day_file).st_size == 0:
                print("Ignoring blank file", day_file)
                continue
            print("Found recent daily file {:s}, opening.".format(day_file))
            os.system(day_file)
            exit()
        if os.path.exists(day_done_file): found_done_file = day_done_file
    if found_done_file: sys.exit("Found {:s} in done folder. Not opening new one.")
    print("Looking back", max_days_new, "days, daily file not found.")
    get_init_sections()
    create_new_file(see_back(d, daily, 0))
    exit()

files_back_in_dir = 0

for x in range(0, max_days_back):
    day_file = see_back(d, daily, x)
    if os.path.exists(day_file):
        if os.stat(day_file).st_size == 0:
            print("Ignoring blank file", day_file)
            continue
        files_back_in_dir += 1
        if verbose and files_back_in_dir <= files_back_wanted: print("Skipping", day_file)
    if files_back_in_dir > files_back_wanted:
        print("Got daily file", day_file, files_back_wanted, "files back.")
        os.system(day_file)
        exit()

print("Failed to get a file in the last", max_days_back, "days")

