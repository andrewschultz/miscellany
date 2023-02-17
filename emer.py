# emer.py
# reads in emer.txt
#
# todo:
# * account for weeklies
# * allow copying over
# * allow editing emer.txt

import sys
import os
import pendulum
from collections import defaultdict

type_of = defaultdict(str)
shortcuts = defaultdict(str)

valid_types = [ 'h', 'd', 'w' ]

with open("emer.txt") as file:
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

try:
    if sys.argv[1] not in shortcuts:
        sys.exit("{} is not a valid shortcut. Check emer.txt for those.".format(sys.argv[1]))
except:
    sys.exit("Need an argument, preferably a shortcut from {}".format(list(shortcuts)))

file_name = shortcuts[sys.argv[1]]

t = pendulum.now()

fb = os.path.basename(file_name)

if type_of[file_name] == 'h':
    format_string = 'YYYY-MM-DD-HH'
else:
    format_string = 'YYYY-MM-DD'

out_file = '{}-{}'.format(fb, t.format(format_string))
out_file = os.path.normpath(os.path.join('c:/writing/emergency', out_file))

if os.path.exists(out_file):
    mt.bailfail(out_file, "already exists. Not copying over.")
else:
    print("copy {} {}".format(file_name, out_file))
