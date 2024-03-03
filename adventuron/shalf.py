import sys

if len(sys.argv) < 3:
	sys.exit("Need 2 words.")

spaces_before = 3

if len(sys.argv) == 4:
    spaces_before = int(sys.argv[3])

spaces_before *= 3

sbstring = ' ' * spaces_before

my_point = "point_{}_{}".format(sys.argv[1], sys.argv[2])

# no need for spaces
print("   {} : boolean \"false\" ;".format(my_point))
print()

print("   puz_{} : string \"<{} {}<#f80>>\" ;".format(my_point, sys.argv[1], sys.argv[2]))
print()

print(sbstring + ": match \"{} {}\" {{".format(sys.argv[1], sys.argv[2]))
print(sbstring + "   : if ({}) {{".format(my_point))
print(sbstring + "      : print \"Already done!\" ;")
print(sbstring + "   }")
print(sbstring + "   : print \"Narrative text.\" ;")
print(sbstring + "   : set_true \"{}\" ;".format(my_point))
print(sbstring + "   : gosub \"add_point\" ;")
print(sbstring + "   : done ;")
print(sbstring + "}")
#print(sbstring + ": if (footnotes_available && !bonus_point_{}_{}) {{".format(sys.argv[1], sys.argv[2]))
print(sbstring + ": if (!{}) {{".format(my_point, sys.argv[1], sys.argv[2]))
print(sbstring + "   : match \"{} _;_ {}\" {{".format(sys.argv[1], sys.argv[2]))
print(sbstring + "      : gosub \"say_half\" ;")
#print(sbstring + "      : gosub \"say_half_b\" ;")
print(sbstring + "      : done ;")
print(sbstring + "   }")
print(sbstring + "}")
