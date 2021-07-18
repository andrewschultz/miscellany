# regv.py : (crude) regex testing verb generator

import re
import sys
import i7
import mytools as mt

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


def crank_out_verb_tests(this_file):
    next_break = False
    big_ary = []
    look_for_say = False
    wrongo_verb = ''
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
            if not line.startswith('understand'): continue
            if ' as something new' in line: continue
            look_for_say = True
            ary = line.strip().split('"')[1::2]
            for a in ary:
                big_ary.extend(expand_verbs(a))

user_project = ''
cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in i7.i7x:
        if user_project:
            sys.exit("Redefining user project from {} to {}.".format(user_project, arg))
        user_project = i7.i7x[arg]
    else:
        sys.exit("Could not find project for {}.".format(arg))
    cmd_count += 1

if not user_project:
    my_proj = i7.dir2proj(empty_if_unmatched = True)
    if not my_proj:
        sys.exit("Could not get project from current directory. Bailing.")
    print("Pulling", my_proj, "from current directory.")
else:
    my_proj = user_project

if my_proj not in i7.i7f:
    crank_out_verb_tests(i7.main_src(my_proj))
    sys.exit()

for x in i7.i7f[my_proj]:
    crank_out_verb_tests(x)