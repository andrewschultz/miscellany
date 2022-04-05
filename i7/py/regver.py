#
# regver.py: verify that important tests are not commented out in reg-* files
#

import os
import sys
import glob
from collections import defaultdict

def check_one_file(my_file):
    commented_sections = defaultdict(int)
    includes = defaultdict(int)
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("* _"):
                commented_sections[line[2:].strip()] = line_count
                continue
            if line.startswith(">{include}"):
                my_entry = line[10:].strip()
                includes[line[10:].strip()] = line_count
    for x in commented_sections:
        if x not in includes:
            print(x, "is commented at line", commented_sections[x], "but is not in {include}s.")

file = ''
wild_card = "reg-*.txt"

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    cmd_count += 1

    file = sys.argv[1]
except:
    sys.exit("Need a file to work through.")

if os.path.exists(file):
    check_one_file(file)
    sys.exit()

reg-glob = glob.glob(wild_card)

for f in reg_glob:
    check_one_file(f)