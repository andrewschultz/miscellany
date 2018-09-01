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

def valid_first_start(l):
    if "I didn't understand that sentence" in l: return True
    return False

def valid_first_end(l):
    if "Scene 'Entire Game' ends" in l: return True
    return False

def valid_second_start(l):
    if "Themselves" in q.strip(): return True
    if l.startswith("There seems to be no such object anywhere in the model world."): return True
    return False

def valid_second_end(l):
    if l.startswith(" response ("): return True
    if l.startswith("*** No such past tense condition"): return True
    return False

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
        if not first_block_yet and valid_first_start(q):
            reading_text = True
            print(q_c, "start reading 1st block:", q)
            first_block_yet = True
        elif not second_block_yet and valid_second_start(q):
            reading_text = True
            print(q_c, "start reading 2nd block:", q.strip())
            second_block_yet = True
        continue
    if second_block_yet and valid_second_end(q):
        print(q_c, "end reading second block:", q.strip())
        reading_text = False
        continue
    if first_block_yet and valid_first_end(q):
        print(q_c, "end reading first block:", q.strip())
        reading_text = False
        continue
    #print(q_c, q)

if not first_block_yet: print("Uh oh, didn't find first block.")
if not second_block_yet: print("Uh oh, didn't find second block.")
if reading_text:
    if not second_block_yet: print("Uh oh, didn't break out of first block.")
    else: print("Uh oh, didn't break out of second block.")