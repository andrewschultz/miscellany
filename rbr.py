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
import codecs
from collections import defaultdict
from shutil import copy
from filecmp import cmp
import mytools as mt
import colorama

my_strings = defaultdict(str)
branch_variables = defaultdict(list)
branch_check = defaultdict(lambda: defaultdict(list))
to_match = defaultdict(str)
branch_list = defaultdict(list)
times = defaultdict(int)
abbrevs = defaultdict(lambda: defaultdict(str))
apostrophes = defaultdict(list)
generic_bracket_error = defaultdict(int)
okay_apostrophes = defaultdict(bool)
new_files = defaultdict(list)
changed_files = defaultdict(list)
unchanged_files = defaultdict(list)
absent_files = defaultdict(list)
postproc_if_changed = defaultdict(list)
ignores = defaultdict(str)
apost_changes = defaultdict(int)

rbr_wild_card = ''

branch_timestamp_skip_check = True

ignore_unsaved_changes = False
ignore_first_file_changes = False
force_postproc = False
github_okay = False
flag_all_brackets = True
edit_individual_files = False
verify_nudges = False
always_be_writing = False
edit_main_branch = False
debug = False
force_all_regs = False
strict_name_force_on = False
strict_name_force_off = False
wrong_check = False
show_unchanged = False
look_through_winmerge = False

max_undo_tracking = 10
start_line = 0
start_command = ''
max_flag_brackets = 0
cur_flag_brackets = 0
ignore_next_bracket = False
ignore_wrong_before = 0

quiet = False
copy_over_post = True

prt_color = colorama.Back.GREEN + colorama.Fore.WHITE + "PRT" + colorama.Style.RESET_ALL

rbr_bookmark_indices = ["loc", "room", "rm", #places
  "itm", "item", "thing", #things
  "npc", "per" #people
  ] #this is to give a lot of options for ###new so I don't have to remember anything too exact

in_file = ""
in_dir = os.getcwd()
exe_proj = ""

default_rbrs = defaultdict(str)

class branch_struct():

    def __init__(self, line_of_text):
        self.stability_check = False

        bail_after = False
        ary = line_of_text.strip().split(',')

        for vals in ary:
            if '=' not in vals:
                bail_after = True
                mt.warn("WARNING comma separated line needs a=b. Possible values are file=, abbr=, desc=, flags=.")
                mt.warn("    " + line_of_text.strip())
                mt.warn("    " + vals)
                continue
            ary2 = vals.split('=')
            if ary2[0] == 'file':
                self.output_name = ary2[1].lower()
            elif ary2[0] == 'abbr':
                self.list_of_abbrevs = ary2[1].lower().split('/')
            elif ary2[0] == 'desc':
                self.description = ary2[1]
            elif ary2[0] == 'flags':
                flag_array = ary[1].split('/')
                for f in flag_array:
                    if f == 'stable':
                        self.stability_check = True

        self.currently_writing = False
        self.hard_lock = False
        self.in_header = True

        self.current_buffer_string = ''
        self.any_changes = False
        self.branch_variables = defaultdict(int)

        if bail_after:
            sys.exit()

    def ready_to_write(self):
        if self.hard_lock or not self.currently_writing:
            return False
        return True

    def write_line(self, line_to_write):
        if self.ready_to_write():
            self.current_buffer_string += line_to_write

    def write_if_intersects(self, line_to_write, abbrev_array):
        if self.intersects(abbrev_array):
            self.currernt_buffer_string += line_to_write

    def intersects(self, abbrev_array):
        return not (not (set(abbrev_array) & set(self.list_of_abbrevs)))

    def zap_extra_spaces(self):
        self.current_buffer_string = re.sub("(\n{3,})", "\n\n", self.current_buffer_string)

    def check_changes(self):
        f = open(self.temp_out(), "w")
        f.write(self.current_buffer_string)
        f.close()
        if not os.path.exists(self.out_file()):
            return colorama.Fore.CYAN + 'New file created'
        if cmp(self.out_file(), self.temp_out()):
            return colorama.Fore.YELLOW + 'Unchanged'
        if self.stability_check and not ignore_first_file_changes:
            mt.fail("{} had changes. If they are acceptable, -f1.".format(self.out_file()))
            mt.wm(self.out_file(), self.temp_out())
            sys.exit()
        elif look_through_winmerge:
            mt.wm(self.out_file(), self.temp_out())
            if os.path.getmtime(self.out_file()) > os.path.getmtime(self.temp_out()):
                return colorama.Fore.RED + 'User inspected and changed'
            return colorama.Fore.MAGENTA + 'User inspected and unchanged'
        return colorama.Fore.GREEN + 'Changed'
        sys.exit() # temporary, as we look to shift to the branch class

    def out_file(self):
        return os.path.join(i7.proj2dir(exe_proj), self.output_name)

    def temp_out(self):
        return "c:\\writing\\temp\\delnew-{}".format(self.output_name)

    def variable_adjust(self, var_line, err_stub):
        if '+' not in var_line and '-' not in var_line and '=' not in var_line:
            mt.fail("ERROR need +/-/= in variable-adjust {}.".format(err_stub))
            return
        temp = var_line.replace(' ', '')

        my_var = re.sub("[-=\+].*", "", temp).upper()
        my_op = re.sub(".*?([-=\+]+).*", r'\1', temp)
        my_num = re.sub(".*?[-=\+]+", "", temp)

        if my_var not in self.branch_variables:
            if my_op != '=':
                mt.warn("WARNING tried to operate on undeclared variable {} {}.".format(my_var, err_stub))
                return
            self.branch_variables[my_var] = int(my_num)

        if my_num in branch_variables: # this is very bad at the moment as we could have VAR+=OTHERVAR, but for now we just use ==
            my_num = self.branch_variables[my_num]
        elif my_num:
            my_num = int(my_num)
        if my_op == "++":
            self.branch_variables[my_var] += 1
        elif my_op == "--":
            self.branch_variables[my_var] -= 1
        elif my_op == "=":
            self.branch_variables[my_var] = my_num
        elif my_op == "-=":
            self.branch_variables[my_var] -= my_num
        elif my_op == "+=":
            self.branch_variables[my_var] += my_num
        elif my_op == "=":
            self.branch_variables[my_var] = my_num
        else:
            mt.warn("{} {} {}.".format("Unknown operator" if len(my_op) < 3 else "Likely badly formed variable adjust", my_var, err_stub))

        return

def postopen_stub():
    print("Reminder that -np disables copy-over-post and -p enables it. Default is to copy the REG files over to the {} directory.".format(prt_color))
    mt.postopen_files()

def abbrevs_to_ints(my_ary, line_count = '(undef)'):
    my_ary_1 = [to_match[x] if x in to_match else x for x in my_ary]
    try:
        my_ary_2 = [int(x[1:]) for x in my_ary_1]
    except:
        return []
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

def make_new_reg(this_file, overwrite = False):
    this_proj = i7.dir2proj(to_abbrev = True)
    local_file_name = "reg-{}-{}.txt".format(this_proj, this_file)
    github_file_name = "{}\\Testing\\standalone\\{}".format(i7.proj2dir(this_proj, to_github = True), local_file_name)
    print("Opening", local_file_name)
    print("Opening", github_file_name)
    if os.path.exists(github_file_name):
        if overwrite:
            mt.warn("Overwriting", github_file_name)
        else:
            mt.warn(github_file_name, "exists. Skipping. Use -o to overwrite.")
            return
    f = open(github_file_name, "w")
    f.write("## r{}\n\
** game: /home/andrew/prt/debug-{}.z8\n\
** interpreter: /home/andrew/prt/dfrotz -m -w5000 -h25\n\n\
* main\n\n".format(local_file_name, i7.dir2proj()))
    f.close()
    mt.npo(github_file_name)
    sys.exit()

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
    for q in re.findall("\{[A-Z][A-Z0-9]+\}", my_line):
        #print(q, q[1:-1], branch_variables[q[1:-1]], branch_variables[q[1:-1]][file_idx])
        qt = q[1:-1]
        if qt not in branch_variables:
            if print_errs:
                mt.warn("Bad variable", qt, "at", line_count)
            if qt in my_strings:
                mt.okay("    Maybe just add a $ to {} as there is such a string variable.".format(qt))
            continue
        my_line = re.sub(q, str(branch_variables[q[1:-1]][file_idx]), my_line)
    return my_line

def string_fill(var_line, line_count):
    temp = var_line
    for q in re.findall("\{\$[A-Z][A-Z0-9]+\}", var_line):
        q0 = q[2:-1]
        if q0 not in my_strings:
            mt.warn("WARNING line {} unrecognized string {}.".format(line_count, q0)) #?? printed more than once e.g. put in a bogus string at end
            if q0 in branch_variables:
                mt.okay("    Maybe just get rid of the leading $ as there is a numerical variable {}.".format(q0))
            continue
        temp = re.sub("\{\$" + q0 + "\}", my_strings[q0], temp)
    return temp

def score_search(my_search):
    my_search = my_search.replace('.', ' ').replace('-', ' ')
    g = glob.glob("rbr-*.txt")
    blank_before = False
    for f in g:
        with open(f) as file:
            for (line_count, line) in enumerate(file, 1):
                if not line.strip():
                    blank_before = True
                    continue
                if blank_before and line.startswith(">") and my_search in line.lower():
                    mt.okay("Found score {} {}".format(f, line_count))
                    mt.add_post(f, line_count)
                blank_before = False
    mt.post_open()
    mt.warnbail("No scoring/command string found for {}.".format(my_search))

def apostrophe_check(line, line_count, warns):
    if line.startswith('#'):
        return False
    apost_line = i7.text_convert(line, erase_brackets = False, ignore_array = apostrophes[exe_proj], color_punc_change = True)
    if line == apost_line:
        return False
    print(warns + 1, "Possible apostrophe-to-quote change needed line", line_count)
    print("  Before:", line.strip())
    print("   After:", apost_line.strip())
    a1 = line.split(' ')
    a2 = apost_line.split(' ')
    mv = min(len(a1), len(a2))
    for x in range(0, mv):
        if "'" in a1[x] and a1[x].replace("'", '"') == a2[x]:
            apost_changes[a1[x]] += 1
    return True

def reg_verify_file(my_file, allow_edit = False):
    mb = os.path.basename(my_file)
    positive_found = fail_found = False
    retval = 0
    out_string = ''
    with codecs.open(my_file, encoding='utf8', errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('##') and re.sub("^#+ (file name: *)?", "", line).startswith('reg'):
                if mb in line:
                    positive_found = True
                    continue
                mt.fail("ERROR {} had mis-identifying line {} {}".format(mb, line_count, line.strip()))
                line = re.sub('reg-.*?txt', mb, line)
                retval = line_count
                fail_found = True
            if line.startswith('# ') and 'reg-' in line and not positive_found:
                mt.warn("ERROR {} needs ## to start, not # {} {}".format(mb, line_count, line.strip()))
                line = line.replace('# ', '## ', 1)
                fail_found = True
            out_string += line.rstrip() + "\n"
    if allow_edit and fail_found:
        rbr_temp_header = "c:\\writing\\temp\\delete-rbrheader.txt"
        f = open(rbr_temp_header, "w", encoding='utf8')
        f.write(out_string)
        f.close()
        mt.wm(my_file, rbr_temp_header)
        return 0
    if not positive_found and not fail_found:
        mt.warn("WARNING {} had no positive test file identification.".format(mb))
        return -1
    return retval

def reg_verify_dir(open_unmarked = False, bail = True, allow_edit = False):
    max_open = 5
    cur_open = 0
    actual_open = 0
    my_glob = glob.glob("reg-*.txt")
    if len(my_glob) == 0:
        if bail:
            sys.exit()
        return
    this_proj = i7.dir2proj(os.getcwd())
    print(this_proj, "has", len(my_glob), "REG files") # this is odd! Why do I have different results with the default?
    for g in my_glob:
        if g.endswith('.bak'):
            print(colorama.Fore.CYAN + "IGNORED backup file {}, which you probably want to delete.".format(g))
            continue
        temp = reg_verify_file(g, allow_edit = allow_edit)
        if temp < 1 and not open_unmarked:
            continue
        elif temp == 0:
            continue
        else:
            cur_open += 1
            if cur_open <= max_open:
                actual_open += 1
                mt.add_post(g, 1 if temp == -1 else temp)
            else:
                mt.warn("UNOPENED file needs fixing: {}".format(os.path.basename(g)))
    if cur_open == 0:
        mt.okay("All {} reg- files in {} verified as properly annotated.".format(len(my_glob), this_proj))
    else:
        print(colorama.Fore.BLUE + "{} opened of total {} to fix.".format(actual_open, cur_open) + mt.WTXT)
    mt.post_open()
    if bail:
        sys.exit()

def reg_verify_all_dirs(open_unmarked = False):
    for g in glob.glob("c:/games/inform/*.inform"):
        if not os.path.isdir(g):
            continue
        os.chdir(os.path.join(g, "source"))
        reg_verify_dir(open_unmarked, bail = False)
    sys.exit()

def extraneous_brackets(line):
    if line.startswith("#"):
        return False
    if ignore_next_bracket:
        return False
    if line.lower().startswith("[note"):
        return False
    if line.startswith('/'):
        return False
    return '[' in line or ']' in line

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
    if extraneous_brackets(line):
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

def post_copy(in_file, file_array = []):
    if copy_over_post:
        if force_all_regs:
            print("Copying all files over to {} directory.".format(prt_color))
            for q in file_array: copy(q, os.path.join(i7.prt, os.path.basename(q)))
        elif len(changed_files.keys()):
            print("Copying changed files over to {} directory.".format(prt_color))
            for q in list(changed_files.keys()):
                mt.okay(q, "=>", ', '.join(changed_files[q]))
                for r in changed_files[q]:
                    copy(r, os.path.join(i7.prt, os.path.basename(r)))
                #changed_files.pop(q)
        elif len(absent_files.keys()):
            print("Copying files not in {} over to {} directory.".format(prt_color, prt_color))
            for q in list(absent_files.keys()):
                mt.okay(q, "=>", ', '.join([x[1] for x in absent_files[q]]))
                for r in absent_files[q]:
                    copy(r[0], r[1])
                #absent_files.pop(q)
        elif len(my_file_list_valid) == 1:
            print(colorama.Fore.YELLOW + "No files copied over to {} directory.".format(prt_color + colorama.Fore.YELLOW) + colorama.Style.RESET_ALL, "Try -fp or -pf to force copying of all files encompassed by", in_file)

def usage():
    print("-er = edit branch file (default = for directory you are in)")
    print("-e = edit rbr.txt")
    print("-c = edit rbr.py")
    print("-d = debug on")
    print("-f = flag all brackets")
    print("-q = Quiet")
    print("-np = no copy over post, -p = copy over post (default)")
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

# most clear difference = 58 (53 is usual) for require UPPERCASE and require trailing space
command_requirements = 0b110101
max_cmd_req = (1<<6) - 1
CMD_REQUIRE_LOWERCASE = 1
CMD_REQUIRE_UPPERCASE = 2
CMD_REQUIRE_NOTRAILINGSPACE = 4
CMD_REQUIRE_TRAILINGSPACE = 8
CMD_REQUIRE_PERIOD_ZAP = 16
CMD_REQUIRE_HYPHEN_ZAP = 32

def bad_command(my_line):
    my_line = re.sub(" *#.*", "", my_line)
    if not my_line.strip().startswith('>'):
        return ''
    if command_requirements & CMD_REQUIRE_LOWERCASE:
        if my_line != my_line.lower():
            return "needs all lower case"
    if command_requirements & CMD_REQUIRE_UPPERCASE:
        if my_line != my_line.upper():
            return "needs all upper case"
    if command_requirements & CMD_REQUIRE_NOTRAILINGSPACE:
        if ' >' in my_line or '> ' in my_line:
            return "needs to zap space before/after >"
    if command_requirements & CMD_REQUIRE_TRAILINGSPACE:
        if '>' in my_line and '> ' not in my_line and ' >' not in my_line:
            return "needs inserted space before/after >"
    if command_requirements & CMD_REQUIRE_PERIOD_ZAP:
        if '.' in my_line:
            return "needs to zap period"
    if command_requirements & CMD_REQUIRE_HYPHEN_ZAP:
        if '-' in my_line:
            return "needs to zap hyphen"
    return ''

def bracket_ignore_next(my_line):
    mll = my_line.lower()
    return mll.startswith("#brackets ok") or mll.startswith("#ok brackets") or mll.startswith("#ignore next bracket") or mll.startswith("#ignore bracket")

def get_file(fname):
    global absent_files
    global changed_files
    global ignore_next_bracket
    global command_requirements
    if not os.path.isfile(fname):
        sys.exit(in_file + " not found.")
    fb = os.path.basename(fname)
    if (not ignore_unsaved_changes) and mt.is_npp_modified(fname):
        print("It looks like {} has been modified without saving. You may wish to run the script. -iuc overrides this.".format(fb))
    local_branch_dict = defaultdict(branch_struct)
    got_any_test_name = False
    warns = 0
    last_cmd = ""
    file_output = defaultdict(str)
    file_descriptions = []
    file_array = []
    file_array_base = []
    line_count = 0
    temp_diverge = False
    if not quiet: print("Poking at", fname)
    old_actives = []
    preproc_commands = []
    at_section = ''
    last_at = 0
    last_eq = 0
    warns_so_far = 0
    to_match.clear()
    last_atted_command = ""
    untested_commands = defaultdict(list)
    untested_ignore = list(ignores['global'])
    untested_ignore.extend(x for x in ignores[proj_of(fname)] if x not in ignores['global'])
    untested_default = list(untested_ignore)
    wrong_lines = []
    last_cmd_line = -1
    branch_variables.clear()
    found_start = False
    balance_undos = False
    track_balance_undos = False
    ignore_extra_undos = False
    temp_diverge_warned = False
    ignore_next_balance = False
    skip_apostrophe_check = False
    need_start_command = (start_command != '')
    is_last_blank = False
    last_line = ''
    old_grouping = ''
    in_grouping = False
    flag_wrong_at_end = 0
    fatal_error = False
    with open(fname) as file:
        for (line_count, line) in enumerate(file, 1):
            llo = line.lower()
            if line.startswith("====alphabetize"): # this is to work in conjunction with ttc
                continue
            if line.startswith("cmdflags="):
                try:
                    cmd_temp = int(re.sub(".*=", "", line).strip())
                    if cmd_temp > max_cmd_req or cmd_temp < 0:
                        print("WARNING CMDFLAGS should be between 0 and {} at line but is {}", max_cmd_req, line_count, cmd_temp)
                    command_requirements = cmd_temp
                except:
                    print("WARNING invalid CMDFLAGS at line", line_count, line.strip())
                continue
            if line.startswith("=>"):
                line = line[1:] # cheap trick so I can search for priority point-scoring
            if line.startswith("@"):
                line = line.strip()
                flag_repeat_groupings = True
                if line.endswith("+"):
                    flag_repeat_groupings = False
                    line = re.sub("\++$", "", line)
                if flag_repeat_groupings and old_grouping == line[1:]:
                    mt.warn("Two groupings can/should be merged, or you should put a + after. The second is \"{}\" at line {}.".format(line[1:].strip(), line_count))
                    mt.add_postopen(fname, line_count, priority=5)
                    if in_grouping:
                        continue
                elif not flag_repeat_groupings and not (old_grouping == line[1:]):
                    mt.warn("False repeat grouping marker for {} at line {}".format(line[1:], line_count))
                    mt.add_postopen(fname, line_count, priority=5)
                    if in_grouping:
                        continue
                in_grouping = True
                old_grouping = line[1:]
            elif not line.strip():
                in_grouping = False
            elif not in_grouping:
                old_grouping = ""
            if last_line.startswith("@") and line.startswith('\\\\'):
                print("WARNING \\\\ follows @ section start in {} at line {}.".format(fb, line_count))
                mt.add_postopen(fname, line_count - 1, priority=3)
            if last_line == '\\\\' and not line.strip():
                print("WARNING \\\\ followed by blank line in {} at line {}.".format(fb, line_count))
                mt.add_postopen(fname, line_count - 1, priority=3)
            last_line = line.strip()
            if ignore_next_bracket and not '[' in line and not ']' in line:
                print("WARNING Extraneous OK-BRACKETS {} line {}.".format(fb, line_count - 1))
                mt.add_postopen(fname, line_count - 1, priority=3)
            line_orig = line.strip()
            if is_last_blank and not line_orig:
                print("WARNING (trivial) double spacing at line {} of {}.".format(line_count, fb))
                mt.add_postopen(fname, line_count - 1, priority=2)
            is_last_blank = not line_orig
            temp = bad_command(line)
            if temp:
                print("WARNING bad command at line {} of {}: {} {}".format(line_count, fb, line_orig, temp))
                mt.add_postopen(fname, line_count, priority=7)
            if line.startswith("==") or line.startswith("@"):
                if any(x.isdigit() for x in line):
                    mt.warn("Numbers are not allowed in branch names. Use -a or -b instead of 1 or 2. {} {} attempt to create section failed.")
                    mt.add_postopen(fname, line_count, priority=8)
                    continue
            if llo.startswith("##nobalance"):
                ignore_next_balance = True
            if llo.startswith("##balance undo"):
                if balance_undos:
                    mt.warn("WARNING {} line {}: another balance-undo block is already operational. Add AGAIN to line to avoid this warning.".format(fb, line_count))
                    if len(balance_trace):
                        mt.fail("Not only that, but undos are imbalanced. You have {} commands left over.".format(len(balance_trace)))
                balance_error_yet = False
                balance_undos = True
                track_balance_undos = 'trace' in line or 'track' in line
                ignore_extra_undos = 'ignore-neg' in line
                balance_trace = []
                balance_start = line_count
                continue
            elif balance_undos and line.startswith("#balance undo"):
                print("WARNING {} line {}: need double-pound sign before balance undo.".format(fb, line_count))
                mt.add_postopen(fname, line_count, priority=7)
            if line.startswith("##end undo") or line.startswith("##end balance undo") or (balance_undos and line.startswith('@!')):
                if len(balance_trace):
                    mt.fail("ERROR net undos at end of block that needs to be balanced = {}. Lines {}-{} file {}.{}".format(len(balance_trace), balance_start, line_count, fname, '' if track_balance_undos else ' Add TRACK/TRACE to balance undo comment to trace things.'))
                    mt.add_postopen(fname, line_count)
                balance_undos = False
                if not line.startswith('@!'):
                    continue
            if potentially_faulty_regex(line):
                print("WARNING {} line {} may need starting slash for regex:{}".format(fname, line_count, line_orig))
            if is_rbr_bookmark(line) or line.startswith("###"): #triple comments are ignored
                if "#skip test checking" in line:
                    last_atted_command = ""
                continue
            if line.strip() == "==!" or line.strip() == "@!":
                for b in local_branch_dict:
                    local_branch_dict[b].currently_writing = not local_branch_dict[b].currently_writing
                continue
            if (line.startswith('@') and not line.startswith('@@')):
                my_val = True
                if line[1] == '!':
                    my_val = False
                    my_ary = line[2:].strip().split(',')
                else:
                    my_ary = line[1:].strip().split(',')
                for b in local_branch_dict:
                    local_branch_dict[b].currently_writing = my_val if local_branch_dict[b].intersects(my_ary) else not my_val
                at_section = mt.zap_comment(line[1:].lower().strip()) # fall through, because this is for verifying file validity--also @specific is preferred to ==t2
                last_at = line_count
                continue
            elif line.startswith('@@') or not line.strip():
                if found_start:
                    for b in local_branch_dict:
                        local_branch_dict[b].write_line("\n")
                        local_branch_dict[b].currently_writing = True
                if at_section and last_atted_command:
                    if viable_untested(last_atted_command,untested_ignore):
                        untested_commands[last_atted_command].append(last_cmd_line)
                        mt.add_postopen(fname, line_count, priority=10)
                        last_atted_command = ''
                at_section = ''
                if balance_undos:
                    if len(balance_trace):
                        mt.fail("ERROR net undos at end of block that needs to be balanced = {}. Lines {}-{} file {}.{}".format(len(balance_trace), balance_start, line_count, fname, '' if track_balance_undos else ' Add TRACK/TRACE to balance undo comment to trace things.'))
                        mt.add_postopen(fname, line_count)
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
                if not '}' in line:
                    mt.warn("Line {} needs a }.".format(line_count))
                    mt.add_post(fname, line_count)
                    continue
                line_ary = line[3:].split('}', 1)
                vta_before = line_ary[0]
                vta_after = line_ary[1].rstrip()
                if not (vta_after.startswith('#') or vta_after.startswith('>')):
                    last_atted_command = ''
                try:
                    temp_file_fullname_array = abbrevs_to_ints(vta_before[3:].split(","), line_count)
                except:
                    mt.warn("Bad init-array line {}. Sample: file=reg-bbgg-thru-min.txt,min,minimum walkthrough,stable".format(line_count))
                    mt.warn("    " + llo)
                    mt.npo(fname, line_count)
                if "\\n" in line:
                    print("WARNING {} line {} needs \\\\ and not \\n for line-changes for temporary one-line edit.".format(fname, line_count))
                    mt.add_post(fname, line_count)
                u = vta_after.replace("\\\\", "\n") + "\n"
                paths_array = vta_before.split(',')
                for b in local_branch_dict:
                    local_branch_dict[b].write_if_intersects(u, paths_array)
                for q in temp_file_fullname_array:
                    file_output[file_array[q]] += u
                continue
            if line.startswith("WRONG"):
                if wrong_check:
                    if line_count > ignore_wrong_before:
                        mt.fail("WARNING we have a WRONG currently needing replacement at line {}.".format(line_count))
                        mt.add_postopen(fname, line_count, priority = 6)
                    else:
                        print(colorama.Fore.CYAN + "WARNING we have a WRONG eventually needing replacement at line {} before the user-chosen start line {}.".format(line_count, ignore_wrong_before))
                else:
                    flag_wrong_at_end += 1
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
            if line.startswith("#OK-APOSTROPHE") or line.startswith("#APOSTROPHE-OK") or line.startswith("#OK APOSTROPHE") or line.startswith("#APOSTROPHE OK"):
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
                sys.exit("~ with tab spotted. Please rejig the file into the a=b,c=d format.")
            if bracket_ignore_next(line):
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
            if line.startswith('#--'):
                if line.startswith("#--stable"):
                    mt.warn("#--stable has been deprecated. Specifying a stable file or files should go in the flags instead.")
                    mt.add_post(fname, line_count)
                if line.startswith("#--strict"):
                    mt.warn("#--strict has been deprecated. What was strict is now standard: we use descriptions and not numbers, because it's easier.")
                    mt.add_post(fname, line_count)
                continue
            if "file=" in line and not found_start:
                my_array = [re.sub("^.*?=", "", x) for x in line.strip().split(',')]
                temp_idx = my_array[1].split('/')[0]
                local_branch_dict[temp_idx] = branch_struct(line.strip())
                long_name = prt_temp_loc(my_array[0])
                file_array_base.append(my_array[0])
                file_output[long_name] = ''
                ary2 = my_array[1].split('/')
                for a in ary2:
                    if a in to_match:
                        print(to_match, "WARNING redefinition of shortcut {} at line {} of file {}".format(a, line_count, fb))
                    to_match[a] = 't{}'.format(len(file_array))
                file_array.append(long_name)
                try:
                    file_descriptions.append(my_array[2])
                except:
                    mt.fail("{} line {} does not have 3 entries.".format(fname, line_count))
                    mt.npo(fname, line_count)
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
                continue
            if line.startswith("}}"):
                if len(file_array) == 0:
                    mt.fail("RBR.PY requires }} variable meta-commands to be after files=, because even initialization is tricky.\nWe could, of course, have a list of initialized variables once file= hits, but that'd be a bit of programming I don't want to deal with right now.")
                    mt.npo(fname, line_count)
                    continue
                for b in local_branch_dict:
                    local_branch_dict[b].variable_adjust(line[2:].strip(), "at line {} in {}".format(line_count, fname))
                last_atted_command = ""
                continue
            if not len(file_array): continue # allows for comments at the start
            if line.startswith(")"):
                print("WARNING line starting with ) may need to start with } instead.", fname, line_count)
            if line.startswith("{{"):
                print("WARNING line starting with {{ may need to start with } instead.", fname, line_count)
            if line.startswith("}$"):
                temp_ary = line[2:].strip().split("=")
                my_strings[temp_ary[0]] = '='.join(temp_ary[1:])
                last_atted_command = ''
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
                elif not ignore_too_short and len(l2) < 1:
                    print("WARNING line", line_count, "doesn't cover all files. Change TSV to TSVI to ignore this.")
                    print("TEXT:", line.strip())
                    for x in range(0, len(file_array)):
                        print(l2[x] if x < len(l2) else '?', '~', os.path.basename(file_array[x]))
                for x in range(len(l2)):
                    file_output[file_array[x]] += l2[x] + "\n"
                continue
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
                        if not balance_error_yet and len(balance_trace) > max_undo_tracking:
                            balance_error_yet = True
                            print("Net undos over {} in balanced block line {} file {}--Inform may not be able to go that far back.".format(max_undo_tracking, line_count, fname))
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
            if line.startswith("=one="):
                la = line[5:].split("\t")
                temp_actives = [False] * len(file_array)
                string_out = re.sub(r"\\{2,}", "\n", la[1])
                for x in la[int(0)].split(","): temp_actives[int(x)] = True
                for x in range(0, len(file_array)):
                    if temp_actives[x]: file_output[x] += string_out
                continue
            if line.startswith("===") and not is_equals_header(line):
                mt.warn("WARNING: unmatched triple-equals at {} line {}.".format(fb, line_count))
                continue
            if line.startswith("==") and not is_equals_header(line):
                mt.warn("Uh oh {} line {} may be a bad branch-file redirector: {}".format(fname, line_count, line.strip()))
                warns += 1
                continue
            if debug and line.startswith(">"):
                print("YES", ','.join([b for b in local_branch_dict if local_branch_dict[b].ready_to_write()]), "NO", ','.join([b for b in local_branch_dict if not local_branch_dict[b].ready_to_write()]), line.rstrip())
            if last_atted_command and not line.startswith("#") and not line.startswith(">"):
                last_atted_command = ''
            first_file = True
            if line.startswith("~="):
                line = line.replace("~", "=") # hack to allow ==== headers
            if not len(file_descriptions):
                mt.fail(fname, "needs the new file descriptions. See bbkk, the first to be converted.")
                mt.fail("A blueprint below:")
                mt.fail("  files= must be split up into lines.")
                mt.fail("  the TSV (tab separated values) going to the end of each.")
                mt.failbail("  CSV's in ~t2, etc. should be converted to slashes.")
            for b in local_branch_dict:
                myb = local_branch_dict[b]
                if (myb.in_header):
                    if ("*FILE" in line):
                        found_start = True
                        myb.in_header = False
                        myb.currently_writing = True
                    else:
                        continue
                if not myb.currently_writing and not myb.hard_lock:
                    continue
                line_write = re.sub("\*file", myb.output_name, line, 0, re.IGNORECASE)
                line_write = re.sub("\*fork", "GENERATOR FILE: " + os.path.basename(fname), line_write, 0, re.IGNORECASE)
                line_write = re.sub("\*description", myb.description, line_write, 0, re.IGNORECASE)
                if "{$" in line_write:
                    line_write = string_fill(line_write, line_count)
                if "{" in line_write:
                    line_write = fill_vars(line_write, ct, line_count, first_file)
                local_branch_dict[b].current_buffer_string += line_write
    if not found_start and fb.startswith('rbr'):
        mt.fail("Did not have start command *FILE. Not copying files over.")
        return []
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
    if warns > 0 and not quiet:
        print(warns, "potential bad commands in {}.".format(fname))

    categorizer = defaultdict(list)

    for b in local_branch_dict:
        local_branch_dict[b].zap_extra_spaces()
        f = open(local_branch_dict[b].temp_out(), "w")
        f.write(local_branch_dict[b].current_buffer_string)
        f.close()
        categorizer[local_branch_dict[b].check_changes()].append(local_branch_dict[b].output_name)

    for c in categorizer:
        print(c + ':', ', '.join(categorizer[c]) + colorama.Style.RESET_ALL)

    sys.exit()

    if fatal_error:
        mt.fail("Found fatal error. Not copying files over.")
        return 0
    past_first_file = False
    for x in file_array:
        f = open(x, "w")
        # modifications below to avoid extra spacing. While we could define in_header, sweeping things up with a REGEX is probably easier
        modified_output = re.sub("\n{3,}", "\n\n", file_output[x]) # get rid of extra carriage return spacing
        modified_output = re.sub("^\n+", "", modified_output) # get rid of spacing at the start
        #modified_output = re.sub("\n+\*\*", "\n**", modified_output) # get rid of spacing in the header
        f.write(modified_output)
        f.close()
        if not past_first_file: #temporarily assume first file is strict no-change
            past_first_file = True
            xb = os.path.basename(x)
            if not os.path.exists(xb):
                mt.fail("I could not find {}. It should be in the temp directory. You may wish to disable --stable in the RBR file or type:".format(x))
                mt.fail("    copy {} {}".format(x, xb))
                sys.exit()
            if not cmp(x, xb):
                if not ignore_first_file_changes:
                    mt.fail("#--stable was set. Difference(s) found in main file {}, which was meant to be stable. Windiff-ing then exiting. Use -f1 to allow these changes.".format(xb))
                    mt.wm(x, xb)
                    sys.exit()
                else:
                    mt.warn("Difference(s) found in main file {} but overriden by -f1 command line parameter.".format(xb))
        xb = os.path.basename(x)
        prt_mirror = os.path.join(i7.prt, xb)
        if not os.path.exists(xb):
            new_files[fname].append(xb)
            try:
                copy(x, xb)
            except:
                print("Could not copy temp file", x, "to local file", xb)
                if os.path.islink(xb):
                    print("The problem might be a symlink directed to the wrong file or directory. Look for typos or a forgotten c: at the start.")
        elif not os.path.exists(prt_mirror):
            absent_files[fname].append((xb, prt_mirror))
        elif cmp(x, xb):
            unchanged_files[fname].append(xb)
        else:
            if xb in changed_files:
                print("Oh no! two RBR files seem to point to", xb)
                continue
            changed_files[fname].append(xb)
            copy(x, xb)
        os.remove(x)
        file_output.pop(x)
    for x in file_output:
        mt.fail("WARNING: there may be leftover output for the file_output key {}.".format(x))
    if flag_wrong_at_end:
       print(colorama.Fore.CYAN + "{} WRONG line{} {} found. Use -wc to track them and potentially open the first error.".format(flag_wrong_at_end, mt.plur(flag_wrong_at_end)
       , mt.plur(flag_wrong_at_end, [ 'were', 'was' ])) + colorama.Style.RESET_ALL)
    if not got_any_test_name and os.path.basename(fname).startswith('rbr'):
        print("Uh oh. You don't have any test name specified with * main-thru for {}".format(fname))
        print("Just a warning.")
    return len(absent_files) + len(changed_files)

def valid_point_check(my_line):
    if line.startswith('by one point') or line.startswith('by a point'):
        return True
    if re.sub("^by [a-z]+ points", line):
        return True
    return False

def scrape_cmds(my_file, my_cmds, add_after = True): # this looks for a point-scoring/point scoring command
    retval = False
    need_point = False
    add_edit = False
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if valid_point_check(line) and need_point:
                if add_after:
                    add_edit = True
                else:
                    mt.add_post(my_file, line_count - 2)
                retval = True
                continue
            if not line.strip():
                if add_edit:
                    mt.add_post(my_file, line_count)
                need_point = False
                continue
            if not line.startswith(">"):
                continue
            for x in my_cmds:
                if x in line:
                    need_point = True
    return retval

def show_csv(my_dict, my_msg):
    ret_val = 0
    for q in my_dict:
        lmd = len(my_dict[q])
        print("{} {}{} from {}: {}".format(lmd, my_msg, mt.plur(lmd), q, ', '.join(sorted(my_dict[q]))))
        ret_val += lmd
    return ret_val

def internal_postproc_stuff(anything_changed):
    total_csv = show_csv(new_files, "new file") + show_csv(changed_files, "changed file")
    if show_unchanged:
        total_csv += show_csv(unchanged_files, "unchanged file")
    if anything_changed or force_postproc:
        run_postproc = defaultdict(bool)
        if not anything_changed: print("Forcing postproc even though nothing changed.")
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
    changed_files.clear()
    absent_files.clear()

cur_proj = ""
mwrites = defaultdict(lambda: defaultdict(bool))

def_proj = i7.curdef

with open(i7.rbr_config) as file:
    for (lc, line) in enumerate(file, 1):
        if line.startswith(';'): break
        if line.startswith('#'): continue
        lr = line.strip()
        ll = lr.lower()
        if '>' in ll[1:] and '<' not in ll[1:]:
            print("WARNING: possible erroneous cut and paste. Line", lc, "may need line break before command prompt:", line.strip())
        var_array = wipe_first_word(ll)
        if ll.startswith('dupe'):
            ja = var_array.split("\t")
            times[ja[0]] = int(ja[1])
            continue
        if ll.startswith('default'):
            if def_proj == i7.main_abb(var_array):
                mt.warn("NOTE: we are redefining the rbr-specific default in rbr.txt to the general default in i7p.txt. This is harmless overkill.")
            def_proj = i7.main_abb(var_array)
            continue
        if ll.startswith('project') or ll.startswith('projname'):
            cur_proj = i7.main_abb(var_array)
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
            default_rbrs[cur_proj] = var_array
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
            branch_list[cur_proj] = var_array.split(",")
            if cur_proj in i7.i7xr.keys(): branch_list[i7.i7xr[cur_proj]] = var_array.split(",")
            if cur_proj in i7.i7x.keys(): branch_list[i7.i7x[cur_proj]] = var_array.split(",")
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
        j = ll.split("\t")
        if len(j) < 2:
            mt.warn("Need tab in", line.strip())
            continue
        hk = i7.lpro(j[0])
        branch_list[j[0]] = j[1]
        if hk:
            print(hk, j[1])
            branch_list[hk] = j[1]
        else:
            print(j[0], hk, "not recognized as project or shortcut")

count = 1

cmds_to_find = []

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
    elif arg == 'q': quiet = True
    elif arg == 'su': show_unchanged = True
    elif arg in ( 'nsu', 'sun') : show_unchanged = False
    elif arg in ( 'nq', 'qn' ): quiet = False
    elif arg == 'np': copy_over_post = False
    elif arg == 'p': copy_over_post = True
    elif arg == 'fp': force_postproc = True
    elif arg in ( 'w', 'wc', 'cw' ):
        wrong_check = True
    elif arg[:3] in ( 'pt=', 'pt:' ) or arg[:2] in ( 'p=', 'p:' ):
        cmds_to_find.append(re.sub("^.*?[=:]", "", arg).replace('-', ' ').replace('.', ' '))
    elif arg[0] == 'w' and arg[1:].isdigit():
        wrong_check = True
        ignore_wrong_before = int(arg[1:])
    elif arg[:2] in ( 'wc', 'cw' ) and arg[2:].isdigit():
        wrong_check = True
        ignore_wrong_before = int(arg[2:])
    elif arg.startswith('m:') or arg.startswith('m='):
        for a in arg[2:].split(','):
            make_new_reg(arg[2:], overwrite = False)
        sys.exit()
    elif arg.startswith('mo:') or arg.startswith('mo='):
        for a in arg[3:].split(','):
            make_new_reg(arg[3:], overwrite = True)
        sys.exit()
    elif arg[:2] == 'sl': start_line = int(arg[2:])
    elif arg[:3] == 'sc:': start_command = arg[3:].replace('-', ' ')
    elif arg in ( 'wcn', 'nwc', 'nw', 'wn'): wrong_check = False
    elif arg == 'f1': ignore_first_file_changes = True
    elif arg == 'st': strict_name_force_on = True
    elif arg in ( 'nst', 'stn'): strict_name_force_off = True
    elif arg in ( 'pf', 'pc', 'cp' ): copy_over_post = force_all_regs = True
    elif arg == 'iuc':
        ignore_unsaved_changed = True
    elif arg.startswith('='):
        rbr_wild_card = arg[1:]
    elif arg.startswith('p='):
        if exe_proj: sys.exit("Tried to define 2 projects. Do things one at a time.")
        exe_proj = i7.i7x[arg[2:]]
    elif arg in i7.i7x.keys():
        if exe_proj: sys.exit("Tried to define 2 projects. Do things one at a time.")
        exe_proj = i7.i7x[arg]
    elif can_make_rbr(arg, verbose = True): in_file = can_make_rbr(arg)
    elif arg == 'gh': github_okay = True
    elif arg in ( 'rv', 'vr' ):
        reg_verify_dir(open_unmarked = False)
    elif arg in ( 'rva', 'vra' ):
        reg_verify_dir(open_unmarked = True)
    elif arg in ( 'rve', 'vre' ):
        reg_verify_dir(open_unmarked = True, allow_edit = True)
    elif arg == 'rv*':
        for a in i7.i7xr:
            try:
                i7.go_proj(a)
                reg_verify_dir(open_unmarked = True, allow_edit = True)
            except:
                pass
        sys.exit()
    elif mt.alfmatch('rv<d', arg):
        reg_verify_all_dirs(open_unmarked = False)
    elif mt.alfmatch('rv|ad', arg):
        reg_verify_all_dirs(open_unmarked = True)
    elif arg == '?': usage()
    elif arg in abbrevs.keys(): poss_abbrev.append(arg)
    elif arg[0] == 'f':
        flag_all_brackets = True
        if arg[1:].isdigit():
            max_flag_brackets = int(arg[1:])
    elif arg[:2] == 's:' or arg[:2] == 's=':
        score_search(arg[2:])
    elif arg == 'wm':
        look_through_winmerge = True
    else:
        print("Bad argument", count, arg)
        print("Possible projects: ", ', '.join(sorted(branch_list.keys())))
        usage()
        sys.exit()
    count += 1

if strict_name_force_on and strict_name_force_off:
    sys.exit("Conflicting force-strict options on command line. Bailing.")

my_dir = os.getcwd()

if my_dir == i7.prt:
    sys.exit("Can't run from the {} directory. Move to an Inform source directory.".format(prt_color))

if 'github' in my_dir.lower():
    newpath = i7.proj2dir(i7.dir2proj(), bail_if_nothing = True)
    if newpath:
        mt.warn("Moving to non-github directory {}, since the REG files created may fork.".format(newpath))
        os.chdir(newpath)
    elif not github_okay:
        mt.bailfail("GITHUB is in your path. Mark this as okay with a -gh flag, or move to your regular directory. You probably want to move to the non-github directory.")

if exe_proj:
    try:
        i7.go_proj(exe_proj)
    except:
        sys.exit("Could not find a path to", exe_proj)

my_file_list_valid = []

if not exe_proj: # I moved this and chdir above if in_file. It should be okay, but I note it for later reference.
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

if in_file:
    os.chdir(os.path.dirname(os.path.abspath(in_file)))
    mydir = os.getcwd()
    if edit_main_branch:
        print("Opening branch file", in_file)
        os.system(in_file)
    else:
        my_file_list_valid = [in_file]
        temp = get_file(in_file)
        post_copy(in_file)
        internal_postproc_stuff(temp > 0)
        postopen_stub()
    sys.exit()

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

if cmds_to_find:
    for x in my_file_list:
        scrape_cmds(x, cmds_to_find)
    mt.open_post(empty_flags = mt.NOTE_EMPTY)
    sys.exit()

for x in my_file_list: # this is probably not necessary, but it is worth catching in case we do make odd files somehow.
    if os.path.exists(x):
        my_file_list_valid.append(x)
    else:
        print("Ignoring bad/nonexistent branch file", x)

if len(my_file_list_valid) == 0:
    sys.exit("Uh oh, no valid files left after initial check. Bailing.")

sweeping_changes = 0

for x in my_file_list_valid:
    if branch_timestamp_skip_check and no_new_branch_edits(x):
        print("Skipping", x, "for no new edits.")
        continue
    if rbr_wild_card and rbr_wild_card not in x:
        print("Skipping", x, "which does not match wild card.")
        continue
    sweeping_changes += get_file(x)
    post_copy(x)

if len(apost_changes):
    print("FLAGGED APOSTROPHE CHANGES/SUGGESTIONS/FREQUENCY (#OK-APOSTROPHE or #APOSTROPHE-OK to allow")
    for x in sorted(apost_changes, key=apost_changes.get, reverse=True):
        add_note = '(lower-case version is in apostrophes-to-ignore)' if x.lower() in apostrophes[exe_proj] else ''
        print(x, apost_changes[x], add_note)

internal_postproc_stuff(sweeping_changes)

postopen_stub()