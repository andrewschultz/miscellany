# gq.py
#
# replaces gq.pl
#
# usage gq.py as my_text (for alex smart)
# usage gq.py `as to search for the word AS
# can use one word or two

from collections import defaultdict
import mytools as mt
import re
import i7
import sys
import os

# variables in CFG file

max_overall = 100
max_in_file = 25

# constants

history_max = 100
my_cfg = "c:/writing/scripts/gqcfg.txt"

# options only on cmd line

view_history = False
post_open_matches = True

# variables not in CFG file

found_overall = 0

frequencies = defaultdict(int)

cmd_count = 1
my_text = []
default_proj = i7.dir2proj()
my_proj = ""

def hist_file_of(my_proj):
    return os.path.normpath(os.path.join("c:/writing/scripts/gqfiles", "gq-{}.txt".format(my_proj)))

def write_history(my_file, my_query):
    first_line = ' '.join(my_query).strip()
    try:
        f = open(my_file, "r")
    except:
        print("File open failed for", my_file, "so I'll make you create it.")
        sys.exit()
    ary = [x.strip() for x in f.readlines()]
    f.close()
    if first_line in ary:
        print(first_line, "already in history.")
        ary.remove(first_line)
    ary.insert(0, first_line)
    if len(ary) > history_max:
        print("Removing excess history",', '.join(ary[history_max:]))
        ary = ary[:history_max]
    f = open(my_file, "w")
    f.write("\n".join(ary))
    for x in range(0, len(ary)):
        print(x, ary[x])
    f.close()

def read_cfg():
    with open(my_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(';'): break
            if line.startswith(';'): continue
            if '=' in line:
                lary = line.strip().lower().split("=")
                if lary[0] == "max_overall":
                    global max_overall
                    max_overall = int(lary[1])
                elif lary[0] == "min_overall":
                    global min_overall
                    min_overall = int(lary[1])
                else:
                    print("Unknown = reading CFG, line", line_count, line.strip())

def find_text_in_file(my_text, projfile):
    global found_overall
    bf = i7.inform_short_name(projfile)
    if found_overall == max_overall:
        return -1
    found_so_far = 0
    with open(projfile) as file:
        for (line_count, line) in enumerate (file, 1):
            found_one = False
            if not my_text[1]:
                if re.search(r'\b{}(s?)\b'.format(my_text[0]), line, re.IGNORECASE):
                    found_one = True
            else:
                if re.search(r'\b({}{}|{}{})(s?)\b'.format(my_text[0], my_text[1], my_text[1], my_text[0]), line, re.IGNORECASE):
                    found_one = True
                elif re.search(r'\b{}{}(s?)\b'.format(my_text[0])) and re.search(r'\b{}{}(s?)\b'.format(my_text[1])):
                    found_one = True
            if found_one:
                if max_overall and found_overall == max_overall:
                    print("Found maximum overall", max_overall)
                    return found_so_far
                if max_in_file and found_so_far == max_in_file:
                    print("Found maximum per file", max_in_file)
                    return found_so_far
                if not found_so_far:
                    print('=' * 25, bf, "found matches", '=' * 25)
                found_so_far += 1
                found_overall += 1
                print("    ({:5d}):".format(line_count), line.strip())
                if post_open_matches:
                    mt.add_postopen(projfile, line_count)
    return found_so_far

def related_projects(my_proj):
    cur_proj = ""
    for x in i7.i7com:
        if my_proj in i7.i7com[x].split(","):
            if cur_proj:
                if i7.i7com[x] == i7.i7com[x]:
                    continue
                else:
                    print("WARNING, redefinition of project-umbrella for", myproj)
            cur_proj = x
    try:
        return i7.i7com[cur_proj].split(",")
    except:
        return [my_proj]

######################################main file below

read_cfg()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in i7.i7x:
        my_proj = i7.i7x[arg]
    elif arg in i7.i7xr:
        my_proj = i7.i7x[arg]
    elif arg == 'npo' or arg == 'pon':
        post_open_matches = False
    elif arg == 'po':
        post_open_matches = True
    elif arg[:2] == 'mf' and arg[2:].isdigit():
        max_in_file = int(arg[2:])
    elif arg[:2] == 'mo' and arg[2:].isdigit():
        max_overall = int(arg[2:])
    elif arg == 'vh':
        view_history = True
    else:
        if len(my_text) == 2:
            sys.exit("Found more than 2 text string to search. Bailing.")
        arg = arg.replace("`", "")
        my_text.append(arg)
        print("String", len(my_text), arg)
    cmd_count += 1

if not my_proj:
    if not default_proj:
        sys.exit("Must be in a project directory or specify a project.")
    print("Using default project", default_proj)
    my_proj = default_proj

#file_list = i7.i7com[default_proj]
proj_umbrella = related_projects(my_proj)

history_file = hist_file_of(my_proj)

if view_history:
    print(history_file)
    mt.npo(history_file)

if not len(my_text):
    sys.exit("You need to specify text to find.")

if len(my_text) == 1:
    print("No second word to search.")
    my_text.append('')

print("Looking through projects:", ', '.join(proj_umbrella))

for proj in proj_umbrella:
    if proj not in i7.i7f:
        print("WARNING", proj, "does not have project files associated with it. It may not be a valid inform project.")
        continue
    for projfile in i7.i7f[proj]:
        frequencies[i7.inform_short_name(projfile)] = find_text_in_file(my_text, projfile)

write_history(history_file, my_text)

if not found_overall: sys.exit("Nothing found.")

print("    ---- total differences printed:", found_overall)
for x in sorted(frequencies, key=frequencies.get, reverse=True):
    if frequencies[x] < 1: continue
    print("    ---- {} match{} in {}".format(frequencies[x], 'es' if frequencies[x] > 1 else '', i7.inform_short_name(x)))

temp_array = [i7.inform_short_name(x) for x in frequencies if frequencies[x] == 0]
if len(temp_array):
    print("No matches for", ', '.join(temp_array))

temp_array = [i7.inform_short_name(x) for x in frequencies if frequencies[x] == -1]
if len(temp_array):
    print("Left untested:", ', '.join(temp_array))

mt.post_open()
