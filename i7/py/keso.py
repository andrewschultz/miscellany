# keso.py
#
# sorts notes from google keep and modifies them a bit if necessary
#

import os
import re
import sys
import pyperclip
from collections import defaultdict

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

count = 0

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'fi': read_paste = True
    elif arg == 'nf': read_paste = False
    count += 1

read_paste = False

if read_paste:
    x = pyperclip.paste()
    y = x.split("\n")
    out_file = kfile
else:
    f = open(kfile, "r")
    y = [ g.rstrip() for g in f.readlines() ]
    out_file = kfile2

y2 = []
finals = []
strips = 0
strip_length = 0

def is_palindrome(x):
    x = re.sub("[^a-zA-Z]", "", x.lower())
    return x == x[::-1]

def dict_append(a, b, c):
    if b not in a.keys(): a[b] = []
    a[b].append(c)
    return

for z in y:
    if '=' * 10 in z.strip(): continue
    if not z.strip(): continue
    if z.strip() != z.lstrip():
        strips += 1
        strip_length += len(z.strip()) - len(z.lstrip())
    y2.append(z.strip())

# here we sort specific cases
for z in y2:
    if z.startswith('===='): continue
    elif re.search("[0-9]+ total sorted ideas", z): continue
    elif is_palindrome(z): dict_append(specials, 'palindromes', z)
    elif is_anagrammy(z): dict_append(specials, 'anagrams', z)
    elif ' / ' in z: dict_append(specials, 'vvff', z)
    elif re.search("([0-9]=|=[0-9]| \* )", z): dict_append(specials, 'spoonerisms', z)
    elif ' ' not in z: dict_append(specials, 'possible names', z)
    elif 'what a story' in z.lower(): dict_append(specials, 'what a story', z)
    elif '==' in z: dict_append(specials, 'btp', z)
    else: finals.append(z)

k = open(out_file, "w")

sep = "=" * 60

if len(specials.keys()):
    for q in sorted(specials.keys()): k.write("{:s}{:s} ({:s}):\n{:s}\n\n".format(sep, q, (cmds[q] if q in cmds.keys() else "may need loading instructions"), (separator[q] if q in separator.keys() else "\n").join(specials[q])))
    k.write(sep + "general" + "\n")

k.write("\n".join(sorted(finals, key=len, reverse=True)))
k.write("\n{:d} total sorted ideas\n".format(len(finals)))
k.close()

print("Opening", out_file)
os.system(out_file)
