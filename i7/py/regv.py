# regv.py : (crude) regex testing verb generator
#
# to do: flag ignores (maybe)
#        also, maybe have a list of meta files for each project e.g. files:fourbyfouria=x.txt,y.txt,etc
#
# to do: allow for different testing subdirs when syncing, not just "testing"
#        allow for reg- and rbr- when syncing
#        allow for to-clipboard options
#

from collections import defaultdict
import os
import re
import sys
import i7
import mytools as mt
import pathlib
import glob

debug = False
ignores = defaultdict(lambda: defaultdict(bool))
open_after = False
use_recursive = True
search_branches = True
include_include_file_verbs = True
use_github_paths = True # this shouldn't make a difference, but github is likely more up to date (?)
# for use_github_paths, we also may wish to define the copy-over directory as the github directory
sync_between = False

regv_ignore = "c:/writing/scripts/regvi.txt"

def usage(my_message = "USAGE"):
    print("=" * 40 + my_message)
    print("L = look up cases, P = print cases. Mutually exclusive but can be combined with D=debug.")
    print("E = edit ignore file.")
    print("O = open source after.")
    print("G = use Github path, GN/NG/GY/YG toggles. Default = off.")
    print("I = include (heh) includes, IN/NI/IY/YI toggle. Default = on.")
    print("R = recursively search files, RN/NR/RY/YR toggle. Default = on.")
    print("B = recursively search files, BN/NB/BY/YB toggle. Default = on.")
    print("You can also specify a project name on the command line.")
    sys.exit()

def read_regv_ignores():
    with open(regv_ignore) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            (prefix, data) = mt.cfg_data_split(line)
            prefix = i7.long_name(prefix, debug=True)
            for x in data.split(","):
                ignores[prefix][x] = True


def valid_understand(my_line):
    if not my_line.startswith('understand'): return False
    if ' as something new' in my_line: return False
    if ' as a mistake' in my_line: return False
    if not re.search(r' as [^ ]+ing\b', my_line): return False
    return True

def expand_verbs(my_string):
    # print("Expanding", my_string)
    if '/' not in my_string:
        return [ my_string ]
    temp_ary = []
    ary = my_string.split(' ')
    for x in ary:
        if '/' not in x: continue
        for y in x.split('/'):
            temp = my_string.replace(x, y, 1)
            temp_ary.extend(expand_verbs(temp))
        break
    return temp_ary

def verbs_from_line(my_line):
    ret_ary = []
    ary = my_line.strip().split('"')[1::2]
    for a in ary:
        ret_ary.extend(expand_verbs(a))
    return ret_ary

def find_verbs(file_list):
    argless = defaultdict(str)
    witharg = defaultdict(str)
    for f in file_list:
        bn = os.path.basename(f)
        with open(f) as file:
            for (line_count, line) in enumerate (file, 1):
                if not valid_understand(line):
                    continue
                for q in verbs_from_line(line):
                    if '[' in q:
                        q = re.sub(" *\[.*", "", q)
                        witharg[q] = "{}={}".format(f, line_count)
                    else:
                        argless[q] = "{}={}".format(f, line_count)
    return (argless, witharg)

def file_and_line(my_string):
    ary = my_string.split('=')
    if len(ary) != 1:
        return(ary[0], 99999)
    try:
        t2 = int(ary[1])
    except:
        t2 = 99999
    return(ary[0], t2)

def process_misses(my_dict, list_desc):
    this_list = sorted([x for x in my_dict if my_dict[x] != "found" and not x in ignores[my_proj]], key = lambda y: file_and_line(my_dict[y]))
    if len(this_list) == 0:
        print("Hooray! Nothing missing in {}.".format(list_desc))
    else:
        print("Missing {} entries in {}.".format(len(this_list), list_desc))
        for t in this_list:
            print("  ---->", t, "~", my_dict[t])
            temp = my_dict[t].split("=")
            if debug: print("Adding", temp[0], temp[1])
            mt.add_postopen(temp[0], int(temp[1]))
    return len(this_list)

def regs_of(my_path, wild_card, recursive_check = use_recursive):
    if wild_card.endswith(".txt"):
        full_wild_card = wild_card
    else:
        full_wild_card = wild_card + "-*.txt"
    if recursive_check:
        temp = pathlib.Path(my_path).rglob(full_wild_card)
    else:
        temp = glob.glob(os.path.normpath(os.path.join(my_path, full_wild_card)))
    return list(temp)

def look_up_test_cases(my_proj, my_list):
    my_path = i7.proj2dir(my_proj, to_github = use_github_paths)
    g = regs_of(my_path, "reg")
    if search_branches:
        g.extend(regs_of(my_path, "rbr"))
    (argless, witharg) = find_verbs(my_list)
    for testfile in g:
        tb = os.path.basename(testfile)
        with open(testfile) as file:
            for (line_count, line) in enumerate (file, 1):
                if not line.startswith(">"):
                    continue
                ary = line[1:].strip().lower().split(' ')
                got_candidate = False
                for x in range(len(ary), -1, -1):
                    if got_candidate: continue
                    verb_candidate = ' '.join(ary[0:x]).lower()
                    if verb_candidate in argless:
                        if len(ary) == x:
                            if debug and not argless[verb_candidate]:
                                print("Found argless", verb_candidate, tb, line_count)
                            argless[verb_candidate] = "found"
                            got_candidate = True
                    if verb_candidate in witharg:
                        if len(ary) > x:
                            if debug and not witharg[verb_candidate]:
                                print("Found with-arg", verb_candidate, tb, line_count)
                            witharg[verb_candidate] = "found"
                            got_candidate = True
    x = process_misses(argless, "verbs without arguments")
    y = process_misses(witharg, "verbs with arguments")
    if not x + y:
        print("Total success!")
    else:
        print("If you want to ignore some verbs, look in {}.".format(regv_ignore))

def crank_out_verb_tests(this_file):
    next_break = False
    big_ary = []
    look_for_say = False
    wrongo_verb = ''
    print("###################verb tests for", this_file)
    with open(this_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.strip():
                if big_ary:
                    for x in big_ary:
                        print("> {}\n<WRONG>".format(x))
                    old_big_ary = big_ary
                    big_ary = []
                next_break = True
            if look_for_say:
                if 'say "' in line:
                    line_mod = re.sub("^.*?say \"", "", line)
                    line_mod = re.sub("\"[^\"]*$", "", line_mod)
                    wrongo_verb += '# ' + line_mod + "\n"
                    continue
                if wrongo_verb and not line.strip():
                    print("# possible text for", old_big_ary)
                    print(wrongo_verb)
                    wrongo_verb = ''
                    look_for_say = False
                    continue
            if not valid_understand(line): continue
            look_for_say = True
            big_ary.extend(verbs_from_line(line))

def write_sync_commands(github_tests = "testing"):
    inform_path = i7.proj2dir(my_proj, to_github = False)
    github_path = i7.proj2dir(my_proj, to_github = True)
    if github_tests:
        github_path = os.path.join(github_path, "testing")
    inform_reg = regs_of(inform_path, "reg-*.txt", False)
    github_reg = regs_of(github_path, "reg-*.txt", True)
    inform_base = [ os.path.basename(x) for x in inform_reg ]
    github_base = [ os.path.basename(x) for x in github_reg ]
    link_to = [ x for x in inform_reg if os.path.basename(x) not in github_base ]
    link_check = [ x for x in inform_reg if os.path.basename(x) in github_base ]
    link_from = [ x for x in github_reg if os.path.basename(x) not in inform_base ]
    total_unlinked = 0
    for x in link_check:
        if not os.path.islink(x):
            to_link_to = [ y for y in github_reg if os.path.basename(y) == os.path.basename(x) ]
            print("Link check...")
            if len(to_link_to) > 1:
                print("WARNING duplicately named files ... check before linking")
            print("  erase {}".format(x))
            for y in to_link_to:
                print("  mklink {} {}".format(x, y))
            total_unlinked += 1
    if total_unlinked == 0:
        print("All games/inform reg-* files are linked.")
    if len(link_to) > 0:
        print("Make links to github for:")
        for l in link_to:
            print("move {} {}".format(l, os.path.join(github_path, os.path.basename(l))))
            print("mklink {} {}".format(l, os.path.join(github_path, os.path.basename(l))))
    else:
        print("All github regex testfiles are linked to.")
    if len(link_from) > 0:
        for l in link_from:
            print("mklink {} {}".format(os.path.join(inform_path, os.path.basename(l)), l))
    else:
        print("All games/inform regex testfiles are linked from.")


user_project = ''
cmd_count = 1
lookup_cases = False

read_regv_ignores()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in i7.i7x:
        if user_project:
            sys.exit("Redefining user project from {} to {}.".format(user_project, arg))
        user_project = i7.i7x[arg]
    elif arg == 'd':
        debug = True
    elif arg == 'l':
        lookup_cases = True
    elif arg in ( 'ld', 'dl' ):
        lookup_cases = debug = True
    elif arg in ( 'g', 'gy', 'yg' ):
        use_github_paths = True
    elif arg in ( 'gn', 'ng' ):
        use_github_paths = False
    elif arg in ( 'i', 'iy', 'yi' ):
        include_include_file_verbs = True
    elif arg in ( 'in', 'ni' ):
        include_include_file_verbs = False
    elif arg in ( 'r', 'ry', 'yr' ):
        use_recursive = True
    elif arg in ( 'rn', 'nr' ):
        use_recursive = False
    elif arg in ( 'b', 'by', 'yb' ):
        search_branches = True
    elif arg in ( 'bn', 'nb' ):
        search_branches = False
    elif arg == 'p':
        lookup_cases = False
    elif arg in ( 'pd', 'dp' ):
        lookup_cases = False
        debug = True
    elif arg == 's':
        sync_between = True
    elif arg == 'e':
        os.system(regv_ignore)
    elif arg == 'o':
        open_after = True
    elif arg == '?':
        usage()
    else:
        usage("Could not find project for {}.".format(arg))
    cmd_count += 1

if not user_project:
    my_proj = i7.dir2proj(empty_if_unmatched = True)
    if not my_proj:
        sys.exit("Could not get project from current directory. Bailing.")
    print("Pulling", my_proj, "from current directory.")
else:
    my_proj = user_project

if sync_between:
    write_sync_commands()
    sys.exit()

project_file_list = i7.i7f[my_proj] if my_proj in i7.i7f else [ i7.main_src(my_proj) ]

if include_include_file_verbs:
    for x in i7.i7com:
        if my_proj in i7.i7com[x]:
            if x in i7.i7f:
                project_file_list.extend(i7.i7f[x])

if lookup_cases:
    look_up_test_cases(my_proj, project_file_list)
    if open_after:
        mt.post_open()
    elif len(mt.file_post_list) > 0:
        print("Set o to open source after at the first ignored verb(s) in each file.")
    sys.exit()

for x in project_file_list:
    crank_out_verb_tests(x)
