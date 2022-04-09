#
# ttc.py
# tables to test cases in Inform 7
#
# requires auxiliary ttc.txt file
#
# can be run with no arguments or on a project
#

import glob
from collections import defaultdict
import mytools as mt
import i7
import sys
import re
import os

ttc_cfg = "c:/writing/scripts/ttc.txt"

class SimpleTestCase:
    found_yet = False
    suggested_text = 'None'

    def __init__(self, some_text = 'None'):
        self.suggested_text = some_text

class TablePicker:
    table_names = defaultdict(tuple) # each tuple is (array of column #'s, then test case)
    wild_cards = defaultdict(tuple) # each tuple is (array of column #'s, then test case)

    def __init__(self):
        pass

table_specs = defaultdict(lambda: defaultdict(TablePicker))

def get_cases(this_proj):
    return_dict = defaultdict(bool)
    for this_file in table_specs[this_proj]:
        print("Reading file", this_file, "for test cases...")
        in_table = False
        table_header_nethis_filet = False
        current_table = ''
        with open(this_file) as file:
            for (line_count, line) in enumerate (file, 1):
                if not in_table:
                    if not line.startswith("table of"):
                        continue
                    current_table = re.sub(" \[.*", "", line.strip())
                    current_table = re.sub(" +\(continued\).*", "", current_table)
                    if current_table in table_specs[this_proj][this_file].table_names:
                        in_table = True
                        table_header_next = True
                    continue
                if table_header_next == True:
                    table_header_next = False
                    continue
                if not line.strip():
                    in_table = False
                    continue
                columns = line.strip().split('\t')
                relevant_text_array = [columns[y] for y in table_specs[this_proj][this_file].table_names[current_table][0]]
                possible_text = '<NONE>' if table_specs[this_proj][this_file].table_names[current_table][1] == -20 else columns[table_specs[this_proj][this_file].table_names[current_table][1]].replace('"', '')
                test_case_name = "ttc-{}-{}".format(current_table, '-'.join(relevant_text_array)).replace(' ', '-').lower().replace('"', '').replace('--', '-')
                if test_case_name in return_dict:
                    print("Oops. We have a duplicate test case {} line {}.".format(line_count, test_case_name))
                else:
                    return_dict[test_case_name] = SimpleTestCase(possible_text)
    return return_dict

def verify_cases(this_proj, this_case_list, prefix = 'rbr'):
    dir_to_go = i7.proj2dir(this_proj)
    if dir_to_go != os.getcwd():
        print("Changing to", dir_to_go)
        os.chdir(dir_to_go)
    glob_string = prefix + "-*.txt"
    test_file_glob = glob.glob(glob_string)
    if len(test_file_glob) == 0:
        print("No test files found in", glob_string)
        return
    for my_rbr in test_file_glob:
        print("Checking test file", my_rbr, "to verify test cases are present...")
        with open(my_rbr) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("#+ttc"):
                    test_to_check = line[2:].lower().strip()
                    if test_to_check not in this_case_list:
                        print("Errant re-test case {} at {} line {}.".format(test_to_check, my_rbr, line_count))
                        continue
                    if this_case_list[test_to_check][0] == False:
                        print("Re-test before test case {} at {} line {}.".format(test_to_check, my_rbr, line_count))
                    continue
                if not line.startswith("#ttc"):
                    continue
                test_to_check = line[1:].lower().strip()
                if test_to_check not in this_case_list:
                    print("Errant test case {} at {} line {}.".format(test_to_check, my_rbr, line_count))
                elif test_to_check :
                    this_case_list[test_to_check].found_yet = True
    misses = [x for x in this_case_list if this_case_list[x].found_yet == False]
    if len(misses) == 0:
        print("No test cases were missed!")
    else:
        print("{} missed test cases:".format(len(misses)))
        for m in misses:
            print('#' + m)
            print(">(COMMAND HERE)")
            print(this_case_list[m].suggested_text)
    return

with open(ttc_cfg) as file:
    for (line_count, line) in enumerate (file, 1):
        if line.startswith('#'):
            continue
        if line.startswith(';'):
            break
        (prefix, data) = mt.cfg_data_split(line)
        if prefix == 'project':
            cur_proj = i7.long_name(data)
            if not cur_proj:
                print("WARNING bad project specified line {}: {}".format(line_count, data))
        elif prefix == 'file':
            cur_file = i7.hdr(cur_proj, data)
            if cur_file in table_specs:
                print("WARNING duplicate file {} at line {}".format(cur_file, line_count))
            else:
                table_specs[cur_proj][cur_file] = TablePicker()
        elif prefix == 'table':
            ary = data.split("\t")
            try:
                for tn in ary[0].split(','):
                    table_specs[cur_proj][cur_file].table_names[tn] = ( [int(x) for x in ary[1].split(',')], int(ary[2]))
            except:
                print(line_count, data)
                print("You may need 2 tabs above. 1st entry = tables, 2nd entry = columns that create the test case name, 3rd entry = rough text")
                print("Also, make sure entries 2/3 are integers.")
        else:
            print("Invalid data", prefix, "line", line_count)

my_proj = i7.dir2proj()

if my_proj not in table_specs:
    print(my_proj, "not in table_specs.")
    print("Here is which are:", ', '.join(sorted(table_specs)))
    sys.exit()

case_list = get_cases(my_proj)
case_test = verify_cases(my_proj, case_list)