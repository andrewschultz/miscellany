# zr.py
#
# trivial capitalizations and room name expansion
#
# e.g. "Bile Libe" converts all bile libe to Bile Libe, in libe>in Bile Libe converts "in libe" to "in bile libe"
#
# named zr.py because ZeroRez was the original in Ailihphilia until changed to DevReserved.
#
# zr.txt or 'e' on cmd line brings up cfg file
#

from collections import defaultdict
from shutil import copy
from filecmp import cmp
import os
import re
import sys
import i7

zr_data = "c:/writing/scripts/zr.txt"

default_proj = ""
proj = i7.dir2proj(os.getcwd())
print(proj)
if proj: print("Getting directory/project", proj, "from command line directory. If you define another, it will overwrite this.")

only_test = False
source_only = False
quick_quote_reject = True

line_to_open = 0
open_post = False

max_total_errs = 0
max_errs_left = 0
max_errs_per_file = 0

always_adj = defaultdict(bool)
cap_search = defaultdict(bool)
regex_detail = defaultdict(str)
in_expand = defaultdict(str)

text_change = defaultdict(str)
text_raw = defaultdict(str)

count = 1

######################begin functions

def usage():
    print("Currently you can specify the project to change to, with a shortcut or full name.")
    print("c edits the source, though you can just type np zr.py instead.")
    print("e edits the text, though you can just type zr.txt instead.")
    print("o/no/on toggles opening zr.txt post-errors.")
    print('qq is quick quotes reject. understand "x y" as X y will be skipped.')
    print("t only tests things. It doesn't copy back over.")
    print("e# = max errs per file, t# = max total errors")

def check_superfluous_zr(my_dir):
    oj = os.path.join(my_dir, "zr.txt")
    if os.path.exists(oj) and os.getcwd() != "c:/writing/scripts":
        print("WARNING superfluous zr.txt in " + my_dir + ". They should all be migrated to", zr_data + ". I am opening the local and regular zr.txt.")
        os.system(zr_data)
        os.system(oj)
        print("erase", oj)
        exit()

def title_unless_caps(a, b):
    if a.startswith('"') and a.endswith('"'): return a
    if a == a.upper(): return a
    # this is a hack but it does the job of tracking quotes
    # the alternative is a look-behind regex that is very confusing indeed
    if a.startswith('"'): b = '"' + b
    if a.endswith('"'): b = b + '"'
    return b

def with_quotes(a, b):
    if "'{:s}'".format(a) in b: return True
    if '"{:s}"'.format(a) in b: return True
    return False

def check_source(a):
    noncaps_difs = 0
    caps_difs = 0
    b = a + "2"
    short = os.path.basename(a)
    short2 = os.path.basename(b)
    fout = open(b, "w", newline='\n') # STORY.NI files have unix line endings
    global max_total_errs
    global max_errs_left
    with open(a) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("test") and "with" in line:
                fout.write(line)
                continue
            if (max_errs_per_file and (noncaps_difs + caps_difs >= max_errs_per_file)) or (max_total_errs and (noncaps_difs + caps_difs >= max_errs_left)):
                fout.write(line)
                continue
            ll = line
            if 'use1 entry on' in ll.lower():
                print("NOTE replacing use1 entry on with use1 entry with at line", line_count)
                ll = re.sub("use1 entry on", "use1 entry with", ll)
                noncaps_difs += 1
            if 'useoning noun on' in ll.lower():
                print("NOTE replacing use1 entry on with use1 entry with at line", line_count)
                ll = re.sub("useoning noun on", "useoning noun with", ll)
                noncaps_difs += 1
            if ll.startswith('understand') and 'when' not in ll:
                fout.write(ll)
                continue
            if '[ic]' not in ll: # ignore changes/cases
                for t in text_change.keys():
                    if text_raw[t] in ll.lower():
                        ll_old = ll
                        ll = re.sub(r'\b{:s}\b'.format(t), text_change[t], ll, 0, re.IGNORECASE)
                        if ll_old != ll:
                            print('NOTE {:s} line {:d} non-caps-replacing "{:s}" with "{:s}"'.format(short, line_count, text_raw[t], text_change[t]))
                            noncaps_difs += 1
                this_line_yet = False
                for x in cs:
                    if x.lower() in line.lower():
                        ll_old = ll
                        if quick_quote_reject and with_quotes(x.lower(), line.lower()): continue
                        # once I understand regex better, I want to try this...
                        # ll = re.sub(r'(?<=^(([^"]*(?<!\\)"[^"]*(?<!\\)"[^"]*)*|[^"]*))\b{:s}\b'.format(regex_detail[x] if x in regex_detail.keys() else x), lambda match: title_unless_caps(match.group(0), x, match), ll, 0, re.IGNORECASE)
                        ll = re.sub(r'(\"?)\b{:s}\b(\"?)'.format(regex_detail[x] if x in regex_detail.keys() else x),
                        # ll = re.sub(r'\b{:s}\b'.format(regex_detail[x] if x in regex_detail.keys() else x),
                          lambda match: title_unless_caps(match.group(0), x), ll, 0, re.IGNORECASE)
                        if ll != ll_old:
                            err = "capitalized" if len(ll) == len(ll_old) else "represented"
                            caps_difs += 1
                            print("                    also mis{:s}".format(err) if this_line_yet else "Line {:d} of {:s} mis{:s}".format(line_count, short, err), x, "" if this_line_yet else "==={:s}".format(line.strip()))
                            this_line_yet = True
            fout.write(ll)
    fout.close()
    difs = noncaps_difs + caps_difs
    max_errs_left -= difs
    if (max_errs_per_file and (noncaps_difs + caps_difs >= max_errs_per_file)) or (max_total_errs and (noncaps_difs + caps_difs >= max_errs_left)):
        print(short, "hit the maximum number of errors and may or may not have overrun. You may wish to rerun.")
    if not cmp(a, b):
        if difs == 0:
            print("There are no flagged differences, but", short, "is not", short2 + ". This should not happen. Bailing.")
            exit()
        print(difs, "differences", noncaps_difs, "noncaps", caps_difs, "caps differences, copying", short, "back over")
        if only_test:
            print("Testing differences, so, not copying back over.")
            os.system("wm \"{:s}\" \"{:s}\"".format(a, b))
        else:
            try:
                copy(b, a)
            except:
                print("Couldn't copy back to story.ni.")
                exit()
            try:
                os.remove(b)
            except:
                print("Tried and failed to remove story.ni2.")
                exit()
    else:
        if difs:
            print("Oops! I flagged differences in", short, "but the changed file is the same as the old one. This means there is a bug but not a lethal one. Check the changed line candidates.")
            # os.system("wm \"{:s}\" \"{:s}\"".format(a, b))
        else:
            print("No differences in", short + ", no copying back over" + (", so not running diff" if only_test else "") + ".")
        try:
            os.remove(b)
        except:
            print("Tried and failed to delete tempfile", b)

#############end functions

if not os.path.exists(zr_data): print("You need the data file {:s} for this to work.".format(zr_data))

while count < len(sys.argv):
    myarg = sys.argv[count].lower()
    if (myarg[0] == '-'):
        myarg = myarg[1:]
    if myarg == 'e':
        check_superfluous_zr(os.getcwd())
    elif myarg == 'c':
        i7.open_source()
    elif myarg == 's': source_only = True
    elif myarg == 't': only_test = True
    elif myarg[0] == 'e' and myarg[1:].isdigit: errs_per_file = int(myarg[1:])
    elif (myarg[0] == 'te' or myarg[0] == 'et') and myarg[2:].isdigit: max_total_errs = int(myarg[2:])
    elif myarg == 'q': quick_quote_reject = True
    elif myarg == 'o': open_post = True
    elif myarg == 'no' or myarg == 'on': open_post = False
    elif myarg == 'qn' or myarg == 'nq': quick_quote_reject = False
    elif myarg in i7.i7x.keys():
        proj = i7.i7x[myarg]
        print("Changing project to", proj)
    else:
        print("Bad argument", sys.argv[count])
        usage()
    count += 1

with open(zr_data) as file: #ugh. I hate reading stuff in twice, but it's this or defining a double-array dictionary.
    for (line_count, line) in enumerate(file, 1):
        if line.startswith("DEFAULTPROJ="):
            temp = line[12:].strip().lower()
            default_proj = i7.proj_exp(temp)
            break

if not default_proj:
    if not proj: sys.exit("You need to define a default project or be in a directory where I can determine your project.")
    else: print("WARNING: you did not have a default project in zr.txt.")

if proj: check_superfluous_zr(i7.proj2dir(proj))

got_proj = False
in_proj = False

rxd = []
with open(zr_data) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith('#'): continue
        if line.startswith(';'): break
        if line.startswith("DEFAULTPROJ"): continue
        if line.startswith("PROJ"):
            if not line.startswith("PROJ="): sys.exit("You need to start line {:d} with PROJ= not {:s}.".format(line_count, line[:5]))
            cur_proj = i7.proj_exp(line.lower().strip()[5:])
            if cur_proj == proj:
                got_proj = True
                in_proj = True
            else:
                in_proj = False
            continue
        if not in_proj: continue
        add_first_loc_word = False
        if line.startswith("in:"):
            line = line[3:]
            add_first_loc_word = True
        if ',' in line: line = re.sub(" *#.*$", "", line) #remove comments at the end
        if '>' in line and "\t" not in line: # this could get hairy later if I use forward-checks in regexes
            ary = line.strip().split(">") #this is converting one text to another e.g. in bile>in libe>in Bile Libe
            last_one = ary[len(ary) - 1].strip()
            for x in range(0, len(ary) - 1):
                text_change[ary[x].lower().strip()] = last_one
        always = False
        if line.startswith('a:'):
            line = re.sub('a:', '', line)
            always = True
        if not line.strip(): continue
        if "\t" in line:
            line_ary = line.strip().split("\t")
            regex_detail[line_ary[0]] = line_ary[1]
            continue
        q = re.split(" *, *", line.strip())
        for q1 in range(0, len(q)):
            if not q[q1].strip(): continue
            temp = q[q1]
            if temp in cap_search:
                print("WARNING line {:d}:".format(line_count), "entry", q1, "=", temp, "already accounted for, probably a duplicate.")
                if not line_to_open: line_to_open = line_count
            cap_search[temp] = True
            if always:
                always_adj[temp] = True
            if add_first_loc_word:
                ary = temp.split(" ")
                if len(ary) == 1:
                    print("WARNING room name {:s} has no spaces. Skipping.".format(temp))
                    sys.exit()
                    continue
                al = len(ary)
                from_last_word = r'(if|in) {:s}([^-])'.format(ary[al-1].lower())
                from_first_word = r'(if|in) {:s}(!>? {:s})' .format(ary[0].lower(), ary[1].lower())
                to_phrase = r'\1 {:s}'.format(temp)
                text_change[from_last_word] = to_phrase
                text_change[from_first_word] = to_phrase + r'\2'
                #print(from_last_word, "&", from_first_word, "->", to_phrase)

for q in text_change:
    text_raw[q] = re.sub(" *[\[\(].*", "", q)

if not got_proj:
    print("Couldn't find anything in the data file {:s} for project {:s}.".format(zr_data, proj))
    if proj == 'stale-tales-slate': print("The Stale Tales Slate is too general. You need to choose Roiling or Shuffling.")
    sys.exit()

cs = sorted(list(cap_search))

for x in i7.i7f[proj]:
    if 'tests' in x.lower(): continue
    if source_only and 'story.ni' not in x.lower(): continue
    check_source(x)

if line_to_open:
    if not open_post: sys.exit("Use -o to open the config file at the line that threw a warning.")
    i7.npo(zr_data, line_to_open)
elif open_post: sys.exit("No errors/inconsistencies found in " + zr_data)