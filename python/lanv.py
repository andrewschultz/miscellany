# lanv.py
#
# sorts out the cases of the i6 languageverb function
#
# usage: (no arguments yet, just looks at story.ni)

import sys
import os
import i7
import re
from collections import defaultdict

c = 0

ignore_verbs = defaultdict(lambda: defaultdict(bool))
lv_entries = defaultdict(int)
understand_entries = defaultdict(int)

lasts = [ '' ] * 6
cur_nfr = 0
cur_lev = 0

ignore_file = "c:/writing/scripts/lanv.txt"

lanv_ignore = "lanv.py should ignore this"

def read_language_verb(f):
    got_lv_yet = False
    with open(f) as file:
        for (line_count, line) in enumerate(file, 1):
            if '[ LanguageVerb i;' in line: got_lv_yet = True
            if not got_lv_yet: continue
            if 'after "Language.i6t".' in line: break
            if "'" in line:
                j = re.compile("'([a-z ]+)[\\\/]*'")
                for q in j.findall(line):
                    if q in lv_entries.keys(): print("WARNING", q, "appears in", lv_entries[q], "and is repeated at", line_count)
                    else: lv_entries[q] = line_count
                # print(j.findall(line))
    if not got_lv_yet: sys.exit("{:s} has no LanguageVerb replacement function. Bailing.")
    return

def read_ignore_file():
    cur_proj = "general"
    with open(ignore_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if line.lower().startswith("project="):
                l = re.sub(".*=", "", line.strip())
                cur_proj = l.lower()
                continue
            ll = line.lower().strip().split(',')
            #print(cur_proj, ll)
            for verb in ll:
                if verb in ignore_verbs[cur_proj].keys():
                    print(cur_proj, "has duplicate verb", verb," at line", line_count, "in", ignore_file)
                    continue
                ignore_verbs[cur_proj][verb] = True

count = 1
tried_yet = ''
default_project = "ailihphilia"

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg == 'c': i7.open_source()
    elif arg == 'e': i7.open_config()
    else:
        if tried_yet: sys.exit("Tried to define a project name -- or a bad flag -- twice. {:s}/{:s}.".format(tried_yet, arg))
        tried_yet = arg
        proj_name = i7.proj_exp(arg, False)
        if not proj_name: print ("WARNING", arg, "not identified as a project.")
    count += 1

if not proj_name:
    if i7.dir2proj(os.getcwd()): proj_name = i7.dir2proj(os.getcwd())
    else: proj_name = default_project
    print("No project name, going with", proj_name)

file_name = i7.src(proj_name)

read_language_verb(file_name)
read_ignore_file()

ever_ignore_section = ignore_section = False

with open(file_name) as file:
    for (line_count, line) in enumerate(file, 1):
        inl = i7.new_lev(line)
        if inl:
            # print('before', line.strip(), cur_lev, cur_nfr)
            # print(line_count, line.strip())
            cur_lev = inl
            nfr = 'not for release' in line.lower()
            if nfr: cur_nfr = (cur_lev if cur_lev > cur_nfr else cur_nfr)
            elif cur_lev >= cur_nfr: cur_nfr = 0
            for x in range(0, cur_lev): lasts[x] = ''
            lasts[cur_lev - 1] = line.strip()
            outline_str = '/'.join(lasts[cur_lev - 1:])
            ignore_section = False
            # print('after', line.strip(), cur_lev, cur_nfr)
        if cur_lev > cur_nfr:
            if lanv_ignore in line:
                ever_ignore_section = ignore_section = True
                continue
            if ignore_section: continue
            if line.startswith("understand") and 'as something new' in line:
                c += 1
                j = re.compile('"([a-z \/]+)"')
                for q in j.findall(line):
                    q2 = q.split('/')
                    #print(line_count, q2)
                    for q3 in q2:
                        if q3 in understand_entries.keys(): print("Line", line_count, "WARNING", q3, "appears in", understand_entries[q3], "and is repeated at", line_count)
                        else: understand_entries[q3] = line_count
                #print(cur_lev, cur_nfr, c, outline_str, line_count, line.strip())
                continue

my_ignore = set(ignore_verbs["general"].keys()).union(set(ignore_verbs[proj_name].keys()))

x = set(understand_entries.keys()).union(set(lv_entries.keys())).difference(my_ignore)

x1 = x.difference(set(lv_entries.keys()))
x2 = x.difference(set(understand_entries.keys()))

if len(x1):
    print("================BELOW needs LV entry or needs to be in the ignore file.")
    for y in sorted(list(x1), key=understand_entries.get):
        if y not in lv_entries.keys(): print("{:5d}:".format(understand_entries[y]), y)

if len(x2):
    print("================BELOW need UNDERSTAND/AS line or needs to be in the ignore file. Or maybe it can be deleted altogether, since it might not be in reachable code.")
    for y in sorted(list(x2), key=lv_entries.get):
        if y not in understand_entries.keys(): print("{:5d}:".format(lv_entries[y]), y, )

if len(x1): print(len(x1), "PRESENT understand     /MISSING no languageverb")
if len(x2): print(len(x2), "MISSING no languageverb/PRESENT understand")

if not ever_ignore_section: print("No", '"[{:s}]"'.format(lanv_ignore), "anywhere in story.ni. This isn't critical, but if there are specific verbs the game disables, it is a help.")
