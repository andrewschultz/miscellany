# toast.py
#
# read text decompiled from Jacques Frechet's Toastball web page
#
# https://github.com/jcmf/glulx-strings
#
# usage: toast.py (optional file, else clipboard)
#

import pyperclip
import sys

count = 1
non_garbage = []
reading_text = second_block_yet = first_block_yet = False
file_name = ''

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if os.path.exists(arg):
        if file_name: sys.exit("2 file names")
        file_name = arg
    count += 1

if not file_name:
    disassem = pyperclip.paste()
    lines = disassem.split("\n")
else:
    f = open("file_name", "r")
    lines = f.readlines()

for (q_c, q) in enumerate(lines, 1):
    if not reading_text:
        if "I didn't understand that sentence" in q and not first_block_yet:
            reading_text = True
            print(q_c, "start reading 1st block:", q)
            first_block_yet = True
        elif not second_block_yet and "Themselves" in q.strip():
            reading_text = True
            print(q_c, "start reading 2nd block:", "!!" + q.strip() + "!")
            second_block_yet = True
        continue
    if second_block_yet and q.startswith(" response ("):
        reading_text = False
        continue
    if first_block_yet and "Scene 'Entire Game' ends" in q:
        reading_text = False
        continue
    #print(q_c, q)

if not first_block_yet: print("Uh oh, didn't find first block.")
if not second_block_yet: print("Uh oh, didn't find second block.")
