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
ai_gen = "lug,lover,nob"
default_gender_string = "lug"
gender_strings = []
flags = re.IGNORECASE

count = 0
acount = 1

while acount < len(sys.argv):
    arg = sys.argv[acount].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'm': genders = M_GENDER
    elif arg == 'n': genders = NO_GENDER
    elif arg == 'f': genders = F_GENDER
    elif arg == 'ai': gender_strings = ai_gen.split(",")
    elif len(gender_strings): sys.exit("Tried to define 2 search strings.")
    else: gender_strings = re.sub("-", " ", arg).split(",")
    acount += 1

if not gender_strings:
    print("Going with default string", default_gender_string)
    gender_strings = [ default_gender_string ]

grex = r"\b({:s})\b".format("|".join(gender_strings))

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        if re.search(grex, line, re.IGNORECASE):
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

if not count: print("Found nothing for", grex)