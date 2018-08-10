# lanv.py
#
# sorts out the cases of the i6 languageverb function
#
# usage: (no arguments yet, just looks at story.ni)

import i7
import re
from collections import defaultdict

c = 0

ignore_verbs = defaultdict(int)
lv_entries = defaultdict(int)
understand_entries = defaultdict(int)

lasts = [ '' ] * 6
cur_nfr = 0
cur_lev = 0

proj_name = "ailihphilia"
file_name = "story.ni"
ignore_file = "c:/writing/scripts/lanv.txt"

def read_language_verb(f):
    got_lv_yet = False
    with open(f) as file:
        for (line_count, line) in enumerate(file, 1):
            if '[ LanguageVerb i;' in line: got_lv_yet = True
            if not got_lv_yet: continue
            if 'after "Language.i6t".' in line: break
            if "'" in line:
                j = re.compile("'([a-z]+)[\\\/]*'")
                for q in j.findall(line):
                    if q in lv_entries.keys(): print("WARNING", q, "appears in", lv_entries[q], "and is repeated at", line_count)
                    else: lv_entries[q] = line_count
                print(j.findall(line))
    if not got_lv_yet: sys.exit("{:s} has no LanguageVerb replacement function. Bailing.")
    return

def read_ignore_file():
    with open(ignore_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): next

read_language_verb(file_name)
read_ignore_file()

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
            # print('after', line.strip(), cur_lev, cur_nfr)
        if cur_lev > cur_nfr:
            if line.startswith("understand") and 'as something new' in line:
                c += 1
                j = re.compile('"([a-z ]+)"')
                for q in j.findall(line):
                    if q in understand_entries.keys(): print("WARNING", q, "appears in", understand_entries[q], "and is repeated at", line_count)
                    else: understand_entries[q] = line_count
                #print(cur_lev, cur_nfr, c, outline_str, line_count, line.strip())
                continue

x = sorted(list(set(understand_entries.keys()).union(set(lv_entries.keys())).difference(set(ignore_verbs.keys()))))

for y in x:
    if y not in lv_entries.keys(): print(y, understand_entries[y], "needs LV entry or needs to be in the ignore file.")

for y in x:
    if y not in understand_entries.keys(): print(y, lv_entries[y], "needs UNDERSTAND/AS line or needs to be in the ignore file.")
