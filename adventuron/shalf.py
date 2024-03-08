import sys

default_indents = 3
indents = 3

#default we can change
bonus_point = False
add_command = False

cmd_words = []

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.isdigit():
        if indents:
            sys.exit("Re-redefined default 3-spaces before.")
        indents = arg
    elif arg in ( 'ac', 'ca' ):
        add_command = True
    elif arg == 'b':
        bonus_point = True
    elif arg == 'c': # core
        bonus_point = False
    else:
        cmd_words.extend(arg.split('-'))
    cmd_count += 1

if len(cmd_words) != 2:
    sys.exit("Need 2 command words. You have {}, {}.".format(len(cmd_words), ' '.join(cmd_words)))

if not indents:
    print("Going with default indents", default_indents)
    indents = default_indents

sbstring = ' ' * (3 * indents)

bonus_prefix = 'bonus_' if bonus_point else ''

my_point = "{}point_{}_{}".format(bonus_prefix, cmd_words[0], cmd_words[1])

# no need for spaces
print("   {} : boolean \"false\" ;".format(my_point))
print()

print("   puz_{} : dynamic_string {{( opt_color_coding ? \"<{} {}<#f80>>\" : \"{} {}\" )}} ;".format(my_point, cmd_words[0], cmd_words[1], cmd_words[0], cmd_words[1]))
print()

if (add_command):
    print(sbstring[:-3] + "on_command {")

print(sbstring + ": match \"{} {}\" {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + "   : if ({}) {{".format(my_point))
print(sbstring + "      : print \"Already done!\" ;")
print(sbstring + "      : done ;")
print(sbstring + "   }")
print(sbstring + "   : print \"Narrative text.\" ;")
print(sbstring + "   : set_true \"{}\" ;".format(my_point))
print(sbstring + "   : gosub \"add_{}\" ;".format('bonus' if bonus_point else 'point'))
print(sbstring + "   : done ;")
print(sbstring + "}")
#print(sbstring + ": if (footnotes_available && !bonus_point_{}_{}) {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + ": if (!{}) {{".format(my_point, cmd_words[0], cmd_words[1]))
print(sbstring + "   : match \"{} _;_ {}\" {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + "      : set_integer var=\"tempint\" \"x\" ;")
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

