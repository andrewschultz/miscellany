#
# ttc.py
# track test cases in Inform 7
#
# originally "tables to test cases" but non-table test cases can be tracked
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
from shutil import copy
from filecmp import cmp

rbr_globals = []

ttc_base = "ttc.txt"
ttc_dir = "c:/Users/Andrew/Documents/github/configs/ttc"

ttc_cfg = os.path.normpath(os.path.join(ttc_dir, ttc_base))

got_cfg_errors = False

alphabetize = False
global_error_note = False
open_after = True
show_suggested_file = show_suggested_syntax = show_suggested_text = True

cfg_error_bail = True

collapse_extra_dashes = True

duplicate_test_force = duplicate_test_prevent = False

testcase_wild_card = testcase_wild_card_negative = ''

custom_table_prefixes = defaultdict(list)
global_stray_table_org = defaultdict(list)
ignorable_rule_lines = defaultdict(list)

say_equivalents = defaultdict(str)

okay_duplicates = 0

blank_stuff = [ 'a rule', 'a topic', 'a text' ]
valid_fork_starts = [ 'unless ', 'if ', 'else', 'repeat', 'while' ]

FIND_ABSOLUTE_CASE = 0
FIND_REGEX_CASE = 1
IGNORE_ABSOLUTE_CASE = 2
IGNORE_REGEX_CASE = 3

def common_mistakes():
    print("You may need to run rbr.py if you changed a branch file recently.")
    print("If a test case is not in an rbr file, you may want to add it to EXTRAS.")
    print("remember to add both a GENERATOR and CASEMAPR.")
    sys.exit()

def usage():
    print("sp to clean up spaces is one argument.")
    print("oa = open after, no = don't.")
    print("na = no to all except test cases, ns = no syntax, nt = no text.")
    print("ncd = don't collapse extra dashes.")
    print("q = quiet, no debug info and v[0-2] = debug info level.")
    print("/ = open test file for this project, /m = open main file /proj = open proj's test file")
    print("?? = lists mistakes when everything seems right.")
    sys.exit()

class TestCaseGenerator:
    def __init__(self, match_string = '<unmatchable string>', exact_match = True, prefix_list = [ 'ttc' ], subcase_name_format = [0], print_from_col = '', print_absolute = '', command_generator = [], fixed_command = '', regex_to_check = '', ignore_blank_print = False):
        self.match_string = match_string
        self.exact_match = exact_match
        self.prefix_list = prefix_list
        self.subcase_name_format = subcase_name_format
        self.print_from_col = print_from_col
        self.print_absolute = print_absolute
        self.command_generator = command_generator
        self.fixed_command = fixed_command
        self.regex_to_check = regex_to_check
        self.ignore_blank_print = ignore_blank_print

class SimpleTestCase:

    def __init__(self, suggested_text = 'No suggested text', command_text = '', condition_text = '', expected_file = '', first_file_found = '<NONE>', first_line_found = 0):
        self.found_yet = False
        self.suggested_text = suggested_text
        self.command_text = command_text
        self.condition_text = condition_text
        self.expected_file = expected_file
        self.first_file_found = first_file_found
        self.first_line_found = first_line_found

class ValuesPicker:

    def __init__(self, command_template = 'CMD', expected_file = 'HINT', expected_text = 'TEXT'):
        self.command_template = command_template
        self.expected_file = expected_file
        self.expected_text = expected_text

class RulesPicker:

    def __init__(self):
        self.valid_hint_regexes = defaultdict(list)
        self.regex_to_abbr = defaultdict(str)
        self.rules_on_lines = []
        self.rules_off_lines = []
        self.rules_on_found = defaultdict(bool)
        self.rules_off_found = defaultdict(bool)

class TablePicker:

    def __init__(self):
        self.generators = []
        self.ignore = []
        self.ignore_wild = []
        self.stopper = ''
        self.okay_duplicate_counter = defaultdict(int)
        self.okay_duplicate_regexes = []
        self.absolute_string = []

class MatrixSpecs:

    def __init__(self, matrix = [], out_file = '<FILE>', out_verb = 'FILL IN VERB', out_text = 'FILL IN TEXT', can_repeat = True):
        self.matrix = matrix
        self.out_file = out_file
        self.out_verb = out_verb
        self.out_text = out_text
        self.can_repeat = can_repeat

class TestCaseMapper:

    def __init__(self):
        self.mappers_in_order = []
        self.text_and_type_map = defaultdict(tuple)

class FlexStringMatcher:

    FLEXMATCH_UNDEFINED = -1
    FLEXMATCH_ANYWHERE = 0
    FLEXMATCH_STARTSWITH = 1
    FLEXMATCH_BRANCH = 2
    FLEXMATCH_REGEX = 3

    def __init__(self, string_to_parse):
        self.case_search_type = self.FLEXMATCH_UNDEFINED
        self.main_string_to_parse = ''
        self.branch_string_to_parse = ''
        self.end_string_to_parse = ''

        if string_to_parse.startswith('s:'):
            self.main_string_to_parse = string_to_parse[2:]
            self.case_search_type = self.FLEXMATCH_STARTSWITH
        elif string_to_parse.startswith('r:'):
            self.main_string_to_parse = string_to_parse[2:]
            self.case_search_type = self.FLEXMATCH_REGEX
        elif string_to_parse.startswith('b:'):
            self.main_string_to_parse = string_to_parse[2:]
            self.case_search_type = self.FLEXMATCH_BRANCH
        elif '/' in string_to_parse:
            self.case_search_type = self.FLEXMATCH_BRANCH
            mt.warn("Put b: before string {} to specify a branch string.".format(string_to_parse))
        else:
            self.case_search_type = self.FLEXMATCH_ANYWHERE

        if self.case_search_type == self.FLEXMATCH_BRANCH:
            ary = string_to_parse.split('/')
            if len(ary) < 3:
                mt.warn("A flexmatch string has only 2 slashes: {}".format(string_to_parse))
            self.main_string_to_parse = ary[0]
            self.branch_strings_to_parse = ary[1:-1] if len(ary) > 2 else [ 'INVALID' ]
            self.end_string_to_parse = ary[-1]
            return

        self.main_string_to_parse = string_to_parse

        if self.case_search_type == self.FLEXMATCH_REGEX:
            check_suspicious_regex(self.main_string_to_parse, 0)
        else:
            check_regex_in_absolute(self.main_string_to_parse, 0)

    def got_match(self, string_to_match):
        if self.case_search_type == self.FLEXMATCH_STARTSWITH:
            return string_to_match.startswith(self.main_string)
        elif self.case_search_type == self.FLEXMATCH_ANYWHERE:
            return self.main_string_to_parse in string_to_match
        elif self.case_search_type == self.FLEXMATCH_REGEX:
            return re.search(self.main_string_to_parse, string_to_match)
        elif self.case_search_type == self.FLEXMATCH_BRANCH:
            for b in self.branch_strings_to_parse:
                x = self.main_string_to_parse + b + self.end_string_to_parse
                if x == string_to_match:
                    return True
            return False
        mt.warn("Unidentified Flexmatch type for {}".format(self.main_string_to_parse))

class TestCaseToFileMapper:

    GOODMATCH = 1
    NOMATCH = 0
    BADMATCH = -1

    def __init__(self, data):
        ary = data.split(',')
        self.case_from = FlexStringMatcher(ary[0])
        self.file_to = FlexStringMatcher(ary[1])

    def case_file_match(self, this_case, this_file):
        if self.case_from.got_match(this_case):
            if self.file_to.got_match(this_file):
                return GOODMATCH
            else:
                return BADMATCH
        return NOMATCH

class UntestableCaseMapper:

    def __init__(self, prefix, data, line_count = 0, this_cfg = 'no file specified'):
        self.the_case = FlexStringMatcher(data)

    def untestable_match(self, this_case):
        return self.the_case.got_match(this_case)


odd_cases = defaultdict(list)
extra_project_files = defaultdict(list)
value_specs = defaultdict(lambda: defaultdict(lambda: defaultdict(ValuesPicker)))
rules_specs = defaultdict(lambda: defaultdict(RulesPicker))
table_specs = defaultdict(lambda: defaultdict(TablePicker))
file_abbrev_maps = defaultdict(lambda: defaultdict(str))

#to delete eventually
case_mapper = defaultdict(TestCaseMapper)

case_to_file_mapper = defaultdict(lambda: defaultdict(CaseToFileMapper))
untestable_case_mapper = defaultdict(list)

test_case_matrices = defaultdict(list)

verbose_level = 0

def strip_end_comments(my_string):
    return re.sub("\[.*?\]$", "", my_string.strip())

def quote_flatten(my_val):
    if my_val.startswith('"') and my_val.endswith('"'):
        return my_val[1:-1]
    if my_val == 'a rule' or my_val == 'a thing':
        return '--'
    return my_val

def test_case_of(x):
    temp = x.lower().replace('"', '').replace(' ', '-').replace('|', '-').replace('/', '-').replace('(', '').replace(')', '')
    return re.sub('--+', '-', temp)

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

def has_meaningful_content(my_string):
    my_string = re.sub("\[.*?\]$", "", my_string).strip()
    if not my_string.replace('-', ''):
        return False
    if my_string in blank_stuff:
        return False
    return True

def renumber(entry, my_dict):
    number_to_add = 2
    candidate_entry = entry + "-2"
    while candidate_entry in my_dict:
        number_to_add += 1
        candidate_entry = "{}-{}".format(entry, number_to_add)
    return candidate_entry

def text_from_row_values(template_string, header_strings, row_strings):
    retval = template_string
    for count in range (0, len(header_strings)):
        h0 = "{" + header_strings[count] + "}"
        retval = retval.replace(h0, row_strings[count])
    if '`' in template_string:
        for count in range (0, len(header_strings)):
            h0 = "{" + header_strings[count] + "`}"
            retval = retval.replace(h0, re.sub("\|.*", "", row_strings[count]))
    retval = retval.replace('\\n', '\n')
    return retval

def testcase_match(my_verb = ''):
    possible_verbs = [ 'n', 's', 'e', 'w', 'undo' ]
    guesses = defaultdict(str)
    global rbr_globals
    if not rbr_globals:
        rbr_globals = glob.glob("rbr-*.txt")
    last_line = ''
    line_start = '>' + (my_verb if my_verb else 'general command')
    need_case = got_case = 0
    for x in rbr_globals:
        with open(x) as file:
            for (line_count, line) in enumerate (file, 1):
                if not line.startswith(">"):
                    last_line = line
                    continue
                ls = line[1:].strip()
                if my_verb:
                    if not ls.startswith(my_verb):
                        last_line = line
                        continue
                else:
                    if ls in possible_verbs:
                        last_line = line
                        continue
                if not retest_agnostic_starts(last_line, include_null = True):
                    mt.warn("Line {} has {} without test case above it.".format(line_count, ls))
                    if ls in guesses:
                        mt.warn("    SUGGESTION: {}".format(guesses[ls]))
                    mt.add_post_open(x, line_count)
                    need_case += 1
                elif ls not in guesses:
                    guesses[ls] = last_line.strip()
                    got_case += 1
                last_line = line
    if need_case + got_case == 0:
        mt.warn("No test cases for >{} found!".format(line_start))
    elif need_case > 0:
        mt.fail("{} successful, {} need test cases for {}.".format(got_case, need_case, line_start))
    else:
        mt.okay("Every {} has a test case!".format(line_start))
    mt.post_open()
    sys.exit()

def mark_rbr_open(file_name, orig_line_count, comp_line):
    global rbr_globals
    if not rbr_globals:
        rbr_globals = glob.glob("rbr-*.txt")
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

def check_regex_in_absolute(my_data, my_line_count = 0, my_file = '<UNKNOWN>'):
    if '*' in my_data or '^' in my_data or '$' in my_data:
        print("Possible regex appears in absolute definition {} at line {}.".format(my_data, my_line_count))

def check_suspicious_regex(my_regex, my_line_count = 0, my_file = '<UNKNOWN>'):
    if '-*' in my_regex:
        print("-* in regex {} line {} may result in a too-greedy regex. Maybe change to -.*".format(my_file, my_line_count))
        mt.add_post(my_file, my_line_count)

def inform_extension_file(file_abbrev, my_proj):
    if file_abbrev == 'story' or file_abbrev == 'main':
        return i7.main_src(my_proj)
    first_try = os.path.join(i7.ext_dir, file_abbrev)
    if os.path.exists(first_try):
        return first_try
    if os.path.exists(first_try + '.i7x'):
        return first_try + '.i7x'
    if ',' in file_abbrev:
        ary = file_abbrev.split(',')
        temp_cur_file = i7.hdr(ary[0], ary[1])
        if temp_cur_file:
            return temp_cur_file
    else:
        temp_cur_file = i7.hdr(my_proj, file_abbrev)
        if temp_cur_file:
            return temp_cur_file
    return ''

def retest_agnostic(x):
    try:
        if x[1] == '+':
            return x[0] + x[2:]
    except:
        pass
    return x

def retest_agnostic_starts(my_comment, include_null = False):
    my_comment = retest_agnostic(my_comment)
    for s in ['#testcase-', '#ttc-']:
        if my_comment.startswith(s):
            return True
    if include_null:
        if my_comment.startswith("#null-testcase") or my_comment.startswith("#null testcase") or my_comment.startswith("#null test case"):
            return True
    return False

def cr_tweak_sorted(my_array, line_count):
    if len(my_array) < 2:
        mt.warn("Oops, array of length {} at line {}.".format(len(my_array), line_count))
    new_array = sorted([re.sub(r"(\\\\\n)+$", "", x) for x in my_array], key=lambda x:retest_agnostic(x))
    return '\\\\\n'.join(new_array)

def alphabetize_this_rbr(this_file, check_cues = [ '@mis' ]): # todo: focus on specific test case, or focus on first/last command (minor options)
    ever_alphabetized = am_alphabetizing = False
    alphabet_array = []
    out_string  = ''
    ttc_alf = "c:/writing/temp/ttc-alphabetize.txt"
    need_nontrivial_alphabetize = False
    got_alphabetize_header = False
    last_section_start = -1
    test_cases_this_chunk = 0
    in_testcase_group = False
    with open(this_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if need_nontrivial_alphabetize:
                if retest_agnostic_starts(line):
                    test_cases_this_chunk += 1
                    #print(line_count, am_alphabetizing, need_nontrivial_alphabetize, test_cases_this_chunk)
            if line.strip() in check_cues:
                need_nontrivial_alphabetize = True
                got_alphabetize_header = False
                last_section_start = line_count + 1
                test_cases_this_chunk = 0
            if line.startswith("====alphabetize"):
                err_suffix = " in {} line {}. Fix before continuing.".format(this_file, line_count)
                if line.startswith("====alphabetize on"):
                    if am_alphabetizing:
                        print("Double alphabetize-on", err_suffix)
                        return
                    ever_alphabetized = am_alphabetizing = got_alphabetize_header = True
                    out_string += line
                    test_cases_this_chunk = True
                    continue
                if line.startswith("====alphabetize off"):
                    if not am_alphabetizing:
                        print("Double alphabetize-off", err_suffix)
                        return
                    if need_nontrivial_alphabetize and not got_alphabetize_header and test_cases_this_chunk > 1:
                        mt.warn("WARNING section line {}-{} needs ====alphabetize on to start nontrivial protected section.".format(last_section_start, line_count))
                        mt.add_post(this_file, line_count)
                    out_string += cr_tweak_sorted(alphabet_array, line_count)
                    out_string += line
                    need_nontrivial_alphabetize = False
                    am_alphabetizing = False
                    alphabet_array = []
                    continue
                print("Invalid ====alphabetize needs on or off", err_suffix)
                continue
            if not am_alphabetizing:
                out_string += line
                if not line.strip() and need_nontrivial_alphabetize and not got_alphabetize_header:
                    if test_cases_this_chunk > 1:
                        mt.warn("WARNING section line {}-{} needs ====alphabetize on to start nontrivial protected section.".format(last_section_start, line_count))
                        mt.add_post(this_file, last_section_start)
                    need_nontrivial_alphabetize = False
                    test_cases_this_chunk = 0
                continue
            else:
                if not line.strip():
                    mt.warn("WARNING line {} needs ====alphabetize off instead of a blank line, but this may be added anyway.".format(line_count))
                    am_alphabetizing = False
                    mt.add_post(this_file, line_count)
                    out_string += cr_tweak_sorted(alphabet_array, line_count)
                    out_string += "====alphabetize off\n"
                    out_string += line
                    need_nontrivial_alphabetize = False
                    alphabet_array = []
                    continue
            if retest_agnostic_starts(line) and not in_testcase_group:
                alphabet_array.append(line)
                in_testcase_group = True
            else:
                try:
                    alphabet_array[-1] += line
                    in_testcase_group = False
                except:
                    print("Make sure you start an alphabetized section with a test case. {} line {} did not.".format(this_file, line_count))
                    mt.add_post(this_file, line_count, priority=13)
                    mt.post_open()
                    return
    if am_alphabetizing:
        print("Forgot to set alphabetize-off in", my_file)
        return
    if not ever_alphabetized:
        print("Nothing to alphabetize in", this_file)
        return
    f = open(ttc_alf, "w")
    f.write(out_string)
    f.close()
    if cmp(this_file, ttc_alf):
        print("No changes to", this_file)
        mt.post_open()
        return
    if not mt.alfcomp(this_file, ttc_alf):
        print("UH OH data was lost/corrupted in sorting.")
        mt.post_open()
        return
    mt.wm(this_file, ttc_alf)
    raw = input("Y to copy over, O to open first difference >")
    if not raw:
        sys.exit()
    if raw.lower()[0] == 'y':
        copy(ttc_alf, this_file)
    elif raw.lower()[0] == 'o':
        mt.open_first_diff(this_file, ttc_alf)
    sys.exit()

def alphabetize_my_rbrs(this_proj, prefix = 'rbr'):
    glob_string = prefix + "-*.txt"
    to_alph = glob.glob(glob_string)
    for this_file in to_alph:
        print("Alphabetizing", this_file)
        alphabetize_this_rbr(this_file)
    sys.exit()

def get_mistakes(this_proj):
    mistake_file = i7.hdr(this_proj, "mi")
    mistake_dict = defaultdict(SimpleTestCase)
    if not os.path.exists(mistake_file):
        mt.warn("Skipping mistake file for {}.".format(this_proj))
        return mistake_dict
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

def start_tabs_of(x):
    count = 0
    while len(x) > count and x[count] == '\t':
        count += 1
    return count

def has_valid_fork_starts(my_line):
    for x in valid_fork_starts:
        if my_line.startswith(x):
            return True
    return False

def if_to_testcase(if_line):
    new_line = re.sub("[,:].*", "", if_line).strip()
    for x in valid_fork_starts:
        if new_line.startswith(x):
            new_line = new_line.replace('"', '').replace(' ', '-')
            return new_line
    return ''

def rule_test_prefix(my_line, my_prefix_list):
    for prefix in my_prefix_list:
        for regex in my_prefix_list[prefix]:
            if re.search(regex, my_line):
                return prefix
    return ''

def is_say_line(this_line, this_proj):
    return re.search('^\t+(say|{}) +"'.format(say_equivalents[this_proj]), this_line)

def say_line_of(this_line, this_proj):
    ret_val = re.sub('^\t+(say|{}) +"'.format(say_equivalents[this_proj]), "", this_line.rstrip())
    return re.sub('".*', '', ret_val)

def is_ruleshift_line(this_line):
    return re.search(r'^\t+(abide|follow|process|consider) +', this_line)

def ignorable_line(my_line, this_proj):
    for r in ignorable_rule_lines[this_proj]:
        if r in my_line:
            return True
    return False

def get_value_cases(this_proj):
    global global_error_note
    return_dict = defaultdict(bool)
    for this_file in value_specs[this_proj]:
        if not value_specs[this_proj][this_file]:
            return return_dict
        fb = os.path.basename(this_file)
        with open(this_file) as file:
            for (line_count, line) in enumerate (file, 1):
                if line.startswith('\t'):
                    continue
                if line.startswith('to '):
                    continue
                my_stuff = i7.i7_code_sentences_of(line)
                for txt in value_specs[this_proj][this_file]:
                    for m in my_stuff:
                        if txt in m:
                            if txt + ' of' not in m:
                                continue
                            test_case_name = 'testcase-values-{}'.format(m.replace(' ', '-').lower())
                            likely_subject = m.replace('-', ' ').lower()
                            likely_subject = re.sub("^.*?of ", "", likely_subject)
                            likely_subject = re.sub(" (is|are) .*", "", likely_subject)
                            my_command_template = value_specs[this_proj][this_file][txt].command_template.replace('{SUBJ}', likely_subject)
                            if test_case_name not in return_dict:
                                return_dict[test_case_name] = SimpleTestCase(suggested_text = value_specs[this_proj][this_file][txt].expected_text, command_text = my_command_template, condition_text = '', expected_file = value_specs[this_proj][this_file][txt].expected_file)
                            else:
                                print("Ignoring duplicate test case {} line {}".format(test_case_name, line_count))
    return return_dict

def get_rule_cases(this_proj):
    global global_error_note
    return_dict = defaultdict(bool)
    rule_line_count = 0
    in_rules = False
    any_if_yet = False
    ifs_depth_array = []
    for this_file in rules_specs[this_proj]:
        scan_current_text = True
        if len(rules_specs[this_proj][this_file].rules_on_lines) or len(rules_specs[this_proj][this_file].rules_off_lines):
            scan_current_text = False
        fb = os.path.basename(this_file)
        with open(this_file) as file:
            for (line_count, line) in enumerate (file, 1):
                if not line.strip():
                    in_rules = False
                for x in rules_specs[this_proj][this_file].rules_on_lines:
                    if line.startswith(x):
                        scan_current_text = True
                        rules_specs[this_proj][this_file].rules_on_found[x] = True
                for x in rules_specs[this_proj][this_file].rules_off_lines:
                    if line.startswith(x):
                        scan_current_text = False
                        rules_specs[this_proj][this_file].rules_off_found[x] = True
                if not scan_current_text:
                    continue
                if not in_rules:
                    my_prefix = rule_test_prefix(line, rules_specs[this_proj][this_file].valid_hint_regexes)
                    if not my_prefix:
                        continue
                    ifs_depth_array = []
                    in_rules = True
                    any_if_yet = False
                    any_rule_yet = False
                    this_rule = re.sub(".*this is the +", "", line.strip())
                    this_rule = re.sub(" *\)? *:.*", "", this_rule)
                    this_rule = this_rule.replace(' ', '-')
                    test_case_sub_name = 'default'
                    test_case_full_name = 'testcase-rules-{}-default'.format(this_rule)
                    l2 = re.sub("^.*?:", "", line).strip()
                    if l2:
                        line = "\t" + l2
                    else:
                        line = ''
                if not in_rules:
                    continue
                if ignorable_line(line, this_proj):
                    continue
                st = start_tabs_of(line)
                if st > len(ifs_depth_array) + 1:
                    mt.warn("WARNING TABS EXCEED ARRAY LENGTH BY MORE THAN ONE: {} {} {} {} {}".format(fb, line_count, st, len(ifs_depth_array), line.strip()[:50]))
                    mt.add_post(this_file, line_count, priority=4)
                temp = if_to_testcase(line)
                write_test_case = not (not line.strip())
                fixed_case_name = False
                if st == 1 and not temp:
                    test_case_sub_name = "fallthrough" if (any_if_yet or any_rule_yet) else "default"
                    fixed_case_name = True
                elif temp == 'else':
                    ifs_depth_array = ifs_depth_array[:st+1]
                    test_case_sub_name = 'else-' + '-'.join(ifs_depth_array[:st+1])
                    write_test_case = False
                elif temp:
                    any_if_yet = True
                    ifs_depth_array = ifs_depth_array[:st-1]
                    ifs_depth_array.append(temp)
                else:
                    ifs_depth_array = ifs_depth_array[:st-1]
                if temp:
                    if ',' not in line:
                        write_test_case = False
                if not write_test_case:
                    continue
                if is_say_line(line, this_proj):
                    what_said = say_line_of(line, this_proj)
                elif st == 1 and is_ruleshift_line(line):
                    test_case_sub_name = re.sub(';.*', "", line.strip()).replace(' ', '-')
                    what_said = test_case_sub_name
                    any_rule_yet = True
                else:
                    if '"' in line.strip() and has_valid_fork_starts(line.strip()):
                        what_said = line.strip().split('"')[1]
                    else:
                        what_said = "<" + line.strip() + ">"
                if not what_said:
                    what_said = "<no data found>"
                if not fixed_case_name:
                    test_case_sub_name = '-'.join(ifs_depth_array)
                test_case_full_name = test_case_of(my_prefix + '-' + this_rule + '-' + test_case_sub_name)
                my_expected_file = rules_specs[this_proj][this_file].regex_to_abbr[my_prefix] if my_prefix in rules_specs[this_proj][this_file].regex_to_abbr else 'undef'
                if test_case_full_name not in return_dict:
                    return_dict[test_case_full_name] = SimpleTestCase(suggested_text = what_said, command_text = 'rule-cmd', condition_text = '', expected_file = my_expected_file)
                else:
                    return_dict[test_case_full_name].suggested_text += "\n" + what_said
        for x in rules_specs[this_proj][this_file].rules_on_found:
            if not rules_specs[this_proj][this_file].rules_on_found[x]:
                mt.warn("WARNING: rules-on token {} not found in {}.".format(x, fb))
        for x in rules_specs[this_proj][this_file].rules_off_found:
            if not rules_specs[this_proj][this_file].rules_off_found[x]:
                mt.warn("WARNING: rules-off token {} not found in {}.".format(x, fb))
        if scan_current_text and len(rules_specs[this_proj][this_file].rules_off_found):
            mt.warn("WARNING: scan-current-text is on at end of file with rules_on and rules_off markers.")
    return return_dict

def csv_or_range(x, throw_warning = False):
    if x.startswith('o='):
        throw_warning = False
    if ',' in x:
        return x.split(',')
    if '~' in x:
        step = 1
        temp = [int(y) for y in x.split('~')]
        if len(temp) > 2:
            step = temp[2]
        return [str(x) for x in range(temp[0], temp[1] + 1, step)]
    if throw_warning:
        mt.warn("CFG file has potential matrix without commas or tildes: {}.".format(x))
    return [x]

# this function pulls the potential test cases from tables in the source code.
def get_table_cases(this_proj):
    global global_error_note
    return_dict = defaultdict(bool)
    table_line_count = 0
    any_dupes_yet = False
    dupe_so_far = 0
    for this_matrix in test_case_matrices[this_proj]:
        any_yet = False
        main_matrix = []
        for x in this_matrix.matrix:
            main_matrix.append(csv_or_range(x, any_yet))
        out_matrix = itertools.product(*main_matrix)
        for f in out_matrix:
            if not this_matrix.can_repeat and len(set(f)) < len(f):
                continue
            f0 = 'testcase-' + '-'.join(f)
            return_dict[f0] = SimpleTestCase(command_text = this_matrix.out_verb, expected_file = this_matrix.out_file, suggested_text=this_matrix.out_text)
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
        dupe_orig = table_specs[this_proj][this_file].okay_duplicate_counter.copy()
        these_table_gens = []
        dupe_dict = defaultdict(int)
        header_compilation = "<unknown>"
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
                    stray_table = False
                    these_table_gens = []
                    for tg in table_specs[this_proj][this_file].generators:
                        if tg.exact_match:
                            if line.strip().lower() == tg.match_string:
                                these_table_gens.append(tg)
                        else:
                            if re.search(tg.match_string, line.strip().lower()):
                                these_table_gens.append(tg)
                    table_header_next = True
                    if len(these_table_gens):
                        read_table_data = True
                    else:
                        stray_table = True
                        read_table_data = False
                        table_line_count = -1
                    continue
                if table_header_next:
                    headers = [re.sub(" *\(.*", "", x) for x in line.strip().lower().split("\t")]
                    header_compilation = ','.join(headers)
                    table_header_next = False
                    table_line_count = 0
                    continue
                if not line.strip() or line.startswith('['): # we have reached the end of the table.
                    if stray_table:
                        global_error_note = True
                        mt.fail("Stray table {} ({} line{}, {}-{}) should be put into test cases or ignore=.".format(current_table, table_line_count, mt.plur(table_line_count), line_count - table_line_count, line_count - 1))
                        table_overall_undecided += 1
                        table_lines_undecided += table_line_count
                        tables_found[current_table] = True
                        global_stray_table_org[header_compilation].append(current_table)
                    in_table = False
                    read_table_data = False
                    cur_wild_card = ''
                    continue
                table_line_count += 1
                if not read_table_data:
                    continue
                columns = [ quote_flatten(x) for x in line.strip().split('\t') ]
                old_columns = list(columns)
                for my_generator in these_table_gens:
                    sub_case = my_generator.subcase_name_format
                    if '{linecount}' in sub_case:
                        sub_case = sub_case.replace('{linecount}', str(table_line_count))
                    sub_case = text_from_row_values(sub_case, headers, columns)
                    if not sub_case.replace('-', ''):
                        continue
                    if collapse_extra_dashes:
                        sub_case = re.sub("--+", "-", sub_case)
                        sub_case = re.sub("-+$", "", sub_case)
                    for p in my_generator.prefix_list:
                        if my_generator.regex_to_check:
                            if not re.search(my_generator.regex_to_check, sub_case):
                                continue
                        test_case_name = test_case_of(p + '-' + current_table + '-' + sub_case)
                        if test_case_name in return_dict and wild_card_match(test_case_name, table_specs[this_proj][this_file].okay_duplicate_regexes):
                            continue
                        if my_generator.print_absolute:
                            possible_text = my_generator.print_absolute
                        else:
                            possible_text = text_from_row_values(my_generator.print_from_col, headers, columns)
                            for c in range (0, len(headers)):
                                h0 = "{" + headers[c] + "}"
                                possible_text = possible_text.replace(h0, i7.i7_text_convert(columns[c], erase_brackets = False, remove_end_quotes = True))
                        if test_case_name in table_specs[this_proj][this_file].okay_duplicate_counter:
                            table_specs[this_proj][this_file].okay_duplicate_counter[test_case_name] -= 1
                            if table_specs[this_proj][this_file].okay_duplicate_counter[test_case_name] < 0:
                                print("POTENTIAL ERROR: too many duplicate listings for {} in {}. Check okdup statement.".format(test_case_name, this_file))
                        elif test_case_name in return_dict:
                            print("POTENTIAL ERROR: source code provided duplicate test case/column entry {} at line {} of {}. Use okdup/okdupr if this is correct, or try the code below.".format(test_case_name, line_count, fb))
                            if test_case_name not in dupe_dict:
                                dupe_dict[test_case_name] = 1
                            dupe_dict[test_case_name] += 1
                            continue
                        if possible_text.startswith('"') and possible_text.count('"') == 2:
                            possible_text = re.sub("\".*", "", possible_text[1:])
                        temp_command = ''
                        if my_generator.fixed_command:
                            temp_command = my_generator.fixed_command
                        elif my_generator.command_generator:
                            temp_command = my_generator.command_generator
                            for h in range(0, len(headers)):
                                h0 = "{" + headers[h] + "}"
                                if h0 in temp_command:
                                    temp_command = temp_command.replace(h0, columns[h])
                            if '{{' in temp_command:
                                mt.warn("Temp command {}/{} did not match to a header.".format(temp_command, my_generator.command_generator))
                        if my_generator.ignore_blank_print and not has_meaningful_content(possible_text):
                            continue
                        return_dict[test_case_name] = SimpleTestCase(possible_text, command_text = temp_command)
            if table_lines_undecided > 0:
                if table_overall_undecided != len(tables_found):
                    unique_tables = "/{}".format(len(tables_found))
                else:
                    unique_tables = ''
                print("{} table line{} from {}{} table{} still to decide on in ttc.txt for {}.".format(table_lines_undecided, mt.plur(table_lines_undecided), table_overall_undecided, unique_tables, mt.plur(table_overall_undecided), fb))
        if len(dupe_dict):
            print("=============================CFG FILE INFO SUGGESTIONS (replace ~ with \t)")
        for dd in dupe_dict:
            mt.okay("okdup={}~{}".format(dd, dupe_dict[dd]))
        for dupe in table_specs[this_proj][this_file].okay_duplicate_counter:
            if table_specs[this_proj][this_file].okay_duplicate_counter[dupe] == 0:
                continue
            if not any_dupes_yet:
                any_dupes_yet = True
                mt.warn("NOTE: we count the number of duplicates, not the total number of occurrences.")
            print("Too {} duplicates for entry {}: off by {}, should have {}.".format('many' if table_specs[this_proj][this_file].okay_duplicate_counter[dupe] < 0 else 'few', dupe, abs(table_specs[this_proj][this_file].okay_duplicate_counter[dupe]), dupe_orig[dupe]))
    return return_dict

def change_dir_if_needed(new_dir = ''):
    if not new_dir:
        new_dir = i7.proj2dir(my_proj)
    if os.getcwd().lower() != new_dir.lower():
        print("Changing to", new_dir)
        os.chdir(new_dir)

def expected_file(my_case, this_proj):
    for q in case_mapper[this_proj].mappers_in_order:
        the_case = case_mapper[this_proj].text_and_type_map[q][1]
        if the_case == IGNORE_ABSOLUTE_CASE or the_case == IGNORE_REGEX_CASE:
            continue
        q1 = q.replace(' ', '-')
        if the_case == FIND_ABSOLUTE_CASE and q1 in my_case:
            temp = case_mapper[this_proj].text_and_type_map[q][0]
            temp = temp.replace('reg-', '').replace('.*', '')
            return temp
        if the_case == FIND_REGEX_CASE and q1 in my_case:
            temp = case_mapper[this_proj].text_and_type_map[q][0]
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
        print("Possible match(es):", end_match_ary[:5], '' if len(end_match_ary) < 5 else '(5 of {} total)'.format(len(end_match_ary)))

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
def verify_cases(this_proj, this_case_list, my_globs = [ 'rbr-*.txt', 'reg-*-lone-*.txt' ]):
    global okay_duplicates
    global global_error_note
    already_suggested = defaultdict(bool)
    change_dir_if_needed()
    test_file_glob = []
    for m in my_globs:
        test_file_glob.extend(glob.glob(m))
    dupes_flagged = 0
    errant_cases = 0
    last_abbrev = ''
    if len(test_file_glob) == 0:
        print("No test files found in", my_globs)
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
        pre_asterisk_warn = False
        can_write_testcases = not flag_spacing
        tests_in_header = 0
        this_file_dupes = []
        with open(my_rbr) as file:
            for (line_count, line) in enumerate(file, 1):
                line = line.strip()
                if line.startswith('#'):
                    line = re.sub(" #.*", "", line)
                if line.startswith("+#"):
                    print("BACKWARDS RETEST CASE {} line {}: {}".format(base, line_count, line.strip()))
                    mt.add_postopen(my_rbr, line_count)
                if line.startswith("*"):
                    can_write_testcases = True
                if line.endswith("@"):
                    line = line.replace('@', '')
                if line.endswith("#ok"):
                    line = line.replace('#ok', '').rstrip()
                    mt.warn("{} line {} has #ok syntax but should use @.".format(my_rbr, line_count))
                if not can_write_testcases and valid_ttc(line, this_proj):
                    tests_in_header += 1
                    if pre_asterisk_warn:
                        continue
                    pre_asterisk_warn = True
                    global_error_note = True
                    mt.warn("WARNING test case still in header for copy/pasting {} line {}.".format(base, line_count))
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
                        errant_cases += 1
                        print("Errant {}test case #{:3d} {} at {} line {}.".format('re-' if '+' in this_case else '', errant_cases, raw_case, base, line_count))
                        if raw_case not in already_suggested:
                            look_for_similars(raw_case, this_case_list)
                            already_suggested[raw_case] = True
                        mt.add_postopen(my_rbr, line_count)
                        continue
                    if this_case_list[raw_case].found_yet == False and this_case.startswith('#+'):
                        global_error_note = True
                        print("Re-test before test case {} at {} line {}.".format(raw_case, base, line_count))
                        this_case_list[raw_case].first_file_found = base
                        this_case_list[raw_case].first_line_found = line_count
                        this_case_list[raw_case].found_yet = True
                        mt.add_postopen(my_rbr, line_count)
                    if this_case_list[raw_case].found_yet == True and not this_case.startswith('#+'):
                        global_error_note = True
                        dupes_flagged += 1
                        print("Duplicate test case #{} {} at {} line {} copies {}{} (use + to note duplicate).".format(dupes_flagged, raw_case, base, line_count, this_case_list[raw_case].first_file_found + '/' if this_case_list[raw_case].first_file_found != my_rbr else '', this_case_list[raw_case].first_line_found))
                        mt.add_postopen(my_rbr, line_count)
                        this_file_dupes.append(line_count)
                    if raw_case not in this_case_list:
                        global_error_note = True
                        print("Errant test case {} at {} line {}.".format(raw_case, base, line_count))
                        mt.add_postopen(my_rbr, line_count)
                    elif raw_case:
                        if not this_case_list[raw_case].found_yet:
                            this_case_list[raw_case].first_file_found = base
                            this_case_list[raw_case].first_line_found = line_count
                        this_case_list[raw_case].found_yet = True
                    if this_case_list[raw_case].found_yet == True and this_case.startswith('#+'):
                        okay_duplicates += 1
        if len(this_file_dupes):
            mt.warn("This file's duplicates: {}".format(','.join([str(x) for x in this_file_dupes])))
        if tests_in_header > 0:
            print(tests_in_header, "total tests to sort from header in", base)
    misses = [x for x in this_case_list if this_case_list[x].found_yet == False]
    if len(misses) == 0:
        print("No test cases were missed!")
    else:
        mt.warn("missed test case{} listed below:".format(mt.plur(len(misses))))
        global_error_note = True
        cases_printed = 0
        for m in sorted(misses):
            if testcase_wild_card and not re.search(testcase_wild_card, m):
                continue
            if testcase_wild_card_negative and re.search(testcase_wild_card_negative, m):
                continue
            cases_printed += 1
            if show_suggested_file:
                my_abbrev = this_case_list[m].expected_file if this_case_list[m].expected_file else expected_file(m, this_proj)
                if my_abbrev in file_abbrev_maps[my_proj]:
                    my_abbrev = file_abbrev_maps[my_proj][my_abbrev]
                else:
                    alt_abbrev = re.sub(".*-", "", my_abbrev).replace('.txt', '')
                    if alt_abbrev in file_abbrev_maps[my_proj]:
                        my_abbrev = file_abbrev_maps[my_proj][alt_abbrev]
                if my_abbrev == last_abbrev:
                    print('\\\\')
                else:
                    print('@' + my_abbrev)
                    last_abbrev = my_abbrev
            if not show_suggested_text:
                upper_range = 1
            elif duplicate_test_force:
                upper_range = 2
            elif duplicate_test_prevent:
                upper_range = 1
            elif '[if' in this_case_list[m].suggested_text or '[one of]' in this_case_list[m].suggested_text or '[unless' in this_case_list[m].suggested_text:
                upper_range = 2
            else:
                upper_range = 1
            for i in range(0, upper_range):
                print('#' + ('+' if i else '') + m)
                if show_suggested_syntax:
                    if this_case_list[m].command_text:
                        print(">{}".format(this_case_list[m].command_text))
                    else:
                        print(">VERB {}".format(m.replace('-', ' ')))
                if show_suggested_text:
                    if this_case_list[m].suggested_text:
                        print(this_case_list[m].suggested_text)
                    else:
                        print('<TEST CASE HAD NO SUGGESTED TEXT>')
                    if this_case_list[m].condition_text:
                        print("#condition: {}".format(this_case_list[m].condition_text))
                if i < upper_range - 1:
                    print("\\\\")
        if len(misses) > 0:
            sys.stderr.write((colorama.Fore.MAGENTA if cases_printed == 0 else colorama.Fore.YELLOW if cases_printed != len(misses) else colorama.Fore.BLUE) + "{} of {} missed test case{} seen above.".format(cases_printed, len(misses), mt.plur(len(misses))) + mt.WTXT + "\n")
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
        if not os.path.exists(fb):
            print("Likely stale link for", fb, "so skipping.")
            continue
        with open(file_name) as file:
            for (line_count, line) in enumerate (file, 1):
                if not valid_ttc(line):
                    continue
                line_mod = line[1:].lower().strip()
                is_retest = False
                if line_mod.startswith('+'):
                    is_retest = True
                    line_mod = line_mod[1:]
                ignore_test_case_mapping = False
                if line_mod.endswith("@"):
                    ignore_test_case_mapping = True
                    line_mod = line_mod[:-1].rstrip()
                if line_mod.endswith("#ok"):
                    ignore_test_case_mapping = True
                    line_mod = line_mod[:-3].rstrip()
                match_array = []
                this_success = True
#    for q in case_mapper[this_proj].mappers_in_order:
#        the_case = case_mapper[this_proj].text_and_type_map[1]
                for t in case_mapper[this_proj].mappers_in_order:
                    case_type = case_mapper[this_proj].text_and_type_map[t][1]
                    case_file = case_mapper[this_proj].text_and_type_map[t][0]
                    t1 = t.replace(' ', '-')
                    if case_type == FIND_ABSOLUTE_CASE:
                        if t1 not in line_mod:
                            continue
                        if ignore_test_case_mapping or case_file in fb:
                            match_array.append(t1)
                            break
                        else:
                            print("Test case", line_mod, "sorted into wrong file", fb, "should have absolute wild card", case_mapper[this_proj].text_and_type_map[t])
                            mark_rbr_open(file_name, line_count, line)
                            wrong_file += 1
                            this_success = False
                    elif case_type == FIND_REGEX_CASE:
                        if not re.search(t1, line_mod):
                            continue
                        if ignore_test_case_mapping or re.search(case_file, fb):
                            match_array.append(t1)
                            break
                        else:
                            print("Test case", line_mod, "sorted into wrong file", fb, "should have regex", case_mapper[this_proj].text_and_type_map[t])
                            mark_rbr_open(file_name, line_count, line)
                            wrong_file += 1
                            this_success = False
                total_matches = len(match_array)
                if total_matches == 0:
                    case_type = 'test'
                    if line_mod.startswith('+'):
                        line_mod = line_mod[1:]
                        case_type = 'retest'
                    unsorted += 1
                    mt.warn("WARNING ({}) {} case in reg* file pool has no assigned file-pattern: {} {} {}".format('valid' if line_mod in case_list else 'invalid', case_type, fb, line_count, line_mod))
                    mark_rbr_open(file_name, line_count, line)
                    this_success = False
                elif total_matches > 1:
                    double_sorted_cases += (total_matches == 2)
                    double_sorted_lines += 1
                    mt.warn("WARNING {} case potentially sorted into two files:".format(case_type), line_mod, "line_mod", line_count, ' / '.join(match_array))
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
        mt.okay("NO MISPLACED TEST CASES FOUND ANYWHERE IN GENERATED FILES: {} total successes.".format(total_successful))
    else:
        print("{} unsorted={} Double sorted cases/lines={}/{} case-in-wrong-file={} successful={}".format(fb, total_unsorted, total_double_sorted_cases, total_double_sorted_lines, total_wrong_file, total_successful))
    global okay_duplicates
    if okay_duplicates:
        print("Total successful cases in reg-* files, including duplicates: {} + {} = {}.".format(total_successful, okay_duplicates, total_successful + okay_duplicates))

cur_file = "<NONE>"

def read_cfg_file(this_cfg):
    #global table_specs
    #global rules_specs
    already_included[this_cfg] = True
    tb = os.path.basename(this_cfg)
    local_cfg_errors = total_cfg_errors = 0
    with open(this_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('#'):
                continue
            if line.startswith(';'):
                break
            if line.startswith('<'):
                ls = line.strip()
                if not ls.endswith('>'):
                    mt.warn("WARNING need <> at line {} in {}.".format(line_count, this_cfg))
                    continue
                if '/' not in ls and '\\' not in ls:
                    file_to_find = os.path.normpath(os.path.join(ttc_dir, ls[1:-1]))
                    if file_to_find in already_included:
                        mt.warn("WARNING duplicate inclusion of {} at {} line {}.".format(file_to_find, this_cfg, line_count))
                        continue
                    if verbose_level > 0:
                        print("Checking through {}".format(file_to_find))
                    total_cfg_errors += read_cfg_file(file_to_find)
                continue
            (prefix, data) = mt.cfg_data_split(line, lowercase_data = False)
            if len(mt.mt_default_dict) and '$' in line:
                old_data = data
                data = mt.string_expand(data, mt.mt_default_dict, force_lower = True)
            if prefix.startswith("$"):
                if prefix.endswith("+"):
                    var_name = prefix[1:-1]
                    if var_name not in mt.mt_default_dict:
                        mt.warn(var_name, "uses += but is not in the variable dictionary. So you may have a typo.")
                        mt.mt_default_dict[var_name] = data
                    else:
                        mt.mt_default_dict[var_name] += ',' + data
                else:
                    var_name = prefix[1:]
                    mt.mt_default_dict[var_name] = data
            elif prefix == 'abbr':
                ary = data.split(",")
                for a in ary:
                    ary2 = a.split('=')
                    file_abbrev_maps[cur_proj][ary2[0]] = ary2[1]
            elif prefix == 'caseignore':
                ary = data.split(",")
                for x in range(0, len(ary), 2):
                    check_regex_in_absolute(ary[x], line_count)
                    if ary[x] in case_mapper[cur_proj].mappers_in_order:
                        print("Duplicate test case {} in {} at line {} of the cfg file.".format(ary[x], cur_proj, line_count))
                        if cfg_error_bail:
                            mt.add_postopen(this_cfg, line_count)
                            local_cfg_errors += 1
                    else:
                        case_mapper[cur_proj].mappers_in_order.append(ary[x])
                        case_mapper[cur_proj].text_and_type_map[ary[x]] = (ary[x+1], IGNORE_ABSOLUTE_CASE)
            elif prefix == 'caseignorer':
                ary = data.split(",")
                for x in range(0, len(ary), 2):
                    check_suspicious_regex(ary[x], line_count, this_cfg)
                    if ary[x] in case_mapper[cur_proj].mappers_in_order:
                        print("Duplicate test case {} in {} at line {} of the cfg file.".format(ary[x], cur_proj, line_count))
                        if cfg_error_bail:
                            mt.add_postopen(this_cfg, line_count)
                            local_cfg_errors += 1
                    else:
                        case_mapper[cur_proj].mappers_in_order.append(ary[x])
                        case_mapper[cur_proj].text_and_type_map[ary[x]] = (ary[x+1], FIND_REGEX_CASE)
            elif prefix == 'casemap':
                ary = data.split(",")
                for x in range(0, len(ary), 2):
                    check_regex_in_absolute(ary[x], line_count)
                    if ary[x] in case_mapper[cur_proj].mappers_in_order:
                        print("Duplicate test case {} in {} at line {} of the cfg file.".format(ary[x], cur_proj, line_count))
                        mt.add_postopen(this_cfg, line_count)
                    else:
                        case_mapper[cur_proj].mappers_in_order.append(ary[x])
                        case_mapper[cur_proj].text_and_type_map[ary[x]] = (ary[x+1], FIND_ABSOLUTE_CASE)
            elif prefix == 'casemapr':
                ary = data.split(",")
                for x in range(0, len(ary), 2):
                    check_suspicious_regex(ary[x], line_count, this_cfg)
                    if ary[x] in case_mapper[cur_proj].mappers_in_order:
                        print("Duplicate test case {} in {} at line {} of the cfg file.".format(ary[x], cur_proj, line_count))
                        mt.add_postopen(this_cfg, line_count)
                    else:
                        case_mapper[cur_proj].mappers_in_order.append(ary[x])
                        case_mapper[cur_proj].text_and_type_map[ary[x]] = (ary[x+1], FIND_REGEX_CASE)
            elif prefix == 'code_to_ignore':
                if '\t' in data:
                    ignorable_rule_lines[cur_proj].extend(data.split('\t'))
                else:
                    ignorable_rule_lines[cur_proj].extend(data.split(','))
            elif prefix == 'custpref':
                ary = data.split('\t')
                custom_table_prefixes[ary[0]] = ary[1].split(',')
            elif prefix == 'extra':
                for x in data.split(','):
                    if re.search('^reg.*-lone-.*txt', x):
                        mt.warn("WARNING possible redundant test file ... reg-lone is covered in the big glob, so duplicate cases may be erroneously flagged.")
                    extra_project_files[cur_proj].append(x)
            elif prefix in ( 'rule_file', 'rules_file' ):
                temp_cur_file = inform_extension_file(data, cur_proj)
                if not temp_cur_file:
                    mt.warn("WARNING could not get file from {} at {} line {}.".format(data, this_cfg, line_count))
                    if cfg_error_bail:
                        mt.add_postopen(this_cfg, line_count)
                        local_cfg_errors += 1
                    continue
                cur_file = temp_cur_file
                if cur_file in rules_specs[cur_proj]:
                    mt.warn("WARNING duplicate file {} at line {}".format(cur_file, line_count))
                    if cfg_error_bail:
                        mt.add_postopen(this_cfg, line_count)
                        local_cfg_errors += 1
                else:
                    rules_specs[cur_proj][cur_file] = RulesPicker()
            elif prefix in ( 'rule_picker', 'rules_picker' ):
                ary = data.split('\t')
                my_to_file = "unknown"
                my_regex = ""
                for idx in range(1, len(ary)):
                    if '=' not in ary[idx]:
                        mt.warn("WARNING no = {} line {} TSV entry {} = {}".format(tb, line_count, idx, ary[idx]))
                        if cfg_error_bail:
                            mt.add_postopen(this_cfg, line_count)
                            local_cfg_errors += 1
                        mt.add_post_open(this_cfg, line_count)
                        continue
                    sub_array = ary[idx].split('=', 1)
                    generator_type = sub_array[0]
                    generator_data = sub_array[1]
                    if generator_type in ( 'r', 'regex' ):
                        my_regex = generator_data
                    elif generator_type in ( 'fileabbr', 'file_abbr', 't', 'tf', 'testfile' ):
                        my_to_file = generator_data
                if not my_regex:
                    mt.warn("Rules specs needs a regex line {}.".format(line_count))
                    mt.add_postopen(this_cfg, line_count)
                    continue
                rules_specs[cur_proj][cur_file].valid_hint_regexes[ary[0]].append(my_regex)
                rules_specs[cur_proj][cur_file].regex_to_abbr[my_regex] = my_to_file
            elif prefix in ( 'rules_yes', 'rule_yes', 'rules_on', 'rule_on' ):
                ary = data.split('\t')
                rules_specs[cur_proj][cur_file].rules_on_lines.extend(ary)
                for a in ary:
                    rules_specs[cur_proj][cur_file].rules_on_found[a] = False
            elif prefix in ( 'rules_no', 'rule_no', 'rules_off', 'rule_off' ):
                ary = data.split('\t')
                rules_specs[cur_proj][cur_file].rules_off_lines.extend(ary)
                for a in ary:
                    rules_specs[cur_proj][cur_file].rules_off_found[a] = False
            elif prefix in ( 'table_file', 'tables_file' ):
                temp_cur_file = inform_extension_file(data, cur_proj)
                if not temp_cur_file:
                    mt.warn("WARNING could not get file from {} at {} line {}.".format(data, this_cfg, line_count))
                    if cfg_error_bail:
                        mt.add_postopen(this_cfg, line_count)
                        local_cfg_errors += 1
                    continue
                cur_file = temp_cur_file
                if cur_file in table_specs[cur_proj]:
                    mt.warn("WARNING duplicate file {} at line {}".format(cur_file, line_count))
                    mt.add_postopen(this_cfg, line_count)
                else:
                    table_specs[cur_proj][cur_file] = TablePicker()
            elif prefix in ( 'value_file', 'values_file' ):
                temp_cur_file = inform_extension_file(data, cur_proj)
                if not temp_cur_file:
                    if cfg_error_bail:
                        mt.add_postopen(this_cfg, line_count)
                        local_cfg_errors += 1
                    mt.warn("WARNING could not get file from {} at {} line {}.".format(data, this_cfg, line_count))
                    continue
                cur_file = temp_cur_file
                if cur_file in table_specs[cur_proj]:
                    mt.warn("WARNING duplicate file {} at line {}".format(cur_file, line_count))
                    mt.add_postopen(this_cfg, line_count)
            elif prefix in ( 'value_picker', 'values_picker' ):
                ary = data.split('\t')
                while len(ary) < 4:
                    ary.append('<UNDEF>')
                my_cmd = '<CMD>'
                my_file = 'myfile'
                my_text = 'expected text'
                my_token = 'source token'
                eq = sum(['=' in x for x in ary])
                if len(ary) != 4:
                    mt.warn("values_picker needs 4 TSV elements. Skipping this. It may cause a lot of unexpected errors.")
                    continue
                if eq > 0 and eq < 4:
                    mt.warn("value_picker either lists cases in order (source token, command, file abbreviation, rough text) or has token= cmd= file= text=. Skipping this. It may cause a lot of unexpected errors.")
                    mt.warn("    " + ','.join(ary))
                    continue
                if eq == 0:
                    value_specs[cur_proj][cur_file][ary[0]] = ValuesPicker(command_template = ary[1], expected_file = ary[2], expected_text = ary[3])
                else:
                    for a in ary:
                        a0 = a.split('=')
                        if a0[0] == 'token':
                            my_token = a0[1]
                        elif a0[0] == 'cmd':
                            my_cmd = a0[1]
                        elif a0[0] == 'file':
                            my_file = a0[1]
                        elif a0[0] == 'text':
                            my_text = a0[1]
                        else:
                            mt.warn("Unknown value_specs parameter {}.".format(ao[0]))
                    value_specs[cur_proj][cur_file][my_token] = ValuesPicker(command_template = my_cmd, expected_file = my_file, expected_text = my_text)
                #SimpleTestCase(suggested_text = suffix, command_text = full_commands.replace('-', ' '), condition_text = conditions, expected_file = 'mis')
            elif prefix == 'ignore':
                ary = data.split(',')
                for d in ary:
                    check_regex_in_absolute(d, line_count)
                    if data in table_specs[cur_proj][cur_file].ignore:
                        mt.warn("WARNING duplicate ignore", cur_file, line_count, d)
                        mt.add_postopen(this_cfg, line_count)
                    else:
                        table_specs[cur_proj][cur_file].ignore.append(d)
            elif prefix in ( 'ignorew', 'igw' ):
                if data in table_specs[cur_proj][cur_file].ignore_wild:
                    mt.warn("WARNING duplicate ignore", cur_file, line_count, data)
                    mt.add_postopen(this_cfg, line_count)
                else:
                    table_specs[cur_proj][cur_file].ignore_wild.append(data)
            elif prefix in ( 'matrix', 'matrixr' ):
                temp_in_ary = data.split("\t")
                temp_out_array = []
                temp_out_file = temp_verb = temp_test_text = ''
                for a in temp_in_ary:
                    if a.startswith('f=') or a.startswith('o='):
                        temp_out_file = a[2:]
                    elif a.startswith('v='):
                        temp_verb = a[2:]
                    elif a.startswith('t='):
                        temp_test_text = a[2:]
                    else:
                        temp_out_array.append(a)
                test_case_matrices[cur_proj].append(MatrixSpecs(matrix = temp_out_array, out_file = temp_out_file, out_verb = temp_verb, out_text = temp_test_text, can_repeat = (prefix == 'matrix')))
            elif prefix == 'okdup':
                ary = data.split(",")
                if not cur_file:
                    mt.warn("WARNING: you probably want to put an OKDUP in a specific file.")
                for a in ary:
                    check_regex_in_absolute(a, line_count)
                    if '~' not in a:
                        table_specs[cur_proj][cur_file].okay_duplicate_counter[a] = 2
                    else:
                        a2 = a.split("~")
                        table_specs[cur_proj][cur_file].okay_duplicate_counter[a2[0]] = int(a2[1])
            elif prefix == 'okdupr':
                if not cur_file:
                    mt.warn("WARNING: you probably want to put an OKDUP in a specific file.")
                check_suspicious_regex(data, line_count, this_cfg)
                table_specs[cur_proj][cur_file].okay_duplicate_regexes.append(data)
            elif prefix in ( 'oddcase', 'oddcases' ):
                odd_cases[cur_proj].extend(data.split(','))
            elif prefix == 'project':
                cur_proj = i7.long_name(data)
                if not cur_proj:
                    mt.warn("WARNING bad project specified line {}: {}".format(line_count, data))
                    mt.add_postopen(this_cfg, line_count)
                if cur_proj in case_mapper:
                    mt.warn("WARNING redefined case_mapper for {} line {} of {}.".format(cur_proj, line_count, this_cfg))
                else:
                    case_mapper[cur_proj] = TestCaseMapper()
            elif prefix == 'say':
                say_equivalents[cur_proj] = data
            elif prefix == 'stopper':
                table_specs[cur_proj][cur_file].stopper = data
            elif prefix in ('gen', 'generator', 'table'):
                ary = data.split("\t")
                my_prefixes = [ 'ttc' ]
                my_command_generator_list = []
                this_col_list = []
                my_fixed_command = ''
                my_command_generator_list = []
                this_regex_to_check = ''
                this_print_from_col = ''
                this_print_absolute = ''
                this_subcase_name_format = [ ]
                this_ignore_blank_suggestions = False
                generator_dict = defaultdict(str)
                this_ignore_blank_print = False
                try:
                    for idx in range(1, len(ary)):
                        if '=' not in ary[idx]:
                            mt.warn("WARNING no = {} line {} TSV entry {} = {}".format(tb, line_count, idx, ary[idx]))
                            if cfg_error_bail:
                                mt.add_postopen(this_cfg, line_count)
                                local_cfg_errors += 1
                            continue
                        sub_array = ary[idx].split('=', 1)
                        generator_type = sub_array[0]
                        generator_data = sub_array[1]
                        if generator_type in generator_dict:
                            mt.warn("WARNING duplicate generator type {} line {} TSV entry {} = {}".format(generator_type, line_count, idx, generator_type))
                            if cfg_error_bail:
                                mt.add_postopen(this_cfg, line_count)
                                local_cfg_errors += 1
                        if generator_type == 'cmdgen':
                            my_command_generator = generator_data
                        elif generator_type == 'coltoprint':
                            my_col_print = [int(x) for x in generator_data.split(',')]
                        elif generator_type in ( 'fc', 'fixedcommand' ):
                            my_fixed_command = generator_data
                        elif generator_type in ( 'prefix', 'prefixes' ):
                            my_prefixes = generator_data.split(',')
                        elif generator_type == 'printfixed':
                            this_print_absolute = generator_data.replace('\\n', '\n')
                        elif generator_type == 'ignoreblankprint':
                            this_ignore_blank_print = int(generator_data)
                        elif generator_type == 'printfromcol':
                            this_print_from_col = generator_data
                        elif generator_type == 'readcol' or generator_type == 'subcase':
                            if generator_type == 'readcol':
                                mt.warn("Change readcol to subcase in {} line {}.".format(this_cfg, line_count))
                            this_subcase_name_format = generator_data
                        elif generator_type == 'regcheck':
                            this_regex_to_check = generator_data
                        else:
                            mt.warn("WARNING unidentified start {} line {} TSV entry {} = {}".format(tb, line_count, idx, generator_type))
                            if cfg_error_bail:
                                mt.add_postopen(this_cfg, line_count)
                                local_cfg_errors += 1
                    this_generator = TestCaseGenerator(match_string = ary[0], exact_match = 'table' in prefix, subcase_name_format = this_subcase_name_format, print_from_col = this_print_from_col, print_absolute = this_print_absolute, prefix_list = my_prefixes, command_generator = my_command_generator, fixed_command = my_fixed_command, regex_to_check = this_regex_to_check, ignore_blank_print = this_ignore_blank_print)
                    table_specs[cur_proj][cur_file].generators.append(this_generator)
                except:
                    print("Exception reading CFG", line_count, data)
                    print("You *may* need 2 tabs above. 1st entry = tables, 2nd entry = columns that create the test case name, 3rd entry = rough text, 4th entry = columns that create command")
                    print("Also, make sure entries 2/3 are integers.")
                    sys.exit()
            elif prefix == 'untestable':
                untestable_case_mapper[cur_proj].append(UntestableCaseMapper(prefix, data))
            else:
                print("Invalid prefix", prefix, "line", line_count, "overlooked data", data)
    total_cfg_errors += local_cfg_errors
    if local_cfg_errors > 0:
        mt.fail("Errors ({}) were found in {}. Setting -ncb disables cfg error bail, which is on by default.".format(local_cfg_errors, ' / '.join([os.path.basename(x) for x in mt.file_post_list])))
    return total_cfg_errors

def add_rbr_testcase_nums(my_string):
    adjust_out = "c:/writing/temp/ttc-adjust-numbers.txt"
    final_string = ''
    global rbr_globals
    if not rbr_globals:
        rbr_globals = glob.glob("rbr-*.txt")
    x = 0
    increment = 1
    while x < len(my_string) and not my_string[x].isalpha():
        x += 1
    if x == my_string:
        mt.failbail("PLUS needs a string and a starting number, separated by commas.")
    ary = my_string[x:].split(',')
    try:
        starter = int(ary[1])
    except:
        sys.exit("2nd CSV must be a number.")
    try:
        increment = int(ary(2))
    except:
        print("Default increment of 1, no INT in 2nd CSV")
    wild_card = ary[0]
    with open(rbr_globals[0]) as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.startswith('#'):
                final_string += line
                continue
            if not (wild_card in my_string):
                final_string += line
                continue
            ary = line.strip().split('-')
            new_ary = []
            for a in ary:
                if a.isdigit() and int(a) >= starter:
                    b = str(int(a) + increment)
                    new_ary.append(b)
                else:
                    new_ary.append(a)
            new_str = '-'.join(new_ary)
            final_string += new_str + "\n"
    f = open(adjust_out, "w")
    f.write(final_string)
    f.close()
    mt.wm(rbr_globals[0], adjust_out)
    sys.exit()

def test_file_from_project(my_project):
    first_try = os.path.join(ttc_dir, "ttc-{}.txt".format(my_project))
    if os.path.exists(first_try):
        return first_try
    z = i7.long_name(my_project)
    ret_val = ''
    got_one = False
    if z not in i7.i7xa:
        mt.warn("Could not derive project from current directory. Going with default of {}.".format(i7.curdef))
        z = i7.long_name(i7.curdef)
    for a in i7.i7xa[z]:
        tempfile = os.path.join(ttc_dir, "ttc-{}.txt".format(a))
        if os.path.exists(tempfile):
            if got_one:
                sys.exit("Ambiguous ... {} or {}.".format(tempfile, ret_val))
            got_one = True
            ret_val = tempfile
    if not ret_val:
        mt.fail("Could not find file for project {}.".format(my_project))
        mt.fail("Here is syntax to use to create a file:")
        to_file = os.path.normpath(os.path.join(ttc_dir, "ttc-{}.txt".format(i7.main_abbr(my_project))))
        from_file = i7.notes_file(my_project)
        mt.fail("    notepad {}".format(to_file))
        sys.exit()
    return ret_val

already_included = defaultdict(bool)

if 'ncb' in sys.argv:
    sys.argv.remove('ncb')
    cfg_error_bail = False

my_cfg_errors = read_cfg_file(ttc_cfg)

if my_cfg_errors and cfg_error_bail: # we could do this in the function, but what if there is more than one error file?
    print(my_cfg_errors)
    mt.post_open()

my_proj = i7.dir2proj()

cmd_count = 1

while cmd_count < len(sys.argv):
    argraw = sys.argv[cmd_count]
    (arg, num, valfound) = mt.parnum(argraw)
    cmd_count += 1
    if arg == 'sp':
        clean_up_spaces(my_proj)
        sys.exit()
    elif arg == 'v':
        if valfound:
            verbose_level = num
        else:
            verbose_level = 1
    elif arg == '/':
        mt.npo(test_file_from_project(i7.dir2proj()))
    elif arg[0] == '/':
        if arg[1:] == 'm':
            mt.npo(ttc_cfg)
        proj_look = arg[1:]
        if proj_look not in i7.i7x:
            sys.exit("No i7x key for {}.".format(proj_look))
        temp = i7.i7x[proj_look]
        my_stuff = [x for x in i7.i7x if i7.i7x[x] == temp]
        current_cfg = ''
        for m in my_stuff:
            this_cfg = test_file_from_project(m)
            if os.path.exists(this_cfg):
                if current_cfg:
                    mt.warn("WARNING re-defined CFGs in parameters")
                    mt.warn("    FIRST", current_cfg)
                    mt.warn("    NOW", this_cfg)
                current_cfg = this_cfg
        if current_cfg:
            mt.npo(current_cfg)
        sys.exit("No CFGs found for {}.".format(temp))
    elif mt.alfmatch(arg, 'ncd'):
        collapse_extra_dashes = False
    elif arg in ( 'a', 'alf' ):
        alphabetize = True
    elif arg in ( 'oa', 'ao' ):
        open_after = True
    elif arg in ( 'no', 'on' ):
        open_after = False
    elif arg in ( 'dt', 'td' ):
        duplicate_test_force = True
    elif mt.alfmatch(arg, 'ndt'):
        duplicate_test_prevent = True
    elif arg in ( 'na', 'an' ):
        show_suggested_syntax = show_suggested_text = show_suggested_file = False
    elif mt.alfmatch(arg, 'nst') or arg in ( 'qt', 'tq' ):
        show_suggested_syntax = show_suggested_text = False
    elif arg in ( 'ns', 'sn' ):
        show_suggested_syntax = False
    elif arg in ( 'nt', 'tn' ):
        show_suggested_text = False
    elif arg.startswith('tm='):
        testcase_match(arg[3:])
    elif arg.startswith('tma'):
        testcase_match()
    elif arg.startswith('tw='):
        testcase_wild_card = arg[3:]
    elif arg.startswith('twn='):
        testcase_wild_card_negative = arg[4:]
    elif arg.startswith('plus'):
        add_rbr_testcase_nums(argraw)
    elif arg == 'q':
        verbose_level = 0
    elif arg == '?':
        usage()
    elif arg == '??':
        usage()
    else:
        print("BAD ARGUMENT", arg)
        usage()

all_specs = set(list(table_specs)).union(set(list(rules_specs)))

if not my_proj:
    sys.exit("You need to be in a valid project directory or specify a project.")

if my_proj not in all_specs:
    print("{} not in table_specs or rules_specs.".format('<BLANK PROJECT>' if not my_proj else my_proj))
    print("Here is which are:", ', '.join(sorted(all_specs)))
    sys.exit()

if alphabetize:
    alphabetize_my_rbrs(my_proj)
    sys.exit()

case_list = get_table_cases(my_proj)
case_list.update(get_rule_cases(my_proj))
case_list.update(get_mistakes(my_proj))
case_list.update(get_value_cases(my_proj))

case_copy = list(case_list)

for c in case_copy:
    for u in untestable_case_mapper[my_proj]:
        if u.untestable_match(c):
            if verbose_level > 0:
                print("UNTESTABLE CASE: {}".format(c))
            case_list.pop(c)

case_test = verify_cases(my_proj, case_list)
verify_case_placement(my_proj)

if global_error_note: print("?? shows common errors, if the results weren't what you expected.")

if len(global_stray_table_org):
    print("Global stray table info")
    for g in global_stray_table_org:
        print(g, len(global_stray_table_org[g]), global_stray_table_org[g][:5])

if my_cfg_errors:
    mt.warn("This is a warning to note CFG files had parsing errors. Remove NCB to keep the focus on what the errors are.")

if open_after:
    mt.post_open()
