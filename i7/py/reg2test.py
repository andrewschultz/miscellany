#reg2test
# this tests

from collections import defaultdict
import os
import re
import sys
import glob
import mytools as mt
import i7
import colorama
import pyperclip

ignorables = [ 'posf', 'score', 'thisalt' ]

write_test_file = True
tests_to_clipboard = False
verify_test = False
truncate_hyphens = True
to_print = defaultdict(str)
write_out = defaultdict(tuple)

my_proj = i7.dir2proj()

wild_cards = []
failures = successes = 0
clip_string = ''

temp_out = "c:/writing/temp/reg2test-temp.txt"

def usage(my_header = 'USAGE FOR REG2TEST'):
    print(my_header)
    print("nh/hn/th/ht = truncate hyphens, h/hy/yh = don't truncate hyphens")
    sys.exit()

def match_any(my_string, my_wild_cards):
    for w in my_wild_cards:
        if w in my_string:
            return True
    return False

def write_new_test_cases():
    my_file = i7.hdr(my_proj, 'te')
    vals = [x[1] for x in write_out.values()]
    f = open(temp_out, "w")
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line_count in vals:
                print("Changing line", line_count)
                ary = [x for x in write_out if write_out[x][1] == line_count]
                f.write(to_print[ary[0]] + "\n")
                continue
            f.write(line)
    f.close()
    if compare_before_recopy:
        mt.wm(my_file, temp_out)
    copy(temp_out, my_file)
    os.remove(temp_out)
    sys.exit()

def verify_test_case(test_case_name):
    my_file = i7.hdr(my_proj, 'te')
    got_test_case = False
    global clip_string
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
                print(colorama.Fore.YELLOW + "WARNING different strings for {}.".format(test_case_name) + colorama.Style.RESET_ALL)
                print("EXP:", expected_string)
                print("GOT:", line.strip())
                mt.add_postopen(my_file, line_count)
                write_out[test_case_name] = (my_file, line_count)
                return False
            else:
                print(colorama.Fore.GREEN + "Successfully found proper test case for {}.".format(test_case_name) + colorama.Style.RESET_ALL)
            return True
    print(colorama.Fore.RED + "No test case {} found in {}.".format(test_case_name, os.path.basename(my_file)) + colorama.Style.RESET_ALL + " to add it, copy/paste below:")
    print(to_print[test_case_name])
    return False

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
            if cmd == 'undo':
                try:
                    command_list.pop()
                except:
                    print("Uh oh. Tried to UNDO when there was nothing to undo.")
                continue
            command_list.append(cmd)
    command_list = [ x for x in command_list if x not in ignorables ]
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
    elif arg == 'c':
        tests_to_clipboard = True
    elif arg == 'w':
        write_test_file = True
    elif arg in ( 'wc', 'cw' ):
        write_test_file = True
        compare_before_recopy = True
    elif arg.startswith('w='):
        wild_cards.extend(arg[2:].split(','))
    elif len(arg) > 6:
        wild_cards.extend(arg.split(','))
    else:
        usage(my_header = "illegal command {}".format(arg))
    cmd_count += 1

my_files = glob.glob("reg-*.txt")

if not len(wild_cards):
    sys.exit("Need to define wild card.")

if not len(my_files):
    sys.exit("No reg-* files found in current/specified directory.")

for x in my_files:
    if not match_any(x, wild_cards):
        continue
    this_test = i7_test_name(x)
    to_print[this_test] = convert_reg2test(x)
    if verify_test:
        temp = verify_test_case(this_test)
        if (not temp) and tests_to_clipboard:
            clip_string += to_print[this_test] + "\n"
        successes += temp
        failures += not temp
    else:
        print(to_print[this_test])

if verify_test:
    if failures:
        print("Failures", failures)
        print("Successes", successes)
    else:
        print("All tests succeeded!")

if clip_string:
    pyperclip.copy(clip_string)

if write_test_file:
    if len(write_out) == 0:
        sys.exit("Nothing to write to test file.")
    write_new_test_cases()

mt.post_open()
