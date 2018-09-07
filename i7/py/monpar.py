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

file_name = ""
count = 1

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c': read_file = False
    else: file_name = sys.argv[1]
    count += 1

d = Differ()

if read_file:
    if not file_name: sys.exit("Need file name.")
    f = open(file_name, "r")
    rl = [ q.strip() for q in f.readlines() ]
    print("Reading", file_name, len(rl), "lines")
else:
    f1 = pyperclip.paste()
    rl = re.split("(\r?)\n", f1)
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

