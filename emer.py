# emer.py
# reads in emer.txt
#
# todo:
# * account for weeklies
# * allow copying over
# * delete old copies
# * delete wildcard
# * delete/open most recent
#
# main usage:
# emer.py nps (back up notepad file, daily)
# emer.py da (back up daily file)

import sys
import os
import pendulum
from collections import defaultdict
from shutil import copy
import mytools as mt

type_of = defaultdict(str)
shortcuts = defaultdict(str)

valid_types = [ 'h', 'd', 'w' ]

my_short = ''

find_daily = False

emergency_dir = "c:\\writing\\emergency"
cfg_file = "c:\\writing\\scripts\\emer.txt"

def usage(heading="Basic EMER.PY usage"):
    print("Emer.py cannot be run without an argument.")
    print("Emer.py da copies over the daily file.")
    print("Emer.py nps copies over the notepad sessions file.")
    sys.exit()

with open(cfg_file) as file:
    for (line_count, line) in enumerate (file, 1):
        a = line.strip().split("\t")
        if not os.path.exists(a[0]):
            mt.warn("Could not find", a[0])
            continue
        if a[1] not in valid_types:
            print(a[1], "not in valid types. They are", ', '.join(valid_types))
            continue
        type_of[a[0]] = a[1]
        shortcuts[a[2]] = a[0]

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == 'da':
        find_daily = True
    elif arg == 'e':
        mt.open(cfg_file)
    elif arg in shortcuts:
        if my_short:
            sys.exit("Can only backup one file at a time.")
        my_short = arg
    elif arg == '?':
        usage('BRIEF USAGE')
    else:
        usage('UNKNOWN COMMAND LINE ARGUMENT{}'.format(arg))
    cmd_count += 1

if find_daily:
    my_type = 'h'
    file_name = mt.last_daily_of(full_return_path = True)
elif not my_short:
    sys.exit("Need an argument, preferably a shortcut from {}".format(list(shortcuts)))
else:
    file_name = shortcuts[my_short]
    my_type = type_of[file_name]

t = pendulum.now()

fb = os.path.basename(file_name)

if my_type == 'h':
    format_string = 'YYYY-MM-DD-HH'
else:
    format_string = 'YYYY-MM-DD'

a = fb.rsplit('.', 1)
a[0] = '{}-{}'.format(a[0], t.format(format_string))
out_file = '.'.join(a)
out_file = os.path.normpath(os.path.join(emergency_dir, out_file))

if os.path.exists(out_file):
    mt.bailfail(out_file, "already exists. Not copying over.")
else:
    copy(file_name, out_file)
    mt.okay("Copied {} to {}.".format(file_name, out_file))
