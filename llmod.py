# llmod.py: gets rid of lalaland (or other default room) references

from filecmp import cmp
import os
import re

f1 = 'story.ni'
f2 = 'story.ni2'

def mootify(a):
	ll = re.sub(r"move (.*) to lalaland", "moot $1", a, 0, re.IGNORECASE)
	ll = re.sub(r"now (.*) is in lalaland", "moot $1", ll, 0, re.IGNORECASE)
	ll = re.sub("not in " + discard_room, "not moot", ll, 0, re.IGNORECASE)
	ll = re.sub("in " + discard_room, "moot", ll, 0, re.IGNORECASE)
	return ll

fout = open(f2, "w", newline='\n')

discard_room = "lalaland"

print(mootify("now stuff is in lalaland;"))
print(mootify("move stuff to lalaland;"))

difs = 0
line_count = 0

with open(f1) as file:
	for line in file:
		line_count = line_count + 1
		if discard_room not in line.lower() or '[ic]' in line:
			fout.write(line)
			continue
		ll = mootify(line)
		if ll != line:
			difs = difs + 1
			print("Dif", difs, "at", line_count)
		fout.write(ll)

fout.close()

if cmp(f1, f2):
	print("No changes, no copying over.")
	os.remove(f2)
else:
	print(difs, "total differences.")
	os.system("wm {:s} {:s}".format(f1, f2))