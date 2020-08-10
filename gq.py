# gq.py
# replaces gq.pl

import re
import i7
import sys
import os

def find_text_in_file(my_text, my_text_2, projfile):
    bf = os.path.basename(projfile)
    results_yet = False
    with open(projfile) as file:
        for (line_count, line) in enumerate (file, 1):
            found_one = False
            if not my_text_2:
                if re.search(r'\b{}(s?)\b'.format(my_text), line, re.IGNORECASE):
                    found_one = True
            else:
                if re.search(r'\b({}{}|{}{})\b'.format(my_text, my_text_2, my_text_2, my_text), line, re.IGNORECASE):
                    found_one = True
            if found_one:
                if not results_yet:
                    print('=' * 25, bf, "found matches", '=' * 25)
                    results_yet = True
                print("    Line", line_count, ':', line.strip())

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

try:
    my_text = sys.argv[1]
except:
    sys.exit("You need to specify text to find.")

try:
    my_text_2 = sys.argv[2]
except:
    print("No second word to search.")
    my_text_2 = ""

default_dir = i7.dir2proj()
if not default_dir:
	default_dir = i7.dict_val_or_similar(i7.curdef, i7.i7x)

my_proj = i7.proj2dir(default_dir)

print("Project", my_proj)

#file_list = i7.i7com[default_dir]
proj_umbrella = related_projects(default_dir)

print("Looking through projects:", ', '.join(proj_umbrella))

for proj in proj_umbrella:
    for projfile in i7.i7f[proj]:
        find_text_in_file(my_text, my_text_2, projfile)

#why do arrows move cursor?