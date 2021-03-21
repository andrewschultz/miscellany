import sys
from collections import defaultdict
import re
import mytools as mt
import shutil

copy_back = False

# constants
my_project = "spo"

# to become variable later
my_file = "c:/writing/spopal.otl"
my_file_temp = "c:/writing/temp/glom-spopal.otl"
my_regex = r' +[0-9\*]{2} +'

#cmd line variables

max_changes = 1

# dictionaries

so_far = defaultdict(int)
delete_after = defaultdict(int)

def separator_value_of(x):
    x = x.strip()
    if x == '00' or x == '**': return 100
    if x.isdigit(): return int(x)
    return 0

def first_separator_of(x):
    sep_regex = r'({})'.format(my_regex)
    return re.search(sep_regex, x)[0]

def highest_separator_of(y):
    sep_regex = r'({})'.format(my_regex)
    f = re.findall(sep_regex, y)
    return max(f, key=lambda x:separator_value_of(x))

def custom_array(x, go_lower = True):
    my_line = mt.zap_comment(x).strip()
    if go_lower: my_line = my_line.lower()
    retval = re.split(my_regex, my_line)
    return retval

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg[0] == 'm':
        max_changes = int(arg[1:])
    cmd_count += 1

f = open(my_file, "r")
line_array = f.readlines()
f.close()

cur_changes = 0

for line_count in range(0, len(line_array)):
    l = line_array[line_count]
    lb = l
    lary = custom_array(l)
    if len(lary) > 1:
        #print(line_count, lary)
        after_array = []
        for x in lary:
            if x in so_far:
                if so_far[x] not in after_array:
                    print(x, "was at line", so_far[x])
                    after_array.append(so_far[x])
            else:
                so_far[x] = line_count
        if len(after_array):
            cur_changes += 1
            if max_changes and cur_changes == max_changes + 1:
                print("Went over max changes of", max_changes)
                break
            for a in after_array:
                print("Adding line", a)
                l = mt.comment_combine([l, first_separator_of(l) + line_array[a]], cr_at_end = False)
            print("New combined line:", l)
            new_split = l.split('#')
            #print("new split", new_split)
            hisep = highest_separator_of(new_split[0])
            final_array = custom_array(new_split[0], go_lower = False)
            #print("Parsing", final_array)
            final_dict = defaultdict(bool)
            for u in final_array:
                if u.lower() not in final_dict.values():
                    final_dict[u] = u.lower()
            final_text = hisep.join(sorted(final_dict, key=lambda x:x.lower()))
            if len(new_split) > 1:
                final_text += " #" + new_split[1]
            #print(line_count, "from", ','.join([str(x) for x in after_array]), ":", final_array, "->", final_text)
            for q in after_array:
                delete_after[q] = True
                print("Zapping", q, line_array[q].strip())
            final_new_line = final_text.strip() + "\n"
            if len(final_new_line) == len(lb):
                print("No length changed for line", line_count, "because of likely duplicate information.")
            line_array[line_count] = final_new_line

f = open(my_file_temp, "w")

for line_count in range(0, len(line_array)):
    if line_count in delete_after:
        continue
    f.write(line_array[line_count])

f.close()

mt.calf(my_file, my_file_temp)

if copy_back:
    pass #shutil.copy(my_file_temp, my_file)
else:
    mt.wm(my_file, my_file_temp)
