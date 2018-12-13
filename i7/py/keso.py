# keso.py
#
# sorts notes from google keep and modifies them a bit if necessary
#

# todo: MAKE SURE THAT COMMENTS ARE SORTED TOO

import os
import re
import sys
import pyperclip
from collections import defaultdict
from fractions import gcd
from functools import reduce

kfile = "c:/writing/temp/to_keep.txt"
kfile2 = "c:/writing/temp/to_keep_2.txt"
kfilef = "c:/writing/temp/to_keep_final.txt"

comment_cfg = "c:/writing/scripts.kesotxt"

cmds = defaultdict(str)
cmds['palindromes'] = "ni no ai"
cmds['anagrams'] = "ni an"
cmds['vvff'] = "ni no vv"
cmds['spoonerisms'] = "np spopal"

comment_sortable = defaultdict(str)

cs_rx = '|'.join(comment_sortable)
cs_rx_val = '|'.join([comment_sortable[x] for x in comment_sortable])

specials = defaultdict(list)

separator = defaultdict(str)
separator['possible names'] = "\t"

touch_up = False
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

def read_comment_sortable():
    with open(comment_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            if '=' not in line:
                print("WARNING cfg file", comment_cfg, "needs = to split from/to sections.")
                continue
            a = line.lower().split("=")
            b = a.split(",")
            for q in b: comment_sortable[q] = a[1]

def touch_up_ideas(): # this is for converting stuff to multi line that would otherwise get garbled
    a1 = kfile2.readlines()
    f2 = open(kfilef, "w")
    limericks = []
    limid = []
    for x in a1:
        if x.count("/") == 4 and len(x) > 120 and len(x) < 240:
            temp = re.sub(" *\/ ", "\n", x)
            limericks.append("====\n" + x)
            continue
        if x.startswith("lid:"):
            limid.append(x[4:])
            continue
        f2.write(x + "\n")
    if len(limericks):
        f2.write("\n\n\\lim\n")
        for q in limericks: f2.write(q + "\n")
    if len(limid):
        f2.write("\n\n\\lid\n")
        for q in limid: f2.write(q + "\n")
    close(f2)
    os.system(kfilef)

def sortable_comments(my_l):
    if re.search(r'#{:s}\b'.format(cs_rx), my_l): return re.sub(r'#{:s}'.format(cs_rx), lambda x: comment_sortable[x.group(1)], my_l)
    if re.search(r'#{:s}\b'.format(cs_rx_val), my_l): return re.sub(r'#{:s}'.format(cs_rx_val), lambda x: x.group(1), my_l)
    if re.search(r'#{:s}'.format(cs_rx), my_l): return re.sub(r'#{:s}'.format(cs_rx), lambda x: comment_sortable[x.group(1)], my_l)
    if re.search(r'#{:s}'.format(cs_rx_val), my_l): return re.sub(r'#{:s}'.format(cs_rx_val), lambda x: x.group(1), my_l)

def new_line_embedded(x):
    if re.search("\b(uline|new line|newline)\b", x):
        return re.split(" *\b(uline|new line|newline)\b *", x)
    return []

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
    elif arg == 'tu': touch_up = True
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

if touch_up: touch_up_ideas()

embeddings = []

if read_paste: file_or_clip = "the clipboard text"
else: file_or_clip = kfile

for z in y:
    if not header_yet:
        if "=start actual notes" in z.lower():
            header_yet = True
            if not check_header: sys.exit("Header check is turned off, but =start actual notes text was found in {:s}. Change this with -ch or -hc.".format(file_or_clip))
        if check_header: continue
    if '=' * 10 in z.strip(): continue
    if not z.strip(): continue
    if z.strip() != z.lstrip():
        strips += 1
        strip_length += len(z.strip()) - len(z.lstrip())
    if z.new_line_embedded():
        embeddings.append(z)
        y = y + z.new_line_embedded()
        continue
    else:
        y2.append(z.strip())

if check_header and not header_yet:
    sys.exit("check_header set to true, but we did not find a header in {:s}. Bailing. Use -nh or -hn to turn this off.".format(file_or_clip))

# here we sort specific cases
for z in y2:
    z_raw = z if z.startswith("#") else re.sub(" *#.*", "", z)
    z_comments = re.sub("^ *?#", "", z) if '#' in z else ""
    z_c_s = sortable_comments(z_comments)
    if z_raw.startswith('===='): continue
    elif re.search("[0-9]+ total sorted ideas", z_raw): continue
    elif z_c_s: dict_append(specials, z_c_s, z)
    elif sortable_comments(z_comments):
    elif is_palindrome(z_raw): dict_append(specials, 'palindromes', z)
    elif is_onetwo(z_raw): dict_append(specials, 'onetwos', z)
    elif ' / ' in z_raw or ',,' in z_raw: dict_append(specials, 'vvff', z)
    elif '==' in z_raw: dict_append(specials, 'btp', z)
    elif '*' in z_raw or re.search("( [0-9=]{2}|[0-9=]{2} )", z_raw): dict_append(specials, 'spoonerisms', z)
    elif ' ' not in z_raw or "\t" in z_raw: dict_append(specials, 'possible names', z)
    elif 'what a story' in z_raw.lower(): dict_append(specials, 'what a story', z)
    elif is_anagrammy(z_raw): dict_append(specials, 'anagrams', z)
    else:
        finals.append(z)

k = open(out_file, "w")

sep = "=" * 60

if len(specials.keys()):
    for q in sorted(specials.keys()): k.write("{:s}{:s} ({:s}):\n{:s}\n\n".format(sep, q, (cmds[q] if q in cmds.keys() else "may need loading instructions"), (separator[q] if q in separator.keys() else "\n").join(specials[q])))
    k.write(sep + "general" + "\n")

k.write("\n".join(sorted(finals, key=lambda l:len(l) if by_length else l, reverse=by_length)))
k.write("\n{:d} total sorted ideas\n".format(len(finals)))
k.close()

if embeddings:
    print(len(embeddings), "embedded lines:")
    for q in embeddings: print("      ", q)

print("Opening", out_file)
os.system(out_file)
