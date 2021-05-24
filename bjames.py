import sys

cmd_count = 1
deficit = 0
game_time = 0

def bill_james(deficit, game_time, has_possession):
    print("With{} possession:".format('' if has_possession else 'out'))
    coefficient = deficit - 3.5 + has_possession
    factor = coefficient ** 2 / game_time
    mins = "{}:{:02d}".format(game_time // 60, game_time % 60)
    print("{:.4f} % safe at {}".format(factor * 100, mins))
    deficit_safe_when = int(coefficient ** 2)
    print("Safe game_time: {}:{:02d}".format(deficit_safe_when//60, deficit_safe_when % 60))

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if '-' in arg:
        if deficit:
            sys.exit("Already have deficit.")
        try:
            scores = arg.split('-')
            deficit = abs(int(scores[0]) - int(scores[1]))
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
    cmd_count += 1

bill_james(deficit, game_time, True)
print()
bill_james(deficit, game_time, False)
