# genc.py
#
# cursory check for obvious gender switches/mistakes in code
#

import sys
import re

NO_GENDER = 0
M_GENDER = 1
F_GENDER = 2

genders = NO_GENDER
default_gender_string = "lug"
gender_string = ""
flags = re.IGNORECASE

count = 0
acount = 1

while acount < len(sys.argv):
    arg = sys.argv[acount].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'm': genders = M_GENDER
    elif arg == 'n': genders = NO_GENDER
    elif arg == 'f': genders = F_GENDER
    elif gender_string:
        sys.exit("Tried to define 2 search strings.")
    else:
        gender_string = arg
    acount += 1

if not gender_string:
    print("Going with default string", default_gender_string)
    gender_string = default_gender_string

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        if re.search(r'\b{:s}\b'.format(gender_string), line, re.IGNORECASE):
            line = re.sub("\[[^\]*]\]", "", line)
            if genders == NO_GENDER and re.search(r'\b(he|him|his|her|hers|she)\b', line.lower(), re.IGNORECASE):
                count += 1
                print(count, line_count, line.strip())
            if genders == M_GENDER and re.search(r'\b(her|hers|she)\b', line.lower(), re.IGNORECASE):
                count += 1
                print(count, line_count, line.strip())
            if genders == F_GENDER and re.search(r'\b(he|him|his)\b', line.lower(), re.IGNORECASE):
                count += 1
                print(count, line_count, line.strip())

if not count: print("Found nothing for", gender_string)