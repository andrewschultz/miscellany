############################################
#hrcheck.py (formerly hrcheck.pl/sov.pl for stack overflow stuff)
#
#scheduling stuff, and stuff
#hrcheck.txt edited for what, when
#
#example of one line:
#
#11|FFX "http://www.thefreedictionary.com"
#
#Weekly thing
#5|8|FFX "http://btpowerhouse.com"
#
#tphb = quarter hours
#:(0-5) = 0 past, 10 past, etc.

import sys
import os
import datetime
import re

from collections import defaultdict

hour_parts = 4

of_day = defaultdict(str)
of_week = defaultdict(lambda: defaultdict(str))
of_month = defaultdict(lambda: defaultdict(str))

check_file  = "c:\\writing\\scripts\\hrcheck.txt";
check_private = "c:\\writing\\scripts\\hrcheckp.txt";
xtra_file   = "c:\\writing\\scripts\\hrcheckx.txt";

lock_file   = "c:\\writing\\scripts\\hrchecklock.txt";
queue_file   = "c:\\writing\\scripts\\hrcheckqueue.txt";

code   = "c:\\writing\\scripts\\hrcheck.py";

bailFile   = "c:\\writing\\scripts\\hrcheck-bailfile.txt";
forgotFile = "c:\\writing\\scripts\\hrcheck-forgotfile.txt";
anyExtra   = 0;
extraFiles = [];

show_warnings = False

# thanks to https://stackoverflow.com/questions/42950/get-last-day-of-the-month-in-python

def is_time(t):
    x = t.count(":")
    if x != 1: sys.exit("Time must have 1 colon")
    y = t.split(":")
    return y[0].isdigit() and y[1].isdigit()

def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return (date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)).day

def usage():
    print("=" * 50)
    print("hh = normalizes to half hour e.g. :12 or :18 look for both :00 and :15 tipoffs. nh/hn turns it off.")
    print("rp/p/r decides whether to print or run current commands")
    print("l = lock the lockfile, u = unlock the lockfile, q = run the queue file")
    exit()

def garbage_collect(x):
    y = re.sub("^\\\\", "", x) # stuff that needs to go first or last
    return y

def my_time(x):
    hr = { 'h': 2, 'p': 3, 'b': 1, 't': 0 }
    for q in hr:
        if x[-1] == q:
            return int(x[:-1]) * 4 + hr[q]
    return int(x) * 4

def make_time_array(j, k):
    quarter_hour = 0
    my_weekday = 0
    my_monthday = 0
    monthday_array = []
    weekday_array = []
    day_array = []
    j = garbage_collect(j)
    slash_array = j.split("/")
    kn = k + "\n"
    for q in slash_array:
        if q.startswith("m="):
            monthday_array = q[2:].split(",")
        elif q.startswith("d="):
            weekday_array = q[2:].split(",")
        else:
            hour_array = [my_time(x) for x in q.split(",")]
    if len(monthday_array):
        for m in monthday_array:
            for h in hour_array:
                # print("Month/hour adding", m, h)
                of_month[h][m] += kn
    if len(weekday_array):
        for w in weekday_array:
            for h in hour_array:
                # print("Week/hour adding", w, h)
                of_week[h][w] += kn
    if not len(monthday_array) and not len(weekday_array):
        for h in hour_array:
            of_day[h] += kn
    return

def read_hourly_check(a):
    old_line = ""
    old_cmd = ""
    with open(a) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if line.startswith("="):
                if show_warnings: print("WARNING line {:d} =bookmarks not supported (yet).".format(line_count))
                continue
            if "|" not in line:
                if show_warnings: print("WARNING odd line {:d}:\n    {:s}".format(line_count, line.lower().strip()))
                continue
            line = line.lower().strip()
            if line[0] == '"':
                line = old_cmd + line[1:]
                print("Line {:d} of {:s} copies previous line and is {:s}.".format(line_count, a, line.strip()))
            a1 = line.split("|")
            if len(a1) > 2:
                if show_warnings: print("WARNING too many variables, can't yet parse line {:d}:\n    {:s}".format(line_count, line))
                continue
            a3 = re.sub("\t", "\n", a1[-1])
            make_time_array(a1[0], a3)
            old_line = line
            old_cmd = re.sub("\|[^\|]*$", "", old_line)

def carve_up(q, msg):
    if not q: return 0
    retval = 0
    ary = q.strip().split("\n")
    for x in ary:
        if not x: continue
        if x.startswith("http"): x = "start " + x
        if print_cmd: print("***running", msg, x)
        if run_cmd: os.system(x)
        retval += 1
    return retval

def see_what_to_run(ti, wd, md, hh):
    totals = 0
    totals += carve_up(of_day[ti], "daily run on")
    totals += carve_up(of_week[ti][wd], "weekly run on")
    totals += carve_up(of_month[ti][md], "monthly run on")
    totals += carve_up(of_month[ti][md-last_of_month+1], "monthly run on")
    if hh:
        totals += carve_up(of_day[ti ^ 1], "daily run on")
        totals += carve_up(of_week[ti ^ 1][wd], "weekly run on")
        totals += carve_up(of_month[ti ^ 1][md], "monthly run on")
        totals += carve_up(of_month[ti ^ 1][md-last_of_month+1], "monthly run on")
    print("Ran", totals, "scripts for {:d}h/{:d}w/{:d}m".format(ti,wd,md))

def file_lock():
    if not os.path.exists(lock_file): return False
    with open(lock_file) as file:
        for line in file:
            if line.startswith("locked"): return True
    return False

def lock_lock_file():
    f = open(lock_file, "w")
    f.write("locked")
    f.close()

def unlock_lock_file():
    f = open(lock_file, "w")
    f.write("unlocked")
    f.close()

def run_queue_file():
    already_done = defaultdict(bool)
    f = open(queue_file, "r")
    with open(queue_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            l0 = line.lower().strip()
            if l0 in already_done.keys(): continue
            already_done[l0] = True
            my_list = [int(x) for x in l0.split(",")]
            if len(my_list) != 3:
                print("WARNING line {:d} needs time index, day of week, day of month in {:s}: {:s}".format(line_count, queue_file, line.strip()))
                continue
            see_what_to_run(my_list[0], my_list[1], my_list[2], half_hour)
    f.close()
    f = open(queue_file, "w")
    f.write("#queue file format = (time index),(day of week),(day of month)\n")
    f.close()

queue_run = 0
count = 1
half_hour = False
run_cmd = True
print_cmd = True
time_array = []
minute_delta = 0
mday = -1
wkday = -1

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg == 'hh':
        half_hour = True
    elif arg == 'nh' or arg == 'hn':
        half_hour = False
    elif re.search("^[pr]+$", arg):
        run_cmd = 'r' in arg
        print_cmd = 'p' in arg
    elif arg == 'l':
        lock_lock_file()
        exit()
    elif arg == 'u':
        unlock_lock_file()
        exit()
    elif arg == 'q':
        unlock_lock_file()
        queue_run = 1
    elif is_time(arg):
        time_array = [int(q) for q in arg.split(":")]
    elif arg[0] == 'm':
        mday = int(arg[1:])
    elif arg[0] == 'w':
        wkday = int(arg[1:])
    elif arg == '?':
        usage()
        exit()
    else:
        print("Bad argument", count, arg)
        usage()
        exit()
    count += 1

n = datetime.datetime.now()

if len(time_array):
    time_index = time_array[0] * hour_parts + (time_array[1] * hour_parts) // 60
else:
    n -= datetime.timedelta(minutes=minute_delta)
    if minute_delta: print("WARNING shifting", minute_delta, "back" if minute_delta < 0 else "forward")
    time_index = n.hour * 4 + (n.minute * hour_parts) // 60

if mday == -1: mday = n.day
if wkday == -1: wkday = n.weekday()

last_of_month = last_day_of_month(n)

if file_lock():
    f = open(queue_file, "a")
    string_to_write = "{:d},{:d},{:d}".format(time_index,wkday,mday)
    f.write(string_to_write + "\n")
    print("Wrote", string_to_write, "to", queue_file, "since it is locked.")

read_hourly_check(check_file)
read_hourly_check(check_private)
read_hourly_check(xtra_file)

if queue_run == 1:
    run_queue_file()
else:
    print("Running", time_index)
    see_what_to_run(time_index, wkday, mday, half_hour)
