#
# logm.py
# modifies the log date
#
# no arguments needed ... 3 minutes before midnight is the default
# ! = random, so = seconds, max of 1 hour before
# daylight savings time is accounted for

import random
import re
import os
import sys
import time
from time import mktime
from datetime import datetime

def my_time(t):
    return time.strftime("%a %b %d %H:%M:%S", time.localtime(t))

def usage(arg = ""):
    if arg: print("Invalid command", arg)
    else: print("USAGE")
    print("=" * 50)
    print("r or x executes the command")
    print("l at the end runs git log too")
    print("m# specifies minutes before midnight")
    print("s# specifies seconds before midnight in addition to minutes")
    print("so# specifies *only* seconds before midnight, setting minutes to 0")
    print("! specifies a random number of seconds before midnight, from 1 to 600. Default is {:d}.".format(min_before * 60 + sec_before))
    print()
    print("Standard usage is probably logm.py rl (!) (3)")
    print()
    print("a number specifies the days back to look. If it is before midnight, nothing happens.")


min_before = 3
sec_before = 0

days = 0
count = 1
run_cmd = False
run_log = False

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if re.search("^[rxl]+", arg):
        run_cmd = 'r' in arg or 'x' in arg
        cmd_counts = arg.count('r') + arg.count('x')
        run_log = 'l' in arg
        if cmd_counts == 0: print("WARNING an L without an R or X means nothing.")
        elif cmd_counts > 1: print("WARNING extra r/x in the argument to run the command mean nothing.")
    elif arg.isdigit(): days = int(arg)
    elif arg == '!':
        min_before = 0
        sec_before = int(random.random()) * 600 + 1
        print("Random seconds before =", sec_before)
    elif arg[0] == 'm':
        if arg[1:].isdigit(): min_before = int(arg[1:])
        else: sys.exit("-m must take a positive integer after!")
    elif arg[:2] == 'so':
        if arg[2:].isdigit():
            sec_before = int(arg[2:])
            min_before = 0
        else: sys.exit("-so must take a positive integer after!")
    elif arg[0] == 's':
        if arg[1:].isdigit(): sec_before = int(arg[1:])
        else: sys.exit("-s must take a positive integer after!")
    elif arg == '?': usage()
    else: usage()
    count += 1

if sec_before > 60 and min_before > 0: sys.exit(">60 seconds + minutes may be confusing. Use -so to remove this.")
if min_before > 60 or sec_before > 3600: sys.exit("Minutes and/or seconds are too high. 3600 sec is the limit, and you have {:d}.".format(min_before * 60 + sec_before))

x = time.localtime().tm_isdst
y = time.localtime()

z = int(time.time())

z00 = (int(z/86400)) * 86400

z0 = (int(z/86400) - days) * 86400

z2 = time.localtime(z0)

z1 = (int(z/86400) - days) * 86400 + 21600 - min_before * 60 - sec_before
z1 += z2.tm_isdst * 3600 # daylight savings adjustment

zadj = z0 + (5-x) * 3600

print("Here is the current time:", my_time(z))
print("Here is the cutoff time:", my_time(zadj))

if z1 < zadj:
    sys.exit("Current time is {:s} so you don't need to shift anything today. I try for yesterday until {:s}.\nYou can use a number on the command line to specify days back.".format(my_time(z), time.strftime("%H:%M:%S", time.localtime(zadj))))

out_string = "git commit --amend --date=\"{:s} -0{:d}00\"".format(time.strftime(my_time(z1)), 6 - x)

print(out_string)

if run_cmd:
    os.system(out_string)
    if run_log:
        time.sleep(4)
        os.system("git log")
else:
    print("Use -r to run.")
