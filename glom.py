#
# glom.py
#
# this gloms together similar/linked ideas.
#
# see flipflops for Buck The Past or ...
#
# ... welp haunted stuff, or otherwise
#

import sys
from collections import defaultdict
import re
import shutil
import filecmp
from daily import last_daily_file
import mytools as mt
import i7

cfg_file = "c:/writing/scripts/glom.txt"

default_from_cfg = ''

# constants
my_project = ""

class glom_project:
    def __init__(self, name): #alphabetical, except when similar are lumped together
        self.file = ''
        self.tempfile = ''
        self.splitregex = []
        self.alphabetize = defaultdict(bool)
        self.flaggables = []

my_gloms = defaultdict(glom_project)

#cmd line variables

check_sectioning = False
copy_back = False
max_changes = 25
user_max_line = 0

# dictionaries

so_far = defaultdict(int)
delete_after = defaultdict(int)

def usage(message = 'Usage for glom.py'):
    print(message)
    print('=' * 50)
    print("m# = max changes, ml# = max line")
    print("c/co = copy over, cn/nc = don't copy over")
    print("cs checks sections")
    exit()

def separator_value_of(x):
    x = x.strip()
    if x == '00' or x == '**': return 100
    if x.isdigit(): return int(x)
    return 0

def first_separator_of(my_regex, x):
    sep_regex = r'({})'.format(my_regex, x)
    return re.search(sep_regex, x)[0]

def highest_separator_of(my_regex, y):
    sep_regex = r'({})'.format(my_regex)
    f = re.findall(sep_regex, y)
    return max(f, key=lambda x:separator_value_of(x))

def custom_array(x, my_regex, go_lower = True):
    my_line = mt.zap_comment(x).strip()
    if go_lower: my_line = my_line.lower()
    retval = re.split(my_regex, my_line)
    return retval

def get_all_ideas(my_file, my_regex):
    my_dict = defaultdict(int)
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            ca = custom_array(line, my_regex)
            if len(ca) > 1:
                for idea in ca:
                    my_dict[glom_modification_of(idea, this_glom.alphabetize[my_regex])] = line_count
    return my_dict

def glom_modification_of(my_idea, alphabetize_this):
    replace_no_space = ",.!':;"
    my_idea = my_idea.lower()
    for r in replace_no_space:
        my_idea = my_idea.replace(r, '')
    my_idea = my_idea.replace('-', ' ')
    word_array = my_idea.split(' ')
    if alphabetize_this:
        word_array = sorted(word_array)
    return ' '.join(word_array)

def show_vanishing_idea_lines(main_dict, compare_dict, file_1, file_2):
    set_difference = sorted(set(list(main_dict)) - set(list(compare_dict)))
    if not len(set_difference):
        return 0
    max_len = max([len(x) for x in set_difference])
    for x in sorted(set_difference, key=lambda x: main_dict[x]):
        print("{:{maxsize}s} not in {} but was at line {} for {}".format(x, file_2, main_dict[x], file_1, maxsize = max_len))
    return len(set_difference)

def compare_idea_lists(file_1, file_2, my_regex):
    my_1 = get_all_ideas(file_1, my_regex)
    my_2 = get_all_ideas(file_2, my_regex)
    left = 0
    right = 0
    my_both = sorted(set(list(my_1)) | set(list(my_2)))
    left = show_vanishing_idea_lines(my_1, my_2, file_1, file_2)
    right = show_vanishing_idea_lines(my_2, my_1, file_2, file_1)
    if left or right:
        print("Missing ideas. {} vanished from left, {} vanished from right. Bailing.".format(left, right))
        sys.exit()
    print("No missing ideas on file rewrite.")

def run_one_regex(line_array, my_regex):
    global cur_changes
    alphabetize_this = this_glom.alphabetize[my_regex]
    for line_count in range(0, max_line):
        l = line_array[line_count]
        lb = l
        lary = custom_array(l, my_regex)
        if len(lary) > 1:
            #print(line_count, lary)
            after_array = []
            for x in lary:
                xg = glom_modification_of(x, alphabetize_this)
                if xg in so_far:
                    if so_far[xg] not in after_array and so_far[xg] not in delete_after:
                        #print(x, "was at line", so_far[x])
                        after_array.append(so_far[xg])
                else:
                    so_far[xg] = line_count
            if len(after_array):
                cur_changes += 1
                if max_changes and cur_changes == max_changes + 1:
                    print("Went over max listable changes of", max_changes)
                    break
                for a in after_array:
                    l = mt.comment_combine([l, first_separator_of(my_regex, l) + line_array[a]], cr_at_end = False, to_flag = this_glom.flaggables)
                #print("New combined line:", l)
                new_split = l.split('#')
                #print("new split", new_split)
                hisep = highest_separator_of(my_regex, new_split[0])
                final_array = custom_array(new_split[0], my_regex, go_lower = False)
                #print("Parsing", final_array)
                final_dict = defaultdict(bool)
                for u in final_array:
                    u_mod = glom_modification_of(u, alphabetize_this)
                    if u_mod not in final_dict.values():
                        final_dict[u] = u_mod
                    if u in so_far:
                        so_far[u] = line_count
                if len(final_dict) == 1:
                    print("WARNING line {} collapsed to just one argument: {}.".format(line_count + 1, list(final_dict)[0]))
                final_text = hisep.join(sorted(final_dict, key=lambda x:x.lower()))
                if len(new_split) > 1:
                    final_text += " #" + new_split[1]
                #print(line_count, "from", ','.join([str(x) for x in after_array]), ":", final_array, "->", final_text)
                for q in after_array:
                    if q != line_count:
                        delete_after[q] = True
                    #print("Zapping", q, line_array[q].strip())
                final_new_line = final_text.strip() + "\n"
                print("    -> edited line ({} from {}):".format(line_count+1, ', '.join([str(x+1) for x in after_array])), final_new_line.strip())
                if len(final_new_line) == len(lb):
                    pass #print("No length changed for line", line_count, "because of likely duplicate information.")
                line_array[line_count] = final_new_line
    return line_array

def read_cfg_file():
    global default_from_cfg
    current_project = ''
    with open(cfg_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if not line.strip(): continue
            (prefix, data) = mt.cfg_data_split(line, strip_data_right_only = True)
            if prefix == 'default':
                if default_from_cfg:
                    print("WARNING default from cfg renamed at line", line_count)
                default_from_cfg = data
                continue
            if prefix == 'project':
                current_project = data
                if current_project in my_gloms:
                    print(current_project, "already in gloms.")
                else:
                    my_gloms[current_project] = glom_project(current_project)
                this_glom = my_gloms[current_project]
                continue
            if not current_project:
                sys.exit("Need a current project before actual options at line {}.".format(line_count))
            if prefix == 'file':
                this_glom.file = data
            elif prefix == 'flag':
                this_glom.flaggables.extend(data.split(','))
            elif prefix == 'tempfile':
                this_glom.tempfile = data
            elif prefix == 'splitregex':
                this_glom.splitregex.append(r'{}'.format(data))
                this_glom.alphabetize[data] = False
            elif prefix == 'splitregexa':
                this_glom.splitregex.append(r'{}'.format(data))
                this_glom.alphabetize[data] = True
            else:
                print("Bad prefix line", line_count, prefix)

read_cfg_file()

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in my_gloms:
        my_project = arg
    elif arg[:2] == 'p=' or arg[:2] == 'p:' or arg[:2] == 's=' or arg[:2] == 's:':
        my_project = arg[2:]
    elif arg[0] == 'm' and arg[1:].isdigit():
        max_changes = int(arg[1:])
    elif arg[:2] == 'ml' and arg[2:].isdigit():
        user_max_line = int(arg[2:])
    elif arg == 'c' or arg == 'co':
        copy_back = True
    elif arg == 'cn' or arg == 'nc':
        copy_back = False
    elif arg == 'cs':
        check_sectioning = True
    elif arg == '?':
        usage()
    elif arg in my_gloms:
            print("p= also works.")
            my_project = arg
    else:
        usage("Unknown parameter {}.".format(arg))
    cmd_count += 1

if not my_project:
    this_try = i7.dir2proj(to_abbrev = True)
    if this_try:
        if this_try in my_gloms:
            print(mt.PASS + "Since we are in an Inform project directory with a GLOM project, we are going with {}.".format(this_try) + mt.WTXT)
            my_project = this_try
        else:
            print(mt.WARN + "We are in an Inform project directory, but it has no GLOM project. Edit glom.txt to fix this." + mt.WTXT)
    if not my_project:
        if default_from_cfg:
            my_project = default_from_cfg
            print("Going with default cfg project {}.".format(my_project))
        else:
            sys.exit("Could not find project {}, and we are in a directory.".format(my_project))

if my_project not in my_gloms:
    sys.exit("No glom project for {}.".format(my_project))

this_glom = my_gloms[my_project]

if check_sectioning:
    mt.check_properly_sectioned(this_glom.file)

if this_glom.file == "last-daily":
    this_glom.file = last_daily_file()

f = open(this_glom.file, "r")
line_array = f.readlines()
f.close()

cur_changes = 0

max_line = len(line_array)
if user_max_line:
    if user_max_line > max_line:
        print("user-defined maximum line to edit is greater than lines in {}.".format(this_glom_file))
    else:
        max_line = user_max_line

for my_regex in this_glom.splitregex:
    line_array = run_one_regex(line_array, my_regex)

f = open(this_glom.tempfile, "w")

for line_count in range(0, len(line_array)):
    if line_count in delete_after:
        continue
    f.write(line_array[line_count])

f.close()

for my_regex in this_glom.splitregex:
    compare_idea_lists(this_glom.file, this_glom.tempfile, my_regex)

if cur_changes:
    if max_changes and cur_changes > max_changes:
        cur_changes = max_changes
    print(cur_changes, "total modifications caught this run.")

if copy_back:
    if check_sectioning:
        mt.check_properly_sectioned(this_glom.tempfile)
    shutil.copy(this_glom.tempfile, this_glom.file)
    print("Temp file copied back. Changes are permanent.")
else:
    mt.wm(this_glom.file, this_glom.tempfile)
    if not filecmp.cmp(this_glom.file, this_glom.tempfile):
        print("Use the -co flag to copy over when you're ready.")
