# ni.py
# python based replacement (of sorts) for batch files ni.bat and gh.bat
# they will be renamed niold.bat and ghold.bat
#
# check them for odd oneoffs to add to the flags before getting rid of the old file
#
# remember to check i7clash.py ni.py frequently as I add commands
#
# also, ni-remaining.bat will have a lot of stuff for special commands
# we want to go through them. This is intended to be a can-opener.
# special case: STS UNI universal (don't expand STS to stale-tales-slate? Or change the name? Or make i7.hdr(x) look for lower case as well or give it an option?)

import sys
import os
from collections import defaultdict
import mytools as mt
import i7
from shutil import move

to_project = i7.dir2proj()

force_batch_move = False
source_opened = False
get_main_source = False
get_notes = False
goto_github = False
hfx_ary = []
user_project = ''

temp_batch_file = "c:\\writing\\temp\\ni-temp.bat"
temp_batch_file_backup = "c:\\writing\\temp\\ni-temp-backup.bat"

ni_cfg = "c:/writing/scripts/ni.txt"

map_to = defaultdict(str) # this maps command line arguments to a specific file e.g. gglo (general global) = c:\Users\Andrew\Documents\github\gloco

def usage(header="Generic usage writeup"):
    mt.okay(header)
    print("This is a quasi-replacement for the batch file ni.bat.")
    print()
    mt.warn("Examples of usage:")
    print("ni t opens the source file in the current directory.")
    print("ni vf ta opens up VVFF's tables.")
    print()
    print("ni otf / dtf = opens / deletes temp file. Shorthand is o, while b opens the backup temp file from the previous run.")
    sys.exit()

def read_special_commands():
    with open(ni_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            l = line.lower().strip()
            if '~' not in l:
                continue
            a1 = l.split('=')
            if len(a1) > 2:
                mt.warn("WARNING line {} has >1 =.".format(len(a1)))
            a2 = a1[0].split(',')
            if not os.path.exists(a1[1]):
                mt.fail("NO SUCH FILE {} line {}".format(a1[1], line_count))
                continue
            for a in a2:
                if a in map_to:
                    mt.warn("Duplicate instance of {} in mapto file.".format(a))
                else:
                    map_to[a] = a1[1]

cmd_count = 1

if len(sys.argv) == 1:
    usage("No commands given")

read_special_commands()

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == 'gh':
        goto_github = True
    elif arg in ('ggl', 'gglo'):
        mt.npo(i7.gloco)
    elif arg == 't':
        get_main_source = True
    elif arg == '-':
        force_batch_move = True
    elif arg == 'no':
        get_notes = True
    elif arg in ( 'd', 'dtf', 'dt', 'tfd', 'td' ):
        if os.path.exists(temp_batch_file):
            os.remove(temp_batch_file)
        else:
            mt.failbail("No {} to delete.".format(temp_batch_file))
        mt.bailokay("{} deleted.".format(temp_batch_file))
    elif arg in ( 'o', 'otf', 'ot', 'otf', 'tfo', 'to' ):
        if os.path.exists(temp_batch_file):
            mt.okay("Opening temp batch file {}.".format(temp_batch_file))
            mt.npo(temp_batch_file, print_cmd = False)
        else:
            mt.failbail("{} is not present.".format(temp_batch_file))
    elif arg in ( 'b', 'btf', 'bt', 'btf', 'tfb', 'tb' ):
        if os.path_exists(temp_batch_file_backup):
            mt.okay("Opening backup temp batch file {}.".format(temp_batch_file_backup))
            mt.npo(temp_batch_file_backup, print_cmd = False)
        else:
            mt.failbail("{} is not present.".format(temp_batch_file_backup))
    elif arg.startswith('s='):
        temp = arg[2:]
        if temp in map_to:
            mt.npo(map_to[temp])
        else:
            print(map_to)
            mt.bailfail("Bad value {} for s=.".format(temp))
    elif arg == '?':
        usage("USAGE")
    elif arg in i7.i7hfx:
        hfx_ary.append(arg)
    elif arg in i7.i7x:
        if user_project:
            mt.bailfail("Defined 2 projects: {} and {}.".format(user_project, arg))
        user_project = arg
    elif arg in map_to:
        mt.warn(arg, "is in the map_to file, but it's safest to prefix it with s=.")
        mt.npo(map_to[temp])
    else:
        usage("Bad parameter {}.".format(arg))
    cmd_count += 1

if user_project:
    to_project = user_project
elif not to_project:
    if 'glo' in hfx_ary:
        mt.warn("Since global headers were in the array, I'm opening the general GLOCO file.")
        mt.npo(i7.gloco)
    mt.bailfail("Could not find project to act on.")

if get_main_source:
    main_source = i7.main_src(to_project)
    if not os.path.exists(main_source):
        mt.fail("Uh oh. This is bad. {} does not exist. Check for it in github, maybe?".format(main_source))
    print("Opening {} main source {}...".format(to_project, main_source))
    mt.npo(main_source, print_cmd = False, bail = False)
    source_opened = True

if get_notes:
    notes_file = os.path.join(i7.proj2dir(to_project), "notes.txt")
    if not os.path.exists(notes_file):
        mt.bailfail(notes_file, "does not exist. We may need to create it with noc or cno.")
    print("Opening {} notes...".format(to_project))
    mt.npo(notes_file, print_cmd = False, bail = False)
    source_opened = True

for h in hfx_ary:
    this_file = i7.hdr(to_project, h)
    if os.path.exists(this_file):
        mt.okay("Opening", this_file)
        mt.npo(this_file, bail=False, print_cmd = False)
        source_opened = True
    elif h == "glo":
        mt.warn("Since global headers were in the array, and {} has no global header, I'm opening the general GLOCO file.".format(to_project))
        mt.npo(i7.gloco)
    else:
        mt.bailfail("Could not open {}.".format(this_file))

if os.path.exists(temp_batch_file):
    move(temp_batch_file, temp_batch_file_backup)

if (not force_batch_move) and source_opened:
    sys.exit()

f = open(temp_batch_file, "w")
f.write("@echo off\n\n")
f.write("cd {}\n".format(i7.proj2dir(to_project, to_github = goto_github)))
f.close()

