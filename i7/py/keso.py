# keso.py
#
# sorts notes from google keep and modifies them a bit if necessary
#

import os
import re
import sys
import pyperclip
from collections import defaultdict
from fractions import gcd
from functools import reduce

kfile = "c:/writing/temp/to_keep.txt"
kfile2 = "c:/writing/temp/to_keep_2.txt"

cmds = defaultdict(str)
cmds['palindromes'] = "ni no ai"
cmds['anagrams'] = "ni an"
cmds['vvff'] = "ni no vv"
cmds['spoonerisms'] = "np spopal"

specials = defaultdict(list)

separator = defaultdict(str)
separator['possible names'] = "\t"

by_length = True
read_paste = False

count = 0

check_header = True
header_yet = False

##############start functions

y2 = []
finals = []
strips = 0
strip_length = 0

def is_palindrome(x):
    x = re.sub("[^a-zA-Z]", "", x.lower())
    return x == x[::-1]

def is_onetwo(x):
    x2 = x.strip().lower()
    if x2.startswith("1") or x2.startswith("one"):
        if "2" in x2 or re.search("\b(two|to)\b", x2): return True
    return False

def is_anagrammy(x):
    if x.lower().startswith("anagram"): return True
    q = defaultdict(int)
    y = re.sub("^anagram(s)(:) *", "", x.lower(), 0, re.IGNORECASE)
    y = re.sub("[^a-z]", "", y)
    for j in y: q[j] += 1
    gc = reduce(gcd, q.values())
    return gc > 1

def dict_append(a, b, c):
    if b not in a.keys(): a[b] = []
    a[b].append(c)
    return

##############end functions

if read_paste:
    x = pyperclip.paste()
    y = x.split("\n")
    out_file = kfile
else:
    f = open(kfile, "r")
    y = [ g.rstrip() for g in f.readlines() ]
    out_file = kfile2

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'fi': read_paste = False
    elif arg == 'nf': read_paste = True
    elif arg == 'l': by_length = True
    elif arg == 'a': by_length = False
    elif arg == 'ch' or arg == 'hc': check_header = True
    elif arg == 'nh' or arg == 'hn': check_header = False
    elif arg == 'e' or arg == 'e1' or arg == '1e':
        os.system(kfile)
        exit()
    elif arg == 'e2' or arg == '2e':
        os.system(kfile2)
        exit()
    elif arg == 'eb' or arg == 'be' or arg == 'b':
        os.system(kfile)
        os.system(kfile2)
        exit()
    count += 1

for z in y:
    if not header_yet:
        if "=start actual notes" in z.lower():
            header_yet = True
            if not check_header: sys.exit("Header check is turned off, but =start actual notes text was found in file. Change this with -ch or -hc.")
        if check_header: continue
    if '=' * 10 in z.strip(): continue
    if not z.strip(): continue
    if z.strip() != z.lstrip():
        strips += 1
        strip_length += len(z.strip()) - len(z.lstrip())
    y2.append(z.strip())

if check_header and not header_yet:
    sys.exit("check_header set to true, but we did not find a header. Bailing. Use -nh or -hn to turn this off.")

# here we sort specific cases
for z in y2:
    z_raw = z if z.startswith("#") else re.sub(" *#.*", "", z)
    z_comments = re.sub("^ *?#", "", z)
    if z_raw.startswith('===='): continue
    elif re.search("[0-9]+ total sorted ideas", z_raw): continue
    elif is_palindrome(z_raw): dict_append(specials, 'palindromes', z)
    elif is_onetwo(z_raw): dict_append(specials, 'onetwos', z)
    elif ' / ' in z_raw or ',,' in z_raw: dict_append(specials, 'vvff', z)
    elif '==' in z_raw: dict_append(specials, 'btp', z)
    elif '*' in z_raw or re.search("( [0-9=]{2}|[0-9=]{2} )", z_raw): dict_append(specials, 'spoonerisms', z)
    elif ' ' not in z_raw or "\t" in z_raw: dict_append(specials, 'possible names', z)
    elif 'what a story' in z_raw.lower(): dict_append(specials, 'what a story', z)
    elif is_anagrammy(z_raw): dict_append(specials, 'anagrams', z)
    else: finals.append(z)

k = open(out_file, "w")

sep = "=" * 60

if len(specials.keys()):
    for q in sorted(specials.keys()): k.write("{:s}{:s} ({:s}):\n{:s}\n\n".format(sep, q, (cmds[q] if q in cmds.keys() else "may need loading instructions"), (separator[q] if q in separator.keys() else "\n").join(specials[q])))
    k.write(sep + "general" + "\n")

k.write("\n".join(sorted(finals, key=lambda l:len(l) if by_length else l, reverse=by_length)))
k.write("\n{:d} total sorted ideas\n".format(len(finals)))
k.close()

print("Opening", out_file)
os.system(out_file)
