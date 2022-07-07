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
import itertools
import colorama
from string import ascii_lowercase

rbr_globals = []
ttc_cfg = "c:/writing/scripts/ttc.txt"

global_error_note = False
open_after = True
show_suggested_file = show_suggested_syntax = show_suggested_text = True

custom_table_prefixes = defaultdict(list)

def common_mistakes():
    print("You may need to run rbr.py if you changed a branch file recently.")
    print("If a test case is not in an rbr file, you may want to add it to EXTRAS.")
    print("remember to add both a GENERATOR and CASEMAPR.")
    sys.exit()

def usage():
    print("sp to clean up spaces is one argument.")
    print("oa = open after, no = don't.")
    print("na = no to all except test cases, ns = no syntax, nt = no text")
    print("q = quiet, no debug info and v[0-2] = debug info level")
    print("?? = lists mistakes when everything seems right.")
    sys.exit()

class TestCaseGenerator:
    def __init__(self, match_string = '<unmatchable string>', exact_match = True, prefix_list = [ 'ttc' ], read_col_list = [0], print_col_list = [1]):
        self.match_string = match_string
        self.exact_match = exact_match
        self.prefix_list = prefix_list
        self.read_col_list = read_col_list
        self.print_col_list = print_col_list

class SimpleTestCase:

    def __init__(self, suggested_text = 'None', command_text = '', condition_text = '', expected_file = ''):
        self.found_yet = False
        self.suggested_text = suggested_text
        self.command_text = command_text
        self.condition_text = condition_text
        self.expected_file = expected_file

class TablePicker:

    def __init__(self):
        self.generators = []
        self.ignore = []
        self.ignore_wild = []
        self.stopper = ''
        self.untestables = []
        self.untestable_regexes = []
        self.okay_duplicates = defaultdict(int)
        self.okay_duplicate_regexes = []

odd_cases = defaultdict(list)
extra_project_files = defaultdict(list)
table_specs = defaultdict(lambda: defaultdict(TablePicker))
test_case_file_mapper_match = defaultdict(lambda: defaultdict(str))
test_case_file_mapper_regex = defaultdict(lambda: defaultdict(str))

matrices = defaultdict(list)

verbose_level = 0

def strip_end_comments(my_string):
    return re.sub("\[.*?\]$", "", my_string.strip())

def wild_card_match(my_string_to_match, my_cards, to_lower = True):
    if to_lower:
        my_string_to_match = my_string_to_match.lower()
    for x in my_cards:
        if re.search(x, my_string_to_match):
            return x
    return False

def tweak_text(column_entry):
    column_entry = strip_end_comments(column_entry.replace('/', '-').replace("'", ''))
    if '"' not in column_entry:
        return column_entry
    qary = column_entry.split('"')
    return qary[1]

def renumber(entry, my_dict):
    number_to_add = 2
    candidate_entry = entry + "-2"
    while candidate_entry in my_dict:
        number_to_add += 1
        candidate_entry = "{}-{}".format(entry, number_to_add)
    return candidate_entry

def mark_rbr_open(file_name, orig_line_count, comp_line):
    global rbr_globals
    if not rbr_globals:
        rbr_globals = glob.glob("rbr-*")
    for x in rbr_globals:
        with open(x) as file:
            for (line_count, line) in enumerate (file, 1):
                if line.lower() == comp_line.lower():
                    mt.add_open(x, line_count)
                    print("Found RBR line", line_count, comp_line.strip())
                    return
    mt.add_open(file_name, orig_line_count)
    return

def spacing_pass(my_line):
    if my_line.startswith("}}") or my_line.startswith("#"):
        return True
    return False

def starts_with_text(my_line, my_file):
    if not my_line.strip():
        return False
    if my_line.strip == "\\\\" and 'rbr' not in my_file:
        return True
    if my_line.startswith("/"):
        return True
    if my_line.startswith("["):
        return True
    if my_line.startswith('"'):
        return True
    if my_line.startswith("!"):
        return True
    if my_line.startswith(">"):
        return True
    if my_line.startswith("#") or my_line.startswith("@"):
        return False
    return my_line[0].isalpha()

def get_mistakes(this_proj):
    mistake_file = i7.hdr(this_proj, "mi")
    mistake_dict = defaultdict(SimpleTestCase)
    test_prefix = 'testcase-mistake-{}-'.format(this_proj)
    with open(mistake_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.startswith("understand") or not 'as a mistake' in line:
                continue
            prefix = re.sub("as a mistake.*", "", line.strip())
            suffix = re.sub(".*\(\"", "", line.strip())
            conditions = suffix
            conditions = re.sub(".*(when|while)", "", conditions).replace('.', '')
            conditions = re.sub("\[.*", "", conditions).strip()
            full_commands = '-'.join(prefix.split('"')[1::2])
            full_commands = full_commands.replace('[', '').replace(']', '').replace(' ', '-').replace('/', '-')
            test_case = test_prefix + full_commands
            suffix = suffix.replace('[b]', '').replace('[r]', '')
            suffix = re.sub("\".*", "", suffix)
            if test_case in mistake_dict:
                test_case = renumber(test_case, mistake_dict)
                if verbose_level > 0:
                    print(this_proj, "mistake file: renaming", re.sub(".[0-9]+$", "", test_case), "to", test_case)
            mistake_dict[test_case] = SimpleTestCase(suggested_text = suffix, command_text = full_commands.replace('-', ' '), condition_text = conditions, expected_file = 'mis')
    return mistake_dict

# this function pulls the potential test cases from the source code.
def get_cases(this_proj):
    global global_error_note
    return_dict = defaultdict(bool)
    table_line_count = 0
    any_dupes_yet = False
    for matrix in matrices[this_proj]:
        mult_matrix = matrix[0].split(",")
        for x in range(1, len(matrix)):
            mult_matrix = list(itertools.product(mult_matrix, [a.strip() for a in matrix[x].split(',')]))
        for f in mult_matrix:
            f0 = 'testcase-' + '-'.join(f)
            return_dict[f0] = SimpleTestCase("WHAT WE EXPECT FROM " + f0)
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
        tables_found = defaultdict(bool)
        dupe_orig = table_specs[this_proj][this_file].okay_duplicates.copy()
        these_table_gens = []
        with open(this_file) as file:
            for (line_count, line) in enumerate (file, 1):
                if table_specs[this_proj][this_file].stopper and table_specs[this_proj][this_file].stopper in line:
                    break
                if not in_table:
                    if not line.startswith("table of"):
                        continue
                    current_table = re.sub("[ \t]+\[.*", "", line.strip())
                    current_table = re.sub("[ \t]+\(continued\).*", "", current_table)
                    if wild_card_match(current_table, table_specs[this_proj][this_file].ignore_wild):
                        continue
                    if current_table in table_specs[this_proj][this_file].ignore:
                        continue
                    in_table = True
                    these_table_gens = []
                    for tg in table_specs[this_proj][this_file].generators:
                        if tg.exact_match:
                            if line.strip().lower() == tg.match_string:
                                these_table_gens.append(tg)
                        else:
                            if re.search(tg.match_string, line.strip().lower()):
                                these_table_gens.append(tg)
                    if len(these_table_gens):
                        table_header_next = True
                    else:
                        stray_table = True
                        read_table_data = False
                        table_line_count = -1
                    continue
                if table_header_next == True:
                    table_header_next = False
                    table_line_count = 0
                    read_table_data = True
                    continue
                if not line.strip() or line.startswith('['): # we have reached the end of the table.
                    if stray_table:
                        global_error_note = True
                        print(colorama.Fore.RED + "Stray table {} ({} line{}, {}-{}) should be put into test cases or ignore=.".format(current_table, table_line_count, mt.plur(table_line_count), line_count - table_line_count, line_count - 1) + colorama.Style.RESET_ALL)
                        table_overall_undecided += 1
                        table_lines_undecided += table_line_count
                        tables_found[current_table] = True
                    in_table = False
                    read_table_data = False
                    cur_wild_card = ''
                    continue
                table_line_count += 1
                if not read_table_data:
                    continue
                columns = line.strip().split('\t')
                for my_generator in these_table_gens:
                    subcase = ''
                    for x in my_generator.read_col_list:
                        if x == -1:
                            subcase += '-{}'.format(table_line_count)
                        else:
                            if columns[x].startswith('"'):
                                columns[x] = re.sub(r'".*', '', columns[x][1:])
                            subcase += '-{}'.format(columns[x]).replace('"', '')
                    if not subcase.replace('-', '') or subcase == '-a rule' or subcase == 'a thing':
                        continue
                    for p in my_generator.prefix_list:
                        test_case_name = (p + '-' + current_table + subcase).lower().replace('"', '').replace(' ', '-').replace('--', '-').replace('/', '-')
                        if test_case_name in return_dict and wild_card_match(test_case_name, table_specs[this_proj][this_file].okay_duplicate_regexes):
                            continue
                        possible_text = ''
                        for c in my_generator.print_col_list:
                            try:
                                temp_text = columns[c]
                                if temp_text.startswith('"'):
                                    temp_text = re.sub(r'".*', '', temp_text[1:])
                                possible_text += '-{}'.format(columns[c])
                            except:
                                possible_text += '---'
                        possible_text = possible_text[1:]
                        if test_case_name in table_specs[this_proj][this_file].okay_duplicates:
                            table_specs[this_proj][this_file].okay_duplicates[test_case_name] -= 1
                            if table_specs[this_proj][this_file].okay_duplicates[test_case_name] < 0:
                                print("Potential error: too many duplicate listings for {} in {}. Check okdup statement.".format(test_case_name, this_file))
                            continue
                        if test_case_name in return_dict:
                            print("POTENTIAL ERROR: source code provided duplicate test case/column entry {} at line {} of {}. Use okdup/okdupr if this is correct.".format(test_case_name, line_count, fb))
                        elif test_case_name in table_specs[this_proj][this_file].untestables:
                            if verbose_level > 0:
                                print("UNTESTABLE ABSOLUTE", test_case_name)
                        elif wild_card_match(test_case_name, table_specs[this_proj][this_file].untestable_regexes):
                            if verbose_level > 0:
                                print("UNTESTABLE REGEX", test_case_name)
                        else:
                            if possible_text.startswith('"') and possible_text.endswith('"'):
                                possible_text = possible_text[1:-1]
                            return_dict[test_case_name] = SimpleTestCase(possible_text)
            if table_lines_undecided > 0:
                if table_overall_undecided != len(tables_found):
                    unique_tables = "/{}".format(len(tables_found))
                else:
                    unique_tables = ''
                print("{} table line{} from {}{} table{} still to decide on in ttc.txt for {}.".format(table_lines_undecided, mt.plur(table_lines_undecided), table_overall_undecided, unique_tables, mt.plur(table_overall_undecided), fb))
        for dupe in table_specs[this_proj][this_file].okay_duplicates:
            if table_specs[this_proj][this_file].okay_duplicates[dupe] == 0:
                continue
            if not any_dupes_yet:
                any_dupes_yet = True
                print(colorama.Fore.YELLOW + "NOTE: we count the number of duplicates, not the total number of occurrences." + colorama.Style.RESET_ALL)
            print("Too {} duplicates for entry {}: off by {}, should have {}.".format('many' if table_specs[this_proj][this_file].okay_duplicates[dupe] < 0 else 'few', dupe, abs(table_specs[this_proj][this_file].okay_duplicates[dupe]), dupe_orig[dupe]))
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
        last_line_text = False
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

def base_of(my_str):
    if my_str.startswith("#+"):
        return my_str[2:]
    if my_str.startswith("#"):
        return my_str[1:]
    return my_str

def is_ttc_comment(my_str):
    return my_str.startswith("#ttc") or my_str.startswith("#+ttc") or my_str.startswith("#testcase") or my_str.startswith("#+testcase")

def rbr_cases_of(my_line):
    if is_ttc_comment(my_line):
        return [ my_line.strip().lower() ]
    if not my_line.startswith("{"):
        return []
    my_line = re.sub("^\{.*?\}", "", my_line.strip())
    return [x for x in re.split("\\\\", my_line) if is_ttc_comment(x)]

# this verifies test cases are in rbr* or reg* files at least once, following ttc = first time, +ttc = those after.
def verify_cases(this_proj, this_case_list, prefix = 'rbr'):
    global global_error_note
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
        base = os.path.basename(my_rbr)
        flag_spacing = base.startswith("rbr-") or base.startswith("reg-")
        last_line_text = False
        with open(my_rbr) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith("+#"):
                    print("BACKWARDS RETEST CASE {} line {}: {}".format(base, line_count, line.strip()))
                    mt.add_postopen(my_rbr, line_count)
                if line.startswith("*"):
                    can_write_testcases = True
                if not can_write_testcases and valid_ttc(line, this_proj):
                    tests_in_header += 1
                    if pre_asterisk_warn:
                        continue
                    pre_asterisk_warn = True
                    global_error_note = True
                    print("WARNING test case still in header for copy/pasting {} line {}.".format(base, line_count))
                    mt.add_postopen(my_rbr, line_count, priority=3) # high priority in reality but low priority since we know where the offending lines are: at the start of the file!
                    continue
                if flag_spacing:
                    if last_line_text and valid_ttc(line, this_proj):
                        global_error_note = True
                        print("    Spacing issue {} line {}.".format(base, line_count))
                        mt.add_postopen(my_rbr, line_count)
                    if not spacing_pass(line):
                        last_line_text = starts_with_text(line, base)
                my_cases = rbr_cases_of(line)
                for this_case in my_cases:
                    raw_case = base_of(this_case)
                    if raw_case not in this_case_list:
                        global_error_note = True
                        print("Errant {} {}test case at {} line {}.".format(raw_case, 're-' if '+' in this_case else '', base, line_count))
                        look_for_similars(raw_case, this_case_list)
                        mt.add_postopen(my_rbr, line_count)
                        continue
                    if this_case_list[raw_case].found_yet == False and this_case.startswith('#+'):
                        global_error_note = True
                        print("Re-test before test case {} at {} line {}.".format(raw_case, base, line_count))
                        this_case_list[raw_case].found_yet = True
                        mt.add_postopen(my_rbr, line_count)
                    if this_case_list[raw_case].found_yet == True and not this_case.startswith('#+'):
                        global_error_note = True
                        print("Duplicate test case {} at {} line {} must be acknowledged with preceding +.".format(raw_case, base, line_count))
                        mt.add_postopen(my_rbr, line_count)
                    if raw_case not in this_case_list:
                        global_error_note = True
                        print("Errant test case {} at {} line {}.".format(raw_case, base, line_count))
                        mt.add_postopen(my_rbr, line_count)
                    elif raw_case:
                        this_case_list[raw_case].found_yet = True
    misses = [x for x in this_case_list if this_case_list[x].found_yet == False]
    if len(misses) == 0:
        print("No test cases were missed!")
    else:
        print("missed test case{} listed below:".format(mt.plur(len(misses))))
        global_error_note = True
        for m in sorted(misses):
            if show_suggested_file:
                if this_case_list[m].expected_file:
                    print('@' + this_case_list[m].expected_file)
                else:
                    print('@' + expected_file(m, this_proj))
            print('#' + m)
            if show_suggested_syntax:
                if this_case_list[m].command_text:
                    print(">{}".format(this_case_list[m].command_text))
                else:
                    print(">VERB {}".format(m.replace('-', ' ')))
            if show_suggested_text:
                print(this_case_list[m].suggested_text)
                if this_case_list[m].condition_text:
                    print("#condition: {}".format(this_case_list[m].condition_text))
        if len(misses) > 0:
            print("{} missed test case{} seen above.".format(len(misses), mt.plur(len(misses))))
    return

def valid_ttc(my_line, my_proj=''):
    if not my_line.startswith('#'):
        return False
    my_line = my_line[1:]
    if my_line.startswith('+'):
        my_line = my_line[1:]
    if my_proj:
        for x in odd_cases[my_proj]:
            if my_line.startswith(x):
                return True
    return my_line.startswith('ttc-') or my_line.startswith('testcase-')

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
                line_mod = line[1:].lower().strip()
                is_retest = False
                if line_mod.startswith('+'):
                    is_retest = True
                match_array = []
                this_success = True
                for t in test_case_file_mapper_match[this_proj]:
                    t1 = t.replace(' ', '-')
                    if re.search(t, line_mod):
                        if re.search(t, line_mod):
                            match_array.append(t)
                        if not re.search(test_case_file_mapper_match[this_proj][t], fb):
                            print("Test case", line_mod, "sorted into wrong file", fb, "should have wild card", test_case_file_mapper_match[this_proj][t])
                            mark_rbr_open(file_name, line_count, line)
                            wrong_file += 1
                            this_success = False
                for t in test_case_file_mapper_regex[this_proj]:
                    t1 = t.replace(' ', '-')
                    if not re.search(t1, line_mod):
                        continue
                    if re.search(t1, line_mod):
                        match_array.append(t1)
                    if not re.search(test_case_file_mapper_regex[this_proj][t], fb):
                        print("Test case", line_mod, "sorted into wrong file", fb, "should have regex", test_case_file_mapper_regex[this_proj][t])
                        mark_rbr_open(file_name, line_count, line)
                        wrong_file += 1
                        this_success = False
                total_matches = len(match_array)
                if total_matches == 0:
                    unsorted += 1
                    print("WARNING ({}) test case in reg* file pool has no assigned file-pattern: {} {} {}".format('valid' if line_mod in case_list else 'invalid', fb, line_count, line_mod))
                    mark_rbr_open(file_name, line_count, line)
                    this_success = False
                elif total_matches > 1:
                    double_sorted_cases += (total_matches == 2)
                    double_sorted_lines += 1
                    print("WARNING test case potentially sorted into two files:", line_mod, "line_mod", line_count, ' / '.join(match_array))
                    mark_rbr_open(file_name, line_count, line)
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
        print(colorama.Fore.GREEN + "NO MISPLACED TEST CASES FOUND ANYWHERE IN GENERATED FILES: {} total successes.".format(total_successful) + colorama.Style.RESET_ALL)
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
        if len(mt.mt_default_dict) and '$' in line:
            old_data = data
            data = mt.string_expand(data, mt.mt_default_dict, force_lower = True)
        if prefix.startswith("$"):
            mt.mt_default_dict[prefix[1:]] = data
        elif prefix == 'casemap':
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
        elif prefix == 'custpref':
            ary = data.split('\t')
            custom_table_prefixes[ary[0]] = ary[1].split(',')
            print(ary[0], custom_table_prefixes[ary[0]])
        elif prefix == 'extra':
            extra_project_files[cur_proj].extend([x.strip() for x in data.split(',')])
        elif prefix == 'file':
            cur_file = i7.hdr(cur_proj, data)
            if cur_file in table_specs:
                print("WARNING duplicate file {} at line {}".format(cur_file, line_count))
                mt.add_postopen(ttc_cfg, line_count)
            else:
                table_specs[cur_proj][cur_file] = TablePicker()
        elif prefix == 'ignore':
            ary = data.split(',')
            for d in ary:
                if data in table_specs[cur_proj][cur_file].ignore:
                    print("WARNING duplicate ignore", cur_file, line_count, d)
                    mt.add_postopen(ttc_cfg, line_count)
                else:
                    table_specs[cur_proj][cur_file].ignore.append(d)
        elif prefix in ( 'ignorew', 'igw' ):
            if data in table_specs[cur_proj][cur_file].ignore_wild:
                print("WARNING duplicate ignore", cur_file, line_count, data)
                mt.add_postopen(ttc_cfg, line_count)
            else:
                table_specs[cur_proj][cur_file].ignore_wild.append(data)
        elif prefix == 'matrix':
            matrices[cur_proj].append(data.split("\t"))
        elif prefix == 'okdup':
            ary = data.split(",")
            if not cur_file:
                print("WARNING: you probably want to put an OKDUP in a specific file.")
            for a in ary:
                if '~' not in a:
                    table_specs[cur_proj][cur_file].okay_duplicates[a] = 1
                else:
                    a2 = a.split("~")
                    table_specs[cur_proj][cur_file].okay_duplicates[a2[0]] = int(a2[1])
        elif prefix == 'okdupr':
            if not cur_file:
                print("WARNING: you probably want to put an OKDUP in a specific file.")
            table_specs[cur_proj][cur_file].okay_duplicate_regexes.append(data)
        elif prefix in ( 'oddcase', 'oddcases' ):
            odd_cases[cur_proj].extend(data.split(','))
        elif prefix == 'project':
            cur_proj = i7.long_name(data)
            if not cur_proj:
                print("WARNING bad project specified line {}: {}".format(line_count, data))
                mt.add_postopen(ttc_cfg, line_count)
        elif prefix == 'stopper':
            table_specs[cur_proj][cur_file].stopper = data
        elif prefix in ('gen', 'generator', 'table'):
            ary = data.split("\t")
            try:
                my_prefixes = ary[3].split(',') if len(ary) > 3 else [ 'ttc' ]
                this_generator = TestCaseGenerator(match_string = ary[0], exact_match = 'table' in prefix, read_col_list = [int(x) for x in ary[1].split(',')], print_col_list = [int(x) for x in ary[2].split(',')], prefix_list = my_prefixes)
                table_specs[cur_proj][cur_file].generators.append(this_generator)
            except:
                print("Exception reading CFG", line_count, data)
                print("You *may* need 2 tabs above. 1st entry = tables, 2nd entry = columns that create the test case name, 3rd entry = rough text")
                print("Also, make sure entries 2/3 are integers.")
        elif prefix in ( 'untestable', 'untestables' ):
            ary = data.split(",")
            for a in ary:
                if a.startswith('#'):
                    print("Stripping # from untestable at line", line_count)
                    a = a[1:]
                    mt.add_postopen(ttc_cfg, line_count, priority = 4)
                if a in table_specs[cur_proj][cur_file].untestables:
                    print("Duplicate untestable", a)
                    continue
                table_specs[cur_proj][cur_file].untestables.append(a)
        elif prefix in ( 'untestabler' ):
            ary = data.split(",")
            for a in ary:
                if a.startswith('#'):
                    print("Stripping # from untestable at line", line_count)
                    a = a[1:]
                    mt.add_postopen(ttc_cfg, line_count, priority = 4)
                if a in table_specs[cur_proj][cur_file].untestable_regexes:
                    print("Duplicate regex", a, cur_proj, line_count)
                    continue
                table_specs[cur_proj][cur_file].untestable_regexes.append(a)
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
    elif arg == '??':
        usage()
    else:
        print("BAD ARGUMENT", arg)
        usage()

if my_proj not in table_specs:
    print("{} not in table_specs.".format('<BLANK PROJECT>' if not my_proj else my_proj))
    print("Here is which are:", ', '.join(sorted(table_specs)))
    sys.exit()

case_list = get_cases(my_proj)
case_list.update(get_mistakes(my_proj))
case_test = verify_cases(my_proj, case_list)
verify_case_placement(my_proj)

if global_error_note: print("?? shows common errors, if the results weren't what you expected.")

if open_after:
    mt.post_open()
