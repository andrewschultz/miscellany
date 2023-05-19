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
import glob
import datetime
from pathlib import Path # this forces us to use Python 3.4 but it's worth it
import mytools as mt
import pyperclip
import colorama
from collections import defaultdict

my_quotes = defaultdict(str)

imk_cfg = "c:/writing/scripts/imk.txt"

count = 1
file_args = []

to_clipboard = True
overwrite = False
open_post_conversion = True

base_file_noxt = ""

if not os.path.exists(i7.extdir): sys.exit("Uh oh! Extension directory {:s} not found!".format(i7.extdir))

def usage():
    print("=" * 50)
    print("-o / -f / -fo = overwrite file")
    print("-n / -on / -no = don't open post conversion. Default = open.")
    print("-ds / -sd = verify. Number after changes max files to open.")
    sys.exit()

def possible_mod(my_arg):
    if my_arg.startswith("+"):
        return my_arg[1:].replace('-', ' ').title()
    return my_arg

def check_valid_combo(my_abbrev, abbrev_class, dict_of_abbrevs):
    if my_abbrev in dict_of_abbrevs: return
    if my_abbrev.startswith("+"): return
    sys.exit("You may need to define a valid {} abbreviation--{} turned up nothing. Or you can use + to force things.".format(abbrev_class, my_abbrev))

def has_default_text(x):
    with open(x) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('"'):
                if 'This should briefly' in line:
                    return line_count
                else:
                    return 0
    return 0

def default_search(max_files = 5):
    extras = []
    cur_files = 0
    for x in glob.glob(i7.ext_dir + "/*.i7x"):
        hdt = has_default_text(x)
        if hdt:
            xb = os.path.basename(x)
            cur_files += 1
            if cur_files > max_files:
                extras.append(xb)
            else:
                print("Opening", xb, "line", hdt)
                mt.add_open(x, hdt)
                got_any = True
    if len(extras):
        extra_dict = defaultdict(list)
        for e in extras:
            extra_dict[e[:5]].append(e)
        for d in sorted(extra_dict):
            if len(extra_dict[d]) == 1:
                print("    --", extra_dict[d][0])
            else:
                o = os.path.commonprefix(extra_dict[d])
                where_to_start = o
                where_2 = max(x for x in range(0, len(o)) if o[x] == ' ')
                o = o[:where_2]
                print("    {}: {}".format(o, ', '.join([x[len(o):].strip() for x in extra_dict[d]])))
    if not cur_files:
        print("All purposes written in!")
    mt.post_open()

to_create = []

with open(imk_cfg) as file:
    for (line_count, line) in enumerate (file, 1):
        if line.startswith(';'):
            break
        elif line.startswith('#'):
            continue
        ary = line.strip().split('=', 1)
        if '"' in ary[1]:
            mt.warn("Replacing double quotes with single quotes in summary for {} header file type.".format(ary[0]))
        my_quotes[ary[0]] = ary[1].replace('"', "'")

if len(sys.argv) == 1:
    usage()

while count < len(sys.argv):
    arg = mt.nohy(sys.argv[count])
    if arg in ( 'o', 'of', 'fo'):
        print("Overwrite option is on.")
        overwrite = True
    elif arg in ( 'n', 'on', 'no' ):
        print("Not opening post-conversion.")
        open_post_conversion = False
    elif arg in ( 'c', 'tc' ):
        print("Header include sent to clipboard.")
        to_clipboard = True
    elif mt.alpha_match('nc', arg) or mt.alpha_match('cnt', arg):
        print("Header include not sent to clipboard.")
        to_clipboard = False
    elif arg in ('ds', 'sd'):
        default_search()
        sys.exit()
    elif arg[:2] in ('ds', 'sd') and arg[2:].isdigit():
        default_search(max_files = int(arg[2:]))
    elif arg == '?':
        usage()
    else:
        if to_create:
            sys.exit("You can't create more than one file per run. Run with ? or no arguments to see what works.")
        if ',' not in arg:
            if count == 1:
                to_create = sys.argv[1:]
                break
        else:
            to_create = sys.argv[1].split(',')
    count += 1

this_proj = i7.dir2proj()

if len(to_create) == 1:
    intended_out = os.path.exists(i7.hdr(this_proj, to_create[1]))
    if os.path.exists(intended_out):
        sys.exit("The intended output file already exists, and besides, you forgot to specify the project, too. Add a project of {}.".format(i7.dir2proj(to_abbrev = True)))
    if intended_out:
        sys.exit("Creating a new include file is a rare enough occurrence, we want to specify the project. The implicit one from this directory is {}.".format(i7.dir2proj(to_abbrev = True)))
    sys.exit("Could not find a valid project/header combination. Bailing.")

if len(to_create) < 2 or len(to_create) > 3:
    sys.exit("You need to specify project, header, (optional other project directed to).")

if to_create[1] in i7.i7x and to_create[0] not in i7.i7x:
    print("It looks like you put the project name second, so I am flipping the arguments. No big deal.")
    to_create[0], to_create[1] = to_create[1], to_create[0]

if len(to_create) == 2:
    print("Assuming project-to is project-from.")
    to_create.append(to_create[0])

if to_create[1] not in my_quotes:
    sys.exit("Edit imk.txt to add a to-create for {}.".format(to_create[1]))

combos_and_projects = list(i7.i7x)
combos_and_projects.extend(i7.i7com)

check_valid_combo(to_create[0], 'project', combos_and_projects)
check_valid_combo(to_create[1], 'header file', i7.i7hfx)
check_valid_combo(to_create[2], 'project', combos_and_projects)

to_create = [possible_mod(x) for x in to_create]

orig_file = i7.hdr(to_create[0], to_create[1])
base_file = i7.hdr(to_create[0], to_create[1], base = True)
base_file_noxt = re.sub("\..*", "", base_file)

github_dir = i7.proj2dir(to_create[2], to_github = True)
github_file = github_dir + "\\" + base_file
link_command = "mklink \"{}\" \"{}\"".format(orig_file, github_file)

if to_clipboard:
    include_text = "include {} by Andrew Schultz.".format(base_file_noxt)
    pyperclip.copy(include_text)
    print(colorama.Fore.GREEN + include_text + mt.WTXT, "sent to clipboard, but in the Inform IDE, you'll need a carriage return after.")

if os.path.exists(orig_file) and not overwrite:
    sys.exit("{} exists. Delete it or use the -o flag to overwrite.".format(orig_file))

if os.path.exists(github_file) and not overwrite:
    if not open_post_conversion: sys.exit("With open post conversion set to off, there is nothing to do here. Bailing.")
    print(github_file, "exists. Opening and not creating. Use the -o flag to overwrite.")
    mt.npo(github_file)

if overwrite:
    print(github_file, "exists but overwriting.")
else:
    print(github_file, "does not exist. Creating.")

now = datetime.datetime.now()

try:
    f = open(github_file, "w")
except:
    print(colorama.Fore.RED + "You may not have created the GitHub directory to place this new file. Run these commands:" + mt.WTXT)
    print(colorama.Fore.RED + "cd \\users\\andrew\\documents\\github" + mt.WTXT)
    print(colorama.Fore.RED + "git clone https://github.com/andrewschultz/{}".format(i7.i7x[to_create[0]]) + mt.WTXT)
    sys.exit()

definition_quote = my_quotes[to_create[1]].format(i7.long_name(to_create[0]).replace('-', ' ').title())

f.write("Version 1/{:02d}{:02d}{:02d} of {:s} by {:s} begins here.\n\n\"{}\"\n\n".format(now.year % 100, now.month, now.day, base_file_noxt, i7.auth, definition_quote))
f.write("{:s} ends here.\n\n---- DOCUMENTATION ----\n".format(base_file_noxt))
f.close()

print("Running link command", link_command)

try:
    if os.path.exists(orig_file):
        os.remove(orig_file)
    os.symlink(github_file, orig_file)
    mt.okay("Linking from {} to {} was successful.".format(orig_file, github_file))
except:
    mt.fail("Linking from {} to {} was unsuccessful.".format(orig_file, github_file))
    print("Run this command from a prompt with administrative rights:")
    mt.warn(link_command)

if open_post_conversion:
    mt.npo(github_file, bail=False)
    my_open_text = "HEADERS:{}=".format(i7.long_name(to_create[0]))
    mt.npo(i7.i7_cfg_file, bail=False, open_at_text = my_open_text)
    print("Be sure to tack on {} to {} in the i7p.txt file.".format(i7.i7hfx[to_create[1]], my_open_text))
    sys.exit()
