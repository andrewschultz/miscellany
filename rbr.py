# rbr.py: regression brancher
#
# takes an rbr*.txt file and separates it into many reg-*
#
# usage rbr.py (project name) e.g. rbr.py ai
#
# or you can run it from a project source directory
#

# todo: keep postproc commands ordered
# todo: postproc globs inside file_array

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

my_strings = defaultdict(str)
branch_variables = defaultdict(list)
to_match = defaultdict(str)
monty_detail = defaultdict(str)
branch_list = defaultdict(list)
times = defaultdict(int)
abbrevs = defaultdict(lambda: defaultdict(str))
generic_bracket_error = defaultdict(int)

new_files = defaultdict(bool)
changed_files = defaultdict(bool)
unchanged_files = defaultdict(bool)

ignore_first_file_changes = False
force_postproc = False
github_okay = False
flag_all_brackets = False
edit_individual_files = False
verify_nudges = False
always_be_writing = False
edit_main_branch = False
debug = False
monty_process = False
force_all_regs = False

max_flag_brackets = 0
cur_flag_brackets = 0

quiet = False
copy_over_post = True

rbr_bookmark_indices = ["loc", "room", "rm", #places
  "itm", "item", "thing", #things
  "npc", "per" #people
  ] #this is to give a lot of options for ###new so I don't have to remember anything too exact

in_file = ""
in_dir = os.getcwd()
proj = ""

show_singletons = False

default_rbrs = defaultdict(str)

def can_make_rbr(x, verbose = False):
    if os.path.exists(x): return x
    x = mt.nohy(x)
    if x in default_rbrs:
        return default_rbrs[x]
    if os.path.exists(x + ".txt"):
        if verbose: print(x, "doesn't exist but {}.{} does. Adding extension.".format(x, "txt"))
        return x + ".txt" # small but real possibility there may be something like vv.txt which would mess things up
    return ""

def prt_temp_loc(x):
    return os.path.normpath(os.path.join(i7.prt_temp, x))

def is_equals_header(x):
    x = x.strip()
    if x.startswith('===') and x.endswith('==='):
        if len(re.findall("[a-zA-Z]", x)): return True
    return False

def is_rbr_bookmark(x):
    x0 = x.lower()
    for ind in rbr_bookmark_indices:
        if x0.startswith("#") and "##new" + ind in x0: return True
    return False

def should_be_nudge(x):
    if not x.startswith('#'): return False
    if x.startswith('##'): return False
    if re.search("(spechelp|mistake|nudge)", x): return True
    return False

def fill_vars(my_line, file_idx):
    for q in re.findall("\{[A-Z]+\}", my_line):
        #print(q, q[1:-1], branch_variables[q[1:-1]], branch_variables[q[1:-1]][file_idx])
        my_line = re.sub(q, str(branch_variables[q[1:-1]][file_idx]), my_line)
    return my_line

def string_fill(var_line):
    temp = var_line
    for q in re.findall("\{\$[A-Z]+\}", var_line):
        q0 = q[2:-1]
        if q0 not in my_strings:
            print("WARNING unrecognized string {}.".format(q0))
            continue
        temp = re.sub("\{\$" + q0 + "\}", my_strings[q0], temp)
    return temp

def branch_variable_adjust(var_line, err_stub, actives):
    temp = var_line.replace(' ', '')
    #print("temp", temp)
    my_var = re.sub("[-=\+].*", "", temp).upper()
    my_op = re.sub(".*?([-=\+]+).*", r'\1', temp)
    my_num = re.sub(".*?[-=\+]+", "", temp)
    if my_num:
        my_num = int(my_num)
    else:
        my_num = 0
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
        branch_variables[my_var] = [my_num] * len(actives)
    #print("Before:", my_var, branch_variables[my_var])
    for q in range(0, len(actives)):
        if not actives[q]: continue
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
            print("Unknown operator {} {}.".format(my_var, err_stub))
    #print("After:", my_var, branch_variables[my_var])
    return

def vet_potential_errors(line, line_count, cur_pot):
    if line.startswith("'") or line.strip().endswith("'"):
        print(cur_pot+1, "Possible apostrophe-to-quote change needed line", line_count, ":", line.strip())
        return True
    elif '[\']' in line or '[line break]' in line or '[paragraph break]' in line:
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
    if '[' in line and ']' in line and not line.startswith('#'):
        lmod = re.sub("^[^\[]*\[", "", line.strip())
        lmod = re.sub("\].*", "", lmod)
        lmod = "{:d} {:s}".format(line_count, lmod)
        generic_bracket_error[lmod] += 1
        if flag_all_brackets:
            global cur_flag_brackets
            cur_flag_brackets += 1
            if max_flag_brackets and cur_flag_brackets > max_flag_brackets: return False
            print(cur_flag_brackets, "Text replacement/brackets artifact in line", line_count, ":", line.strip()) # clean this code up for later error checking, into a function
            return False
    return False

def replace_mapping(x, my_f, my_l):
    if x.startswith('@') or x.startswith('`'): y = x[1:]
    else:
        y = re.sub("=+\{", "", x.strip())
        y = re.sub("\}.*", "", y)
    y = re.sub(" *#.*", "", y) # strip out comments
    y = y.strip()
    if y not in to_match.keys():
        print("Oops, line {:d} of {:s} has undefined matching-class {:s}. Possible classes are {}".format(my_l, my_f, y, ', '.join(to_match)))
        mt.npo(my_f, my_l)
    return "==" + to_match[y]

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
    exit()

def post_copy(file_array):
    if copy_over_post:
        if force_all_regs:
            print("Copying all files over to PRT directory.")
            for q in file_array: copy(q, os.path.join(i7.prt, os.path.basename(q)))
        elif len(changed_files.keys()):
            print("Copying changed files over to PRT directory.")
            for q in changed_files.keys(): copy(q, os.path.join(i7.prt, os.path.basename(q)))
        else:
            print("No files copied over to PRT directory. Try -fp or -pf to force copying of all files encompassed by", in_file)

def examples():
    print("===1,2,4 changes the active file list to #1, 2, 4 for example.")
    print("==t5 means only use file 5 until next empty line. Then it switches back to what was there before. A second ==t wipes out the first saved array.")
    print("==- inverts the active file list")
    print("== ! - ^ 1,2,4 = all but numbers 1, 2, 4")
    print("*FILE is replaced by the file name.")
    print("#-- is a comment only for the branch file.")
    exit()

def usage():
    print("-er = edit branch file (default = for directory you are in)")
    print("-e = edit rbr.txt")
    print("-c = edit rbr.py")
    print("-d = debug on")
    print("-f = flag all brackets")
    print("-m = Monty process")
    print("-q = Quiet")
    print("-np = no copy over post, -p = copy over post (default)")
    print("-si = show singletons with brackets, -nsi/-sin = only count them")
    print("-x = list examples")
    print("shorthand or longterm project names accepted")
    exit()

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
    return re.sub(r'^[a-z]+([=:])?', "", ll, 0, re.IGNORECASE)

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

def get_file(fname):
    check_main_file_change = False
    got_any_test_name = False
    dupe_val = 1
    warns = 0
    last_cmd = ""
    file_list = []
    file_array = []
    line_count = 0
    dupe_file_name = ""
    temp_diverge = False
    if not quiet: print("Poking at", fname)
    actives = []
    old_actives = []
    preproc_commands = []
    postproc_if_changed = defaultdict(list)
    generic_bracket_error.clear()
    with open(fname) as file:
        for (line_count, line) in enumerate(file, 1):
            if is_rbr_bookmark(line):
                continue
            if line.startswith("{--"):
                vta_before = re.sub("\}.*", "", line.strip())
                vta_after = re.sub("^.*?\}", "")
                very_temp_array = [int(x) for x in vta[3:].split(",")]
                for q in very_temp_array:
                    file_list[q].write(re.sub("\\", "\n", vta_after))
                continue
            if line.startswith("~\t"):
                eq_array = line.strip().lower().split("\t")
                if len(eq_array) != 3: sys.exit("Bad equivalence array at line {:d} of file {:s}: needs exactly two tabs.".format(line_count, fname))
                to_match[eq_array[1]] = eq_array[2]
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
                    for x in temp_file_array:
                        if x not in file_array_base:
                            sys.exit("FATAL ERROR: {} is not in the original file array {}.".format(x, file_array_base))
                    if exclude:
                        temp_file_array = [x for x in file_array_base if x not in temp_file_array]
                else:
                    temp_file_array = file_array
                    cmd_to_run = re.sub("^.*?=", "", line_no_com).split(",")
                for tf in temp_file_array:
                    postproc_if_changed[prt_temp_loc(tf)] += cmd_to_run
                continue
            if line.startswith("files="):
                for cmd in preproc_commands: os.system(cmd)
                file_array_base = re.sub(".*=", "", line.lower().strip()).split(',')
                file_array = [prt_temp_loc(f) for f in file_array_base]
                actives = [True] * len(file_array)
                last_cr = [False] * len(file_array)
                for x in file_array:
                    f = open(x, "w", newline="\n")
                    file_list.append(f)
                continue
            if not len(file_array): continue # allows for comments at the start
            if line.startswith("}$"):
                temp_ary = line[2:].strip().split("=")
                my_strings[temp_ary[0]] = '='.join(temp_ary[1:])
                continue
            if line.startswith("}}"):
                if len(file_array) == 0:
                    sys.exit("BAILING. RBR.PY requires }} variable meta-commands to be after files=, because each file needs to know when to access that array.")
                branch_variable_adjust(line[2:].strip(), "at line {} in {}".format(line_count, fname), actives)
                continue
            if re.search("^(`|=\{|@)", line): line = replace_mapping(line, fname, line_count)
            if line.startswith('#--'):
                if line.startswith("#--stable"):
                    check_main_file_change = True
                continue
            if temp_diverge and not line.strip():
                temp_diverge = False
                for x in range(len(actives)):
                    if not last_cr[x]:
                        file_list[x].write("\n") # only actives get a CR
                        last_cr[x] = True
                actives = list(old_actives)
                continue
            if line.strip() == "\\\\": line = "\n"
            warns += vet_potential_errors(line, line_count, warns)
            if line.startswith("dupefile="):
                dupe_file_name = i7.prt + "/temp/" + re.sub(".*=", "", line.lower().strip())
                dupe_file = open(dupe_file_name, "w", newline="\n")
                continue
            if re.search("^TSV(I)?[=:]", line): #tab separated values
                ignore_too_short = line.lower().startswith("tsvi")
                l2 = re.sub("TSV(I)?.", "", line.lower(), 0, re.IGNORECASE).strip().split("\t")
                if len(l2) > len(actives):
                    print("WARNING line", line_count, "has too many TSV values, ignoring")
                    print("TEXT:", line.strip())
                    continue
                elif ignore_too_short and len(l2) < len(actives):
                    print("WARNING line", line_count, "doesn't cover all files. Change TSV to TSVI to ignore this.")
                    print("TEXT:", line.strip())
                for x in range(len(l2)):
                    file_list[x].write(l2[x] + "\n")
                continue
            if all_false(actives):
                if always_be_writing and len(actives):
                    sys.exit("No files written to at line " + line_count + ": " + line.strip())
            if line.startswith(">"): last_cmd = line.lower().strip()
            if line.startswith("===a"):
                actives = [True] * len(actives)
                continue
            if line.strip() == "==!":
                actives = [not x for x in actives]
                continue
            if line.startswith("==!") or line.startswith("==-") or line.startswith("==^"):
                actives = [True] * len(actives)
                try:
                    chgs = line.lower().strip()[3:].split(',')
                    if len(chgs):
                        for x in chgs:
                            actives[int(x)] = False
                    else:
                        print("No elements in ==!/-/^ array, line", line_count)
                except:
                    sys.exit("Failed at line " + line_count + ": " + line.strip())
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
                    if temp_actives[x]: file_list[x].write(string_out)
                continue
            if line.startswith("==t"):
                if temp_diverge:
                    print("Oops, bailing due to second temporary divergence ==t at line", line_count, ":", line.strip())
                    mt.npo(fname, line_count)
                    exit()
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
                        print("uh oh went boom on", x, "at line", line_count)
                        exit()
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
                print("Uh oh line", line_count, "may be a bad command.")
                warns += 1
            if debug and line.startswith(">"): print(act(actives), line.strip())
            for ct in range(0, len(file_list)):
                if actives[ct]:
                    line_write = re.sub("\*file", os.path.basename(file_list[ct].name), line, 0, re.IGNORECASE)
                    line_write = re.sub("\*fork", "GENERATOR FILE: " + os.path.basename(fname), line_write, 0, re.IGNORECASE)
                    if last_cr[ct] and (len(line_write.strip()) == 0):
                        pass
                    else:
                        if "{$" in line_write:
                            #print("BEFORE:", line_write.strip())
                            line_write = string_fill(line_write)
                            #print("AFTER:", line_write.strip())
                        line_write_2 = fill_vars(line_write, ct)
                        #if line_write != line_write_2: print(line_write, "changed to", line_write_2)
                        file_list[ct].write(line_write_2)
                    last_cr[ct] = len(line_write.strip()) == 0
                # if ct == 1: file_list[ct].write(str(line_count) + " " + line)
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
    for ct in range(0, len(file_array)):
        file_list[ct].close()
    if dupe_file_name:
        dupe_file.close()
        file_array.append(dupe_file_name)
    if warns > 0: print(warns, "potential bad commands.")
    new_files.clear()
    changed_files.clear()
    unchanged_files.clear()
    if monty_process:
        print(file_array)
        for x in file_array:
            x2 = os.path.basename(x)
            if x2 in mwrites.keys():
                for y in mwrites[x2].keys():
                    write_monty_file(x2, y)
    if check_main_file_change:
        x = file_array[0]
        xb = os.path.basename(x)
        print(x, xb)
        if not ignore_first_file_changes and not cmp(x, xb):
            print("Differences found in main file {}, which was meant to be stable. Windiff-ing then exiting. Use -f1 to allow these changes.".format(xb))
            mt.wm(x, xb)
            sys.exit()
    for x in file_array:
        xb = os.path.basename(x)
        if not os.path.exists(xb):
            new_files[xb] = True
            copy(x, xb)
        elif cmp(x, xb):
            unchanged_files[xb] = True
        else:
            changed_files[xb] = True
            copy(x, xb)
        os.remove(x)
    if len(generic_bracket_error) > 0:
        singletons = 0
        for x in sorted(generic_bracket_error.keys(), key = lambda x: (generic_bracket_error[x], x)):
            if generic_bracket_error[x] > 1 or show_singletons: print("Bracketed text error ({:d} time(s)) line/stuff =".format(generic_bracket_error[x]), x)
            else: singletons += 1
        if singletons: print("Number of singletons (show detail with -si):", singletons)
    nfk = len(new_files)
    if nfk > 0: print("New files ({}):".format(nfk), ', '.join(sorted(new_files)), 'from', fname)
    cfk = len(changed_files)
    if cfk: print("Changed files ({}):".format(cfk), ', '.join(sorted(changed_files)), 'from', fname)
    ufk = len(unchanged_files)
    lnc = len(new_files.keys()) + len(changed_files.keys()) > 0
    if not lnc:
        if not quiet: print("Nothing changed.")
    elif ufk: print("Unchanged files ({}):".format(ufk), ', '.join(sorted(unchanged_files.keys())), 'from', fname)
    if lnc or force_postproc:
        run_postproc = defaultdict(bool)
        if not lnc: print("Forcing postproc even though nothing changed.")
        to_proc = list(new_files.keys()) + list(changed_files.keys())
        if force_postproc: to_proc += list(unchanged_files.keys())
        for fi in to_proc:
            for cmd in postproc_if_changed[prt_temp_loc(fi)]:
                run_postproc[cmd] = True
        for cmd in run_postproc:
            print("Postproc: running", cmd, "for", fname)
            os.system(cmd)
    else:
        print("There are postproc commands, but no files were changed. Use -fp to force postproc.")
    if not got_any_test_name and os.path.basename(fname).startswith('rbr'):
        print("Uh oh. You don't have any test name specified with * main-thru for {}".format(fname))
        print("Just a warning.")
    sys.exit()
    post_copy(file_array_base)

cur_proj = ""
mwrites = defaultdict(lambda: defaultdict(bool))

with open('c:/writing/scripts/rbr.txt') as file:
    for (lc, line) in enumerate(file, 1):
        ll = line.lower().strip()
        if ll.startswith(';'): break
        if ll.startswith('#'): continue
        if '>' in ll[1:] and '<' not in ll[1:]:
            print("WARNING: possible erroneous cut and paste. Line", lc, "may need line break before command prompt:", line.strip())
        vars = wipe_first_word(ll)
        if ll.startswith('dupe'):
            ja = vars.split("\t")
            times[ja[0]] = int(ja[1])
            continue
        if ll.startswith('default'):
            def_proj = vars
            continue
        if ll.startswith('project') or ll.startswith('projname'):
            cur_proj = vars
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
        if ll.startswith('branchfiles'):
            branch_list[cur_proj] = vars.split(",")
            if cur_proj in i7.i7xr.keys(): branch_list[i7.i7xr[cur_proj]] = vars.split(",")
            if cur_proj in i7.i7x.keys(): branch_list[i7.i7x[cur_proj]] = vars.split(",")
            continue
        if ll.startswith('montyfiles'):
            mfi = vars.split("\t")
            for x in mfi:
                y = x.split("=")
                if '=' not in x:
                    print(x, 'in line', line_count, ll, 'needs an =')
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
        exit()
    elif arg == 'e':
        print("Editing the rbr.txt project configuration file.")
        print("If you meant to edit the main rbr file, you can use -er. But it may be easier to type rbr<TAB>.")
        os.system("rbr.txt")
        exit()
    elif arg[:2] == 'e:':
        edit_individual_files = True
    elif arg == 'er': edit_main_branch = True
    elif arg[:2] == 's4': search_for(arg[2:])
    elif arg[:2] == 'vn' or arg[:2] == 'nv' or arg == 'v': verify_nudges = True
    elif arg == 'd': debug = True
    elif arg == 'nf' or arg == 'fn': flag_all_brackets = False
    elif arg == 'm': monty_process = True
    elif arg == 'q': quiet = True
    elif arg == 'nq' or arg == 'qn': quiet = False
    elif arg == 'np': copy_over_post = False
    elif arg == 'p': copy_over_post = True
    elif arg == 'fp': force_postproc = True
    elif arg == 'f1': ignore_first_file_changes = True
    elif arg == 'pf' or arg == 'pc' or arg == 'cp': copy_over_post = force_all_regs = True
    elif arg in i7.i7x.keys():
        if proj: sys.exit("Tried to define 2 projects. Do things one at a time.")
        proj = i7.i7x[arg]
    elif can_make_rbr(arg, verbose = True): in_file = can_make_rbr(arg)
    elif arg == 'si': show_singletons = True
    elif arg == 'sin' or arg == 'nsi': show_singletons = False
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
        exit()
    count += 1

my_dir = os.getcwd()
if 'github' in my_dir.lower():
    if not github_okay:
        sys.exit("GITHUB is in your path. Mark this as okay with a -gh flag, or move to your regular directory.")

if proj:
    try:
        i7.go_proj(proj)
    except:
        sys.exit("Could not find a path to", proj)

if in_file:
    if not os.path.isfile(in_file): sys.exit(in_file + " not found.")
    os.chdir(os.path.dirname(os.path.abspath(in_file)))
    mydir = os.getcwd()
    if edit_main_branch:
        print("Opening branch file", in_file)
        os.system(in_file)
    else:
        get_file(in_file)
    exit()

if not proj:
    myd = os.getcwd()
    if i7.dir2proj(myd):
        proj = i7.dir2proj(myd)
        print("Going with project from current directory", proj)
    else:
        print("Going with default", def_proj)
        proj = def_proj

if verify_nudges:
    q = glob.glob("reg-*.txt")
    nudge_overall = 0
    for q1 in q:
        if 'nudmis' in q1: continue
        if 'nudges' in q1: continue
        if 'roi-' in q1: continue
        print("Checking nudges (generally valid for Stale Tales Slate only) for", q1)
        nudge_this = 0
        with open(q1) as file:
            for (line_count, line) in enumerate(file, 1):
                if should_be_nudge(line):
                    nudge_overall += 1
                    nudge_this += 1
                    print(nudge_overall, nudge_this, q1, line_count, "mis-assigned nudge-check:", line.strip())
    exit()

for pa in poss_abbrev:
    proj2 = i7.i7xr[proj] if proj in i7.i7xr.keys() else proj
    if proj2 in abbrevs[pa].keys():
        print("Adding specific file", abbrevs[pa][proj2], "from", proj2)
        my_file_list.append(abbrevs[pa][proj2])
    else:
        print(pa, 'has nothing for current project', proj, 'but would be valid for', '/'.join(sorted(abbrevs[pa].keys())))

if edit_individual_files:
    for mf in my_file_list: os.system(mf)
    exit()

if not len(my_file_list):
    my_file_list = list(branch_list[proj])
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
        print("No valid files, going with default", ', '.join(branch_list[proj]))

my_file_list_valid = []

for x in my_file_list: # this is probably not necessary, but it is worth catching in case we do make odd files somehow.
    if os.path.exists(x): my_file_list_valid.append(x)
    else:
        print("Ignoring bad file", x)

if len(my_file_list_valid) == 0:
    sys.exit("Uh oh, no valid files left after initial check. Bailing.")

for x in my_file_list_valid:
    get_file(x)

print("Reminder that -np disables copy-over-post and -p enables it. Default is not to copy the REG files over.")