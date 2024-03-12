import sys

default_indents = 3
indents = -1

#default we can change
bonus_point = False
add_command = False

show_half_clues = True

pre_text = ''
my_index='100'
my_room = 'r99'

if_case = ''
cmd_words = []

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
    elif (arg[0] in 'n', 'm') and arg[1:].isdigit():
        my_index = arg[1:]
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
sbstring = ' ' * (3 * indents)

bonus_prefix = 'bonus_' if bonus_point else ''

my_point = "{}point_{}_{}".format(bonus_prefix, cmd_words[0], cmd_words[1])

# no need for spaces
print("   {} : boolean \"false\" ; # {}".format(my_point, my_index.zfill(2)))
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
print(sbstring + "   : set_integer var=\"tempint\" \"{}\" ;".format(my_index))
print(sbstring + "   : set_true \"{}\" ;".format(my_point))
print(sbstring + "   : gosub \"add_{}\" ;".format('bonus' if bonus_point else 'point'))
print(sbstring + "   : done ;")
print(sbstring + "}")
#print(sbstring + ": if (footnotes_available && !bonus_point_{}_{}) {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + ": if (!{}) {{".format(my_point, cmd_words[0], cmd_words[1]))
print(sbstring + "   : match \"{} _;_ {}\" {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + "      : set_integer var=\"tempint\" \"{}\" ;".format(my_index))
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

