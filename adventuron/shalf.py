# shalf.py
# score-half code generator for Adventuron
# this gives variable definitions as well as code for handling specific cases

import sys

default_indents = 3
indents = -1

#default we can change
bonus_point = False
add_command = False

show_half_clues = True
think_code = False

pre_text = ''
my_index='100'
my_room = 'r99'

if_case = ''
cmd_words = []

def usage():
    print("ac = add on_command before/after code")
    print("b = bonus point, c = core, core is default")
    print("n/m# = my index #")
    print("if = if case before e.g. point_w1_w2. Can use dash.")
    print("nh/hn/sh/hs = hide half clue code.")
    print("Sample command:")
    print("shalf.py me-growth r0414 /meager-oath n23 | clip")
    sys.exit()

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.isdigit():
        if int(arg) >= 10:
            my_index = arg
        else:
            if indents != -1:
                sys.exit("Re-redefined default 3-spaces before.")
            indents = int(arg)
    elif arg in ( 'ac', 'ca' ):
        add_command = True
    elif arg == 'b':
        bonus_point = True
    elif arg == 'c': # core
        bonus_point = False
    elif arg == 'th':
        think_code = True
    elif (arg[0] in 'n', 'm') and arg[1:].isdigit():
        my_index = arg[1:]
    elif arg[:3] == 'if=':
        if_case = arg[3:].replace('-', '_')
    elif arg.startswith('/'):
        pre_text = arg[1:].replace('/', '_').replace('-', '_')
    elif arg.startswith('r='):
        my_room = arg[2:]
        if my_room[0].isdigit():
            my_room = 'r' + my_room
    elif arg.startswith('r') and arg[1:].isdigit():
        my_room = arg
    elif arg == '?':
        usage()
    else:
        cmd_words.extend(arg.split('-'))
    cmd_count += 1

if len(cmd_words) != 2:
    sys.exit("Need 2 command words. You have {}, {}.".format(len(cmd_words), ' '.join(cmd_words)))

if indents == -1:
    sys.stderr.write("Going with default indents {}\n".format(default_indents))
    indents = default_indents

if my_index == 'x':
    sys.stderr.write("Remember, you can say n# to give a number variable.")

sys.stderr.flush()

if if_case:
    indents += 1

sbstring = ' ' * (3 * indents)

bonus_prefix_maincode = 'bonus_' if bonus_point else ''
bonus_prefix_defs = '_bonus' if bonus_point else '_core'

my_point = "{}point_{}_{}".format(bonus_prefix_maincode, cmd_words[0], cmd_words[1])

if not pre_text:
    pre_text = '_'.join(cmd_words)

# no need for spaces
print("   {} : boolean \"false\" ; # {}".format(my_point, my_index.zfill(2)))
print()

print("   puz_point_{} : dynamic_string {{( opt_color_coding ? \"<{}<#f80>>\" : \"{}\" )}} ; # {}".format(pre_text, pre_text.replace('_', ' '), pre_text.replace('_', ' '), my_index.zfill(2)))
print()

if (add_command):
    print(sbstring[:-3] + "on_command {{")

if (if_case):
    print(sbstring[:-3] + ": if ({}) {{".format(if_case))

print(sbstring + ": match \"{} {}\" {{".format(cmd_words[0], cmd_words[1]))

if think_code:
    print(sbstring + "   : if (!point_special_condition) {")
    print(sbstring + "      : print \"You need to do something first!\" ;")
    print(sbstring + "      : set_true \"think_{}_{}\" ;".format(cmd_words[0], cmd_words[1]))
    print(sbstring + "      : gosub \"note_thinks\" ;")
    print(sbstring + "      : done ;")
    print(sbstring + "   }")

print(sbstring + "   : if ({}) {{".format(my_point))
print(sbstring + "      : print \"Already done!\" ;")
print(sbstring + "      : done ;")
print(sbstring + "   }")
print(sbstring + "   : print \"Narrative text.\" ;")
print(sbstring + "   : set_integer var=\"tempint\" \"{}\" ;".format(my_index))
print(sbstring + "   : set_true \"{}\" ;".format(my_point))
print(sbstring + "   : gosub \"add_{}\" ;".format('bonus' if bonus_point else 'point'))
print(sbstring + "   : done ;")
print(sbstring + "}")
#print(sbstring + ": if (footnotes_available && !bonus_point_{}_{}) {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + ": if (!{}) {{".format(my_point, cmd_words[0], cmd_words[1]))
print(sbstring + "   : match \"{} _;_ {}\" {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + "      : set_integer var=\"tempint\" \"{}\" ;".format(my_index))
print(sbstring + "      : set_boolean var=\"already_got_command\" {{( think_{}_{} && !point_{}_{} )}} ; # this is optional. Delete if point does not rely on any other variables.".format(cmd_words[0], cmd_words[1], cmd_words[0], cmd_words[1]))
print(sbstring + "      : set_false \"first_half\" ;")
print(sbstring + "      : match \"{} _\" {{".format(cmd_words[0]))
print(sbstring + "         : set_true \"first_half\" ;")
print(sbstring + "      }")
print(sbstring + "      : gosub \"say_half{}\" ;".format('_b' if bonus_point else ''))
#print(sbstring + "      : gosub \"say_half_b\" ;")
print(sbstring + "      : done ;")
print(sbstring + "   }")
print(sbstring + "}")

if (add_command):
    print(sbstring[:-3] + "}")

if (if_case):
    print(sbstring[:-3] + "}")

if show_half_clues:
    print("          #tried_combo{}".format(bonus_prefix_defs))
    print("         \"false\",")
    print("          #situations{}".format(bonus_prefix_defs))
    print("         \"{{here_{}}}\",".format(my_room))
    print("          #think_first{}".format(bonus_prefix_defs))
    print("         \"<{}<#f80>>\",".format(cmd_words[0].upper()))
    print("          #think_second{}".format(bonus_prefix_defs))
    print("         \"<{}<#f80>>\",".format(cmd_words[1].upper()))
    print("          #got_first{}".format(bonus_prefix_defs))
    print("         \"false\",")
    print("          #got_second{}".format(bonus_prefix_defs))
    print("         \"false\",")
    if bonus_point:
        print("          #bonus_not_found_text{}".format(bonus_prefix_defs))
        print("         \"<unfound yet<#123>>\",")
        print("          #bonus_half_status".format(bonus_prefix_defs))
        print("         \"0\",")
