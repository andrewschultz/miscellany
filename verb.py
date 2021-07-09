import mytools as mt
import pyperclip
from collections import defaultdict
import sys

verb_types = defaultdict(str)
copy_text = True
print_text = False

verb_data = "c:/writing/scripts/verbdata.txt"

def add_clipboard_text(prefix, data):
    ary = data.split(",")
    if '~' in ary[0]:
        a2 = ary[0].split("~")
        ary[0] = a2[1]
        my_action = a2[0] + "ing"
    else:
        my_action = ary[0] + "ing"
    this_string = "chapter {}\n\n".format(ary[0])
    if verb_types[prefix] == "out of world":
        action_type = "out of world"
    else:
        action_type = "applying to one {}".format(verb_types[prefix])
    this_string += "{} is an action {}.\n\n".format(my_action, action_type)
    for x in ary:
        this_string += 'understand the command "{}" as something new.\n'.format(x)
    this_string += "\n"
    for x in ary:
        print(x, prefix, verb_types[prefix])
        if verb_types[prefix] == "out of world":
            second_arg = ''
        else:
            second_arg = " [{}]".format(verb_types[prefix])
        this_string += 'understand "{}{}" as {}.\n'.format(x, second_arg, my_action)
    this_string += "\n"
    this_string += "carry out {}:\n\tthe rule succeeds;\n\n".format(my_action)
    return this_string

with open(verb_data) as file:
    for (line_count, line) in enumerate (file, 1):
        (prefix, data) = mt.cfg_data_split(line)
        ary = prefix.split(",")
        for a in ary:
            if a in verb_types:
                sys.exit("verb_type {} redefined at line {}.".format(a, line_count))
            verb_types[a] = data

clip_text = ""

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    (prefix, data) = mt.cfg_data_split(arg)
    if arg in ( 'pc', 'cp' ):
        copy_text = print_text = True
    elif arg == 'c':
        copy_text = True
        print_text = False
    elif arg == 'p':
        copy_text = False
        print_text = True
    elif arg == 'e':
        mt.npo(verb_data)
        sys.exit()
    elif arg == '?':
        print("Verb types and results:")
        for x in verb_types:
            print(x, verb_types[x])
        sys.exit()
    elif not prefix:
        sys.exit("Badly formed argument {}: there is no default prefix, so we need to specify w= for out of world, etc.".format(arg))
    elif not data:
        sys.exit("You need data after the =/: in {}.".format(arg))
    else:
        clip_text += add_clipboard_text(prefix, data)
    cmd_count += 1

if copy_text:
    print("Copied source text to clipboard.")
    pyperclip.copy(clip_text)

if print_text:
    print(clip_text)
