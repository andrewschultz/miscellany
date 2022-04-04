#reg2test
# this tests

import re
import sys
import glob

ignorables = [ 'score', 'thisalt' ]

try:
    wild_card = sys.argv[1]
except:
    print("You need an argument for the wildcard.")

def convert_reg2test(my_file):
    command_list = []
    test_out_name = my_file.replace(".txt", "").replace("reg-", "")
    test_out_name = re.sub("^.*?-", "", test_out_name)
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.startswith(">"):
                continue
            cmd = line[1:].strip()
            if cmd in ignorables:
                continue
            if cmd == 'undo':
                try:
                    command_list.pop()
                except:
                    print("Uh oh. Tried to UNDO when there was nothing to undo.")
                continue
            command_list.append(cmd)
    return('test {} with "{}"'.format(test_out_name, '/'.join(command_list)))

my_files = glob.glob("reg-*.txt")

for x in my_files:
    if wild_card not in x:
        continue
    to_print = convert_reg2test(x)
    print(to_print)
