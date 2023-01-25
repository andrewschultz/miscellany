# ni.py
# python based replacement (of sorts) for batch files ni.bat and gh.bat
# they will be renamed niold.bat and ghold.bat

import sys
import os
import mytools as mt
import i7

to_project = i7.dir2proj()

def usage(header="Generic usage writeup"):
    mt.okay(header)
    print("This is a quasi-replacement for the batch file ni.bat.")
    print()
    mt.warn("Examples of usage:")
    print("ni t opens the source file in the current directory.")
    print("ni vf ta opens up VVFF's tables.")
    sys.exit()

cmd_count = 1

if len(sys.argv) == 1:
    usage("No commands given")

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == 't':
        get_main_source = True
    elif arg == '?':
        usage("USAGE")
    else:
        usage("Bad parameter {}.".format(arg))
    cmd_count += 1

if not to_project:
    mt.bailfail("Could not find project to act on.")

if get_main_source:
    os.system(i7.main_src(to_project))