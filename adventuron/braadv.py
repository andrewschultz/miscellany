import sys
import re
from collections import defaultdict
import mytools as mt

bracket_count = 0
last_line = 0

debug = False
see_all = True

try:
    if sys.argv[1] == 'd':
        debug = True
except:
    debug = False

def leftbrackets(line):
    return (line.count('{') - line.count('{('))

def rightbrackets(line):
    return (line.count('}') - line.count(')}'))

def bracketdelta(line):
    return leftbrackets(line) - rightbrackets(line)


bracket_last_line = defaultdict(int)

with open("source_code.adv") as file:
    for (line_count, line) in enumerate (file, 1):
        bracket_count += (line.count('{') - line.count('{('))
        bracket_count -= (line.count('}') - line.count(')}'))
        if bracket_count == 0:
            last_line = line_count
        if debug:
            print(line_count, bracket_count, line.rstrip())
        if 'subroutine' in line or see_all:
            bracket_last_line[bracket_count] = line_count

if bracket_count:
    for s in sorted(bracket_last_line):
        print("Last line with {} bracket{}: {}".format(s, 's' if s > 1 else '', line_count))
else:
    print("Brackets all match!")