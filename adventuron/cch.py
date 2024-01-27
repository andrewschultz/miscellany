#
# note: need to account for where we have "" + string_var + ""
# this isn't "bracketed" but it may be something else
#
# also in dynamic_string
# to do: wee_clink : location "It sure is claustrophobic here in the {wee_clink}." ; flagged incorrectly, "location" should be type, also look for reciprocal definitions

import sys
import re
from shutil import copy
import mytools as mt
from collections import defaultdict

from Levenshtein import distance

# these are internals we don't want displayed to the reader
ignored = [ 'latest_warp_number', 'tempint', 'tempint2', 'current_talk_flag', 'found_meta_verbs_flag', 'confidence_meter', 'max_footnotes', 'commands_figured', 'entity' ]
# surprisingly max_footnotes is not used but I still want it there since it could be handy

# remove on post-comp merge
ignored.append('notify_string')

need_ref = False

my_lines_raw = defaultdict(list)
my_lines_var = defaultdict(list)
my_text = defaultdict(str)

in_if = defaultdict(list)
bracketed = defaultdict(list)
defined = defaultdict(list)

cmd_count = 1
my_file = "source_code.adv"
temp_file = "c:/writing/temp/source_code_notabs.adv"
def best_levenshtein(my_string):
    min_distance = 22
    min_array = []
    for x in defined:
        temp = distance(my_string, x)
        if temp > min_distance:
            continue
        if temp == min_distance:
            min_array.append(x)
            continue
        min_array = [x]
        min_distance = temp
    return min_array

def ignore_define(var_string):
    if not var_string:
        return True
    if var_string.startswith("footnote_") and 'status' in var_string:
        return True
    return False

def ignore_count(var_string):
    if var_string.startswith('hub'):
        return True
    return False

def remove_tabs(autowrite = True):
    big_string = ''
    tab_lines = 0
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if '\t' in line:
                line = line.replace('\t', '    ')
                tab_lines += 1
            big_string += line
    if not tab_lines:
        mt.bailfail("Found no tabs to replace.")
    if not autowrite:
        input("Hit return to overwrite.")
    f = open(temp_file, "w")
    f.write(big_string)
    f.close()
    copy(temp_file, my_file)
    sys.exit("Overwrote successfully.")

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg.startswith('-'):
        arg = arg[1:]
    if arg == 'r':
        remove_tabs()
    else:
        sys.exit(f"Invalid parameter {arg}")
    cmd_count += 1

with open(my_file) as file:
    for (line_count, line) in enumerate (file, 1):
        l = line.lower().strip()
        if l.startswith('cc_'):
            ary = l.split(' ')
            variable_name = ary[0]
            my_lines_raw[variable_name] = []
            my_lines_var[variable_name] = []
            my_text[variable_name] = variable_name[3:].replace('_', ' ')

with open(my_file) as file:
    for (line_count, line) in enumerate (file, 1):
        for l in my_lines_raw:
            if my_text[l] in line.lower():
                my_lines_raw[l].append((line_count, line.strip()))
            if l in line.lower():
                my_lines_var[l].append(line_count)

with open(my_file) as file:
    for (line_count, line) in enumerate (file, 1):
        if 'dynamic_integer' in line:
            continue
        x = re.findall("\{.*?\}", line.lower().strip())
        x = [re.sub(".*\{", "{", a) for a in x]
        for i in x:
            if '(' in i:
                continue
            if '?' in i:
                continue
            u = i[1:-1]
            if not u.strip():
                continue
            #print(u, line_count)
            bracketed[u].append(line_count)

with open(my_file) as file:
    for (line_count, line) in enumerate (file, 1):
        if "\t" in line:
            mt.warn("Tab in line {}. It should be replaced with 4 spaces.".format(line_count))
        if ": string" not in line and ": dynamic_string" not in line and ": integer" not in line:
            continue
        if line.strip().startswith(":"):
            continue
        ary = [x.strip().lower() for x in line.strip().split(':')]
        if not ignore_define(ary[0]):
            defined[ary[0]] = line_count

if need_ref:
    for u in sorted(list(my_lines_raw)):
        if len(my_lines_var[u]) == 0:
            mt.warn(u, "needs to be referenced in the code.")
        if len(my_lines_raw[u]) > 0:
            mt.warn(u, "may want to replace something in the code:")
            for mlr in my_lines_raw[u]:
                if mlr[1].startswith('cc_'):
                    continue
                print("    " , mlr[0], mlr[1].strip())

count = 0

y = set(defined) - set(bracketed) - set(ignored)

with open(my_file) as file:
    for (line_count, line) in enumerate (file, 1):
        all_words = []
        if line.strip().startswith('#'):
            continue
        if ': if' in line or ':if' in line:
            main_thing = re.findall('\(.*\)', line.strip())
            a = re.split(r"\b", main_thing[0])
            a = [x for x in a if re.search("[a-z_]", x)]
            for i in a:
                in_if[i] = line_count
            continue
        for y0 in y:
            if 'dynamic_text' in line and y0 in line: # themes definition
                in_if[y0] = line_count
                continue
            ldefs = re.sub("^.*?:", "", line.strip())
            if 'dynamic_string' in line and y0 in line:
                in_if[y0] = line_count
                continue

for b in sorted(y):
    if b in in_if:
        continue
    if ignore_count(b):
        continue
    count += 1
    print(count, b, "is defined but not bracketed.", defined[b])

z = set(bracketed) - set(defined) - set(ignored) - set(in_if)

if not count:
    mt.okay("Everything defined is bracketed!")

if z and y:
    print('=' * 50)

count = 0

for d in sorted(z):
    if d in in_if:
        continue
    if ignore_count(d):
        continue
    count += 1
    print(count, d, "is bracketed but not defined.", bracketed[d])
    print("    Best Levenshtein =", best_levenshtein(d))

if not count:
    mt.okay("All things bracketed are defined!")
