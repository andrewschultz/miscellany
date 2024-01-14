#
# prc.py: processes regex test completed transcript
#
# how this is output is we show all commands
# if there is an error after a command we show that too, if not, we suppress it
# we also want to show the intro
#

import sys
import re
import os.path

this_turn = ''
sect_string = ''
found_err = 0
found_line_err = 0
last_cmd = 0

print_trailing_ok = False

def test_cases_of(test_file):
    ret_array = [ ]
    temp_string = ''
    with open(test_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(">"):
                ret_array.append(temp_string)
                temp_string = ''
            if not line.startswith("#"):
                continue
            if line[1:].startswith("ttc-") or line[1:].startswith("testcase-"):
                temp_string += line
    ret_array.append(temp_string)
    return ret_array

infile = ''
testfile = ''
outfile = ''

verbose = False
launch = False
track_test_cases = True

count = 1

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg == 'v': verbose = True
    elif arg == 't': print_trailing_ok = True
    elif arg == 'l': launch = True
    elif arg == 'c':
        track_test_cases = True
    elif arg in ( 'nc', 'cn', 'tn', 'nt' ):
        track_test_cases = False
    elif not infile:
        infile = sys.argv[count]
    elif not testfile:
        testfile = sys.argv[count]
    else:
        sys.exit("Already defined infile and outfile.")
    count = count + 1

if not infile:
    sys.exit("Must define infile. (Also, an outfile after that.)")

if not testfile:
    sys.exit("Must define testfile after infile of {}".format(infile))

if not os.path.exists(infile):
    sys.exit("Infile {} does not exist.".format(infile))

if not os.path.exists(testfile):
    sys.exit("Test file {} does not exist.".format(testfile))

outfile = re.sub('\\.txt', '-mod.txt', infile)

test_case_array = test_cases_of(testfile)

if os.path.isfile(infile) == 0:
    print(infile, 'doesn\'t exist.')
    sys.exit()

if verbose: print(infile, "to", outfile)

test_case_index = -1

current_section_string = ''
big_output_string = ''
last_output_string = ''
found_command = False

with open(infile) as f:
    for (line_count, line) in enumerate(f, 1):
        if line[:1] == '>':
            if found_line_err == 1:
                big_output_string += '----------------line {:d}-{:d}----------------\n'.format(last_cmd, line_count) + this_turn
                try:
                    if test_case_array[test_case_index]:
                        sect_string += "    !!!! CAUGHT FAILED TEST CASE: " + test_case_array[test_case_index]
                except:
                    pass
                found_err = 1
                found_line_err = 0
                moveBuffer = ''
                last_output_string = big_output_string
            elif not found_command:
                big_output_string = this_turn
            found_command = True
            last_cmd = line_count
            this_turn = ''
            test_case_index += 1
            big_output_string += line
        else:
            this_turn += line
        if "Run-time problem:" in line or "Programming error:" in line or "error: bad escape" in line:
            found_err = 1
            found_line_err = 1
        if re.search("^\\*\\*\\* <[a-zA-Z]+Check !?\"", line):
            found_err = 1
            found_line_err = 1

if found_line_err == 1:
    big_output_string += '----------------line {:d}-{:d}----------------\n'.format(last_cmd, line_count) + this_turn
    try:
        if test_case_array[test_case_index]:
            sect_string += "    !!!! CAUGHT FAILED TEST CASE: " + test_case_array[test_case_index]
    except:
        pass
    last_output_string = big_output_string
else:
    last_output_string += "\n==================cut off early==================\n"

if found_err:
    f1 = open(outfile, 'w')
    f1.write(last_output_string)
    f1.close()

if len(sys.argv) > 2 and sys.argv[2] == '-o':
    os.system(outfile)
