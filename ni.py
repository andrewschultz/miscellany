# ni.py
# python based replacement (of sorts) for batch files ni.bat and gh.bat
# they will be renamed niold.bat and ghold.bat

import sys
import os
import mytools as mt
import i7

to_project = i7.dir2proj()

force_batch_move = False
source_opened = False
get_main_source = False
goto_github = False
hfx_ary = []
user_project = ''

temp_batch_file = "c:\\writing\\temp\\ni-temp.bat"

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
    if arg == 'gh':
        goto_github = True
    elif arg == 't':
        get_main_source = True
    elif arg == '-':
        force_batch_move = True
    elif arg == '?':
        usage("USAGE")
    elif arg in i7.i7hfx:
        hfx_ary.append(arg)
    elif arg in i7.i7x:
        if user_project:
            mt.bailfail("Defined 2 projects: {} and {}.".format(user_project, arg))
        user_project = arg
    else:
        usage("Bad parameter {}.".format(arg))
    cmd_count += 1

if user_project:
    to_project = user_project
elif not to_project:
    mt.bailfail("Could not find project to act on.")

if get_main_source:
    mt.npo(i7.main_src(to_project))
    source_opened = True

for h in hfx_ary:
    this_file = i7.hdr(to_project, h)
    if os.path.exists(this_file):
        mt.okay("Opening", this_file)
        mt.npo(this_file, bail=False)
        source_opened = True
    else:
        mt.bailfail("Could not open {}.".format(this_file))

if not force_batch_move and source_opened:
    sys.exit()

if os.path.exists(temp_batch_file):
    os.remove(temp_batch_file)

f = open(temp_batch_file, "w")
f.write("@echo off\n\n")
f.write("cd {}\n".format(i7.proj2dir(to_project, to_github = goto_github)))
f.close()

