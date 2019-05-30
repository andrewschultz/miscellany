#
# irp.py: Instead Rule Processor
#
# detects if we are in a project directory
# dsw = "doing something with"
# you can also adjust...
#

from collections import defaultdict
import os
import i7
import sys
import mytools as mt
import __main__ as main

adjusts = defaultdict(str)

max_lines = 0
min_lines = 0
rule_count_global = 0
insteads_ignored_global = 0

irp_file = "c:/writing/scripts/irp.txt"
instead_str = "instead of"

def usage():
    print("USAGE")
    print("=" * 50)
    print("all = print all adjusts and exit.")
    print("You can use a project abbreviation to go there, too.")
    print("e = edit {:s}, es = edit {:s}".format(irp_file, main.__file__))
    print("You can also have IRP ignore an instead rule by specifying no-irp in a comment.")
    print("You can also specify a maximum number of lines to print. mi=prefix for min.")
    exit()

def get_potential_adjusts():
    with open(irp_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            if "\t" not in line: sys.exit("Need tabs in {:s} line {:d}.".format(irp_file, line_count))
            ll = line.lower().strip().split("\t")
            adjusts[ll[0]] = ll[1]

def find_instead(q):
    in_instead = False
    out_string = ""
    insteads = 0
    insteads_ignored_local = 0
    insteads_ignored_global = 0
    temp_out_string = ""
    global rule_count_global
    with open(q) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.lower().startswith(instead_str) and not "[no-irp]" in line.lower():
                start_line_count = line_count
                in_instead = True
                temp_out_string = line
                continue
            if in_instead:
                temp_out_string += line
                if not line.strip():
                    in_instead = False
                    if max_lines != 0 and temp_out_string.count("\n") > max_lines:
                        insteads_ignored_local += 1
                        insteads_ignored_global += 1
                        continue
                    if min_lines != 0 and temp_out_string.count("\n") <= min_lines:
                        insteads_ignored_local += 1
                        insteads_ignored_global += 1
                        continue
                    insteads += 1
                    rule_count_global += 1
                    temp_out_string = "({:d}/{:d} L{:d}) ".format(insteads, rule_count_global, line_count) + temp_out_string
                    out_string += temp_out_string
                continue
    if out_string:
        print("====", q, "====")
        print(out_string)
        print(insteads, "total <{:s}> string for".format(instead_str.upper()), q)
    else: print("No <{:s}> string for".format(instead_str.upper()), q)
    if insteads_ignored_local: print("Insteads ignored:", insteads_ignored_local)

cmd_proj = ""

cmd_count = 1

get_potential_adjusts()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if i7.proj_exp(arg, False):
        if cmd_proj: sys.exit("Defined two command line projects. Bailing.")
        cmd_proj = i7.proj_exp(arg)
    elif arg == 'e': i7.npo(irp_file)
    elif arg == 'es': i7.npo(main.__file__)
    elif arg in adjusts:
        if arg[0] == "+": instead_str += " " + adjusts[arg]
        else: instead_str = adjusts[arg]
    elif arg == "all":
        for x in sorted(adjusts): print(x, "->", adjusts[x])
        exit()
    elif arg.isdigit():
        max_lines = int(arg)
    elif arg[:2] == 'mi':
        if arg[2:].isdigit():
            min_lines = int(arg)
        else:
            sys.exit(arg + " needs a number at the end to specify min_lines.")
    else:
        usage()
    cmd_count += 1

print("====Results from running", " ".join(sys.argv))
print()

default_project = "ailihphilia"
my_project = i7.dir2proj(os.getcwd())
if not my_project:
    print("Project directory not located. Using default", default_project)
    my_project = default_project

print("Looking for adjusts:", instead_str)

if cmd_proj: my_project = cmd_proj
else: print("Going with default project", my_project)

q = []

for j in i7.i7nonhdr.values():
    if j not in q: q.append(j)

for k in i7.i7f[my_project]:
    find_instead(k)

if insteads_ignored_global: print(insteads_ignored_global, "insteads ignored globally.")