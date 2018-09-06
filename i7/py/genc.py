# genc.py
#
# cursory check for obvious gender switches/mistakes in code
#
# usage
#   genc.py ai
#   genc.py ailihphilia

from collections import defaultdict
import i7
import sys
import re


gender_file = "c:/writing/scripts/genc.txt"

genregx = defaultdict(str)

MALE=0
FEMALE=1
BOTH=2

genregx[BOTH] = r'\b(he|him|his|her|hers|she)\b'
genregx[MALE] = r'\b(her|hers|she)\b'
genregx[FEMALE] = r'\b(him|his|he)\b'

default_gender_proj = "ailihphilia"
gender_dict = defaultdict(lambda: defaultdict(str))
flags = re.IGNORECASE

gender_strings = ""

count = 0
acount = 1

gender_tests = defaultdict(str)

def to_num(a):
    al = a.lower()
    if al == 'm': return MALE
    if al == 'f': return BOTH
    if al == 'n' or al == 'b': return FEMALE
    sys.exit(a + " is not recognized. Try m n f or b.")

with open(gender_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith('#'): continue
        if line.startswith(';'): break
        try:
            l0 = line.lower().strip().split(":")
            l1 = l0[1].split("=")
            gender_dict[l1[0]][to_num(l0[0])] = l1[1]
            print(l1[0], to_num(l0[0]), l1[1])
        except:
            print(line_count, line)
            sys.exit("Need something of the form m:ailihphilia=a,b,c")

while acount < len(sys.argv):
    arg = sys.argv[acount].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg in gender_tests.keys():
        pass
        # gender_strings = gender_tests[arg].split(",")
    elif i7.proj_exp(arg) in gender_tests.keys(): current_project = i7.proj_exp(arg)
    elif len(gender_strings): sys.exit("Tried to define 2 search strings.")
    else: gender_strings = re.sub("-", " ", arg).split(",")
    acount += 1

if not gender_dict.keys():
    sys.exit("No gender dict for " + default_gender_string)

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        line = re.sub("\[[^\]]*\]", "/", line.lower().strip())
        for q in [MALE, FEMALE, BOTH]:
            if q in gender_dict[default_gender_proj].keys():
                if re.search(genregx[q], line, re.IGNORECASE) and re.search(gender_dict[default_gender_proj][q], line):
                    count += 1
                    print(q, genregx[q], gender_dict[default_gender_proj][q])
                    print(count, line_count, line.strip())

if not count: print("Found nothing for", default_gender_proj)