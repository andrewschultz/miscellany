# itx.py
# open inform table extension file for the given project

from i7 import i7x
import os
import sys

print(i7x)

ext_dir = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz"

proj = ""

open_debug_tables = False
open_runtime_tables = True

for i in range(1, len(sys.argv)):
    if sys.argv[i] == 'dt' or sys.argv[i] == '-dt':
        open_debug_tables = True
        open_runtime_tables = False
    if sys.argv[i] == 'ta' or sys.argv[i] == '-ta':
        open_runtime_tables = True
        open_debug_tables = False
    if sys.argv[i] == 't2' or sys.argv[i] == '-t2':
        open_runtime_tables = True
        open_debug_tables = True
    if proj:
        print("Project defined twice, bailing")
        exit()
    proj = sys.argv[i]

if proj in i7x.keys():
    proj = i7x[proj]

pnh = proj.replace("-", " ")

if open_debug_tables:
    file = "{:s}/{:s} debug tables.i7x".format(ext_dir, pnh)
    if not os.ispath(file):
        print(file, "tables don't exist. Bailing.")
        exit()
    os.system("\"" + file + "\"")
    ran_any = True

if open_runtime_tables:
    file = "{:s}/{:s} tables.i7x".format(ext_dir, pnh)
    if not os.path.exists(file):
        print(file, "tables don't exist. Bailing.")
        exit()
    os.system("\"" + file + "\"")
    ran_any = True

if not ran_any:
    print("You managed to run no tests.")
