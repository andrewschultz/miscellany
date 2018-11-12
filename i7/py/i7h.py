#
# i7h.py
# called by i7h.bat

import re
import os
import sys
import i7

usage_str = "You need a header file or abbreviation, or you need a project/header file combination."

my_stuff = sys.argv[1:]

sl = len(my_stuff)

if sl == 0: sys.exit(usage_str)

if len(my_stuff) == 1:
    x = i7.dir2proj(os.getcwd())
    if x: print("You're in project {:s}, so we'll use that to look for header files.".format(x))
    else:
        x = i7.curdef
        print("Going with default project", x)
    my_stuff = [x] + my_stuff
elif len(my_stuff) == 2:
    if my_stuff[1] in i7.i7x.keys() and my_stuff[0] in i7.i7hfx.keys():
        print("Going header-project instead of project-header")
        my_stuff.reverse()
else:
    print("Too many arguments.")
    sys.exit(usage_str)

if not i7.proj_exp(my_stuff[0]): sys.exit("{:s} is not a valid project or abbreviation.".format(my_stuff[0]))
if my_stuff[1] not in i7.i7hfx.keys() and my_stuff[1] not in i7.i7hfx.values(): sys.exit("{:s} is not a valid header file name or abbreviation.".format(my_stuff[1]))

hdr = re.sub("-", " ", i7.proj_exp(my_stuff[0]))

to_open = "{:s}\\{:s} {:s}.i7x".format(i7.extdir, hdr.title(), i7.th_exp(my_stuff[1]))

if os.path.exists(to_open):
    print("Opening", to_open)
    i7.npo(to_open)
else:
    print("No such path", to_open)