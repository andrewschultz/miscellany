import re

sce = {}
tot = {}

nuthin = "zzzz scenery with no location"

with open("story.ni") as file:
	for line in file:
		if re.search("is scenery\.", line, re.IGNORECASE):
			print("Got an undef")
			line = re.sub(" is scenery.*", "", line.strip().lower(), re.IGNORECASE)
			if nuthin in sce.keys():
				sce[nuthin] = sce[nuthin] + ", " + line
				tot[nuthin] = tot[nuthin] + 1
			else:
				sce[nuthin] = line
				tot[nuthin] = 1
			continue
		if not re.search("\.", line, re.IGNORECASE):
			continue
		if not re.search("^[a-z]", line, re.IGNORECASE):
			continue
		line = re.sub("\..*", "", line.strip())
		if not re.search("scenery in ", line, re.IGNORECASE):
			continue
		line2 = line.strip().lower()
		line2 = re.sub(" (is|are) ([a-z ]*)?scenery.*", "", line2, re.IGNORECASE)
		line3 = line.strip().lower()
		line3 = re.sub(".*scenery in ", "", line3, re.IGNORECASE)
		if line3 in sce.keys():
			sce[line3] = sce[line3] + ", " + line2
			tot[line3] = tot[line3] + 1
		else:
			sce[line3] = line2
			tot[line3] = 1

for x in sorted(sce.keys()):
	print('{:s} ({:d}): {:s}'.format(x.upper(), tot[x], sce[x]))
	# print(x.upper() + ":",tot[x], sce[x])