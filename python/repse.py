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
my_in = ''
my_out = ''

from collections import defaultdict

cmd_count = 1

search_end = False
search_start = True

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if ',' in arg:
        a = arg.split(',')
        if len(a) != 2:
            sys.exit("CSVs need 2 arguments.")
        (my_in, my_out) = (a[0], a[1])
    elif arg == 'e':
        search_end = True
        search_start = False
    elif arg == 's':
        search_start = True
        search_end = False
    elif arg in ( 'b', 'es', 'se' ):
        search_end = search_start = True
    else:
        if arg[0] == '.':
            arg = arg[1:]
        if not my_in:
            print("Assuming non_control parameter {} is input--use commas to make sure".format(arg))
            my_in = arg
        elif not my_out:
            print("Assuming non_control parameter {} is output--use commas to make sure".format(arg))
            my_out = arg
        else:
            sys.exit("Too many non-control parameters. Type ? for usage.")
    cmd_count += 1

if not my_in or not my_out:
    print("Forgot to define defaults.")
    if not my_in:
        my_in = default_in
    if not my_out:
        my_out = default_out

words_by_length = defaultdict(set)

wbl = words_by_length

with open("c:/writing/dict/brit-1word.txt") as file:
    for (line_count, line) in enumerate (file, 1):
        x = line.lower().strip()
        wbl[len(x)].add(x)

delta = len(my_out) - len(my_in)

the_range = range(3, max(wbl) + 1)

for y in the_range:
    z = y + delta
    if z not in the_range:
        continue
    for w in wbl[y]:
        if search_end:
            if w.endswith(my_in):
                w0 = w.replace(my_in, my_out, -1)
                if w0 in wbl[z]:
                    print(w, w0)
        if search_start:
            if w.startswith(my_in):
                w0 = w.replace(my_in, my_out, 1)
                if w0 in wbl[z]:
                    print(w, w0)
