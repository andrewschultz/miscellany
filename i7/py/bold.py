# bold.py
# looks for CAPITALIZED stuff inside quotes to put in BOLD with [b] [r] tags.

import sys
import i7
import re
import pyperclip
import os

from collections import defaultdict

ignores = defaultdict(int)
counts = defaultdict(int)

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
    return x

def code_exception(my_line):
    if "a-text" in my_line or "b-text" in my_line or my_line.startswith("understand"):
        return True
    return False

if clip:
    orig = pyperclip.paste()
    final = bolded_caps(orig)
    print(final)
else:
    get_ignores()
    with open("story.ni") as file:
        for (line_count, line) in enumerate(file, 1):
            if code_exception(line): # letters settler readings don't count
                print(line.rstrip())
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
                #print(count, bolded_caps(line.rstrip()))
            print(new_quote)

if list_caps:
    counts_list = sorted(list(counts))
    print("#{} total ignores".format(len(counts_list)))
    while len(counts_list) > 0:
        print("#{}".format(','.join(["{}={}".format(x, counts[x]) for x in counts_list[:10]])))
        counts_list = counts_list[10:]
