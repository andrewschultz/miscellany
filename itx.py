# itx.py
# open inform table extension file for the given project

from i7 import i7x
import os
import sys
from collections import defaultdict

open_it = defaultdict(bool)

ext_dir = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz"

proj = ""

open_debug_tables = False
open_runtime_tables = True

ext_list = { 'dt': 'debug tables',
  'ta': 'tables',
  'nu': 'nudges',
  'mi': 'mistakes',
  'ra': 'random text'
}

for i in range(1, len(sys.argv)):
    if sys.argv[i] in ext_list.keys():
        open_it[sys.argv[i]] = True
        continue
    if proj:
        print("Project defined twice, bailing:", proj, "!!", sys.argv[i])
        exit()
    proj = sys.argv[i]

opens = open_it.keys()

if len(opens) == 0:
    opens = [ 'tables' ]

if proj in i7x.keys():
    proj = i7x[proj]

pnh = proj.replace("-", " ")

ran_any = 0

for x in opens:
    file = "{:s}/{:s} {:s}.i7x".format(ext_dir, pnh, ext_list[x])
    if not os.path.exists(file):
        print(file, "tables don't exist. Bailing.")
        exit()
    print("Opening", file)
    os.system("\"" + file + "\"")
    ran_any = ran_any + 1

if ran_any == 0:
    print("You managed to run no tests.")
elif ran_any > 1:
    print("If a file is already open, you won't see it kicked to the right hand tab. But you can alt-tab back.")
