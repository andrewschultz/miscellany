# rbr.py: regression brancher
#
# takes an rbr*.txt file and separates it into many reg-*
#
# usage rbr.py (project name) e.g. rbr.py ai
#
# or you can run it from a project source directory

import sys
import re
import os
import i7
import glob
import subprocess
from collections import defaultdict
from shutil import copy
from filecmp import cmp

to_match = defaultdict(str)
monty_detail = defaultdict(str)
branch_list = defaultdict(list)
times = defaultdict(int)
abbrevs = defaultdict(lambda: defaultdict(str))
generic_bracket_error = defaultdict(int)

temp_dir = "c:/games/inform/prt/temp"

flag_all_brackets = False
edit_individual_files = False
verify_nudges = False
always_be_writing = False
edit_main_branch = False
debug = False
monty_process = False

max_flag_brackets = 0
cur_flag_brackets = 0

quiet = False
copy_over_post = True

in_file = ""
in_dir = os.getcwd()
proj = ""

def should_be_nudge(x):
    if not x.startswith('#'): return False
    if x.startswith('##'): return False
    if re.search("(spechelp|mistake|nudge)", x): return True
    return False

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
    if '[' in line and ']' in line:
        lmod = re.sub("^[^\[]*\[", "", line.strip())
        lmod = re.sub("\].*", "", lmod)
        generic_bracket_error[lmod] += 1
        if flag_all_brackets:
            global cur_flag_brackets
            cur_flag_brackets += 1
            if max_flag_brackets and cur_flag_brackets > max_flag_brackets: return False
            print(cur_flag_brackets, "Text replacement/brackets artifact in line", line_count, ":", line.strip()) # clean this code up for later error checking, into a function
            return False
    return False

def replace_mapping(x, my_f, my_l):
    if x.startswith('@'): y = x[1:]
    elif x.startswith('`'): y = x[1:]
    else:
        y = re.sub("=\{", "", x.strip())
        y = re.sub("\}.*", "", y)
    y = y.strip()
    if y not in to_match.keys(): sys.exit("Oops, line {:d} of {:s} has undefined matching-class {:s}.".format(my_l, my_f, y))
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

def post_copy():
    if copy_over_post:
        print("Running prt.pl after -- try -np to disable this")
        subprocess.run(["perl", "c:\\writing\\scripts\\prt.pl"], stdout=subprocess.PIPE)

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
    from_file = os.path.join(temp_dir, fname)
    to_file = os.path.join(temp_dir, new_file_name)
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
    generic_bracket_error.clear()
    with open(fname) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("~\t"):
                eq_array = line.strip().lower().split("\t")
                if len(eq_array) != 3: sys.exit("Bad equivalence array at line {:d} of file {:s}: needs exactly two tabs.".format(line_count, fname))
                to_match[eq_array[1]] = eq_array[2]
                continue
            if line.startswith("files="):
                file_array_base = re.sub(".*=", "", line.lower().strip()).split(',')
                file_array = [os.path.join(temp_dir, f) for f in file_array_base]
                actives = [True] * len(file_array)
                last_cr = [False] * len(file_array)
                for x in file_array:
                    f = open(x, "w", newline="\n")
                    file_list.append(f)
                continue
            if not len(file_array): continue # allows for comments at the start
            if re.search("^(`|=\{|@)", line): line = replace_mapping(line, fname, line_count)
            if line.startswith('#--'): continue
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
                dupe_file_name = re.sub(".*=", "", line.lower().strip())
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
                if not line[3].isnumeric() and line[3] != '!': sys.exit("extra = in header {:s} line {:d}: {:s}".format(fname, line_count, line.strip()))
                ll = re.sub("^=+", "", line.lower().strip()).split(',')
                actives = [False] * len(file_array)
                for x in ll:
                    if x.isdigit(): actives[int(x)] = True
                continue
            if line.startswith("=="):
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
                        file_list[ct].write(line_write)
                    last_cr[ct] = len(line_write.strip()) == 0
                # if ct == 1: file_list[ct].write(str(line_count) + " " + line)
            if actives[dupe_val]:
                if dupe_file_name:
                    dupe_file.write(line)
                    if 'by one point' in line:
                        reps = 1
                        if times[last_cmd[1:]] > 1: reps = times[last_cmd[1:]]
                        for x in range(0, reps):
                            dupe_file.write("\n" + last_cmd + "\n")
                            dupe_file.write("!by one point\n")
    for ct in range(0, len(file_array)):
        file_list[ct].close()
    if dupe_file_name: dupe_file.close()
    if warns > 0: print(warns, "potential bad commands.")
    new_files = defaultdict(bool)
    changed_files = defaultdict(bool)
    unchanged_files = defaultdict(bool)
    if monty_process:
        print(file_array)
        for x in file_array:
            x2 = os.path.basename(x)
            if x2 in mwrites.keys():
                for y in mwrites[x2].keys():
                    write_monty_file(x2, y)
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
            if generic_bracket_error[x] > 1: print(x, generic_bracket_error[x])
            else: singletons += 1
        if singletons: print("Number of singletons:", singletons)
    if len(new_files.keys()) + len(changed_files.keys()) == 0:
        if not quiet: print("Nothing changed.")
        return
    if len(new_files.keys()) > 0: print("New files:", ', '.join(sorted(new_files.keys())), 'from', fname)
    if len(changed_files.keys()) > 0: print("Changed files:", ', '.join(sorted(changed_files.keys())), 'from', fname)
    if len(unchanged_files.keys()) > 0: print("Unchanged files:", ', '.join(sorted(unchanged_files.keys())), 'from', fname)

cur_proj = ""
mwrites = defaultdict(lambda: defaultdict(bool))

with open('c:/writing/scripts/rbr.txt') as file:
    for (lc, line) in enumerate(file, 1):
        ll = line.lower().strip()
        if ll.startswith(';'): break
        if ll.startswith('#'): continue
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
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c':
        i7.open_source()
        exit()
    elif arg == 'e':
        os.system("rbr.txt")
        exit()
    elif arg[:2] == 'e:':
        edit_individual_files = True
    elif arg == 'er': edit_main_branch = True
    elif arg[:2] == 's4': search_for(arg[2:])
    elif arg[:2] == 'vn' or arg[:2] == 'nv' or arg[:1] == 'v': verify_nudges = True
    elif arg == 'd': debug = True
    elif arg[0] == 'f':
        flag_all_brackets = True
        if arg[1:].isdigit():
            max_flag_brackets = int(arg[1:])
    elif arg == 'nf' or arg == 'fn': flag_all_brackets = False
    elif arg == 'm': monty_process = True
    elif arg == 'q': quiet = True
    elif arg == 'nq' or arg == 'qn': quiet = False
    elif arg == 'np': copy_over_post = False
    elif arg == 'p': copy_over_post = True
    elif arg in i7.i7x.keys():
        if proj: sys.exit("Tried to define 2 projects. Do things one at a time.")
        proj = i7.i7x[arg]
    elif os.path.exists(arg): in_file = arg
    elif arg == 'x': examples()
    elif arg == '?': usage()
    elif arg in abbrevs.keys(): poss_abbrev.append(arg)
    else:
        print("Bad argument", count, arg)
        print("Possible projects: ", ', '.join(sorted(branch_list.keys())))
        usage()
        exit()
    count += 1

if in_file:
    if not os.path.isfile(in_file): sys.exit(in_file + " not found.")
    os.chdir(os.path.dirname(os.path.abspath(in_file)))
    mydir = os.getcwd()
    if edit_main_branch:
        print("Opening branch file", in_file)
        os.system(in_file)
    else:
        get_file(in_file)
        post_copy()
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
        print("Checking nudges for", q1)
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

if not len(my_file_list): my_file_list = list(branch_list[proj])

i7.go_proj(proj)
for x in my_file_list:
    get_file(x)

post_copy()