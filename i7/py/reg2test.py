#reg2test
# this tests

import re
import sys
import glob
import mytools as mt

ignorables = [ 'score', 'thisalt' ]

truncate_hyphens = True

try:
    wild_card = sys.argv[1]
except:
    print("You need an argument for the wildcard.")

def usage(my_header = 'USAGE FOR REG2TEST'):
    print(my_header)
    print("nh/hn/th/ht = truncate hyphens, h/hy/yh = don't truncate hyphens")
    sys.exit()

def convert_reg2test(my_file):
    command_list = []
    test_out_name = my_file.replace(".txt", "").replace("reg-", "")
    test_out_name = re.sub("^.*?-", "", test_out_name)
    if truncate_hyphens:
        test_out_name = test_out_name.replace('-', '')
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

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in ( 'nh', 'hn', 'th', 'ht' ):
        truncate_hyphens = True
    elif arg in ( 'h', 'hy', 'yh' ):
        truncate_hyphens = False
    elif len(arg) > 6:
        wild_card = arg
    else:
        usage(my_header = "illegal command {}".format(arg))
    cmd_count += 1

my_files = glob.glob("reg-*.txt")

for x in my_files:
    if wild_card not in x:
        continue
    to_print = convert_reg2test(x)
    print(to_print)
