#
# isvis.py: looks for "visible" in code
#
# with proper exceptions
#
# usage: (no command parameters if in story.ni)
#
# or, list of projects
#

import re
import os
import i7
import sys

max_vis = 0

ary = []

check_rigorous = True

def usage():
    print("USAGE:")
    print("m# for max # of visibles")
    print("rc/cr/r/ry/yr turns on rigor check, currently", i7.oo[check_rigorous])
    print("nr/rn turns it off")
    print("Or write in a project.")
    exit()

def viscap(x):
    return re.sub(r'\bvisible\b', "VISIBLE", x)

def num_valid_visibles(l, debug = False):
    q = ' '.join(re.findall(r'\[[^\]]*\]', l))
    syn = ' '.join(l.split('"')[::2])
    if debug:
        print(q, q.count('visible'), "quotes")
        print(syn, syn.count('visible'), "syntax")
    return q.count('visible') + syn.count('visible')

def ignore_vis(l):
    if "[v]" in l: return True
    if "[v:]" in l: return True #I can do this manually
    if l.startswith("["): return True
    if l.endswith("]"):
        if not "[" in l: return True
        ls = re.sub(r'( *\[([^\]])*\])+', '', l.strip())
        if 'visible' not in ls: return True
    if 'applying to' in l and (('one visible thing' in l) or ('two visible things' in l)): return True #actions definitions are okay

def find_vis(proj_name):
    visibles = 0
    count_idx = 0
    ignored = []
    x = i7.main_src(proj_name)
    if not os.path.exists(x):
        print("Bad project name/abbreviation", proj_name)
        if by_default: print("You may wish to specify an argument or change the directory.")
        return
    print("===================Hunting visibles for", proj_name, "at", x)
    with open(x) as file:
        for (line_count, line) in enumerate(file, 1):
            if not line.startswith("\t"): last_rule = line.strip()
            ll = line.lower().strip()
            if 'visible' in ll and re.search(r'\bvisible\b', ll, re.IGNORECASE):
                if ignore_vis(ll):
                    ignored.append(line_count)
                    continue
                if check_rigorous:
                    tv = num_valid_visibles(ll)
                else:
                    tv = len(re.findall(r'\bvisible\b', ll, re.IGNORECASE))
                if not tv: continue
                visibles += tv
                count_idx += 1
                print("Line", line_count, "Incidence", count_idx)
                print('    l{:s}'.format("" if tv == 1 else " +{:d}".format(tv)), visibles, 'tot', last_rule if line.startswith("\t") else "", viscap(line.lower().strip())) #ask codereview about a better way to do this?
    if not count_idx:
        print('HOORAY! No instances of "visible" to check.' + '' if check_rigorous else ' Use -nr for nonrigorous to pick up more bugs')
    else:
        print(count_idx, "total instance{:s} of visible for story.ni in project".format(i7.plur(count_idx)), proj_name)
    if len(ignored): print(len(ignored), "instance{:s} of VISIBLE ignored in project".format(i7.plur(ignored)), proj_name, ", ".join([str(x) for x in ignored]))

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == 'r' or arg == 'rc' or arg == 'cr' or arg == 'ry' or arg == 'yr':
        check_rigorous = True
    elif arg == 'rn' or arg == 'nr' or arg == 'n':
        check_rigorous = False
    elif arg[0] == 'm' and arg[1:].isdigit(): max_vis = int(arg[1:])
    elif i7.proj_exp(arg, return_nonblank = False):
        if i7.proj_exp(arg, return_nonblank = False) in ary:
            print("Duplicate entry", arg, "at position", cmd_count)
        else:
            ary.append(i7.proj_exp(arg))
    else:
        usage()
    cmd_count += 1

by_default = False
cwp = i7.dir2proj(os.getcwd())

if cwp and not len(ary):
    by_default = True
    story_path = os.path.join(i7.proj2dir(cwp), "story.ni")
    print("Verifying", story_path)
    if os.path.exists(story_path):
        ary = [ i7.dir2proj(os.getcwd()) ]
    else:
        sys.exit("You're in a potentially valid default project directory, but its games/inform directory has no story.ni. Bailing.")

for x in ary:
    if not os.path.exists(os.path.join(x, "story.ni")):
        print("Ignoring project", x, "as it does not have a story.ni.")

if not len(ary): sys.exit("You need to be in a valid github source directory or specify a project.")

for q in ary: find_vis(q)
