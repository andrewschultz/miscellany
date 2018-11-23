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

specials = defaultdict(list)

separator = defaultdict(str)
separator['possible names'] = "\t"

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'fi': read_paste = True
    elif arg == 'nf': read_paste = False
    count += 1

read_paste = False

if read_paste:
    x = pyperclip.paste()
else:
    f = open(kfile), "r"
    x = f.readlines()

y = x.split("\n")
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
    elif ' ' not in z: dict_append(specials, 'possible names', z)
    elif 'what a story' in z.lower(): dict_append(specials, 'what a story', z)
    elif '==' in z: dict_append(specials, 'btp', z)
    else: finals.append(z)

k = open(kfile, "w")

if len(specials.keys()):
    k.write("=" * 80)
    for q in specials.keys(): k.write("\n{:s}{:s}:\n{:s}{:s}".format("=" * 50, q, (separator[q] if q in separator.keys() else "\n").join(specials[q]), "\n" if q in separator.keys() else ""))
    k.write("=" * 80)

k.write("\n".join(sorted(finals, key=len, reverse=True)))
k.write("\n{:d} total sorted ideas\n".format(len(finals)))
k.close()

print("Opening", kfile)
os.system(kfile)
