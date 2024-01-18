import sys
import re
import mytools as mt

maxwidth = 10

cmd_count = 1
my_regex = ''

low_bound = high_bound = 0

get_first = get_last = False

def find_pattern(word_file, word_len, word_pat):
    possibles = []
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            l = line.lower().strip()
            if re.search(word_pat, l):
                possibles.append(l)
    for x in range(0, len(possibles), maxwidth):
        print(word_len, ', '.join(possibles[x:x+10]))
    if not len(possibles):
        mt.warn("Nothing for", word_pat, word_len)

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.startswith('^'):
        mt.warn("Remember you can use / to start a command.")
    if arg.startswith('/'):
        arg = '^' + arg[1:]
    if arg.isdigit():
        low_bound = high_bound = int(arg)
    elif '-' in arg:
        x = arg.split('-')
        try:
            low_bound = int(x[0])
            high_bound = int(x[1])
            if low_bound > high_bound:
                (low_bound, high_bound) = (high_bound, low_bound)
        except:
            sys.exit("Dashes require two numbers on either side.")
    else:
        if my_regex:
            sys.exit("Two potential regexes defined. {} is the first. {} is the second. Replace or remove one.".format(my_regex, arg))
        my_regex = arg.replace('/', '|')
    cmd_count = cmd_count + 1

if not high_bound:
    low_bound = 3
    high_bound = 8

if get_first or get_last:
    if get_first:
        find_pattern(mt.first_name_file)
    if get_last:
        find_pattern(mt.first_name_file)
else:
    for x in range(low_bound, high_bound + 1):
        file_name = "c:\\writing\\dict\\words-{}.txt".format(x)
        find_pattern(file_name, x, my_regex)

    if not high_bound:
        mt.warn("No range, so I went with default 3-8.")
