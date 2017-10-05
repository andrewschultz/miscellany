import re

big_string = ""
procedural = False

with open("story.ni") as file:
	for line in file:
		if procedural:
			if re.search("\tcontinue the action", line):
				last_line = re.sub(":+", ", continue the action;", last_line);
				big_string = big_string + last_line
			else:
				big_string = big_string + last_line + line
			procedural = False
			continue
		procedural = False
		last_line = line
		if re.search("if action is procedural", line):
			procedural = True
			continue
		big_string = big_string + line

big_string.replace("\r\n", "\n")

f = open("story.nij", "w", newline="\n")
f.write(big_string)
f.close()
