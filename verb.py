#################################################################################
#
# verb.py: allows you to create inform 7 verb code from a single line of input
#
# ? gives usage
#

import mytools as mt
import pyperclip
from collections import defaultdict
import sys
import re

verb_types = defaultdict(str)
bracket_text = defaultdict(str)
copy_text = True
print_text = False

verb_data = "c:/writing/scripts/verbdata.txt"
sample_data = []

def add_clipboard_text(prefix, data):
    ary = data.split(",")
    if '~' in ary[0] or '=' in ary[0]:
        a2 = re.split("[~=]", ary[0])
        ary[0] = a2[1]
        my_action = a2[0]
    else:
        my_action = ary[0]
    if not my_action.endswith("ing"):
        my_action += "ing"
    this_string = "chapter {}\n\n".format(my_action)
    if verb_types[prefix] == "out of world":
        action_type = "out of world"
    else:
        action_type = "applying to {}".format(verb_types[prefix])
    this_string += "{} is an action {}.\n\n".format(my_action, action_type)
    for x in ary:
        this_string += 'understand the command "{}" as something new.\n'.format(x)
    this_string += "\n"
    for x in ary:
        second_arg = '' if not bracket_text[prefix] else " [{}]".format(bracket_text[prefix])
        this_string += 'understand "{}{}" as {}.\n'.format(x, second_arg, my_action)
    this_string += "\n"
    this_string += "carry out {}:\n\tthe rule succeeds;\n\n".format(my_action)
    return this_string

with open(verb_data) as file:
    for (line_count, line) in enumerate (file, 1):
        (prefix, data) = mt.cfg_data_split(line)
        if prefix == "sample":
            sample_data.append(data)
            continue
        ary = prefix.split(",")
        for a in ary:
            if a in verb_types:
                sys.exit("verb_type {} redefined at line {}.".format(a, line_count))
            ary = data.split(",")
            verb_types[a] = ary[0]
            bracket_text[a] = ary[1] if len(ary) > 1 else ''

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
        print("{:35} {:30}".format("Verb abbreviation and type", "Action text"))
        for x in verb_types:
            print("{:>4} {:30s} {:30s}".format(x, verb_types[x], bracket_text[x]))
        if len(sample_data) > 0:
            print()
            print("        SAMPLE USAGE")
            for s in sample_data:
                print("   ---->", s)
        else:
            print("No samples. Maybe you should add some in the config file with sample:?")
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
