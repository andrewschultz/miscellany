#
# monpar.py: monty-parse
#
# file name or -c for clipboard
#

from difflib import Differ
import pyperclip
import sys
import re

last_test_text = []
cur_test_text = []

in_test_text = False
read_file = True
compare_file_clipboard = False
auto_clip_from_file = True

file_name = ""
count = 1

def usage():
    print("-c = clipboard")
    print("-fc = file/clipboard compare")
    exit()

# This was a debug function for the first few iterations when the clipboard was not identical to the file it was copied from.
# From which it was copied. It seems like it could need re-use. So I kept it.

# NOTE: this function is never called with the 2nd 2 variables, but I could if I needed to

def file_vs_clipboard(fn, auto_clipboard_from_file = True, max_errs = 10):
    if max_errs == 0: max_errs = 10
    mistakes = 0
    if not fn: sys.exit("Need a file name")
    if auto_clipboard_from_file:
        f_from = open(fn, 'r').read()
        pyperclip.copy(f_from)
    f1 = pyperclip.paste()
    ca = [q.rstrip() for q in re.split("\n", f1)]
    f = open(file_name, "r")
    fa = [ q.rstrip() for q in f.readlines() ]
    f.close()
    linum = 0
    print(len(ca), len(fa))
    for j in range(0, len(ca)):
        linum += 1
        if ca[j] != fa[j]:
            mistakes += 1
            print("Mistake #", mistakes, '/', linum, "clip length", len(ca[j]), "file length", len(fa[j]))
            print("Clipboard!" + ca[j] + "!")
            print("     File!" + fa[j] + "!")
            if mistakes == max_errs: break
    exit()

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c': read_file = False
    elif arg == 'fc':
        compare_file_clipboard = True
        file_name = sys.argv[count+1]
        count += 1
    else: file_name = arg
    count += 1

d = Differ()

if compare_file_clipboard: file_vs_clipboard(file_name)

if read_file:
    if not file_name: sys.exit("Need file name.")
    f = open(file_name, "r")
    rl = [ q.strip() for q in f.readlines() ]
    print("Reading", file_name, len(rl), "lines")
else:
    f1 = pyperclip.paste()
    rl = re.split("\n", f1)
    print("Reading from clipboard", len(rl), "lines")

#print(rl[5])
#exit()

for line in rl:
    if line.startswith(">"):
        if not last_test_text and not cur_test_text:
            print(line, "(no test text before)")
            continue
        if not cur_test_text:
            print(line, "No current test. Maybe this is a test command or an out of world action.")
            continue
        elif cur_test_text == last_test_text:
            print("No change in test text.")
        else:
            print("Changed text.")
            print("\n".join([x for x in list(d.compare(last_test_text, cur_test_text)) if re.search("^[\+\?-]", x)]))
        last_test_text = list(cur_test_text)
        cur_test_text = []
        print(line)
    if "=START TESTS" in line:
        in_test_text = True
        continue
    if "=END TESTS" in line:
        in_test_text = False
        continue
    if in_test_text: cur_test_text.append(line)

