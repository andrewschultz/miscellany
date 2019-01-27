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

import os
import datetime
import re

from collections import defaultdict

hour_parts = 4

of_week = defaultdict(bool)
of_day = defaultdict(lambda: defaultdict(bool))
of_month = defaultdict(lambda: defaultdict(bool))

check_file  = "c:\\writing\\scripts\\hrcheck.txt";
check_private = "c:\\writing\\scripts\\hrcheckp.txt";
xtra_file   = "c:\\writing\\scripts\\hrcheckx.txt";

code   = "c:\\writing\\scripts\\hrcheck.py";

bailFile   = "c:\\writing\\scripts\\hrcheck-bailfile.txt";
forgotFile = "c:\\writing\\scripts\\hrcheck-forgotfile.txt";
anyExtra   = 0;
extraFiles = [];

show_warnings = False

# thanks to https://stackoverflow.com/questions/42950/get-last-day-of-the-month-in-python

def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

def garbage_collect(x):
    y = re.sub("^\\\\", "", x) # stuff that needs to go first or last
    return y

def make_time_array(j, k):
    quarter_hour = 0
    my_weekday = 0
    my_monthday = 0
    j = garbage_collect(j)
    if j[-1] == 'h':
        j = j[:-1]
        quarter_hour = 2
    elif j[-1] == 'p':
        j = j[:-1]
        quarter_hour = 3
    elif j[-1] == 'b':
        j = j[:-1]
        quarter_hour = 1
    elif j[-1] == 't':
        j = j[:-1]
        quarter_hour = 0
    j2 = int(j) * 4 + quarter_hour
    print("Adding to", j2)
    q = len(of_day[j2].keys())
    of_day[j2][k] = q + 1
    return

def read_hourly_check(a):
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
                print("Line {:d} copies previous line and is {:s}.".format(line_count, line.strip()))
            a1 = line.split("|")
            if len(a1) > 2:
                if show_warnings: print("WARNING too many variables, can't yet parse line {:d}:\n    {:s}".format(line_count, line))
                continue
            a2 = a1[0].split(",")
            a3 = a1[-1].split("\t")
            for x in a2:
                for y in a3:
                    make_time_array(x, y)
            old_line = line
            old_cmd = re.sub("\|[^\|]*$", "", old_line)

old_line = ""
old_cmd = ""

n = datetime.datetime.now() # -datetime.timedelta(minutes=-16)
time_index = n.hour * 4 + (n.minute * hour_parts) // 60
wkday = n.weekday()
mday = n.day

print("Time index: {:d} of {:d} Weekday: {:d} Monthday: {:d}".format(time_index,24 * hour_parts,wkday,mday))

read_hourly_check(check_file)
read_hourly_check(check_private)
read_hourly_check(xtra_file)

print("Running", time_index)
for x in of_day[time_index].keys():
    print(x)
    os.system(x)
