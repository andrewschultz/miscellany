# rbr.py: regression brancher
# rbr.py: regression brancher
#
# takes an rbr*.txt file and separates it into many reg-*
#
# usage rbr.py (project name) e.g. rbr.py ai
#
# or you can run it from a project source directory
#

# TODO:
# 1 allow for ignore-list in RBR.PY e.g. if we only want to test mistakes then @nud would not be on but @mis would be
# 2 levels of testing (1, 2) (may be similar to 1)
# 3 search for something in rbr files and open
# 4 keep postproc commands ordered
# 5 postproc globs inside file_array
# 6 eliminate duplicate file-change printouts
# 7 double space warn, eliminate double spaces at end
# rbr.py shouls allow you to end early with ####branch track end
# rbr-globals.txt for rbr: global strings so we don't have to change them. Only read if 1) read globals and 2) there is, indeed, an rbr-globals.txt file
#

import sys
import re
import os
import i7
import glob
import subprocess
from collections import defaultdict
from shutil import copy
from filecmp import cmp
import mytools as mt
import colorama

my_strings = defaultdict(str)
branch_variables = defaultdict(list)
branch_check = defaultdict(lambda: defaultdict(list))
to_match = defaultdict(str)
monty_detail = defaultdict(str)
branch_list = defaultdict(list)
times = defaultdict(int)
abbrevs = defaultdict(lambda: defaultdict(str))
apostrophes = defaultdict(list)
generic_bracket_error = defaultdict(int)
okay_apostrophes = defaultdict(bool)
new_files = defaultdict(list)
changed_files = defaultdict(list)
unchanged_files = defaultdict(list)
postproc_if_changed = defaultdict(list)
ignores = defaultdict(str)
apost_changes = defaultdict(int)

rbr_config = 'c:/writing/scripts/rbr.txt'

branch_timestamp_skip_check = True

ignore_first_file_changes = False
force_postproc = False
github_okay = False
flag_all_brackets = True
edit_individual_files = False
verify_nudges = False
always_be_writing = False
edit_main_branch = False
debug = False
monty_process = False
force_all_regs = False
strict_name_force_on = False
strict_name_force_off = False
wrong_check = False
show_unchanged = False

start_line = 0
start_command = ''
max_flag_brackets = 0
cur_flag_brackets = 0
ignore_next_bracket = False

quiet = False
copy_over_post = True

rbr_bookmark_indices = ["loc", "room", "rm", #places
  "itm", "item", "thing", #things
  "npc", "per" #people
  ] #this is to give a lot of options for ###new so I don't have to remember anything too exact

in_file = ""
in_dir = os.getcwd()
exe_proj = ""

default_rbrs = defaultdict(str)

def postopen_stub():
    print("Reminder that -np disables copy-over-post and -p enables it. Default is not to copy the REG files over.")
    mt.postopen_files()

def abbrevs_to_ints(my_ary):
    my_ary_1 = [to_match[x] if x in to_match else x for x in my_ary]
    try:
        my_ary_2 = [int(x[1:]) for x in my_ary_1]
    except:
        print("Bad array", my_ary, my_ary_1)
        sys.exit()
    return my_ary_2

def name_or_num(my_string):
    try:
        return int(my_string)
    except:
        if my_string in to_match:
            temp = to_match[my_string]
            if temp[0] == 't':
                temp = temp[1:]
                return int(temp)

def can_make_rbr(x, verbose = False):
    if os.path.exists(x): return x
    x = mt.nohy(x)
    if x in default_rbrs:
        return default_rbrs[x]
    if os.path.exists(x + ".txt"):
        if verbose: print(x, "doesn't exist but {}.{} does. Adding extension.".format(x, "txt"))
        return x + ".txt" # small but real possibility there may be something like vv.txt which would mess things up
    return ""

def no_new_branch_edits(x):
    return False

def prt_temp_loc(x):
    return os.path.normpath(os.path.join(i7.prt_temp, x))

def is_equals_header(x):
    x = x.strip()
    if x.startswith('===') and x.endswith('==='):
        if len(re.findall("[a-zA-Z]", x)): return True
    return False

def is_rbr_bookmark(x): # a bookmark is usually ##newloc or ##newthing, and we don't want to print this to the branch files. It's there for quick searching.
    x0 = x.lower()
    for ind in rbr_bookmark_indices:
        if x0.startswith("#") and "##new" + ind in x0: return True
    return False

def should_be_nudge(x):
    if not x.startswith('#'): return False
    if x.startswith('##'): return False
    if re.search("^#(spechelp|mistake|nudge)", x): return True
    return False

def fill_vars(my_line, file_idx, line_count, print_errs):
    for q in re.findall("\{[A-Z]+\}", my_line):
        #print(q, q[1:-1], branch_variables[q[1:-1]], branch_variables[q[1:-1]][file_idx])
        qt = q[1:-1]
        if qt not in branch_variables:
            if print_errs: print("Bad variable", qt, "at", line_count)
            if qt in my_strings: print("  Maybe add a $ as there is such a string variable.")
            continue
        my_line = re.sub(q, str(branch_variables[q[1:-1]][file_idx]), my_line)
    return my_line

def string_fill(var_line, line_count):
    temp = var_line
    for q in re.findall("\{\$[A-Z]+\}", var_line):
        q0 = q[2:-1]
        if q0 not in my_strings:
            print("WARNING line {} unrecognized string {}.".format(line_count, q0)) #?? printed more than once e.g. put in a bogus string at end
            if q0 in branch_variables: print("  Maybe get rid of the $ as there is such a variable.")
            continue
        temp = re.sub("\{\$" + q0 + "\}", my_strings[q0], temp)
    return temp

def branch_variable_adjust(var_line, err_stub, actives):
    if '+' not in var_line and '-' not in var_line and '=' not in var_line:
        print("ERROR need +/-/= in variable-adjust {}.".format(err_stub))
        return
    temp = var_line.replace(' ', '')
    #print("temp", temp)
    my_var = re.sub("[-=\+].*", "", temp).upper()
    my_op = re.sub(".*?([-=\+]+).*", r'\1', temp)
    text_num = re.sub(".*?[-=\+]+", "", temp)
    #print("my_var", my_var)
    #print("my_op", my_op)
    #print("my_num", my_num)
    if my_var not in branch_variables:
        if my_op != '=':
            print("WARNING tried to operate on undeclared variable {} {}.".format(my_var, err_stub))
            return
        for x in actives:
            if not x:
                print("WARNING tried to define a variable {} when not all files were active {}.".format(my_var, err_stub))
                return
        branch_variables[my_var] = [int(text_num)] * len(actives)
    #print("Before:", my_var, branch_variables[my_var])
    for q in range(0, len(actives)):
        if not actives[q]: continue
        if text_num:
            if text_num in branch_variables: # this is very bad at the moment as we could have VAR+=OTHERVAR, but for now we just use ==
                branch_variables[my_var][q] = branch_variables[text_num][q]
                continue
            else:
                my_num = int(text_num)
        else:
            my_num = 0
        if my_op == "++":
            branch_variables[my_var][q] += 1
        elif my_op == "--":
            branch_variables[my_var][q] -= 1
        elif my_op == "=":
            branch_variables[my_var][q] = my_num
        elif my_op == "-=":
            branch_variables[my_var][q] -= my_num
        elif my_op == "+=":
            branch_variables[my_var][q] += my_num
        elif my_op == "=":
            branch_variables[my_var][q] = my_num
        else:
            print("{} {} {}.".format("Unknown operator" if len(my_op) < 3 else "Likely badly formed variable adjust", my_var, err_stub))
    #print("After:", my_var, branch_variables[my_var])
    return

def apostrophe_check(line, line_count, warns):
    if line.startswith('#'):
        return False
    apost_line = i7.text_convert(line, erase_brackets = False, ignore_array = apostrophes[exe_proj])
    if line == apost_line:
        return False
    print(warns + 1, "Possible apostrophe-to-quote change needed line", line_count)
    print("  Before:", "!" + line.strip() + "!")
    print("   After:", "!" + apost_line.strip() + "!")
    a1 = line.split(' ')
    a2 = apost_line.split(' ')
    mv = min(len(a1), len(a2))
    for x in range(0, mv):
        if "'" in a1[x] and a1[x].replace("'", '"') == a2[x]:
            apost_changes[a1[x]] += 1
    return True

def vet_potential_errors(line, line_count, cur_pot):
    global cur_flag_brackets
    if '[\']' in line or '[line break]' in line or '[paragraph break]' in line:
        print(cur_pot+1, "CR/apostrophe coding artifact in line", line_count, ":", line.strip())
        return True
    elif '[i]' in line or '[r]' in line or '[b]' in line:
        print(cur_pot+1, "Formatting artifact in line", line_count, ":", line.strip())
        return True
    if '##location' in line or '##condition' in line:
        print(cur_pot+1, "Excess generated text from mist.py in line", line_count, ":", line.strip())
        return True
    if '[if' in line or '[unless' in line or '[one of]' in line:
        print(cur_pot+1, "Control statement artifact in line", line_count, ":", line.strip()) # clean this code up for later error checking, into a function
        return True
    if '[' in line and ']' in line and not line.startswith('#') and not ignore_next_bracket and not line.lower().startswith("[note"):
        lmod = re.sub("^[^\[]*\[", "", line.strip())
        lmod = re.sub("\].*", "", lmod)
        lmod = "{:d} {:s}".format(line_count, lmod)
        generic_bracket_error[lmod] += 1
        if flag_all_brackets:
            if max_flag_brackets and cur_flag_brackets > max_flag_brackets: return False
            cur_flag_brackets += 1
            print(cur_flag_brackets, "Text replacement/brackets artifact (ignore with #brackets ok) in line", line_count, ":", line.strip()) # clean this code up for later error checking, into a function
            return True
    return False

def replace_mapping(x, my_f, my_l):
    add_negation = False
    if x.startswith('@') or x.startswith('`'):
        y = x[1:]
        if y[0] == '!':
            add_negation = True
            y = y[1:]
    else:
        y = re.sub("=+\{", "", x.strip())
        y = re.sub("\}.*", "", y)
    y = re.sub(" *#.*", "", y) # strip out comments
    y = y.strip()
    if not y:
        print("OOPS blank file-class-match {} line {}.")
        mt.npo(my_f, my_l)
        return
    my_matches = []
    for q in y.split(","):
        if q != q.strip():
            print("WARNING extra space {} line {} in file-mapping.".format(my_f, my_l))
            q = q.strip()
        if q not in to_match.keys():
            print("Oops, line {:d} of {:s} has undefined matching-class {:s}. Possible classes are {}".format(my_l, my_f, q, ', '.join(to_match)))
            mt.npo(my_f, my_l)
            continue
        to_append = to_match[q].replace('t', '')
        if to_append in my_matches:
            print("WARNING duplicate add-to line {} file {}".format(my_l, my_f))
            mt.add_post(my_f, my_l, priority=8)
        else:
            my_matches.append(to_match[q].replace('t', ''))
    return "==t{}{}".format("!" if add_negation else "", ",".join(my_matches))

def search_for(x):
    a1 = glob.glob("reg-*.txt")
    a1 += glob.glob("rbr-*.txt")
    got_count = 0
    for a2 in a1:
        with open(a2) as file:
            for (line_count, line) in enumerate(file, 1):
                if x in line:
                    got_count += 1
                    print(got_count, a2, line_count, line.strip())
    if not got_count: print("Found nothing for", x)
    sys.exit()

def post_copy(file_array, in_file):
    if copy_over_post:
        if force_all_regs:
            print("Copying all files over to PRT directory.")
            for q in file_array: copy(q, os.path.join(i7.prt, os.path.basename(q)))
        elif len(changed_files.keys()):
            print("Copying changed files over to PRT directory.")
            for q in changed_files.keys():
                print(colorama.Fore.GREEN + q, "=>", ', '.join(changed_files[q]) + colorama.Style.RESET_ALL)
                for r in changed_files[q]:
                    copy(r, os.path.join(i7.prt, os.path.basename(r)))
            changed_files.clear()
        elif len(my_file_list_valid) == 1:
            print(colorama.Fore.YELLOW + "No files copied over to PRT directory." + colorama.Style.RESET_ALL, "Try -fp or -pf to force copying of all files encompassed by", in_file)

def examples():
    print("===1,2,4 changes the active file list to #1, 2, 4 for example.")
    print("==t5 means only use file 5 until next empty line. Then it switches back to what was there before. A second ==t wipes out the first saved array.")
    print("==- inverts the active file list")
    print("== ! - ^ 1,2,4 = all but numbers 1, 2, 4")
    print("*FILE is replaced by the file name.")
    print("#-- is a comment only for the branch file, with a few flags:")
    print("  #--stable means the main file should be kept stable.")
    print("  #--strict means strict section referencing (no magic numbers)")
    sys.exit()

def usage():
    print("-er = edit branch file (default = for directory you are in)")
    print("-e = edit rbr.txt")
    print("-c = edit rbr.py")
    print("-d = debug on")
    print("-f = flag all brackets")
    print("-m = Monty process")
    print("-q = Quiet")
    print("-np = no copy over post, -p = copy over post (default)")
    print("-x = list examples")
    print("shorthand or longterm project names accepted")
    sys.exit()

def all_false(a):
    for x in a:
        if x: return False
    return True

def act(a):
    trues = []
    for x in range(len(a)):
        if a[x]: trues.append(str(x))
    return '/'.join(trues)

def wipe_first_word(a):
    return re.sub(r'^[a-z]+([=:])?', "", a, 0, re.IGNORECASE)

def write_monty_file(fname, testnum):
    mytest = monty_detail[testnum]
    new_file_name = re.sub("^reg", "rmo", fname)
    new_file_name = re.sub("\.", "-{:s}-{:s}.".format(testnum, mytest), new_file_name)
    from_file = prt_temp_loc(fname)
    to_file = prt_temp_loc(new_file_name)
    cmd_yet = False
    f = open(new_file_name, "w", newline="\n")
    with open(fname) as file:
        for line in file:
            if line.startswith('>') and not cmd_yet:
                cmd_yet = True
                f.write("#Test kickoff command for {:s} each turn\n>monty {:s}\n\n".format(mytest, testnum))
            f.write(line)
    f.close()
    if not os.path.exists(to_file):
        print('New file', new_file_name)
        copy(from_file, to_file)
    elif cmp(from_file, to_file):
        print('Unchanged file', new_file_name)
        return
    else:
        print('Modified file', new_file_name)
        copy(from_file, to_file)
    return

def potentially_faulty_regex(test_line):
    if "|" in line or "\\" in line:
        if not line.startswith("/") and not line.startswith("#"):
            return True
    return False

def no_parser(cmd):
    return re.sub("^>+ *", "", cmd)

def viable_untested(my_cmd, my_ignores):
    for q in my_ignores:
        if "*" in q:
            if re.search(q, my_cmd):
                return False
        elif my_cmd == q:
            return False
    return True

def proj_of(file_name):
    try:
        temp = os.path.basename(file_name).split('-')[1]
    except:
        return ""
    return temp

def get_file(fname):
    global ignore_next_bracket
    check_main_file_change = False
    got_any_test_name = False
    dupe_val = 1
    warns = 0
    last_cmd = ""
    file_output = defaultdict(str)
    file_array = []
    line_count = 0
    dupe_file_name = ""
    temp_diverge = False
    if not quiet: print("Poking at", fname)
    actives = []
    old_actives = []
    preproc_commands = []
    at_section = ''
    last_at = 0
    last_eq = 0
    warns_so_far = 0
    to_match.clear()
    strict_name_local = False
    last_atted_command = ""
    untested_commands = defaultdict(list)
    untested_ignore = list(ignores['global'])
    untested_ignore.extend(x for x in ignores[proj_of(fname)] if x not in ignores['global'])
    untested_default = list(untested_ignore)
    wrong_lines = []
    last_cmd_line = -1
    branch_variables.clear()
    balance_undos = False
    track_balance_undos = False
    ignore_extra_undos = False
    temp_diverge_warned = False
    ignore_next_balance = False
    skip_apostrophe_check = False
    need_start_command = (start_command != '')
    fb = os.path.basename(fname)
    with open(fname) as file:
        for (line_count, line) in enumerate(file, 1):
            line_orig = line.strip()
            if strict_name_force_on or (strict_name_local and not strict_name_force_off):
                if line.startswith("==") or line.startswith("@") or line.startswith("`"):
                    if any(x.isdigit() for x in line):
                        print("Strict name referencing (letters not numbers) failed {} line {}: {}".format(fname, line_count, line.strip()))
                        mt.add_postopen(fname, line_count, priority=8)
            if line.startswith("##nobalance"):
                ignore_next_balance = True
            if line.startswith("##balance undo"):
                if balance_undos:
                    print("WARNING {} line {}: another balance-undo block is already operational.".format(fb, line_count))
                balance_error_yet = False
                balance_undos = True
                track_balance_undos = 'trace' in line or 'track' in line
                ignore_extra_undos = 'ignore-neg' in line
                balance_trace = []
                balance_start = line_count
                continue
            if potentially_faulty_regex(line):
                print("WARNING", fname, line_count, "may need starting slash for regex:", line_orig)
            if is_rbr_bookmark(line) or line.startswith("###"): #triple comments are ignored
                if "#skip test checking" in line:
                    last_atted_command = ""
                continue
            if line.startswith('@') or line.startswith('`'):
                at_section = mt.zap_comment(line[1:].lower().strip()) # fall through, because this is for verifying file validity--also @specific is preferred to ==t2
                last_at = line_count
            elif not line.strip():
                if at_section and last_atted_command:
                    if viable_untested(last_atted_command,untested_ignore):
                        untested_commands[last_atted_command].append(last_cmd_line)
                        mt.add_postopen(fname, line_count, priority=10)
                        last_atted_command = ''
                at_section = ''
                if balance_undos:
                    if len(balance_trace):
                        print("ERROR net undos at end of block that needs to be balanced = {}. Lines {}-{} file {}.{}".format(len(balance_trace), balance_start, line_count, fname, '' if track_balance_undos else ' Add TRACK/TRACE to balance undo comment to trace things.'))
                    balance_undos = False
            if line.startswith('=='):
                last_eq = line_count
            if line.startswith('#'):
                for x in branch_check[exe_proj]:
                    if line[1:].startswith(x) and at_section != branch_check[exe_proj][x]:
                        lae = max(last_at, last_eq)
                        warns_so_far += 1
                        print("WARNING {} file {} line {} (last @/eq={}) has section {}, needs {} for comment {}.".format(warns_so_far, fname, line_count, lae, at_section if at_section else "<blank>", branch_check[exe_proj][x], line.strip()))
                        mt.add_postopen(fname, line_count, priority=7)
            if line.startswith("{--"): # very temporary array. One line (one-line) edit writing specific files before back to normal.
                vta_before = re.sub("\}.*", "", line.strip())
                vta_after = re.sub("^.*?\}", "", line.strip())
                temp_file_fullname_array = abbrevs_to_ints(vta_before[3:].split(","))
                if "\\n" in line:
                    print("WARNING {} line {} needs \\\\ and not \\n for line-changes for temporary one-line edit.".format(fname, line_count))
                    mt.add_post(fname, line_count)
                u = vta_after.replace("\\\\", "\n") + "\n"
                for q in temp_file_fullname_array:
                    file_output[q] += u
                continue
            if wrong_check and line.startswith("WRONG"):
                wrong_lines.append(line_count)
                mt.add_postopen(fname, line_count, priority=6)
            if line.startswith("OK-APOSTROPHE:"):
                l = re.sub("^.*?:", "", line)
                if not line.strip():
                    okay_apostrophes.clear()
                for l0 in l.strip().split("\t"):
                    okay_apostrophes[l0] = True
                continue
            if line.startswith("DE-IGNORE:"):
                l = re.sub("^.*?:", "", line.strip().lower())
                for x in l.split("\t"):
                    if x not in untested_ignore:
                        print("Warning DE-IGNORE tries to remove element not in ignore list {} at line {}.".format(x, line_count))
                    else:
                        untested_ignore.remove(x)
                continue
            if line.startswith("#OK-APOSTROPHE") or line.startswith("#APOSTROPHE-OK"):
                skip_apostrophe_check = True
                continue
            if line.startswith("ALSO-IGNORE:") or line.startswith("ALSO_IGNORE"):
                l = re.sub("^.*?:", "", line.strip().lower())
                if not l:
                    untested_ignore = list(untested_default)
                else:
                    if "\t" in line:
                        print("WARNING you need to split with commas and not tabs line {}.".format(line_count))
                    for x in l.split(","):
                        if x in untested_ignore:
                            print("Warning ALSO-IGNORE re-adds {} at line {}.".format(x, line_count))
                        else:
                            untested_ignore.append(x)
                continue
            if line.startswith("~\t"):
                eq_array = line.strip().lower().split("\t")
                if len(eq_array) != 3:
                    print("Bad equivalence array at line {} of file {}: needs exactly two tabs.".format(line_count, fb))
                    mt.npo(fname, line_count)
                ary2 = eq_array[1].split(",")
                if eq_array[2][1:].isdigit(): # t0, t1, t2
                    final_digit = int(eq_array[2][1:])
                    if final_digit >= len(actives):
                        print("FATAL ERROR: ~ maps to nonexistent file at line {} of {}. {} should not be more than {}.".format(line_count, fb, final_digit, len(actives)-1))
                        mt.npo(fname, line_count)
                    this_abbrev = eq_array[2]
                else: # "verbs" when one file is, say, reg-roi-others-verbs.txt
                    candidate = -1
                    temp_array = [os.path.basename(x) for x in file_array]
                    for t in range(0, len(temp_array)):
                        if eq_array[2] in temp_array[t]:
                            if candidate > -1:
                                print("Two possible file name candidates for {} at line {}. Bailing.".format(eq_array[2], t))
                                mt.npo(fname, line_count)
                            candidate = t
                    if candidate == -1:
                        print("Found no text-to-number candidates at {} line {}'s right tab. Check that {} matches a file name in a files= line.".format(fb, line_count, eq_array[2]))
                        mt.npo(fname, line_count)
                    this_abbrev = "t{}".format(candidate)
                for a in ary2:
                    if a in to_match:
                        print(to_match, "WARNING redefinition of shortcut {} at line {} of file {}".format(a, line_count, fb))
                    to_match[a] = this_abbrev
                continue
            if line.startswith("#brackets ok") or line.startswith("#ignore next bracket") or line.startswith("#ignore bracket"):
                ignore_next_bracket = True
                continue
            if line.startswith("*") and line[1] != '*': got_any_test_name = True
            if line.startswith("preproc="):
                if len(file_array) > 0:
                    print("WARNING Line {:d} has preproc that should be before files.".format(line_count))
                    continue
                temp = re.sub("^.*?=", "", line.strip()).split(",")
                preproc_commands += temp
            if line.startswith("postproc="):
                if len(file_array) == 0:
                    sys.exit("BAILING. RBR.PY requires postproc= to be after files=, because postproc may depend on certain files.")
                line_no_com = re.sub(" #.*", "", line.strip())
                line_no_com = re.sub("^.*=", "", line_no_com)
                exclude = False
                if line_no_com[0] == '-':
                    line_no_com = line_no_com[1:]
                    exclude = True
                if "/" in line_no_com:
                    temp_array_1 = line_no_com.split("/")
                    temp_file_array = temp_array_1[0].split(",")
                    cmd_to_run = temp_array_1[1].split(",")
                    if exclude:
                        temp_file_array = [x for x in file_array_base if x not in temp_file_array]
                    for x in temp_file_array:
                        if x not in file_array_base:
                            sys.exit("FATAL ERROR: {} is not in the original file array {}.".format(x, file_array_base))
                else:
                    temp_file_array = list(file_array)
                    cmd_to_run = re.sub("^.*?=", "", line_no_com).split(",")
                for tf in temp_file_array:
                    postproc_if_changed[prt_temp_loc(tf)] += cmd_to_run
                continue
            if line.startswith("files="):
                for cmd in preproc_commands: os.system(cmd)
                file_array_base = re.sub(".*=", "", line.lower().strip()).split(',')
                for f in file_array_base:
                    long_name = prt_temp_loc(f)
                    file_array.append(long_name)
                    file_output[long_name] = ''
                    if start_line:
                        file_output[long_name] += '## truncated branches starting with line {}, so rerun without -sl\n'.format(start_line)
                    if start_command:
                        file_output[long_name] += '## truncated branches before command {}, so run withough -sc:\n'.format(start_command)
                    actives.append(True)
                continue
            if not len(file_array): continue # allows for comments at the start
            if line.startswith(")"):
                print("WARNING line starting with ) may need to start with } instead.", fname, line_count)
            if line.startswith("{{"):
                print("WARNING line starting with {{ may need to start with } instead.", fname, line_count)
            if line.startswith("}$"):
                temp_ary = line[2:].strip().split("=")
                my_strings[temp_ary[0]] = '='.join(temp_ary[1:])
                last_atted_command = ""
                continue
            if line.startswith("}}"):
                if len(file_array) == 0:
                    sys.exit("BAILING. RBR.PY requires }} variable meta-commands to be after files=, because each file needs to know when to access that array.")
                branch_variable_adjust(line[2:].strip(), "at line {} in {}".format(line_count, fname), actives)
                last_atted_command = ""
                continue
            if line.strip() == "==!" or line.strip() == "@!":
                actives = [not x for x in actives]
                continue
            if re.search("^(`|=\{|@)", line):
                line = replace_mapping(line, fname, line_count)
            if line.startswith('#--'):
                if line.startswith("#--stable"):
                    check_main_file_change = True
                if line.startswith("#--strict"):
                    strict_name_local = True
                continue
            if temp_diverge and not line.strip():
                temp_diverge = False
                for x in range(len(actives)):
                    file_output[file_array[x]] += "\n"
                actives = list(old_actives)
                continue
            if line.strip() == "\\\\": line = "\n"
            if skip_apostrophe_check:
                skip_apostrophe_check = False
            elif apostrophe_check(line, line_count, warns):
                mt.add_postopen(fname, line_count, priority=5)
                warns += 1
            if vet_potential_errors(line, line_count, warns):
                mt.add_postopen(fname, line_count, priority=5)
                warns += 1
            ignore_next_bracket = False
            if line.startswith("dupefile="):
                dupe_file_name = i7.prt + "/temp/" + re.sub(".*=", "", line.lower().strip())
                dupe_file = open(dupe_file_name, "w", newline="\n")
                continue
            if re.search("^TSV(I)?[=:]", line): #tab separated values
                if ' #' in line:
                    print('WARNING SPACES NOT TABS for TSV line', line_count)
                ignore_too_short = line.lower().startswith("tsvi")
                l2 = re.sub("TSV(I)?.", "", line.lower(), 0, re.IGNORECASE).strip().split("\t")
                if len(l2) > len(file_array):
                    print("WARNING line", line_count, "has too many TSV values, ignoring")
                    for x in range(0, len(l2)):
                        print(l2[x], '~', os.path.basename(file_array[x]) if x < len(file_array) else '?')
                    continue
                elif not ignore_too_short and len(l2) < len(actives):
                    print("WARNING line", line_count, "doesn't cover all files. Change TSV to TSVI to ignore this.")
                    print("TEXT:", line.strip())
                    for x in range(0, len(file_array)):
                        print(l2[x] if x < len(l2) else '?', '~', os.path.basename(file_array[x]))
                for x in range(len(l2)):
                    file_output[file_array[x]] += l2[x] + "\n"
                continue
            if all_false(actives):
                if always_be_writing and len(actives):
                    sys.exit("No files written to at line " + line_count + ": " + line.strip())
            if line.startswith(">"):
                if '#' in line:
                    line = re.sub(" *#.*", "", line) # eliminate comments from line -- we want to be able to GREP for comments if need be
                if balance_undos:
                    if line[1:].strip().startswith("undo"):
                        try:
                            temp_cmd = balance_trace.pop()
                            if temp_cmd == 'no' or temp_cmd == 'yes':
                                balance_trace.pop()
                        except:
                            if not ignore_extra_undos: # we might be ok with an extra undo. It's bad scripting, but it's ok.
                                print("Uh oh, too many undos at file {} line {} in block starting at line {}".format(fname, line_count, balance_start))
                                mt.add_postopen(fname, line_count)
                                balance_error_yet = True
                    elif ignore_next_balance:
                        ignore_next_balance = False
                    else:
                        balance_trace.append(line[1:].strip())
                        if track_balance_undos:
                            print('TRACE:', line_count, ' / '.join(balance_trace))
                        if not balance_error_yet and len(balance_trace) > 10:
                            balance_error_yet = True
                            print("Net undos over 10 in balanced block line {} file {}--Inform may not be able to go that far back.".format(line_count, fname))
                            mt.add_postopen(fname, line_count)
                if line.startswith(">>"):
                    print("ERROR: double prompt at line", line_count, "of", fname)
                last_cmd = line.lower().strip()
                if at_section:
                    if last_atted_command and viable_untested(last_atted_command,untested_ignore):
                        untested_commands[last_atted_command].append(last_cmd_line)
                        mt.add_postopen(fname, line_count, priority=10)
                    last_atted_command = no_parser(last_cmd)
                last_cmd_line = line_count
            if line.startswith("===a"):
                actives = [True] * len(actives)
                continue
            if line.startswith("==!") or line.startswith("==-") or line.startswith("==^") or line.startswith("==!t") or line.startswith("@!"):
                if not line.startswith("@!"):
                    print("@! is the preferred syntax. ==!t, etc., should be deprecated or mapped to strings. Line {} of {}.".format(line_count, fname))
                    line = re.sub("==(!|-|\^|t)", "", line)
                else:
                    line = line[2:]
                actives = [True] * len(actives)
                try:
                    chgs = line.lower().strip()[temp_idx:].split(',')
                    if len(chgs):
                        for x in chgs:
                            actives[name_or_num(x)] = False
                    else:
                        print("No elements in ==!/-/^ array, line", line_count)
                except:
                    sys.exit("Failed extracting not-(item) at line {}: {}".format(line_count, line.strip()))
                continue
            if line.startswith("==+"):
                ll = line.lower().strip()[3:]
                if len(ll) == 0:
                    print("WARNING nothing added", line_count, line.lower().strip())
                    continue
                for x in ll.split(','):
                    if x.isdigit():
                        actives[int(x)] = True
                continue
            if line.startswith("=one="):
                la = line[5:].split("\t")
                temp_actives = [False] * len(file_array)
                string_out = re.sub(r"\\{2,}", "\n", la[1])
                for x in la[int(0)].split(","): temp_actives[int(x)] = True
                for x in range(0, len(file_array)):
                    if temp_actives[x]: file_output[x] += string_out
                continue
            if line.startswith("==t"):
                if temp_diverge:
                    print("ERROR: located second file branch array in {} with ==t at line {}: {}/{}".format(fname, line_count, line_orig, line.strip()))
                    if not temp_diverge_warned:
                        print("    (to make a temporary branch, use brackets and dashes as so: {--F1,F2}")
                        temp_diverge_warned = True
                    mt.add_postopen(fname, line_count)
                old_actives = list(actives)
                temp_diverge = True
                ll = re.sub("^==t(!)?", "", line.lower().strip()).split(',')
                if line.startswith("==t-"): print("WARNING ==t- should be ==t! for total searchable conformance and stuff.")
                towhich = line.startswith("==t!") or line.startswith("==t-")
                actives = [towhich] * len(file_array)
                for x in ll:
                    try:
                        if x.isdigit(): actives[int(x)] = not towhich
                    except:
                        print("uh oh went out of array bounds trying to load file", x, "at line", line_count, "with only", len(actives) - 1, "as max")
                        sys.exit()
                continue
            if line.startswith("==c-"):
                old_actives = list(actives)
                class_name = ll[4:]
                class_array = branch_classes[class_name].split(',')
                actives = [False] * len(file_array)
                for x in class_array:
                    actives[int(x)] = True
            if line.startswith("==c="):
                class_array = ll[4:].split(':')
                if len(class_array) != 2:
                    sys.exit("Line", line_count, "needs exactly 1 : ... ", ll)
                branch_classes[class_array[0]] = class_array[1]
            if line.startswith("==="):
                if not is_equals_header(line):
                    if not line[3].isnumeric() and line[3] != '!': sys.exit("extra = in header {:s} line {:d}: {:s}".format(fname, line_count, line.strip()))
                    ll = re.sub("^=+", "", line.lower().strip()).split(',')
                    actives = [False] * len(file_array)
                    for x in ll:
                        if x.isdigit(): actives[int(x)] = True
                    continue
            if line.startswith("==") and not is_equals_header(line):
                print("Uh oh {} line {} may be a bad branch-file redirector: {}".format(fname, line_count, line.strip()))
                warns += 1
            if debug and line.startswith(">"): print(act(actives), line.strip())
            if last_atted_command and not line.startswith("#") and not line.startswith(">"):
                last_atted_command = ""
            first_file = True
            if line.startswith("~="):
                line = line.replace("~", "=") # hack to allow ==== headers
            for ct in range(0, len(file_array)):
                if actives[ct]:
                    this_file = file_array[ct]
                    if sum(actives) == 1:
                        if need_start_command:
                            if line.startswith('>') and start_command == line_orig[1:]:
                                need_start_command = False
                                print("Found start-command {} at line {}.".format(start_command, line_count))
                            else:
                                continue
                        if start_line > line_count:
                            continue
                    line_write = re.sub("\*file", os.path.basename(this_file), line, 0, re.IGNORECASE)
                    line_write = re.sub("\*fork", "GENERATOR FILE: " + os.path.basename(fname), line_write, 0, re.IGNORECASE)
                    if "{$" in line_write:
                        #print("BEFORE:", line_write.strip())
                        line_write = string_fill(line_write, line_count)
                        #print("AFTER:", line_write.strip())
                    line_write_2 = fill_vars(line_write, ct, line_count, first_file)
                    #if line_write != line_write_2: print(line_write, "changed to", line_write_2)
                    file_output[this_file] += line_write_2
                    first_file = False
            if dupe_val < len(actives) and actives[dupe_val]:
                if dupe_file_name:
                    dupe_file.write(line)
                    if 'Last Lousy Point' in line: dupe_file.write("!by one point\n")
                    if 'by one point' in line or 'Last Lousy Point' in line:
                        reps = 1
                        if times[last_cmd[1:]] > 1: reps = times[last_cmd[1:]]
                        for x in range(0, reps):
                            dupe_file.write("\n" + last_cmd + "\n")
                            dupe_file.write("!{:s}\n".format('Last Lousy Point' if 'Last Lousy Point' in line else 'by one point'))
    if need_start_command:
        print("WARNING: did not find start command {} anywhere in single-file branches, though it was specified on the command line.".format(start_command))
    if len(untested_commands):
        print("POTENTIALLY UNTESTED COMMANDS for {}: (remove with ###skip test checking (optional explanation) below the command, or ALSO_IGNORE:x or x* or IGNOREGLOBAL in rbr.txt)".format(fname))
        cmd_count = 0
        total_count = 0
        for u in sorted(untested_commands, key=untested_commands.get):
            cmd_count += 1
            total_count += len(untested_commands[u])
            print("{} ({}): {} at line{} {}.".format(cmd_count, total_count, u, mt.plur(len(untested_commands[u])), ", ".join([str(x) for x in untested_commands[u]])))
    elif not quiet:
        print("No potentially untested commands in {}.".format(fname))
    if dupe_file_name:
        dupe_file.close()
        file_array.append(dupe_file_name)
    if warns > 0 and not quiet:
        print(warns, "potential bad commands in {}.".format(fname))
    if monty_process:
        for x in file_array:
            x2 = os.path.basename(x)
            if x2 in mwrites.keys():
                for y in mwrites[x2].keys():
                    write_monty_file(x2, y)
    if check_main_file_change:
        x = file_array[0]
        xb = os.path.basename(x)
        print("Making sure {} / {} are identical.".format(x, xb))
        if not ignore_first_file_changes and not cmp(x, xb):
            print("Differences found in main file {}, which was meant to be stable. Windiff-ing then exiting. Use -f1 to allow these changes.".format(xb))
            mt.wm(x, xb)
            sys.exit()
    for x in file_array:
        f = open(x, "w")
        modified_output = re.sub("\n{3,}", "\n\n", file_output[x])
        f.write(modified_output)
        f.close()
        xb = os.path.basename(x)
        if not os.path.exists(xb):
            new_files[fname].append(xb)
            copy(x, xb)
        elif cmp(x, xb):
            unchanged_files[fname].append(xb)
        else:
            if xb in changed_files:
                print("Oh no! two RBR files seem to point to", xb)
                continue
            changed_files[fname].append(xb)
            copy(x, xb)
        os.remove(x)
    if len(wrong_lines) > 1:
        if wrong_check:
            print("{} WRONG line{} to fix: {}".format(len(wrong_lines), mt.plur(len(wrong_lines)), ", ".join([str(x) for x in wrong_lines])))
        else:
            print("{} WRONG line{} were found. Use -wc to track them and potentially open the first error.".format(len(wrong_lines), mt.plur(len(wrong_lines))))
    if not got_any_test_name and os.path.basename(fname).startswith('rbr'):
        print("Uh oh. You don't have any test name specified with * main-thru for {}".format(fname))
        print("Just a warning.")
    post_copy(file_array_base, fname)

def show_csv(my_dict, my_msg):
    ret_val = 0
    for q in my_dict:
        lmd = len(my_dict[q])
        print("{} {}{} from {}: {}".format(lmd, my_msg, mt.plur(lmd), q, ', '.join(sorted(my_dict[q]))))
        ret_val += lmd
    return ret_val

def internal_postproc_stuff():
    total_csv = show_csv(new_files, "new file") + show_csv(changed_files, "changed file")
    if show_unchanged:
        total_csv += show_csv(unchanged_files, "unchanged file")
    if total_csv or force_postproc:
        run_postproc = defaultdict(bool)
        if not total_csv: print("Forcing postproc even though nothing changed.")
        to_proc = []
        for x in new_files:
            to_proc += list(new_files[x])
        for x in changed_files:
            to_proc += list(changed_files[x])
        if force_postproc:
            for x in unchanged_files:
                to_proc += list(unchanged_files[x])
        for fi in to_proc:
            temp_loc = prt_temp_loc(fi)
            for cmd in postproc_if_changed[temp_loc]:
                run_postproc[cmd] = True
        for cmd in run_postproc:
            print("Postproc: running", cmd)
            os.system(cmd)
    else:
        print("There are postproc commands, but no files were changed. Use -fp to force postproc.")

cur_proj = ""
mwrites = defaultdict(lambda: defaultdict(bool))

with open(rbr_config) as file:
    for (lc, line) in enumerate(file, 1):
        if line.startswith(';'): break
        if line.startswith('#'): continue
        lr = line.strip()
        ll = lr.lower()
        if '>' in ll[1:] and '<' not in ll[1:]:
            print("WARNING: possible erroneous cut and paste. Line", lc, "may need line break before command prompt:", line.strip())
        vars = wipe_first_word(ll)
        if ll.startswith('dupe'):
            ja = vars.split("\t")
            times[ja[0]] = int(ja[1])
            continue
        if ll.startswith('default'):
            def_proj = i7.main_abb(vars)
            continue
        if ll.startswith('project') or ll.startswith('projname'):
            cur_proj = i7.main_abb(vars)
            continue
        if ll.startswith('apostrophe'):
            apostrophes[cur_proj].extend(wipe_first_word(lr).split(','))
            continue
        if ll.startswith('abbrevs'):
            temp = ll[8:].split(',')
            for t in temp:
                t2 = t.split('=')
                if len(t2) != 2: sys.exit(t + " needs exactly one = at line" + str(lc))
                abbrevs[t2[0]][cur_proj] = t2[1]
            continue
        if ll.startswith('branchmain'):
            default_rbrs[cur_proj] = vars
            continue
        if ll.startswith('branchcheck'):
            ary0 = ll[12:].split(',')
            for a in ary0:
                x = a.split("/")
                for y in x[1].split("+"):
                    if y in cur_proj:
                        print("WARNING REDEFINITION of branch_check key {} in {} at line {}.".format(y, cur_proj, lc))
                    branch_check[cur_proj][y] = x[0]
            continue
        if ll.startswith('branchfiles'):
            branch_list[cur_proj] = vars.split(",")
            if cur_proj in i7.i7xr.keys(): branch_list[i7.i7xr[cur_proj]] = vars.split(",")
            if cur_proj in i7.i7x.keys(): branch_list[i7.i7x[cur_proj]] = vars.split(",")
            continue
        if ll.startswith("ignoreglobal"):
            if 'global' in ignores:
                print("Redef of IGNOREGLOBAL at line {}.".format(lc))
            y = ll.split('=')
            if '=' not in ll:
                print(ll, 'in line', lc, ll, 'needs an =')
                continue
            ignores['global'] = y[1].strip().split(",")
            continue
        if ll.startswith("ignorelocal"):
            if cur_proj in ignores:
                print("Redef of IGNORELOCAL for {} at line {}.".format(cur_proj, lc))
            y = ll.split('=')
            if '=' not in ll:
                print(ll, 'in line', lc, ll, 'needs an =')
                continue
            ignores[cur_proj] = y[1].strip().split(",")
            continue
        if ll.startswith('montyfiles'):
            mfi = vars.split("\t")
            for ll in mfi:
                y = ll.split("=")
                if '=' not in ll:
                    print(ll, 'in line', lc, ll, 'needs an =')
                    continue
                z = y[1].split(',')
                for z0 in z:
                    mwrites[y[0]][z0] = True
            continue
        if ll.startswith('monty'):
            monties = vars.split(',')
            for x in monties:
                if '=' not in x:
                    print(x, 'in line', line_count, ll, 'needs an =')
                    continue
                y = x.split("=")
                monty_detail[y[0]] = y[1]
            continue
        j = ll.split("\t")
        if len(j) < 2:
            print("Need tab in", line.strip())
        print(j)
        hk = i7.lpro(j[0])
        branch_list[j[0]] = j[1]
        if hk:
            print(hk, j[1])
            branch_list[hk] = j[1]
        else:
            print(j[0], hk, "not recognized as project or shortcut")

count = 1

projs = []
poss_abbrev = []
my_file_list = []

while count < len(sys.argv):
    arg = mt.nohy(sys.argv[count].lower())
    if arg == 'c':
        i7.open_source()
        sys.exit()
    elif arg == 'e':
        print("Editing the rbr.txt project configuration file.")
        print("If you meant to edit the main rbr file, you can use -er. But it may be easier to type rbr<TAB>.")
        os.system("rbr.txt")
        sys.exit()
    elif arg[:2] == 'e:':
        edit_individual_files = True
    elif arg == 'er': edit_main_branch = True
    elif arg[:2] == 's4': search_for(arg[2:])
    elif arg[:2] in ( 'vn', 'nv', 'v'): verify_nudges = True
    elif arg == 'd': debug = True
    elif arg in ( 'nf', 'fn'): flag_all_brackets = False
    elif arg == 'm': monty_process = True
    elif arg == 'q': quiet = True
    elif arg == 'su': show_unchanged = True
    elif arg in ( 'nsu', 'sun') : show_unchanged = False
    elif arg in ( 'nq', 'qn' ): quiet = False
    elif arg == 'np': copy_over_post = False
    elif arg == 'p': copy_over_post = True
    elif arg == 'fp': force_postproc = True
    elif arg == 'wc': wrong_check = True
    elif arg[:2] == 'sl': start_line = int(arg[2:])
    elif arg[:3] == 'sc:': start_command = arg[3:].replace('-', ' ')
    elif arg in ( 'wcn', 'nwc'): wrong_check = False
    elif arg == 'f1': ignore_first_file_changes = True
    elif arg == 'st': strict_name_force_on = True
    elif arg in ( 'nst', 'stn'): strict_name_force_off = True
    elif arg in ( 'pf', 'pc', 'cp' ): copy_over_post = force_all_regs = True
    elif arg in i7.i7x.keys():
        if exe_proj: sys.exit("Tried to define 2 projects. Do things one at a time.")
        exe_proj = i7.i7x[arg]
    elif can_make_rbr(arg, verbose = True): in_file = can_make_rbr(arg)
    elif arg == 'x': examples()
    elif arg == 'gh': github_okay = True
    elif arg == '?': usage()
    elif arg in abbrevs.keys(): poss_abbrev.append(arg)
    elif arg[0] == 'f':
        flag_all_brackets = True
        if arg[1:].isdigit():
            max_flag_brackets = int(arg[1:])
    else:
        print("Bad argument", count, arg)
        print("Possible projects: ", ', '.join(sorted(branch_list.keys())))
        usage()
        sys.exit()
    count += 1

if strict_name_force_on and strict_name_force_off:
    sys.exit("Conflicting force-strict options on command line. Bailing.")

my_dir = os.getcwd()

if my_dir == "c:\\games\\inform\\prt":
    sys.exit("Can't run from the PRT directory. Move to an Inform source directory.")

if 'github' in my_dir.lower():
    if not github_okay:
        sys.exit("GITHUB is in your path. Mark this as okay with a -gh flag, or move to your regular directory.")

if exe_proj:
    try:
        i7.go_proj(exe_proj)
    except:
        sys.exit("Could not find a path to", exe_proj)

my_file_list_valid = []

if in_file:
    if not os.path.isfile(in_file): sys.exit(in_file + " not found.")
    os.chdir(os.path.dirname(os.path.abspath(in_file)))
    mydir = os.getcwd()
    if edit_main_branch:
        print("Opening branch file", in_file)
        os.system(in_file)
    else:
        my_file_list_valid = [in_file]
        get_file(in_file)
        internal_postproc_stuff()
        postopen_stub()
    sys.exit()

if not exe_proj:
    myd = os.getcwd()
    if i7.dir2proj(myd):
        exe_proj = i7.dir2proj(myd, True)
        print("Going with project from current directory", exe_proj)
    else:
        if not def_proj:
            sys.exit("No default project defined, and I could not determine anything from the current directory or command line. Bailing.")
        print("Going with default", def_proj)
        exe_proj = def_proj

old_dir = os.getcwd()
new_dir = i7.proj2dir(exe_proj)
os.chdir(new_dir)

if os.path.normpath(old_dir).lower() != os.path.normpath(new_dir).lower():
    print("We changed PWD from {} to {}.".format(old_dir, new_dir))

if verify_nudges:
    q = glob.glob("reg-*.txt")
    nudge_overall = 0
    for q1 in q:
        if 'nudmis' in q1:
            print("Expected nudges in", q1)
            continue
        if 'nudges' in q1:
            print("Ignoring old nudge file", q1)
            continue
        if 'roi-' in q1: continue
        print("Checking nudges (generally valid for Stale Tales Slate only) for", q1)
        nudge_this = 0
        with open(q1) as file:
            for (line_count, line) in enumerate(file, 1):
                if should_be_nudge(line):
                    nudge_overall += 1
                    nudge_this += 1
                    print(nudge_overall, nudge_this, q1, line_count, "mis-assigned nudge-check:", line.strip())
    sys.exit()

for pa in poss_abbrev:
    proj2 = i7.i7xr[exe_proj] if exe_proj in i7.i7xr.keys() else exe_proj
    if proj2 in abbrevs[pa].keys():
        print("Adding specific file", abbrevs[pa][proj2], "from", proj2)
        my_file_list.append(abbrevs[pa][proj2])
    else:
        print(pa, 'has nothing for current project', exe_proj, 'but would be valid for', '/'.join(sorted(abbrevs[pa].keys())))

if edit_individual_files:
    for mf in my_file_list: os.system(mf)
    sys.exit()

if not len(my_file_list):
    my_file_list = list(branch_list[exe_proj])
    if len(my_file_list) == 0:
        print("No valid files specified. Checking rbr- glob.")
        my_file_list = glob.glob("rbr-*")
        if not len(my_file_list) and os.path.exists("testing"):
            print("Looking in testing subdir")
            os.chdir("testing")
            my_file_list = glob.glob("rbr-*")
        if len(my_file_list) == 0: sys.exit("No files found in rbr- glob. Bailing.")
        elif len(my_file_list) == 1: print("Only one rbr- file found ({}). Going with that.".format(my_file_list[0]))
        else:
            sys.exit("Can't handle multiple rbr files yet. I found {}".format(', '.join(my_file_list)))
    else:
        print("No valid files specified on command line. Going with default", ', '.join(branch_list[exe_proj]))

for x in my_file_list: # this is probably not necessary, but it is worth catching in case we do make odd files somehow.
    if os.path.exists(x): my_file_list_valid.append(x)
    else:
        print("Ignoring bad/nonexistent branch file", x)

if len(my_file_list_valid) == 0:
    sys.exit("Uh oh, no valid files left after initial check. Bailing.")

for x in my_file_list_valid:
    if branch_timestamp_skip_check and no_new_branch_edits(x):
        print("Skipping", x, "for no new edits.")
        continue
    get_file(x)

if len(apost_changes):
    for x in sorted(apost_changes, key=apost_changes.get, reverse=True):
        add_note = '(lower-case version is in apostrophes-to-ignore)' if x.lower() in apostrophes[exe_proj] else ''
        print(x, apost_changes[x], add_note)

internal_postproc_stuff()

postopen_stub()