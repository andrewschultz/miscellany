#
# mytools.py
#
# a bunch of auxiliary/helper scripts to make things easier

import re
import pyperclip
import sys
import os
import __main__ as main
from collections import defaultdict
from fractions import gcd
from functools import reduce

def bail_if_not(f, file_desc = ""):
    if not os.path.exists(f): sys.exit("Need {:s}{:s}file {:s}".format(file_desc, " " if file_desc else "", f))

def plur(a):
    return '' if a == 1 else 's'

def cheap_html(text_str, out_file = "c:/writing/temp/temp-htm.htm", title="HTML generated from text", launch = True):
	f = open(out_file, "w")
	f.write("<html>\n<title>{:s}</title>\n<body><\n><pre>\n{:s}\n</pre>\n</body>\n</html>\n".format(title, text_str))
	f.close()
	if launch: os.system(out_file)

def nohy(x): # mostly for command line argument usage, so -s is -S is s is S.
    if x[0] == '-': x = x[1:]
    return x.lower()

nohyp = noh = nohy

def is_anagrammy(x):
    q = defaultdict(int)
    y = re.sub("[^a-z]", "", x.lower())
    for j in y: q[j] += 1
    gc = reduce(gcd, q.values())
    return gc > 1

def is_limerick(x, accept_comments = False): # quick and dirty limerick checker
    if accept_comments and '#lim' in x: return True
    if x.count('/') != 4: return False
    temp = re.sub(".* #", "", x)
    if len(x) > 120 and len(x) < 240: return True

def clipboard_slash_to_limerick(print_it = False):
    x = slash_to_limerick(pyperclip.paste())
    if print_it: print(x)
    pyperclip.copy(x)
    return "!"

def slash_to_limerick(x): # limerick converter
    retval = ""
    print(x.split("\n"))
    for x0 in x.split("\n"):
        if "/" in x0:
            retval += "====\n" + re.sub(" *\/ ", "\n", x0) + "\n"
        else: retval += x0 + "\n"
    return retval.rstrip() + "\n"

def cfgary(x, delimiter="\t"): # A:b,c,d -> [b, c, d]
    if ':' not in x:
        print("WARNING, cfgary called on line without starting colon")
        return []
    temp = re.sub("^[^:]*:", "", x)
    return temp.split(delimiter)

def compare_shuffled_lines(f1, f2, bail = False, max = 0):
    freq = defaultdict(int)
    total = defaultdict(int)
    with open(f1) as file:
        for line in file:
            freq[line.lower().strip()] += 1
            total[line.lower().strip()] += 1
    with open(f2) as file:
        for line in file:
            freq[line.lower().strip()] -= 1
            total[line.lower().strip()] += 1
    difs = [x for x in freq if freq[x]]
    left = 0
    right = 0
    totals = 0
    if len(difs):
        for j in difs:
            if freq[j] > 0 : left += 1
            else: right += 1
            totals += 1
            if not max or totals <= max:
                print('Extra', j, "/", "{:d} of {:d} in {:s}".format(abs(freq[j]), total[j], os.path.basename(f1) if freq[j] > 0 else os.path.basename(f2)))
            elif max and totals == max + 1:
                print("Went over maximum of", max)
        print(os.path.basename(f1), "has", left, "but", os.path.basename(f2), "has", right)
    else:
        print("No shuffle-diffs")
    if bail and len(difs):
        print("Compare shuffled lines is bailing on difference.")
        sys.exit()

csl = cs = compare_shuffled_lines

if os.path.basename(main.__file__) == "mytools.py":
    print("mytools.py is a header file. It should not be run on its own.")
    print("Try running something else with the line import i7, instead, or ? to run a test.")
    exit()
