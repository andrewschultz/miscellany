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
unit_test_file = defaultdict(str)
err_msg = defaultdict(str)
translation = defaultdict(str)

lasts = [ '' ] * 6
cur_nfr = 0
cur_lev = 0

proj_name = ''
lanv_config = "c:/writing/scripts/lanv.txt"

lanv_ignore = "lanv.py should ignore this"

def lang_verb_line(f):
    with open(f) as file:
        for (line_count, line) in enumerate(file, 1):
            if '[ LanguageVerb' in line: return line_count
    sys.exit("Could not fine line with [ LanguageVerb in {:s}. Bailing.".format(f))

def check_unit_tests(proj):
    in_unit_file = defaultdict(str)
    if proj not in unit_test_file.keys(): sys.exit("Couldn't find unit test file for {:s} in {:s}.".format(proj, lanv_config))
    tf = unit_test_file[proj]
    if not os.path.exists(tf): sys.exit("BAILING: {:s} does not exist.".format(unit_test_file[proj]))
    need_text_next = False
    with open(tf) as file:
        for (line_count, line) in enumerate(file, 1):
            if need_text_next:
                need_text_next = False
                if line.startswith('>') or line.startswith('#') or not re.search("[a-z]", line, re.IGNORECASE): print("WARNING Line", line_count, "may need verification text.")
                continue
            if line.startswith(">") and "xtratxt" in line:
                need_text_next = True
                l2 = re.sub("^>", "", line.lower().strip())
                l2 = re.sub(" *xtratxt.*", "", l2)
                in_unit_file[l2] = line_count
    x3 = x.difference(set(in_unit_file.keys()))
    for x4 in sorted(x3):
        if x4 not in translation.keys() or not translation[x4]:
            print(">{:s} xtratxt\nDOESN'T APPEAR TO BE IN LANGUAGEVERB.\n".format(x4))
        else:
            print(">{:s} xtratxt\n{:s}\n{:s}.\n".format(x4, err_msg[x4] if x4 in err_msg.keys() else "I only understood you as far as wanting to", translation[x4]))
    if len(x3): print(len(x3), "total commands to fill into", tf)

def read_language_verb(f):
    got_lv_yet = False
    with open(f) as file:
        for (line_count, line) in enumerate(file, 1):
            if '[ LanguageVerb i;' in line: got_lv_yet = True
            if not got_lv_yet: continue
            if 'after "Language.i6t".' in line: break
            if "'" in line:
                quoted_bit = re.sub(".*print ['\"]", "", line.strip())
                quoted_bit = re.sub("['\"].*", "", quoted_bit)
                if re.search("print ['\"][A-Z]", line):
                    lw = quoted_bit.split(" ")
                    print(lw[0], lw)
                    if lw[0] != lw[0].upper() or get_all_caps:
                        print("WARNING:", quoted_bit, "may need to be in lowercase to start.")
                j = re.compile("'([a-z ]+)[\\\/]*'")
                for q in j.findall(line):
                    if q in lv_entries.keys(): print("WARNING", q, "appears in", lv_entries[q], "and is repeated at", line_count)
                    else:
                        lv_entries[q] = line_count
                        translation[q] = quoted_bit
                # print(j.findall(line))
    if not got_lv_yet: sys.exit("{:s} has no LanguageVerb replacement function. Bailing.")
    sys.exit("!")
    return

def read_lanv_config():
    cur_proj = "general"
    with open(lanv_config) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if line.lower().startswith("project="):
                l = re.sub(".*=", "", line.strip())
                cur_proj = l.lower()
                continue
            if line.lower().startswith("errmsg="):
                l = re.sub(".*=", "", line.strip())
                err_msg[cur_proj] = l
                continue
            if line.lower().startswith("testfile="):
                l = re.sub(".*=", "", line.strip())
                unit_test_file[cur_proj] = l
                continue
            ll = line.lower().strip().split(',')
            #print(cur_proj, ll)
            for verb in ll:
                if verb in ignore_verbs[cur_proj].keys():
                    print(cur_proj, "has duplicate verb", verb," at line", line_count, "in", lanv_config)
                    continue
                ignore_verbs[cur_proj][verb] = True

count = 1
tried_yet = ''
default_project = "ailihphilia"
check_test_file = False
get_all_caps = False

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg == 'c': i7.open_source()
    elif arg == 'cl': open_lang_verb_line = True
    elif arg == 'e': i7.open_config()
    elif arg == 't': check_test_file = True
    elif arg == 'gac': get_all_caps = True # detects ALL CAPS at start of a subject e.g. "SEARCH" is flagged along with "Search"
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

if open_lang_verb_line: i7.npo(file_name, lang_verb_line(file_name))

read_language_verb(file_name)
read_lanv_config()

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
                        else:
                            understand_entries[q3] = line_count
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

if check_test_file: check_unit_tests(proj_name)

if not ever_ignore_section: print("No", '"[{:s}]"'.format(lanv_ignore), "anywhere in story.ni. This isn't critical, but if there are specific verbs the game disables, it is a help.")
