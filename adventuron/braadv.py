import sys
import re
from collections import defaultdict
import mytools as mt

bracket_count = 0
last_line = 0

debug = False
indent = False
see_all = True

try:
    if sys.argv[1] == 'd':
        debug = True
    elif sys.argv[1] == 'i':
        indent = True
except:
    debug = False

def leftbrackets(line):
    return (line.count('{') - line.count('{('))

def rightbrackets(line):
    return (line.count('}') - line.count(')}'))

def bracketdelta(line):
    return leftbrackets(line) - rightbrackets(line)

def starting_spaces_of(line):
    count = 0
    while count < len(line):
        if line[count] != ' ':
            break
        count += 1
    return count

bad_sections = [ 'connections', 'collections' ]
bad_sections = [ 'connections' ]

def valid_section(my_section):
    return not my_section in bad_sections

def indent_check():
    bracket_count = 0
    big_string = ''
    any_changes = False
    this_section = ''
    with open("source_code.adv") as file:
        for (line_count, line) in enumerate (file, 1):
            if bracket_count == 0:
                if '{' in line:
                    header = re.sub("\{.*", "", line).strip()
                    this_section = header
            if line[0] == '}':
                this_section = ''
            bracketless = re.sub("\{.*?\}", "", line)
            bracket_count -= rightbrackets(bracketless)
            if valid_section(this_section):
                if starting_spaces_of(line) != 3 * bracket_count and line.strip():
                    mt.warn("Bad indent section {} line {} have {} need {}.".format(this_section, line_count, starting_spaces_of(line), 3 * bracket_count))
                    l0 = (3 * bracket_count * ' ') + line.lstrip()
                    big_string += l0
                    any_changes = True
                else:
                    big_string += line
            bracket_count += leftbrackets(bracketless)
    if not any_changes:
        mt.okaybail("Indents all correct!")
    f = open("c:/writing/temp/source_code_temp.adv", "w")
    f.write(big_string)
    f.close()
    #mt.wm("c:/writing/temp/source_code_temp.adv", "source_code.adv")
    #sys.exit()
    copy("c:/writing/temp/source_code_temp.adv", "source_code.adv")
    mt.okaybail("Successfully copied correctly indented file over.")

if indent:
    indent_check()

bracket_last_line = defaultdict(int)

with open("source_code.adv") as file:
    for (line_count, line) in enumerate (file, 1):
        bracket_count += bracketdelta(line)
        if bracket_count == 0:
            last_line = line_count
        if line.rstrip() == '}' and bracket_count != 0:
            mt.warn("Solo bracket does not have level 0.")
            mt.add_post("source_code.adv", line_count)
        if debug:
            print(line_count, bracket_count, line.rstrip())
        if 'subroutine' in line or see_all:
            bracket_last_line[bracket_count] = line_count

if bracket_count:
    for s in sorted(bracket_last_line):
        print("Last line with {} bracket{}: {}".format(s, 's' if s > 1 else '', line_count))
else:
    print("Brackets all match!")

mt.post_open()