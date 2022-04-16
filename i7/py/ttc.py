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

open_after = True
show_suggested_file = show_suggested_syntax = show_suggested_text = True

def usage():
    print("sp to clean up spaces is the only argument now.")
    print("q = quiet, no debug info and v[0-2] = debug info level")
    sys.exit()

class SimpleTestCase:

    def __init__(self, some_text = 'None'):
        self.found_yet = False
        self.suggested_text = some_text

class TablePicker:

    def __init__(self):
        self.table_names = defaultdict(tuple) # each tuple is (array of column #'s, then test case)
        self.wild_cards = defaultdict(tuple) # each tuple is (array of column #'s, then test case)
        self.ignore = []
        self.ignore_wild = []
        self.stopper = ''

extra_project_files = defaultdict(list)
table_specs = defaultdict(lambda: defaultdict(TablePicker))
test_case_file_mapper_match = defaultdict(lambda: defaultdict(str))
test_case_file_mapper_regex = defaultdict(lambda: defaultdict(str))

verbose_level = 0

def wild_card_match(my_table, my_cards, to_lower = True):
    if to_lower:
        my_table = my_table.lower()
    for x in my_cards:
        if re.search(x, my_table):
            return x
    return False

def get_cases(this_proj):
    return_dict = defaultdict(bool)
    table_line_count = 0
    for this_file in table_specs[this_proj]:
        if verbose_level > 0:
            print("Reading file", this_file, "for test cases...")
        in_table = False
        current_table = ''
        cur_wild_card = ''
        read_table_data = False
        fb = os.path.basename(this_file)
        table_header_next = False
        stray_table = False
        table_lines_undecided = 0
        table_overall_undecided = 0
        with open(this_file) as file:
            for (line_count, line) in enumerate (file, 1):
                if table_specs[this_proj][this_file].stopper and table_specs[this_proj][this_file].stopper in line:
                    break
                if not in_table:
                    if not line.startswith("table of"):
                        continue
                    current_table = re.sub(" \[.*", "", line.strip())
                    current_table = re.sub(" +\(continued\).*", "", current_table)
                    in_table = True
                    cur_wild_card = wild_card_match(current_table, table_specs[this_proj][this_file].wild_cards)
                    ig_wild_card = wild_card_match(current_table, table_specs[this_proj][this_file].ignore_wild)
                    stray_table = False
                    if current_table in table_specs[this_proj][this_file].table_names:
                        table_header_next = True
                    elif cur_wild_card:
                        table_header_next = True
                    elif current_table in table_specs[this_proj][this_file].ignore:
                        pass
                    elif ig_wild_card:
                        pass
                    else:
                        stray_table = True
                        table_line_count = -1
                    continue
                if table_header_next == True:
                    table_header_next = False
                    table_line_count = 0
                    read_table_data = True
                    continue
                if not line.strip() or line.startswith('['):
                    if stray_table:
                        print("Stray table {} ({} line{}, {}-{}) should be put into test cases or ignore=.".format(current_table, table_line_count, mt.plur(table_line_count), line_count - table_line_count, line_count - 1))
                        table_overall_undecided += 1
                        table_lines_undecided += table_line_count
                    in_table = False
                    read_table_data = False
                    cur_wild_card = ''
                    continue
                table_line_count += 1
                if not read_table_data:
                    continue
                columns = line.strip().split('\t')
                if cur_wild_card:
                    ary_to_poke = table_specs[this_proj][this_file].wild_cards[cur_wild_card]
                else:
                    ary_to_poke = table_specs[this_proj][this_file].table_names[current_table]
                if ary_to_poke[0][0] == -1:
                    sub_test_case = "{}".format(table_line_count)
                else:
                    try:
                        relevant_text_array = [columns[y] for y in ary_to_poke[0]]
                        sub_test_case = '-'.join(relevant_text_array)
                    except:
                        sys.exit("Fatal error parsing columns: {} with {} total at line {} of {}.".format(ary_to_poke[0], len(columns), line_count, fb))
                if ary_to_poke[1] == -20:
                    possible_text = '<NONE>'
                else:
                    try:
                        relevant_text_array = [columns[y] for y in ary_to_poke[1]]
                        possible_text = '\n'.join(relevant_text_array).replace('"', '')
                    except:
                        possible_text = '<ERROR PARSING COLUMNS>'
                test_case_name = "ttc-{}-{}".format(current_table, sub_test_case).replace(' ', '-').lower().replace('"', '').replace('--', '-')
                if test_case_name in return_dict:
                    print("Oops. We have a duplicate test case {} line {}.".format(line_count, test_case_name))
                else:
                    return_dict[test_case_name] = SimpleTestCase(possible_text)
            if table_lines_undecided > 0:
                print("{} table line{} from {} table{} still to decide on in ttc.txt for {}.".format(table_lines_undecided, mt.plur(table_lines_undecided), table_overall_undecided, mt.plur(table_overall_undecided), fb))
    return return_dict

def change_dir_if_needed(new_dir = ''):
    if not new_dir:
        new_dir = i7.proj2dir(my_proj)
    if os.getcwd().lower() != new_dir.lower():
        print("Changing to", new_dir)
        os.chdir(new_dir)

def expected_file(my_case, this_proj):
    for q in test_case_file_mapper_match[this_proj]:
        q1 = q.replace(' ', '-')
        if q1 in my_case:
            temp = test_case_file_mapper_match[this_proj][q]
            temp = temp.replace('reg-', '').replace('.*', '')
            return temp
    for q in test_case_file_mapper_regex[this_proj]:
        q1 = q.replace(' ', '-')
        if re.search(q1, my_case):
            temp = test_case_file_mapper_regex[this_proj][q]
            temp = temp.replace('reg-', '').replace('.*', '')
            return temp
    return "<NO GUESS>"

def clean_up_spaces(this_proj, prefix = 'rbr'):
    change_dir_if_needed()
    glob_string = prefix + "-*.txt"
    test_file_glob = glob.glob(glob_string)
    if len(test_file_glob) == 0:
        print("No test files found in", glob_string)
        return
    for ext in extra_project_files[this_proj]:
        if os.path.exists(ext):
            test_file_glob.append(ext)
        else:
            print("Uh oh extra file", ext, "was not found.")
    out_file = "c:/writing/temp/ttc-mod-file.txt"
    for my_rbr in test_file_glob:
        any_changes = False
        out_string = ''
        with open(my_rbr) as file:
            for (line_count, line) in enumerate(file, 1):
                if not line.startswith('#'):
                    out_string += line
                    continue
                if not 'ttc' in line:
                    out_string += line
                    continue
                if 'rettc' in line:
                    line = line.replace('rettc', '+ttc')
                    any_changes = True
                if ' ' in line: # this may get more stringent if we allow more detailed comments
                    any_changes = True
                    line = line.replace(' ', '-')
                out_string += line
        if not any_changes:
            print(my_rbr, "ok")
            continue
        print("Comparing differences in", my_rbr)
        f = open(out_file, "w")
        f.write(out_string)
        f.close()
        mt.wm(my_rbr, out_file)
    sys.exit()

def similar_end_match(string1, string2):
    for x in range(0, min(len(string1), len(string2))):
        if string1[-x] != string2[-x]:
            break
    if not x or '-' not in string1[-x:]:
        return 0
    return x

def look_for_similars(my_test_case, all_test_cases):
    max_end_match = 0
    end_match_ary = []
    for x in all_test_cases:
        temp = similar_end_match(my_test_case, x)
        if temp == 0 or temp < max_end_match:
            continue
        if temp > max_end_match:
            end_match_ary = []
        end_match_ary.append(x)
        max_end_match = temp
    if len(end_match_ary):
        print("Possible match(es):", end_match_ary)

def verify_cases(this_proj, this_case_list, prefix = 'rbr'):
    change_dir_if_needed()
    glob_string = prefix + "-*.txt"
    test_file_glob = glob.glob(glob_string)
    if len(test_file_glob) == 0:
        print("No test files found in", glob_string)
        return
    for ext in extra_project_files[this_proj]:
        if os.path.exists(ext):
            test_file_glob.append(ext)
        else:
            print("Uh oh extra file", ext, "was not found.")
    for my_rbr in test_file_glob:
        if verbose_level > 0:
            print("Checking test file", my_rbr, "to verify test cases are present...")
        with open(my_rbr) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("#+ttc"):
                    test_to_check = line[2:].lower().strip()
                    if test_to_check not in this_case_list:
                        print("Errant re-test case {} at {} line {}.".format(test_to_check, my_rbr, line_count))
                        look_for_similars(test_to_check, this_case_list)
                        mt.add_postopen(my_rbr, line_count)
                        continue
                    if this_case_list[test_to_check].found_yet == False:
                        print("Re-test before test case {} at {} line {}.".format(test_to_check, my_rbr, line_count))
                        mt.add_postopen(my_rbr, line_count)
                    continue
                if not line.startswith("#ttc"):
                    continue
                test_to_check = line[1:].lower().strip()
                if test_to_check not in this_case_list:
                    print("Errant test case {} at {} line {}.".format(test_to_check, my_rbr, line_count))
                    mt.add_postopen(my_rbr, line_count)
                elif test_to_check :
                    this_case_list[test_to_check].found_yet = True
    misses = [x for x in this_case_list if this_case_list[x].found_yet == False]
    if len(misses) == 0:
        print("No test cases were missed!")
    else:
        print("{} missed test cases:".format(len(misses)))
        for m in misses:
            if show_suggested_file:
                print('@' + expected_file(m, this_proj))
            print('#' + m)
            if show_suggested_syntax:
                print(">VERB {}".format(m.replace('-', ' ')))
            if show_suggested_text:
                print(this_case_list[m].suggested_text)
    return

def valid_ttc(my_line):
    if not my_line.startswith('#'):
        return False
    my_line = my_line[1:]
    if my_line.startswith('+'):
        my_line = my_line[1:]
    return my_line.startswith('ttc')

def verify_case_placement(this_proj):
    mt.center("VERIFYING TEST CASE PLACEMENT IN REG FILES INHERITED FROM RBR FILES")
    change_dir_if_needed()
    reg_glob = glob.glob("reg-*.txt")
    case_verification = defaultdict(bool)
    total_unsorted = 0
    total_double_sorted_cases = 0
    total_double_sorted_lines = 0
    total_wrong_file = 0
    total_successful = 0
    total_tests_in_file = 0
    for file_name in reg_glob:
        unsorted = 0
        double_sorted_cases = 0
        double_sorted_lines = 0
        wrong_file = 0
        successful = 0
        tests_in_file = 0
        fb = os.path.basename(file_name)
        with open(file_name) as file:
            for (line_count, line) in enumerate (file, 1):
                if not valid_ttc(line):
                    continue
                line = line[1:].lower().strip()
                is_retest = False
                if line.startswith('+'):
                    is_retest = True
                match_array = []
                this_success = True
                for t in test_case_file_mapper_match[this_proj]:
                    t1 = t.replace(' ', '-')
                    if re.search(t, line):
                        if re.search(t, line):
                            match_array.append(t)
                        if not re.search(test_case_file_mapper_match[this_proj][t], fb):
                            print("Test case", line, "sorted into wrong file", fb, "should have wild card", test_case_file_mapper_match[this_proj][t])
                            wrong_file += 1
                            this_success = False
                for t in test_case_file_mapper_regex[this_proj]:
                    t1 = t.replace(' ', '-')
                    if not re.search(t1, line):
                        continue
                    if re.search(t1, line):
                        match_array.append(t1)
                    if not re.search(test_case_file_mapper_regex[this_proj][t], fb):
                        print("Test case", line, "sorted into wrong file", fb, "should have wild card", test_case_file_mapper_regex[this_proj][t])
                        wrong_file += 1
                        this_success = False
                total_matches = len(match_array)
                if total_matches == 0:
                    unsorted += 1
                    print("WARNING unsorted test case", line, "line", line_count)
                    this_success = False
                elif total_matches > 1:
                    double_sorted_cases += (total_matches == 2)
                    double_sorted_lines += 1
                    print("WARNING double sorted test case", line, "line", line_count, ' / '.join(match_array))
                    this_success = False
                else:
                    pass
                    #print(line, "works.") # uncomment if we want unquiet
                successful += this_success
                tests_in_file += 1
        if successful == tests_in_file:
            output_string = "NO ERRORS FOUND IN {}: {} successes.".format(fb, successful)
            if verbose_level == 1 and successful > 0:
                print(output_string)
            elif verbose_level == 2:
                print(output_string)
        else:
            print("{} unsorted={} Double sorted cases/lines={}/{} case-in-wrong-file={} successful={}".format(fb, unsorted, double_sorted_cases, double_sorted_lines, wrong_file, successful))
        total_unsorted += unsorted
        total_double_sorted_cases += double_sorted_cases
        total_double_sorted_lines += double_sorted_lines
        total_wrong_file += wrong_file
        total_successful += successful
        total_tests_in_file += tests_in_file
    if total_successful == total_tests_in_file:
        print("NO MISPLACED TEST CASES FOUND ANYWHERE IN GENERATED FILES: {} total successes.".format(total_successful))
    else:
        print("{} unsorted={} Double sorted cases/lines={}/{} case-in-wrong-file={} successful={}".format(fb, total_unsorted, total_double_sorted_cases, total_double_sorted_lines, total_wrong_file, total_successful))

cur_file = "<NONE>"
with open(ttc_cfg) as file:
    for (line_count, line) in enumerate (file, 1):
        if line.startswith('#'):
            continue
        if line.startswith(';'):
            break
        (prefix, data) = mt.cfg_data_split(line)
        if prefix == 'casemap':
            ary = data.split(",")
            for x in range(0, len(ary), 2):
                if ary[x] in test_case_file_mapper_match[cur_proj]:
                    print("Duplicate test case {} in {} at line {}.".format(x, cur_proj, line_count))
                    mt.add_postopen(ttc_cfg, line_count)
                else:
                    test_case_file_mapper_match[cur_proj][ary[x]] = ary[x+1]
        elif prefix == 'casemapr':
            ary = data.split(",")
            for x in range(0, len(ary), 2):
                if ary[x] in test_case_file_mapper_regex[cur_proj]:
                    print("Duplicate test case {} in {} at line {}.".format(x, cur_proj, line_count))
                    mt.add_postopen(ttc_cfg, line_count)
                else:
                    test_case_file_mapper_regex[cur_proj][ary[x]] = ary[x+1]
        elif prefix == 'extra':
            extra_project_files[cur_proj].extend(data.split(','))
        elif prefix == 'file':
            cur_file = i7.hdr(cur_proj, data)
            if cur_file in table_specs:
                print("WARNING duplicate file {} at line {}".format(cur_file, line_count))
                mt.add_postopen(ttc_cfg, line_count)
            else:
                table_specs[cur_proj][cur_file] = TablePicker()
        elif prefix == 'ignore':
            if data in table_specs[cur_proj][cur_file].ignore:
                print("WARNING duplicate ignore", cur_file, line_count, data)
                mt.add_postopen(ttc_cfg, line_count)
            else:
                table_specs[cur_proj][cur_file].ignore.append(data)
        elif prefix in ( 'ignorew', 'igw' ):
            if data in table_specs[cur_proj][cur_file].ignore_wild:
                print("WARNING duplicate ignore", cur_file, line_count, data)
                mt.add_postopen(ttc_cfg, line_count)
            else:
                table_specs[cur_proj][cur_file].ignore_wild.append(data)
        elif prefix == 'project':
            cur_proj = i7.long_name(data)
            if not cur_proj:
                print("WARNING bad project specified line {}: {}".format(line_count, data))
                mt.add_postopen(ttc_cfg, line_count)
        elif prefix == 'stopper':
            table_specs[cur_proj][cur_file].stopper = data
        elif prefix == 'table':
            ary = data.split("\t")
            try:
                for tn in ary[0].split(','):
                    table_specs[cur_proj][cur_file].table_names[tn] = ( [int(x) for x in ary[1].split(',')], [int(x) for x in ary[2].split(',')])
            except:
                print(line_count, data)
                print("You may need 2 tabs above. 1st entry = tables, 2nd entry = columns that create the test case name, 3rd entry = rough text")
                print("Also, make sure entries 2/3 are integers.")
        elif prefix in ( 'wc', 'wild', 'wildcard', 'wildcards' ):
            ary = data.split("\t")
            try:
                for tn in ary[0].split(','):
                    table_specs[cur_proj][cur_file].wild_cards[tn] = ( [int(x) for x in ary[1].split(',')], [int(x) for x in ary[2].split(',')])
            except:
                print(line_count, data)
                print("You may need 2 tabs above. 1st entry = tables, 2nd entry = columns that create the test case name, 3rd entry = rough text")
                print("Also, make sure entries 2/3 are integers.")
        else:
            print("Invalid prefix", prefix, "line", line_count, "overlooked data", data)

my_proj = i7.dir2proj()

cmd_count = 1

while cmd_count < len(sys.argv):
    (arg, num, valfound) = mt.parnum(sys.argv[cmd_count])
    cmd_count += 1
    if arg == 'sp':
        clean_up_spaces(my_proj)
        sys.exit()
    elif arg == 'v':
        if valfound:
            verbose_level = num
        else:
            verbose_level = 1
    elif arg in ( 'oa', 'ao' ):
        open_after = True
    elif arg in ( 'no', 'on' ):
        open_after = False
    elif arg in ( 'na', 'an' ):
        show_suggested_syntax = show_suggested_text = show_suggested_file = False
    elif mt.alfmatch(arg, 'nst') or arg in ( 'qt', 'tq' ):
        show_suggested_syntax = show_suggested_text = False
    elif arg in ( 'ns', 'sn' ):
        show_suggested_syntax = False
    elif arg in ( 'nt', 'tn' ):
        show_suggested_text = False
    elif arg == 'q':
        verbose_level = 0
    elif arg == '?':
        usage()
    else:
        print("BAD ARGUMENT", arg)
        usage()

if my_proj not in table_specs:
    print(my_proj, "not in table_specs.")
    print("Here is which are:", ', '.join(sorted(table_specs)))
    sys.exit()

case_list = get_cases(my_proj)
case_test = verify_cases(my_proj, case_list)
verify_case_placement(my_proj)

if open_after:
    mt.post_open()
