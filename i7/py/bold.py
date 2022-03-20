# bold.py
# looks for CAPITALIZED stuff inside quotes to put in BOLD with [b] [r] tags.
# ignore = actual bold text to ignore
# ignore_auxiliary = non bold case by case text that should be flagged as ignorable

import mytools as mt
import sys
import i7
import re
import pyperclip
import os

from collections import defaultdict

ignores = defaultdict(int)
counts = defaultdict(int)

show_line_count = False
show_count = False
count = 0
clip = False
list_caps = False

try:
    if sys.argv[1] == 'c':
        clip = True
    elif sys.argv[1] == 'l':
        list_caps = True
except:
    pass

def get_ignores():
    if not os.path.exists("boldi.txt"):
        print("No ignores file boldi.txt.")
        return
    with open("boldi.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                continue
            for x in line.lower().strip().split(','):
                if x in ignores:
                    print("duplicate ignore {} at line {}.".format(x, line_count))
                ignores[x] = 1

def maybe_bold(my_str):
    if my_str.count(' ') > 2:
        return my_str
    if re.search("^[RYGPB\*\?]{3,}$", my_str):
        return my_str
    ml = my_str.lower()
    if ml in ignores:
        return my_str
    counts[ml] += 1
    return '[b]{}[r]'.format(my_str)

def bolded_caps(my_str):
    x = re.sub(r"(?<!(\[b\]))\b([A-Z]{2,}[A-Z ]*[A-Z])\b", lambda x: maybe_bold(x.group(0)), my_str)
    x = x.replace("[b][b]", "[b]")
    x = x.replace("[r][r]", "[r]")
    x = re.sub(r"(\[b\][ A-Z:']+)\[b\]", r'\1', x)
    return x

def code_exception(my_line):
    if "a-text" in my_line or "b-text" in my_line or my_line.startswith("understand"):
        return True
    return False

if clip:
    print("NOTE: deprecated for bold.py | clip")
    orig = pyperclip.paste()
    final = bolded_caps(orig)
    print(final)
else:
    get_ignores()
def process_potential_bolds(my_file):
    count = 0
    # sys.stderr.write("{} starting {}.\n".format('=' * 50, my_file))
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if code_exception(line): # letters settler readings don't count
                continue
            lr = line.rstrip()
            by_quotes = lr.split('"')
            new_ary = []
            for x in range(0, len(by_quotes)):
                if x % 2 == 0:
                    new_ary.append(by_quotes[x])
                else:
                    new_ary.append(bolded_caps(by_quotes[x]))
            new_quote = '"'.join(new_ary)
            if new_quote != lr:
                count += 1
                out_string = new_quote
                if show_line_count:
                    out_string = "{} {}".format(line_count, new_quote)
                if show_count:
                    out_string = "{} {}".format(count, new_quote)
                print(out_string)
    sys.stderr.write("{} {} has {} total boldable lines.\n".format('=' * 50, my_file, count))

my_project = i7.dir2proj()
if not my_project:
    sys.exit("You need to go to a directory with a project.")

if clip:
    print("NOTE: deprecated for bold.py | clip")
    orig = pyperclip.paste()
    final = bolded_caps(orig)
    print(final)
else:
    get_ignores()
    for x in i7.i7f[my_project]:
        process_potential_bolds(x)

if list_caps:
    counts_list = sorted(list(counts))
    print("#{} total ignores".format(len(counts_list)))
    while len(counts_list) > 0:
        print("#{}".format(','.join(["{}={}".format(x, counts[x]) for x in counts_list[:10]])))
        counts_list = counts_list[10:]
