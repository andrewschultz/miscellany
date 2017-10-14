import re

big_string = ""
iffy = False

went_over = False
this_tabs = 0
last_tabs = 0

max_changes = 50
cur_changes = 0

def leading_tabs(l):
    return len(l) - len(l.lstrip('\t'))

with open("story.ni") as file:
    for line in file:
        if iffy:
            this_tabs = leading_tabs(line)
            if (re.search("\t(continue the action|the rule succeeds)", line) or re.search("\t.*instead;( \[.*\])?", line)) and not re.search("\tif ", line) and (this_tabs - last_tabs == 1):
                l2 = re.sub("^\t+", "", line)
                last_line = re.sub(":+", ", " + l2, last_line)
                big_string = big_string + last_line
                cur_changes = cur_changes + 1
            else:
                big_string = big_string + last_line + line
            iffy = False
            continue
        iffy = False
        last_line = line
#        if re.search("if action is iffy", line):
        if re.search("\t+if ", line) and not re.search("instead;", line):
            if cur_changes < max_changes or max_changes > 0:
                iffy = True
                last_tabs = leading_tabs(line)
                continue
            elif cur_changes == max_changes:
                went_over = True
        big_string = big_string + line

big_string.replace("\r\n", "\n")

print(cur_changes, "total cur_changes")

f = open("story.nij", "w", newline="\n")
f.write(big_string)
f.close()
