import sys
import shlex

def bill_james(deficit, game_time, has_possession):
    print("With{} possession:".format('' if has_possession else 'out'))
    coefficient = deficit - 3.5 + has_possession
    factor = coefficient ** 2 / game_time
    mins = "{}:{:02d}".format(game_time // 60, game_time % 60)
    print("{:.4f} % safe at {}".format(factor * 100, mins))
    deficit_safe_when = int(coefficient ** 2)
    print("Safe game_time: {}:{:02d}".format(deficit_safe_when//60, deficit_safe_when % 60))

def read_params(my_ary):
    ary_idx = 1
    deficit = 0
    game_time = 0
    our_score = 0
    their_score = 0

    while ary_idx < len(my_ary):
        arg = my_ary[ary_idx]
        if arg.endswith('h'):
            arg = arg[:-1] + ":30"
        if '-' in arg:
            if deficit:
                sys.exit("Already have deficit.")
            try:
                scores = arg.split('-')
                deficit = abs(int(scores[0]) - int(scores[1]))
                our_score = int(scores[0])
                their_score = int(scores[1])
            except:
                sys.exit("Bad score")
        elif arg.isdigit():
            if deficit:
                sys.exit("Already have deficit.")
            deficit = int(arg)
        elif ':' in arg:
            if arg[0] == ':':
                arg = '0' + arg
            if game_time:
                sys.exit("Already have game_time.")
            try:
                scores = arg.split(":")
                game_time = int(scores[0]) * 60 + int(scores[1])
            except:
                sys.exit("Bad game_time format.")
        else:
            sys.exit("Need a score or deficit, then time remaining. For under a minute you can use : not 0:.")
        ary_idx += 1

    bill_james(deficit, game_time, True)
    print()
    bill_james(deficit, game_time, False)
    print()
    pace_ratio = 2400 / (2400 - game_time)

    if our_score:
        print("Pace: {:.2f} to {:.2f}".format(our_score * pace_ratio, their_score * pace_ratio))

if 'i' not in sys.argv[1:]:
    read_params(sys.argv[1:])
    sys.exit()

if len(sys.argv) > 2:
    temp_ary = sys.argv.remove('i')
    read_params(temp_ary)

while 1:
    i = input("Input lead to evaluate >")
    read_params(shlex.split(i))
