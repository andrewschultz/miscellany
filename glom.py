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
import mytools as mt
import shutil

cfg_file = "c:/writing/scripts/glom.txt"

default_from_cfg = ''

# constants
my_project = ""

class glom_project:
    def __init__(self, name): #alphabetical, except when similar are lumped together
        self.file = ''
        self.tempfile = ''
        self.splitregex = ''

my_gloms = defaultdict(glom_project)

#cmd line variables

copy_back = False
max_changes = 10
user_max_line = 0

# dictionaries

so_far = defaultdict(int)
delete_after = defaultdict(int)

def usage(message = 'Usage for glom.py'):
    print(message)
    print('=' * 50)
    print("m# = max changes, ml# = max line")
    print("c/co = copy over, cn/nc = don't copy over")
    exit()

def separator_value_of(x):
    x = x.strip()
    if x == '00' or x == '**': return 100
    if x.isdigit(): return int(x)
    return 0

def first_separator_of(x):
    sep_regex = r'({})'.format(this_glom.splitregex)
    return re.search(sep_regex, x)[0]

def highest_separator_of(y):
    sep_regex = r'({})'.format(this_glom.splitregex)
    f = re.findall(sep_regex, y)
    return max(f, key=lambda x:separator_value_of(x))

def custom_array(x, go_lower = True):
    my_line = mt.zap_comment(x).strip()
    if go_lower: my_line = my_line.lower()
    retval = re.split(this_glom.splitregex, my_line)
    return retval

def get_all_ideas(my_file):
    my_dict = defaultdict(int)
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            ca = custom_array(line)
            if len(ca) > 1:
                for idea in ca:
                    my_dict[idea] = line_count
    return my_dict

def glom_modification_of(my_idea):
    my_idea = my_idea.lower()
    return my_idea
    if my_idea.count(' ') == 1:
        my_idea = ' '.join(sorted(my_idea.split(' ')))
    return my_idea

def compare_idea_lists(file_1, file_2):
    my_1 = get_all_ideas(file_1)
    my_2 = get_all_ideas(file_2)
    left = 0
    right = 0
    my_both = sorted(set(list(my_1)) | set(list(my_2)))
    for x in my_both: # less serious, so if there are too many mistakes, the next is seen first
        if x not in my_2:
            print(x, "not in", file_2, "but was at line", my_1[x], "for", file_1)
            left += 1
    for x in my_both: # legitimate data loss needs to be seen first, at the bottom, especially if there is more than one screen of it
        if x not in my_1:
            print(x, "not in", file_1, "but was at line", my_2[x], "for", file_2)
            right += 1
    if left or right:
        print("Missing ideas. {} vanished from left, {} vanished from right. Bailing.".format(left, right))
        sys.exit()
    print("No missing ideas on file rewrite.")

def read_cfg_file():
    global default_from_cfg
    current_project = ''
    with open(cfg_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if not line.strip(): continue
            (prefix, data) = mt.cfg_data_split(line)
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
            elif prefix == 'tempfile':
                this_glom.tempfile = data
            elif prefix == 'splitregex':
                this_glom.splitregex = r'{}'.format(data)
            else:
                print("Bad prefix line", line_count, prefix)

read_cfg_file()

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg[0] == 'm' and arg[1:].isdigit():
        max_changes = int(arg[1:])
    elif arg[:2] == 'ml' and arg[2:].isdigit():
        user_max_line = int(arg[2:])
    elif arg == 'c' or arg == 'co':
        copy_back = True
    elif arg == 'cn' or arg == 'nc':
        copy_back = False
    elif arg == '?':
        usage()
    else:
        usage("Unknown parameter {}".format(arg))
    cmd_count += 1

if not my_project:
    if default_from_cfg:
        my_project = default_from_cfg
        print("Going with default cfg project {}.".format(my_project))
    else:
        sys.exit("Could not find project {}.".format(my_project))

if my_project not in my_gloms:
    sys.exit("No glom project for {}.".format(my_project))

this_glom = my_gloms[my_project]

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

for line_count in range(0, max_line):
    l = line_array[line_count]
    lb = l
    lary = custom_array(l)
    if len(lary) > 1:
        #print(line_count, lary)
        after_array = []
        for x in lary:
            if x in so_far:
                if so_far[x] not in after_array and so_far[x] not in delete_after:
                    #print(x, "was at line", so_far[x])
                    after_array.append(so_far[x])
            else:
                so_far[x] = line_count
        if len(after_array):
            cur_changes += 1
            if max_changes and cur_changes == max_changes + 1:
                print("Went over max changes of", max_changes)
                break
            for a in after_array:
                l = mt.comment_combine([l, first_separator_of(l) + line_array[a]], cr_at_end = False)
            #print("New combined line:", l)
            new_split = l.split('#')
            #print("new split", new_split)
            hisep = highest_separator_of(new_split[0])
            final_array = custom_array(new_split[0], go_lower = False)
            #print("Parsing", final_array)
            final_dict = defaultdict(bool)
            for u in final_array:
                u_mod = glom_modification_of(u)
                if u_mod not in final_dict.values():
                    final_dict[u] = u_mod
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

f = open(this_glom.tempfile, "w")

for line_count in range(0, len(line_array)):
    if line_count in delete_after:
        continue
    f.write(line_array[line_count])

f.close()

#mt.calf(this_glom.file, this_glom.tempfile)

compare_idea_lists(this_glom.file, this_glom.tempfile)

if cur_changes:
    if max_changes and cur_changes > max_changes:
        cur_changes = max_changes
    print(cur_changes, "total modifications caught this run.")

if copy_back:
    shutil.copy(this_glom.tempfile, this_glom.file)
    print("Temp file copied back. Changes are permanent.")
else:
    mt.wm(this_glom.file, this_glom.tempfile)
    print("Use the -co flag to copy over when you're ready.")
