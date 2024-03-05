import sys

if len(sys.argv) < 3:
	sys.exit("Need 2 words.")

default_indents = 3
indents = 3

cmd_words = []

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.isdigit():
        if indents:
            sys.exit("Re-redefined default 3-spaces before.")
        indents = arg
    else:
        cmd_words.append(arg)
    cmd_count += 1

if len(cmd_words) != 2:
    sys.exit("Need 2 command words. You have {}, {}".format(len(cmd_words), ' '.join(cmd_words)))

if not indents:
    print("Going with default indents", default_indents)
    indents = default_indents

sbstring = ' ' * (3 * indents)

my_point = "point_{}_{}".format(cmd_words[0], cmd_words[1])

# no need for spaces
print("   {} : boolean \"false\" ;".format(my_point))
print()

print("   puz_{} : dynamic_string {{( opt_color_coding ? \"<{} {}<#f80>>\" : \"{} {}\" )}} ;".format(my_point, cmd_words[0], cmd_words[1], cmd_words[0], cmd_words[1]))
print()

print(sbstring + ": match \"{} {}\" {{".format(cmd_words[0], cmd_words[1]))
print(sbstring + "   : if ({}) {{".format(my_point))
print(sbstring + "      : print \"Already done!\" ;")
print(sbstring + "      : done ;")
print(sbstring + "   }")
print(sbstring + "   : print \"Narrative text.\" ;")
print(sbstring + "   : set_true \"{}\" ;".format(my_point))
print(sbstring + "   : gosub \"add_point\" ;")
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
print(sbstring + "      : gosub \"say_half\" ;")
#print(sbstring + "      : gosub \"say_half_b\" ;")
print(sbstring + "      : done ;")
print(sbstring + "   }")
print(sbstring + "}")
