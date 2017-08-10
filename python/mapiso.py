#
# mapiso.py
#
# isolates the map elements of inform 7 source
#
# regions and "X is a room in (region)."

import re

reg = {}

if not os.path.isfile("story.ni"):
	print("Need story.ni in current directory.")
	exit()

with open("story.ni") as file:
	for line in file:
		if re.search("^\t", line):
			continue
		if re.search("is a[a-z ]* region(?!( that))", line):
			l2 = re.sub(" is a.*", "", line.strip())
			reg[l2] = 1
			print(l2, 'is a region.')
			continue

# special case for Roiling, which has innie and outie rooms

my_reg = "is (a(n innie)? room )?in (" + "|".join(reg.keys()) + ")"

print(my_reg)

with open("story.ni") as file:
	for line in file:
		if re.search("^\t", line):
			continue
		if re.search(my_reg, line, re.IGNORECASE):
			line = re.sub("n innie", "", line)
			line = re.sub("\".*", "", line)
			print(line)
