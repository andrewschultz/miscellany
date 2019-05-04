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

rule_count_global = 0

irp_file = "c:/writing/scripts/irp.txt"
instead_str = "instead of"

def usage():
    print("USAGE")
    print("=" * 50)
    print("all = print all adjusts and exit.")
    print("You can use a project abbreviation to go there, too.")
    print("e = edit {:s}, es = edit {:s}".format(irp_file, main.__file__))
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
    global rule_count_global
    with open(q) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.lower().startswith(instead_str):
                insteads += 1
                rule_count_global += 1
                out_string += "({:d}/{:d} L{:d}) ".format(insteads, rule_count_global, line_count) + line
                in_instead = True
                continue
            if in_instead:
                out_string += line
                if not line.strip(): in_instead = False
                continue
    if out_string:
        print("====", q, "====")
        print(out_string)
        print(insteads, "total <{:s}> string for".format(instead_str.upper()), q)
    else: print("No <{:s}> string for".format(instead_str.upper()), q)

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
    else:
        usage()
    cmd_count += 1

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
