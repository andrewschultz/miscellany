#
# dbh.py
#
# debug hacker python file
#
# this takes a X.i7x file and converts it to X debug.i7x (or anything. The default recommended is just X debug.i7x)
#
# dbh.txt has the data on how to cut tables down
# this is useful for testing debug statements a bit more easily
# for instance, to make sure there are exactly 5 elements in a loop
#
# todo: read in cfg file before doing anything
#       have file priority dict
#       have table priority dict which overrides file priority

import sys
import os
import i7
import re
import filecmp
from shutil import copyfile
from collections import defaultdict
from mytools import nohy

# i7.i7x

dbh = "c:/writing/scripts/dbh.txt"

temp_write = os.path.join(i7.extdir, "dbh-temp.i7x")

proj_from_cmd = i7.dir2proj(to_abbrev = True)
default_project = ""
my_project = ""
found_project = False

reading_operators = False
firsts = defaultdict(int)
lasts = defaultdict(int)

copy_level = 1
default_val = 0
ignore_dict = defaultdict(bool)

def cfg_level(x):
    x0 = re.sub(":.*", "", x)
    x0 = re.sub("^[a-z]+", "", x0, 0, re.IGNORECASE)
    try:
        return int(x0)
    except:
        sys.exit("Bad test-level for {}.".format(x))

def is_ignorable(x):
    if x in ignore_dict: return True
    temp = re.sub("\[.*", "", x).lower().strip()
    if temp in ignore_dict: return True
    for f in re.findall("\[(.*?)\]", x):
        if f in ignore_dict: return true
    return False

def process_operators(infile, tempfile, outfile):
    in_mod = infile
    out_mod = outfile
    in_noxt = re.sub("\.[^\.]*$", "", in_mod)
    out_noxt = re.sub("\.[^\.]*$", "", out_mod)
    if 'i7x' in in_mod and 'i7x' in out_mod:
        in_mod = os.path.join(i7.extdir, in_mod)
        out_mod = os.path.join(i7.extdir, out_mod)
    to_go = 0
    at_end = 0
    in_table = False
    line_count = 0
    fk = list(firsts.keys())
    lk = list(lasts.keys())
    ik = list(ignore_dict.keys())
    end_add = []
    fout=open(tempfile, "w")
    got_dbh = False
    ignore_defaults = False
    with open(in_mod) as file:
        for (line_count, line) in enumerate(file, 1):
            if 'dbh.py' in line:
                got_dbh = True
            if line_count == 1:
                new_line = re.sub(in_noxt, out_noxt, line, 0, re.IGNORECASE)
                fout.write(new_line)
                continue
            if line.strip().endswith("ends here."):
                new_line = re.sub(in_noxt, out_noxt, line, 0, re.IGNORECASE)
                fout.write(new_line)
                continue
            if not line.strip():
                if at_end:
                    for x in range (len(end_add)-at_end, len(end_add)):
                        fout.write(end_add[x])
                in_table = False
            if line.startswith("table") and not in_table:
                for x in fk:
                    if line.startswith(x):
                        to_go = firsts[x] + 1
                        in_table = True
                for x in lk:
                    if line.startswith(x):
                        at_end = lasts[x]
                        in_table = True
                        end_add = []
                if in_table == False:
                    ignore_defaults = False
                    if is_ignorable(line.strip()):
                        ignore_defaults = True
                        to_go = 0
                        print("Ignoring defaults for", line.strip())
                    elif default_val:
                        print("Going with", default_val, "for", line.strip())
                        if default_val > 0:
                            to_go = default_val + 1
                        else:
                            at_end = 0 - default_val
                    in_table = True
            if in_table and not ignore_defaults:
                if to_go < 0 or at_end:
                    continue
                to_go -= 1
            if in_table and at_end:
                end_add.append(line)
                continue
            fout.write(line)
    fout.close()
    if not got_dbh:
        print("You may wish to put a reference/comment to dbh.py somewhere in", in_mod)
    if not os.path.exists(out_mod):
        print(outfile, "does not exist, so I will copy over.")
        copyfile(tempfile, out_mod)
    elif filecmp.cmp(tempfile, out_mod): # note this is the reverse of PERL
        print(tempfile, "is identical to", outfile,"so I won't copy back over.")
    else:
        print(tempfile, "is different from", outfile, "so I will write over.")
        copyfile(tempfile, out_mod)
    return

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = nohy(sys.argv[cmd_count])
    if i7.proj_exp(arg, False):
        if my_project:
            sys.exit("Duplicate projects defined.")
        my_project = arg
    elif re.search("^l[0-9]+", arg):
        try:
            copy_level = int(arg[1:])
        except:
            sys.exit("Copying level must be an integer.")
    else:
        sys.exit("Unrecognized", arg)
    cmd_count += 1

with open(dbh) as file:
    for (line_count, line) in enumerate(file, 1):
        t = line.strip().split("\t")
        if line.startswith("defaultproject"):
            default_project = t[1]
            if not i7.is_main_abb(t[1]):
                print("WARNING default project {} is not main abbreviation {}".format(t[1], i7.main_abb(t[1])))
            continue

if not my_project:
    if proj_from_cmd:
        print("No project on command line, going with project assumed from directory", proj_from_cmd)
        my_project = proj_from_cmd
    elif not default_project:
        sys.exit("No project on command line, no defaultproject in dbh.txt. Bailing.")
    else:
        print("No project defined, going with default {}".format(default_project))
        my_project = default_project

ran_project = False
ignore_til_next_break = False

with open(dbh) as file:
    line_count = 0
    for (line_count, line) in enumerate(file, 1):
        if ignore_til_next_break:
            if not line.strip():
                ignore_til_next_break = False
            continue
        if reading_operators:
            if not line.strip() or line.startswith(";"):
                reading_operators = False
                process_operators(read_file, temp_write, write_file)
                continue
            t = line.strip().split("\t")
            if line.startswith("default"):
                default_val = int(t[1])
                continue
            if line.startswith("ignore"):
                ignore_dict[t[1]] = True
                continue
            if line.startswith("first"):
                try:
                    firsts[t[2]] = int(t[1])
                    print("Take first", t[1], "of", t[2])
                except:
                    print("At line", line_count, "you need an integer in the second column.")
                    exit()
                continue
            if line.startswith("last"):
                try:
                    lasts[t[2]] = int(t[1])
                    print("Take last", t[1], "of", t[2])
                except:
                    print("At line", line_count, "you need an integer in the second column.")
                    exit()
                continue
        if "->" in line:
            if re.search("^l[0-9]+:", line, re.IGNORECASE):
                cl = cfg_level(line)
                if cl > copy_level:
                    print("Ignoring copy-level of", cl, "for", line.strip().lower())
                    ignore_til_next_break = True
                    continue
            line = re.sub("^l[0-9]+:", "", line.lower().strip())
            l = re.sub(":.*", "", line)
            if not i7.is_main_abb(l):
                print("!!!! WARNING {} is not a main abbreviation {}".format(l, i7.main_abb(l)))
                continue
            found_project = True
        if line.startswith(my_project) and "->" in line:
            ran_project = True
            firsts.clear()
            lasts.clear()
            y = re.sub("^[^:]*:", "", line.strip())
            x = y.split("->")
            read_file = x[0].strip()
            write_file = x[1].strip()
            print("Sending" ,x[0], "to", x[1])
            reading_operators = True

if found_project and not ran_project: print("OOPS did not try to run anything for project {}. Maybe you want a different abbreviation, or maybe nothing is defined in {}.".format(my_project, dbh))