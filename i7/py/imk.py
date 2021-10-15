# imk.py: Inform (or I) make a header/include file
#
# usage: project, header full name or abbreviation
#
# e.g. you would create Ailihphilia's tables with
#
# imk.py ai ta
#
# Fourbyfourian Quarryin Beta Testing:
# imk.py 4 be
#
# other/core files can be created with
#
# imk.py "My new odd extension"

import os
import re
import i7
import sys
import datetime
from pathlib import Path # this forces us to use Python 3.4 but it's worth it
import mytools as mt

count = 1
file_args = []

overwrite = False
open_post_conversion = True

base_file_noxt = ""

if not os.path.exists(i7.extdir): sys.exit("Uh oh! Extension directory {:s} not found!".format(i7.extdir))

def usage():
    print("=" * 50)
    print("-o / -f / -fo = overwrite file")
    print("-n / -on / -no = don't open post conversion. Default = open.")

def check_valid_combo(my_abbrev, abbrev_class, dict_of_abbrevs):
    if my_abbrev in dict_of_abbrevs: return
    if my_abbrev in dict_of_abbrevs.values(): return
    sys.exit("You may need to define a valid {} abbreviation--{} turned up nothing.".format(abbrev_class, my_abbrev))

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg == '-o' or arg == '-of' or arg [0] == '-of': overwrite = True
    elif arg == '-n' or arg == '-on' or arg == '-no': open_post_conversion = False
    else:
        if ' ' in arg:
            file_args.append(sys.argv[count])
        else:
            file_args.append(arg)
    count += 1

if len(file_args) == 0:
    sys.exit("I need a valid project and/or header. I have neither.")

if len(file_args) == 1:
    temp = i7.dir2proj()
    if not temp:
        sys.exit("You need to provide a valid project (abbreviation) and header (abbreviation) or be in a product directory and specify a header (abbreviation).")
    print("Assuming default project", temp)
    file_args.insert(0, temp)

if file_args[1] in i7.i7x and file_args[0] not in i7.i7x:
    print("It looks like you put the project name first, so I am flipping the arguments. No big deal.")
    file_args = file_args[::-1]

if len(file_args) == 1 and ' ' in file_args[0]:
    base_file_noxt = file_args[0].strip()
    if base_file_noxt.lower().endswith('.i7x'): base_file_noxt = base_file_noxt[-4]
elif len(file_args) != 2:
    print("You need 2 file arguments: 1st the project, 2nd the module description. You have {:d}.".format(len(file_args)))
    print("Though it is okay to use 1 argument if it has a space in it. That space can be at the beginning or end if there is only one word.");
    usage()

check_valid_combo(file_args[0], 'project', i7.i7x)
check_valid_combo(file_args[1], 'header file', i7.i7hfx)

if not file_args[1] in i7.i7hfx.keys() and not file_args[1] in i7.i7hfx.values():
    sys.exit("You may need to define a valid header file abbreviation--{} turned up nothing.".format(file_args[1]))

if not base_file_noxt:
    my_proj = i7.proj_exp(file_args[0], False)
    if not my_proj: sys.exit("You need to define a valid project or project abbreviation.")
    base_file_noxt = '{:s} {:s}'.format(i7.proj_exp(file_args[0], False), i7.hf_exp(file_args[1])).title().replace('-', ' ')

base_file = base_file_noxt + ".i7x"
nongit_file = i7.extdir + "\\" + base_file # can't use os.path.join since the file may not be there
my_git_proj = i7.i7gx[i7.main_abbr(my_proj)] if my_proj in i7.i7xr else my_proj
git_file = i7.gh_dir + "\\" + my_git_proj + "\\" + base_file

link_command = "mklink \"{}\" \"{}\"".format(nongit_file, git_file)

if os.path.exists(git_file) and not overwrite:
    if not open_post_conversion: sys.exit("With open post conversion set to off, there is nothing to do here. Bailing.")
    print(nongit_file, "exists. Opening and not creating.")
    mt.npo(nongit_file)
else:
    if overwrite:
        print(git_file, "exists but overwriting.")
    else:
        print(git_file, "does not exist. Creating.")
    now = datetime.datetime.now()
    f = open(git_file, "w")
    f.write("Version 1/{:02d}{:02d}{:02d} of {:s} by {:s} begins here.\n\n\"This should briefly describe the purpose of {:s}.\"\n\n".format(now.year % 100, now.month, now.day, base_file_noxt, i7.auth, base_file_noxt))
    f.write("{:s} ends here.\n\n---- DOCUMENTATION ----\n".format(base_file_noxt))
    f.close()

print("Running link command", link_command)
os.system(link_command)

if open_post_conversion: i7.npo(nongit_file)