import pyperclip
import re

non_garbage = []
reading_text = second_block_yet = first_block_yet = False
disassem = pyperclip.paste()

lines = disassem.split("\n")

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
	if second_block_yet and re.search("^ response \(", q):
		reading_text = False
		continue
	if first_block_yet and "Scene 'Entire Game' ends" in q:
		reading_text = False
		continue
	#print(q_c, q)

if not first_block_yet: print("Uh oh, didn't find first block.")
if not second_block_yet: print("Uh oh, didn't find second block.")
