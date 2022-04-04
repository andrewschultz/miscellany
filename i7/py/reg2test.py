#reg2test
# this tests

from collections import defaultdict
import os
import re
import sys
import glob
import mytools as mt
import i7

ignorables = [ 'posf', 'score', 'thisalt' ]

verify_test = False
truncate_hyphens = True
to_print = defaultdict(str)

my_proj = i7.dir2proj()

wild_card = ''

try:
    wild_card = sys.argv[1]
except:
    print("You need an argument for the wildcard.")

def usage(my_header = 'USAGE FOR REG2TEST'):
    print(my_header)
    print("nh/hn/th/ht = truncate hyphens, h/hy/yh = don't truncate hyphens")
    sys.exit()

def verify_test_case(test_case_name):
    my_file = i7.hdr(my_proj, 'te')
    got_test_case = False
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if not line.startswith("test "):
                continue
            if not re.search(r"test +{} +with +".format(test_case_name), line):
                continue
            if '  ' in line:
                print("Warning extra space in line.")
                line = re.sub(" +", " ", line)
            expected_string = to_print[test_case_name]
            if not line.startswith(expected_string):
                print("WARNING different strings for", test_case_name)
                print("EXP:", expected_string)
                print("GOT:", line.strip())
            else:
                print("Successfully found proper test case for", test_case_name)
            return
    print("No test case {} found in {}.".format(test_case_name, os.path.basename(my_file)))

def i7_test_name(file_name):
    file_name = file_name.replace(".txt", "").replace("reg-", "")
    file_name = re.sub("^.*?-", "", file_name)
    if truncate_hyphens:
        file_name = file_name.replace('-', '')
    return file_name

def convert_reg2test(my_file):
    command_list = []
    test_out_name = i7_test_name(my_file)
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
    return('test {} with "{}".'.format(test_out_name, '/'.join(command_list)))

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in ( 'nh', 'hn', 'th', 'ht' ):
        truncate_hyphens = True
    elif arg in ( 'h', 'hy', 'yh' ):
        truncate_hyphens = False
    elif arg == 'v':
        verify_test = True
    elif len(arg) > 6:
        wild_card = arg
    else:
        usage(my_header = "illegal command {}".format(arg))
    cmd_count += 1

my_files = glob.glob("reg-*.txt")

if not wild_card:
    sys.exit("Need to define wild card.")

if not len(my_files):
    sys.exit("No reg-* files found in current/specified directory.")

for x in my_files:
    if wild_card not in x:
        continue
    to_print[i7_test_name(x)] = convert_reg2test(x)
    if verify_test:
        verify_test_case(i7_test_name(x))
    else:
        print(to_print[i7_test_name(x)] + '.')
