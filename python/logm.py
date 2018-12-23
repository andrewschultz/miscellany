#
# logm.py
# modifies the log date
#
# run from the command line not from the git shell
#

import os
import sys
import time
from time import mktime
from datetime import datetime

def usage(arg = ""):
    if arg: print("Invalid command", arg)
    else: print("USAGE")
    print("=" * 50)
    print("r or x executes the command")
    print("a number specifies the days back to look.")


days = 0
count = 1
run_cmd = False

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'r' or arg == 'x': run_cmd = True
    elif arg.isdigit(): days = int(arg)
    elif arg == '?': usage()
    else: usage()
    count += 1

x = time.localtime().tm_isdst
y = time.localtime()

z = int(time.time())

z00 = (int(z/86400)) * 86400

z0 = (int(z/86400) - days) * 86400

z2 = time.localtime(z0)

if z2.tm_isdst:
    z1 = (int(z/86400) - days) * 86400 + 17820
else:
    z1 = (int(z/86400) - days) * 86400 + 21420

if z1 > z00:
    sys.exit("No need to shift anything yet.")

z2 = time.localtime(z1)

out_string = "git commit --amend --date=\"{:s} -0{:d}00\"".format(time.strftime("%a %b %d %H:%M:%S", z2), 6 - x)

print(out_string)

if run_cmd:
    os.system(out_string)
else:
    print("Use -r to run.")
