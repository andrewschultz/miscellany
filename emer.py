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
import re
import pendulum
from collections import defaultdict
from shutil import copy
import mytools as mt
import glob
import time

type_of = defaultdict(str)
shortcuts = defaultdict(str)

valid_types = [ 'h', 'd', 'w' ]

my_short = ''

find_daily = False

emergency_dir = "c:\\writing\\emergency"
cfg_file = "c:\\writing\\scripts\\emer.txt"
delete_days = 14
delete_files = False
test_mode = False

def usage(heading="Basic EMER.PY usage"):
    print("Emer.py cannot be run without an argument.")
    print("Emer.py da copies over the daily file.")
    print("Emer.py nps copies over the notepad sessions file.")
    sys.exit()

def delete_old_files(short_to_delete, days_back, daily_files = False, test_mode = False):
    deleted_files = 0
    this_time = time.time()
    if daily_files:
        regex_start = "[0-9]{8,}-"
        base_file_array = [ regex_start, 'txt' ]
        base_search_string = '2'
    else:
        base_file = os.path.basename(shortcuts[short_to_delete])
        base_file_array = base_file.split('.', -1)
        base_search_string = base_file_array[0] + "-"
        regex_start = base_search_string
    glob_string = os.path.join(emergency_dir, base_search_string + "*")
    regex_search_string = regex_start + "[-0-9]{4}(-[0-9]{2})+"
    if len(base_file_array) > 1:
        regex_search_string += "\." + base_file_array[1]
    regex_search_string = '^{}$'.format(regex_search_string)
    g = glob.glob(glob_string)
    g0 = [x for x in g if re.search(regex_search_string, os.path.basename(x))]
    for f in g0:
        f = os.path.join(emergency_dir, f)
        my_time = os.stat(f).st_mtime
        delta = (this_time - my_time) / 86400
        if delta > days_back:
            print("Deleting {} as it is {:.2f} days back, above the threshold of {}.".format(f, delta, days_back))
            if not test_mode:
                os.remove(f)
            deleted_files += 1
    if deleted_files:
        mt.okay("Deleted {} file{}.".format(deleted_files, mt.plur(deleted_files)))
        if test_mode:
            mt.fail("Not really. You need to set the test_mode flag. I assume this is just testing a new feature.")
    else:
        mt.warn("Deleted no files.")
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
    if arg == 'd':
        sys.exit("You need to tell how many days back to delete after d.")
    elif arg[0] == 'd' and arg[1:].isdigit():
        delete_files = True
        delete_days = int(arg[1:])
        if delete_days == 0:
            sys.exit("Deletion must be at least one day back.")
    elif arg == 'da':
        find_daily = True
    elif arg == 'e':
        mt.open(cfg_file)
    elif arg == 't':
        test_mode = True
    elif arg in shortcuts:
        if my_short:
            sys.exit("Can only backup one file at a time.")
        my_short = arg
    elif arg == '?':
        usage('BRIEF USAGE')
    else:
        usage('UNKNOWN COMMAND LINE ARGUMENT{}'.format(arg))
    cmd_count += 1

if delete_files:
    if find_daily:
        delete_old_files("", delete_days, daily_files = find_daily, test_mode = True)
    else:
        delete_old_files(my_short, delete_days, test_mode = test_mode)

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
