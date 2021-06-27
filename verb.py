import mytools as mt
import pyperclip
from collections import defaultdict
import sys

verb_types = defaultdict(str)

def add_clipboard_text(prefix, data):
    ary = data.split(",")
    this_string = "chapter {}\n\n".format(ary[0])
    my_action = ary[0] + "ing"
    if verb_types[prefix] == "out of world":
        action_type = "out of world"
    else:
        action_type = "applying to one {}".format(verb_types[prefix])
    this_string += "{} is an action {}.\n\n".format(my_action, action_type)
    for x in ary:
        this_string += 'understand the command "{}" as something new.\n'.format(x)
    this_string += "\n"
    for x in ary:
        this_string += 'understand "{}" as {}.\n'.format(x, my_action)
    this_string += "\n"
    this_string += "carry out {}:\n\tthe rule succeeds;\n\n".format(my_action)
    return this_string

with open("c:/writing/scripts/verbdata.txt") as file:
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
    if not prefix or not data:
        sys.exit("Badly formed argument {}".format(arg))
    clip_text += add_clipboard_text(prefix, data)
    cmd_count += 1

pyperclip.copy(clip_text)
print(clip_text)
