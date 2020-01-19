# vreg.py
#
# converts source code for standard Inform verbs to possible test cases
#

import re

check_generals = False

global_cases = 0

def what_to_say(x):
    retval = x.strip()
    if 'say "' in retval:
        y = re.sub(".*say +\"", "", retval)
        return re.sub("\".*", "", y)
    elif " instead" in retval:
        retval = re.sub(" *instead[;\.].*", "", retval)
        retval = re.sub(".*,", "", retval)
    return retval

def find_possible_commands(file_name):
    global global_cases
    get_next_say_or_instead = True
    any_global_yet = global_cases > 0
    in_this_file = 0
    check_section = ''
    last_line_count = 0
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("check"):
                check_section = re.sub("^check *", "", line.strip())
                check_section = re.sub(" *[:\(].*", "", check_section)
            if get_next_say_or_instead:
                temp = what_to_say(line)
                if temp:
                    print(temp)
                    get_next_say_or_instead = False
            if not line.strip():
                if check_generals and check_section:
                    last_line_count += 1
                    if get_next_say_or_instead:
                        print("(had an IF statement I couldn't find text for)")
                    get_next_say_or_instead = False
                    print("#VERB TEST CASE GENERAL {} {}".format(check_section, last_line_count))
                    print(last_line.strip())
                check_section = ''
            if check_section and line.strip().startswith("if noun is"):
                the_noun = re.sub("if noun is *", "", line.strip())
                the_noun = re.sub("[,:].*", "", the_noun)
                in_this_file += 1
                global_cases += 1
                print("VERB TEST CASE SPECIFIC {} {} {} {}".format(check_section, the_noun, in_this_file, "" + str(global_cases) if any_global_yet else ""))
                temp = what_to_say(line)
                if temp:
                    print(temp)
                else:
                    get_next_say_or_instead = True
            elif check_section and "the rule succeeds;" not in line:
                last_line = re.sub(" *instead;.*", "", line.strip())

find_possible_commands("story.ni")
