# ruf.py
# rough tracker for what words can be
# wq.py = word-quick for searching for patterns
#
# this replaces text at the beginning or end of words
#
# keyword in case I forget: replace start, replace end, replaces at the start, replaces at the end
# replaces at the beginning, replaces at the end
#

import sys

default_in = 'st'
default_out = 'b'

from collections import defaultdict

words_by_length = defaultdict(set)

wbl = words_by_length

with open("c:/writing/dict/brit-1word.txt") as file:
    for (line_count, line) in enumerate (file, 1):
        x = line.lower().strip()
        wbl[len(x)].add(x)

delta = len(default_out) - len(default_in)

the_range = range(3, max(wbl) + 1)

for y in the_range:
    z = y + delta
    if z not in the_range:
        continue
    for w in wbl[y]:
        if w.endswith(default_in):
            w0 = w.replace(default_in, default_out, -1)
            if w0 in wbl[z]:
                print(w, w0)
