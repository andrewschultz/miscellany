# imk.py: Inform (or I) make a header/include file
#
# usage: project, header full name or abbreviation
#
# e.g. you would create Ailihphilia's tables with
#
# imk.py ai ta
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

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg == '-o' or arg == '-of' or arg [0] == '-of': overwrite = True
    elif arg == '-n' or arg == '-on' or arg == '-no': open_post_conversion = False
    else:
        if ' ' in arg:
            file_args.append(sys.argv[count])
        else:
            file_args.append(arg)
            print("File arg:", arg)
    count += 1

if len(file_args) == 1 and ' ' in file_args[0]:
    base_file_noxt = file_args[0].strip()
    if base_file_noxt.lower().endswith('.i7x'): base_file_noxt = base_file_noxt[-4]
elif len(file_args) != 2:
    print("You need 2 file arguments: 1st the project, 2nd the module description. You have {:d}.".format(len(file_args)))
    print("Though it is okay to use 1 argument if it has a space in it. That space can be at the beginning or end if there is only one word.");
    usage()

if not base_file_noxt:
    my_proj = i7.proj_exp(file_args[0], False)
    if not my_proj: sys.exit("You need to define a valid project or project abbreviation.")
    base_file_noxt = '{:s} {:s}'.format(i7.proj_exp(file_args[0], False), i7.hf_exp(file_args[1])).title().replace('-', ' ')

base_file = base_file_noxt + ".i7x"
x = i7.extdir + "\\" + base_file # can't use os.path.join since the file may not be there

if os.path.exists(x) and not overwrite:
    if not open_post_conversion: sys.exit("With open post conversion set to off, there is nothing to do here. Bailing.")
    print(x, "exists. Opening and not creating.")
    os.system('"' + x + '"')
else:
    if overwrite:
        print(x, "exists but overwriting.")
    else:
        print(x, "does not exist. Creating.")
    now = datetime.datetime.now()
    f = open(x, "w")
    f.write("Version 1/{:02d}{:02d}{:02d} of {:s} by {:s} begins here.\n\n\"This should briefly describe the purpose of {:s}.\"\n\n".format(now.year % 100, now.month, now.day, base_file_noxt, i7.auth, base_file_noxt))
    f.write("{:s} ends here.\n\n---- DOCUMENTATION ----\n".format(base_file_noxt))
    f.close()

if open_post_conversion: i7.npo(x)