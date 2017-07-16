######################################
# fc.py
#
# no frills Python Freecell game
#
# this deliberately blocks me from playing. If you just want to, replace the variables below as necessary.
#
# 1) time_matters = 86400 2) deliberate_nuisance_rows = 3 3) deliberateNuisanceIncrease = 2
# 4) annoying_nudge = False (set to 0 or false)

import re
import sys
import os
from random import shuffle, randint
import time
# import traceback
import configparser
import argparse
from math import sqrt

# need vc14 for below to work
# from gmpy import invert

config_opt = configparser.ConfigParser()
config_time = configparser.ConfigParser()

opt_file = "fcopt.txt"
save_file = "fcsav.txt"
win_file = "fcwins.txt"
time_file = "fctime.txt"
lock_file = "fclock.txt"

on_off = ['off', 'on']

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

top = ['CL', 'di', 'SP', 'he']
btm = ['UB', 'am', 'AD', 'ar']

spares = [0, 0, 0, 0]
found = [0, 0, 0, 0]
force = 0

move_list = []

delta = 0
 
win = 0

total_undo = 0
total_reset = 0

cmd_churn = False
in_undo = False

won_this_cmd = False

last_reset = 0
start_time = 0

# time before next play variables

time_matters = 1
nag_delay = 86400  # set this to zero if you don't want to restrict the games you can play
min_delay = 70000  # if we can cheat one time
high_time = 0
max_delay = 0
cur_games = 0
max_games = 5

# options to define. How to do better?
chain_show_all = False
vertical = True
dbl_sz_cards = False
auto_reshuf = True
save_position = False
save_on_win = False
quick_bail = False
# this is an experimental feature to annoy me
deliberate_nuisance_rows = 3
deliberateNuisanceIncrease = 2
# this can't be toggled in game but you can beforehand
annoying_nudge = True

# easy mode = A/2 on top. Cheat index tells how many cards of each suit are sorted to the bottom.
cheat_index = 0

# making the game extra secure, not playing 2 at once or tinkering with timing file
have_lock_file = True
disallow_write_source = True

last_score = 0
highlight = 0

only_move = 0

track_undo = 0

break_macro = 0

undo_idx = 0

debug = False

cmd_list = []
cmd_no_meta = []

backup = []
elements = [[], [], [], [], [], [], [], [], []]


def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient * x, x
        y, lasty = lasty - quotient * y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)


def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m


def is_prime(x):
    for a in range(2, int(sqrt(x))):
        if x % a == 0:
            return False
    return True


def rand_prime():
    primes = []
    for j in range(100001, 200001, 2):
        if is_prime(j):
            # print j
            primes.append(j)
    return primes[randint(0, len(primes) - 1)]


def t_or_f(x):
    if x == "False" or x == "0":
        return False
    return True


def print_cond(my_string):
    if not in_undo and not cmd_churn:
        print(my_string)
    return


def shufwarn():
    if not cmd_churn and not in_undo:
        print("That won't make progress. F(##) or ##-# let you move part of an in-order stack over.")


def dump_total(q):  # Negative q means you print. Mostly for debugging.
    retval = 0
    do_print = False
    if q < 0:
        q = 0 - q
        do_print = True
    for z in range(0, len(elements[q])):
        if foundable(elements[q][z]):
            if do_print:
                print(to_card(elements[q][z]), elements[q][z], 'foundable')
            retval += 1
            if elements[q][z] % 13 == 2:  # aces/2's get a special bonus
                retval += 1
            if elements[q][z] % 13 == 1:  # aces/2's get a special bonus
                retval += 2
        if nexties(elements[q][z]):  # not an elif as foundable deserves an extra point
            retval += 1
            if do_print:
                print(to_card(elements[q][z]), elements[q][z], 'nexties')
    return retval


def best_dump_row():
    best_score = -1
    best_row = 0
    best_chains = 10
    for y in range(1, 9):
        if chain_nope(y) == 0:  # if there is nothing to move or dump, then skip this e.g. empty or already in order
            continue
        if dump_total(y) + y_n_can_dump(y) > best_score or (
                        dump_total(y) == best_score and chain_nope(y) < best_chains):
            best_row = y
            best_chains = chain_nope(y)
            best_score = dump_total(y)
    if best_row > 0:
        return best_row
    max_shifts = 10
    for y in range(1, 9):
        if chain_nope(y) == 0:
            continue
        if chain_nope(y) < max_shifts:
            for z in range(1, 9):
                if doable(y, z, 0) > 0:
                    max_shifts = chain_nope(y)
                    best_row = y
    return best_row


def foundable(myc):
    if (myc - 1) % 13 == found[(myc - 1) // 13]:
        return True
    return False


def nexties(myc):  # note that this may be a bit warped looking if you have 5S 5C 2h 2d for instance
    odds = (myc - 1) // 13
    cardval = (myc - 1) % 13
    if cardval < found[(odds + 1) % 4] + 2 and cardval < found[(odds + 3) % 4] + 2:
        return True
    return False


def rip_up(q):
    made_one = False
    if q < 1 or q > 8:
        print("Column/row needs to be 1-8.")
        return False
    if len(elements[q]) == 0:
        print("Already no elements.")
        return True
    go_again = 1
    global cmd_churn
    cmd_churn = True
    movesize = len(move_list)
    max_run = 0
    while go_again == 1 and len(elements[q]) > 0 and max_run < 25 and not in_order(q):
        should_reshuf = True
        if len(elements[q]) > 1:
            if can_put(elements[q][len(elements[q]) - 1], elements[q][len(elements[q]) - 2]):
                should_reshuf = False
        max_run += 1
        go_again = 0
        temp_ary_size = len(move_list)
        read_cmd(str(q))
        if len(move_list) > temp_ary_size:
            go_again = 1
            made_one = True
        check_found()
        if should_reshuf:
            reshuf(-1)
        force_foundation()
        slip_under()
    if max_run == 25:
        print("Oops potential hang at " + str(q))
    check_found()
    if len(move_list) == movesize:
        print("Nothing moved.")
    return made_one


def should_print():
    global in_undo
    global cmd_churn
    if in_undo or cmd_churn:
        return False
    return True


def y_n_can_dump(mycol):  # could also be (int)(not not can_dump(myCol)) but that's a bit odd looking
    if can_dump(mycol) > 0:
        return 1
    return 0


def can_dump(mycol):  # returns column you can dump to
    for thatcol in range(1, 9):
        if doable(mycol, thatcol, 0) > 0:
            return thatcol
    dump_space = 0
    for thiscol in range(1, 9):
        if len(elements[thiscol]) == 0:
            dump_space = dump_space + 1
    if dump_space == 0:
        return 0
    dump_space *= 2
    dump_space -= 1
    for x in range(0, 4):
        if found[x] == 0:
            dump_space = dump_space + 1
    if chains(mycol) > maxmove() // 2:
        return 0
    for tocol in range(1, 9):
        if len(elements[tocol]) == 0:
            return tocol
    return 0


def reshuf(xyz):  # this reshuffles the empty cards
    if not auto_reshuf:
        return False
    retval = False
    try_again = 1
    while try_again:
        try_again = 0
        for i in range(0, 4):
            if i == xyz:
                continue
            if xyz > -1 and spares[i] and abs(spares[i] - spares[xyz]) == 26:
                continue  # this is a very special case for if we put 3C to spares and 3S is there
            if spares[i]:
                for j in range(1, 9):
                    if len(elements[j]):
                        if can_put(spares[i], elements[j][
                                    len(elements[j]) - 1]):  # doesn't matter if there are 2. We can always switch
                            elements[j].append(spares[i])
                            spares[i] = 0
                            try_again = 1
                            retval = True
                            # stupid bug here with if we change auto_reshuf in the middle of the game
                            # solution is to create "ar(x)(y)" which only triggers if auto_reshuf = 0
    shifties = 0
    if force == 1 or only_move > 0:
        return retval
    while auto_shift():
        shifties += 1
        if shifties == 12:
            print('Oops, broke an infinite loop.')
            return False
    return retval


def auto_shift():  # this shifts rows
    for i in range(1, 9):  # this is to check for in-order columns that can be restacked
        if len(elements[i]) == 0 or chain_nope(i) > 0:
            continue
        for j in range(1, 9):
            if len(elements[j]) > 0 and len(elements[i]) <= maxmove():
                if can_put(elements[i][0], elements[j][len(elements[j]) - 1]):
                    if not cmd_churn and not in_undo:
                        print("Autoshifted " + str(i) + " to " + str(j) + ".")
                    shiftcards(i, j, len(elements[i]))
                    return True
    return False


def in_order(row_num):
    if len(elements[row_num]) < 2:
        return 0
    for i in range(1, len(elements[row_num])):
        if not can_put(elements[row_num][i], elements[row_num][i - 1]):
            return 0
    return 1


def chain_total():
    retval = 0
    for i in range(0, 9):
        for v in range(1, len(elements[i])):
            if can_put(elements[i][v], elements[i][v - 1]):
                retval += 1
    return retval


def chain_nope_big():
    retval = 0
    for i in range(0, 9):
        retval += chain_nope(i)
    return retval


def chain_nope_each():
    retval = 0
    for i in range(0, 9):
        if chain_nope(i) > 0:
            retval += 1
    return retval


def chain_nope(rowcand):
    retval = 0  # note this doesn't consider if we have, say, 7C-Ah-6D
    for v in range(1, len(elements[rowcand])):
        if can_put(elements[rowcand][v], elements[rowcand][v - 1]) == 0:  # make sure it is not a (!)
            retval += 1
    return retval


def spare_used():
    retval = 0
    for i in range(0, 4):
        if spares[i]:
            retval += 1
    return retval


def first_empty_row():
    for i in range(1, 9):
        if len(elements[i]) == 0:
            return i
    return 0


def first_matchable_row(cardval):
    for i in range(1, 9):
        if len(elements[i]) > 0:
            if can_put(cardval, elements[i][len(elements[i]) - 1]):
                return i
    return 0


def open_lock_file():
    if os.path.exists(lock_file):
        print('There seems to be another game running. Close it first, or if necessary, delete', lock_file)
        exit()
    f = open(lock_file, 'w')
    f.write('This is a lock_file')
    f.close()
    os.system("attrib +r " + lock_file)


def close_lock_file():
    os.system("attrib -r " + lock_file)
    os.remove(lock_file)
    if os.path.exists(lock_file):
        print('I wasn\'t able to delete', lock_file)


def parse_cmd_line():
    global vertical
    global debug
    global save_on_win
    global cheat_index
    global annoying_nudge
    global quick_bail
    global nag_delay
    global max_games
    open_any_file = False
    parser = argparse.ArgumentParser(description='Play FreeCell.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-o', '--opt_file', action='store_true', dest='opt_file', help='open options file')
    parser.add_argument('-l', '--loadsaveFile', action='store_true', dest='save_file', help='open save file')
    parser.add_argument('-p', '--pythonfile', action='store_true', dest='pythonfile', help='open python source file')
    parser.add_argument('-t', '--textfile', action='store_true', dest='time_file', help='open text/time file\n\n')
    parser.add_argument('-r', '--resettime', action='store_true', dest='resettime', help='open text/time file\n\n')
    parser.add_argument('--getridofthetimewastenag', action='store_false', dest='annoying_nudge')
    parser.add_argument('-c', '--cheat_index', action='store', dest='cheat_index', help='specify cheat index 1-13',
                        type=int)
    parser.add_argument('-e', '--easy', action='store_true', dest='easy', help='easy mode on (A and 2 on top)\n\n')
    parser.add_argument('-d', '--debug', action='store_true', dest='debugOn', help='debug on')
    parser.add_argument('-nd', '--nodebug', action='store_true', dest='debugOff', help='debug off')
    parser.add_argument('-v', '--vertical', action='store_true', dest='verticalOn', help='vertical on')
    parser.add_argument('-nv', '--novertical', action='store_true', dest='verticalOff', help='vertical off')
    parser.add_argument('-s', '--saveonwin', action='store_true', dest='save_on_winOn', help='save-on-win on')
    parser.add_argument('-ns', '--nosaveonwin', action='store_true', dest='save_on_winOff', help='save-on-win off')
    parser.add_argument('-q', '--quickbail', action='store_true', dest='quick_bail', help='quick bail after one win')
    parser.add_argument("--waittilnext", dest='nag_delay', type=int, help='adjust nag_delay')
    parser.add_argument('-mg', '--maxgames', nargs=1, dest='max_games', type=int, help='adjust max_games')
    args = parser.parse_args()
    # let's see if we tried to open any files, first
    if args.resettime:
        print("Resetting the time file", time_file)
        write_time_file()
        exit()
    if args.opt_file:
        os.system(opt_file)
        open_any_file = True
    if args.save_file:
        os.system("fcsav.txt")
        open_any_file = True
    if args.pythonfile:
        os.system("\"c:\\Program Files (x86)\\Notepad++\\notepad++\" fc.py")
        open_any_file = True
    if args.time_file:
        os.system("fctime.txt")
        open_any_file = True
    if open_any_file:
        exit()
    # then let's see about the annoying nudge and cheating
    if args.annoying_nudge is not None:
        annoying_nudge = args.annoying_nudge
    if args.cheat_index is not None:
        if args.cheat_index < 1:
            print("Too low. The cheat index must be between 1 and 13.")
            sys.exit()
        elif args.cheat_index > 13:
            print("Too high. The cheat index must be between 1 and 13.")
            sys.exit()
        cheat_index = args.cheat_index
    elif args.easy is True:
        cheat_index = 2
    # now let's go to the booleans we can change
    if args.debugOn:
        if args.debugOff:
            print("Debug set both ways on command line. Bailing.")
            exit()
        debug = True
    if args.debugOff:
        debug = False
    if args.verticalOn:
        if args.verticalOff:
            print("Vertical set both ways on command line. Bailing.")
            exit()
        vertical = True
    if args.verticalOff:
        vertical = False
    if args.save_on_winOn:
        if args.save_on_winOff:
            print("Save both ways set both ways on command line. Bailing.")
            exit()
        save_on_win = True
    if args.save_on_winOff:
        save_on_win = False
    if args.quick_bail:
        quick_bail = True
    if args.nag_delay and args.nag_delay > 0:
        if args.nag_delay < min_delay:
            print(str(args.nag_delay), 'is not enough. You need a delay of at least', str(min_delay) + '.')
            exit()
        if args.nag_delay > nag_delay:
            print("Whoah, going above the default!")
        nag_delay = args.nag_delay
    if args.max_games and args.max_games > 0:
            max_games = args.max_games
    return


def read_time_file():
    global nag_delay
    global max_delay
    last_time = modulus = remainder = 0
    if os.access(time_file, os.W_OK):
        print("Time file should not have write access outside of the game. attrib +R " + time_file + 
              " or chmod 333 to get things going.")
        exit()
        # zap above to debug
    if not os.path.isfile(time_file):
        print("You need to create fctime.txt with (sample)\n[Section1]\nlast_time = 1491562931" +
              "\nmaxdelay = 0\nmodulus = 178067\nremainder = 73739.")
        exit()
    config_time.read(time_file)
    try:
        modulus = modinv(config_time.getint('Section1', 'modulus'), 200003)
    except configparser.NoOptionError:
        print("Time file needs modulus.")
        exit()
    try:
        remainder = config_time.getint('Section1', 'remainder')
    except configparser.NoOptionError:
        print("Time file needs remainder.")
        exit()
    try:
        max_delay = config_time.getint('Section1', 'max_delay')
    except configparser.NoOptionError:
        print("Time file needs max_delay.")
        exit()
    try:
        last_time = config_time.getint('Section1', 'last_time')
    except configparser.NoOptionError:
        print("Time file needs last_time.")
        exit()
    cur_time = time.time()
    global delta
    delta = int(cur_time - last_time)
    if delta < nag_delay:
        print('Only', str(delta), 'seconds elapsed of', str(nag_delay) + '.')
        exit()
    if delta > 90000000:
        print("Save file probably edited to start playing a bit early. I'm not going to judge.")
    elif delta > max_delay:
        print('New high delay', delta, 'old was', max_delay)
        max_delay = delta
    else:
        print('Delay', delta, 'did not exceed record of', max_delay)
    if last_time % modulus != remainder:
        print("Save file is corrupted. If you need to reset it, choose a modulus of 125000 and do things manually.")
        print(last_time, modulus, remainder, last_time % modulus)
        exit()
    if modulus < 100001 or modulus > 199999:
        print("Modulus is not in range in fctime.txt.")
        exit()
    if not is_prime(modulus):
        print("Modulus", modulus, "is not prime.")
        exit()
    return


def write_time_file():
    os.system("attrib -r " + time_file)
    if not config_time.has_section('Section1'):
        config_time.add_section("Section1")
    last_time = int(time.time())
    modulus = rand_prime()
    remainder = last_time % modulus
    global max_delay
    config_time.set('Section1', 'modulus', str(modinv(modulus, 200003)))  # 200003 is prime. I checked!
    config_time.set('Section1', 'remainder', str(remainder))
    config_time.set('Section1', 'max_delay', str(max_delay))
    config_time.set('Section1', 'last_time', str(last_time))
    with open(time_file, 'w') as configfile:
        config_time.write(configfile)
    os.system("attrib +r " + time_file)
    return


def read_opts():
    if not os.path.isfile(opt_file):
        print("No", opt_file, "so using default options.")
        return
    config_opt.read(opt_file)
    global vertical
    try:
        vertical = config_opt.getboolean('Section1', 'vertical')
    except configparser.NoOptionError:
        print("Opts file needs vertical T/F.")
        exit()
    global auto_reshuf
    try:
        auto_reshuf = config_opt.getboolean('Section1', 'auto_reshuf')
    except configparser.NoOptionError:
        print("Opts file needs auto_reshuf T/F.")
        exit()
    global dbl_sz_cards
    try:
        dbl_sz_cards = config_opt.getboolean('Section1', 'dbl_sz_cards')
    except configparser.NoOptionError:
        print("Opts file needs dbl_sz_cards T/F.")
        exit()
    global save_on_win
    try:
        save_on_win = config_opt.getboolean('Section1', 'save_on_win')
    except configparser.NoOptionError:
        print("Opts file needs save_on_win T/F.")
        exit()
    global save_position
    try:
        save_position = config_opt.getboolean('Section1', 'save_position')
    except configparser.NoOptionError:
        print("Opts file needs save_position T/F.")
        exit()
    global annoying_nudge
    try:
        annoying_nudge = config_opt.getboolean('Section1', 'annoying_nudge')
    except configparser.NoOptionError:
        print("Opts file needs annoying_nudge T/F.")
        exit()
    global chain_show_all
    try:
        chain_show_all = config_opt.getboolean('Section1', 'chain_show_all')
    except configparser.NoOptionError:
        print("Opts file needs chain_show_all T/F.")
        exit()
    return


def send_opts():
    if not config_opt.has_section('Section1'):
        config_opt.add_section("Section1")
    config_opt.set('Section1', 'vertical', str(vertical))
    config_opt.set('Section1', 'auto_reshuf', str(auto_reshuf))
    config_opt.set('Section1', 'dbl_sz_cards', str(dbl_sz_cards))
    config_opt.set('Section1', 'save_on_win', str(save_on_win))
    config_opt.set('Section1', 'save_position', str(save_position))
    config_opt.set('Section1', 'annoying_nudge', str(annoying_nudge))
    config_opt.set('Section1', 'annoying_nudge', str(chain_show_all))
    with open(opt_file, 'w') as configfile:
        config_opt.write(configfile)
    print("Saved options.")
    return


def init_side(in_game_reset):
    global spares
    spares = [0, 0, 0, 0]
    global found
    found = [0, 0, 0, 0]
    global highlight
    global start_time
    global last_reset
    highlight = 0
    if not in_undo:
        last_reset = time.time()
        if in_game_reset != 1:
            start_time = last_reset
        global win
        win = 0
        global move_list
        move_list = []
        global cmd_list
        cmd_list = []
        global cmd_no_meta
        cmd_no_meta = []
    global break_macro
    break_macro = 0


def plur(a):
    if a is 1:
        return ''
    return 's'


def maxmove():
    base = 1
    myexp = 1
    for y in range(0, 4):
        if spares[y] == 0:
            base += 1
    for y in range(1, 9):
        if len(elements[y]) == 0:
            myexp *= 2
    return base * myexp


def can_put(lower, higher):
    if lower == 0 or higher == 0:
        return 0
    temp1 = lower - 1
    temp2 = higher - 1
    if temp1 % 13 == 0:
        return 0
    if temp2 % 13 - temp1 % 13 != 1:
        return 0
    if ((temp2 // 13) + (temp1 // 13)) % 2 == 1:
        return 1
    return 0


totalFoundThisTime = 0
cardlist = ''


def check_found():
    retval = False
    need_to_check = 1
    global totalFoundThisTime
    global cardlist
    if not cmd_churn:
        totalFoundThisTime = 0
        cardlist = ''
    while need_to_check:
        need_to_check = 0
        for y in range(1, 9):
            if len(elements[y]) > 0:
                while elements[y][len(elements[y]) - 1] % 13 == (
                            1 + found[(elements[y][len(elements[y]) - 1] - 1) // 13]) % 13:
                    basesuit = (elements[y][len(elements[y]) - 1] - 1) // 13
                    if found[(basesuit + 1) % 4] < found[basesuit] - 1:
                        break
                    if found[(basesuit + 3) % 4] < found[basesuit] - 1:
                        break
                    need_to_check = 1
                    retval = True
                    totalFoundThisTime += 1
                    found[(elements[y][len(elements[y]) - 1] - 1) // 13] = found[(elements[y][len(
                        elements[y]) - 1] - 1) // 13] + 1
                    cardlist = cardlist + to_card_x(elements[y][len(elements[y]) - 1])
                    elements[y].pop()
                    if len(elements[y]) == 0:
                        break
        for y in range(0, 4):
            # print 'checking ',y,to_card(spares[y])
            if spares[y] > 0:
                if (spares[y] - 1) % 13 == found[(spares[y] - 1) // 13]:
                    sparesuit = (spares[y] - 1) // 13
                    if debug:
                        print('position', y, 'suit', suits[(spares[y] - 1) // 13], 'card', to_card(spares[y]))
                    if found[(sparesuit + 3) % 4] < found[sparesuit] - 1:
                        continue
                    if found[(sparesuit + 1) % 4] < found[sparesuit] - 1:
                        continue
                    cardlist = cardlist + to_card_x(spares[y])
                    totalFoundThisTime += 1
                    found[(spares[y] - 1) // 13] += 1
                    spares[y] = 0
                    need_to_check = 1
                    retval = True
    # print(str(totalFoundThisTime) + " undo " + str(in_undo) + " churn " + str(cmd_churn) + " " + str(should_print()))
    # traceback.print_stack()
    print_found()
    return retval


def print_found():
    global totalFoundThisTime
    global cardlist
    if totalFoundThisTime > 0 and should_print():
        sys.stdout.write(
            str(totalFoundThisTime) + ' card' + plur(totalFoundThisTime) + ' safely to foundation:' + cardlist + '\n')
        totalFoundThisTime = 0
        cardlist = ''


def force_foundation():
    global in_undo
    check_again = 1
    force_str = ""
    global cardlist
    global totalFoundThisTime
    while check_again:
        check_again = 0
        for row in range(1, 9):
            if len(elements[row]) > 0:
                if foundable(elements[row][len(elements[row]) - 1]) == 1:
                    found[(elements[row][len(elements[row]) - 1] - 1) // 13] += 1
                    force_str = force_str + to_card_x(elements[row][len(elements[row]) - 1])
                    if not in_undo:
                        cardlist = cardlist + to_card_x(elements[row][len(elements[row]) - 1])
                        totalFoundThisTime += 1
                    elements[row].pop()
                    check_again = 1
        for xx in range(0, 4):
            if spares[xx]:
                # print("Checking" + to_card_x(spares[xx]))
                if foundable(spares[xx]):
                    force_str = force_str + to_card_x(spares[xx])
                    if not in_undo:
                        cardlist = cardlist + to_card_x(spares[xx])
                        totalFoundThisTime += 1
                    found[(spares[xx] - 1) // 13] += 1
                    spares[xx] = 0
                    check_again = 1
    if force_str:
        if not in_undo:
            move_list.append("r")
            print_cond("Sending all to foundation.")
            print_cond("Forced" + force_str)
        reshuf(-1)
        check_found()
        print_cards()
    else:
        print_cond("Nothing to force to foundation.")
    return


def check_win():
    for y in range(0, 4):
        # print y,found[y]
        if found[y] != 13:
            return 0
    check_winning()


def init_cards():
    global elements
    x = list(range(cheat_index + 1, 14)) + list(range(cheat_index + 14, 27)) + list(
      range(cheat_index + 27, 40)) + list(range(cheat_index + 40, 53))
    shuffle(x)
    for y in reversed(range(1, cheat_index + 1)):
        x[:0] = [y, y + 13, y + 26, y + 39]
    for z in range(0, 52):
        elements[z % 8 + 1].append(x.pop())
    global backup
    backup = [row[:] for row in elements]


def to_card(cardnum):
    if cardnum == 0:
        return '---'
    temp = cardnum - 1
    retval = '' + cards[temp % 13] + suits[temp // 13]
    return retval


def to_card_x(cnum):
    if cnum % 13 == 10:
        return ' ' + to_card(cnum)
    return to_card(cnum)


def print_cards():
    if cmd_churn:
        return
    if in_undo:
        return
    if sum(found) == 52:
        if not check_winning():
            return
    if vertical:
        print_vertical()
    else:
        print_horizontal()


def check_winning():
    global cmd_churn
    # print("Churn now false (check_winning).")
    cmd_churn = False
    print_found()
    global start_time
    global last_reset
    if start_time != -1:
        cur_time = time.time()
        time_taken = cur_time - start_time
        print("%.2f seconds taken." % time_taken)
        if last_reset > start_time:
            print("%.2f seconds taken since last reset." % (cur_time - last_reset))
    else:
        print("No time data kept for loaded game.")
    global total_reset
    global total_undo
    if total_reset > 0:
        print("%d reset used." % total_reset)
    if total_undo > 0:
        print("%d undo used." % total_undo)
    if total_undo == -1:
        print("No undo data from loaded game.")
    if save_on_win:
        with open(win_file, "a") as myfile:
            winstring = time.strftime("sw=%Y-%m-%d-%H-%M-%S", time.localtime())
            myfile.write(winstring)
            myfile.write("\n#START NEW SAVED POSITION\n")
            global backup
            for i in range(1, 9):
                myfile.write(' '.join(str(x) for x in backup[i]) + "\n")
        print("Saved " + winstring)
    global break_macro
    break_macro = 1
    if max_games > 0:
        global cur_games
        cur_games = cur_games + 1
        print('Won', cur_games, 'of', max_games, 'so far.')
        if cur_games == max_games:
            print("Well, that's it. Looks like you've played all your games.")
            go_bye()
    global won_this_cmd
    won_this_cmd = True
    while True:
        try:
            finish = input(
                "You win in %d commands (%d including extraneous) and %d moves! Play again (Y/N, U to undo)?" %
                (len(cmd_no_meta), len(cmd_list), len(move_list))).lower()
        except KeyboardInterrupt:
            print("\nCheaty cheaty. You should just quit instead.")
            exit()
        finish = re.sub(r'^ *', '', finish)
        if len(finish) > 0:
            if finish[0] == 'n' or finish[0] == 'q':
                go_bye()
            if finish[0] == 'y':
                if quick_bail:
                    print("Oops! Quick bailing.")
                    go_bye()
                global deliberate_nuisance_rows
                if deliberate_nuisance_rows > 0:
                    deliberate_nuisance_rows += deliberateNuisanceIncrease
                init_cards()
                init_side(0)
                total_undo = 0
                total_reset = 0
                return 1
            if finish[0] == 'u':
                cur_games -= 1
                cmd_no_meta.pop()
                global in_undo
                in_undo = True
                undo_moves(1)
                in_undo = False
                return 0
        print("Y or N (or U to undo). Case insensitive, cuz I'm a sensitive guy.")


# this detects how long a chain is, e.g. how many in a row
# 10d-9s-8d-7s is 4 not 3
def chains(my_row):
    if len(elements[my_row]) == 0:
        return 0
    retval = 1
    my_temp = len(elements[my_row]) - 1
    while my_temp > 0:
        if can_put(elements[my_row][my_temp], elements[my_row][my_temp - 1]):
            retval += 1
            my_temp = my_temp - 1
        else:
            return retval
    return retval


def one_dig(y):
    if y < 10:
        return str(y)
    return "+"


def print_vertical():
    count = 0
    for y in range(1, 9):
        if chain_nope(y) == 0:
            sys.stdout.write(' *' + one_dig(chains(y)) + '*')
        else:
            sys.stdout.write(' ' + one_dig(chains(y)) + '/' + str(chain_nope(y)))
        if dbl_sz_cards:
            sys.stdout.write(' ')
    print("")
    for y in range(1, 9):
        sys.stdout.write(' ' + str(y) + ': ')
        if dbl_sz_cards:
            sys.stdout.write(' ')
    print("")
    one_more_try = 1
    while one_more_try:
        this_line = ''
        second_line = ''
        one_more_try = 0
        for y in range(1, 9):
            if len(elements[y]) > count:
                one_more_try = 1
                if dbl_sz_cards:
                    temp = str(to_card(elements[y][count]))
                    if to_card(elements[y][count])[0] == ' ':
                        this_line += temp[1]
                        second_line += temp[0]
                    else:
                        this_line += temp[0]
                        second_line += temp[1]
                    this_line += top[(elements[y][count] - 1) // 13]
                    second_line += btm[(elements[y][count] - 1) // 13] + ' '
                else:
                    this_line += str(to_card(elements[y][count]))
                if foundable(elements[y][count]):
                    if nexties(elements[y][count]):
                        this_line += '!'
                    else:
                        this_line += '*'
                elif highlight and (((elements[y][count] - 1) % 13) == highlight - 1):
                    this_line += '+'
                else:
                    this_line += ' '
                if dbl_sz_cards:
                    this_line += ' '
                    second_line += ' '
            else:
                this_line += '    '
                if dbl_sz_cards:
                    this_line += ' '
                    second_line += '     '
        if one_more_try:
            print(this_line)
            if second_line:
                print(second_line)
        count += 1
    print_others()
    # traceback.print_stack()


def print_horizontal():
    for y in range(1, 9):
        sys.stdout.write(str(y) + ':')
        for z in elements[y]:
            sys.stdout.write(' ' + to_card(z))
    print_others()


def org_it(my_list):
    globbed = 1
    while globbed:
        globbed = 0
        for x1 in range(0, len(my_list)):
            for x2 in range(0, len(my_list)):
                if globbed == 0:
                    if my_list[x1][0] == my_list[x2][-1]:
                        globbed = 1
                        temp = my_list[x2] + my_list[x1][1:]
                        del my_list[x2]
                        if x1 > x2:
                            del my_list[x1 - 1]
                        else:
                            del my_list[x1]
                        my_list.insert(0, temp)
    return ' ' + ' '.join(my_list)


def bot_card(mycol):
    return elements[mycol][len(elements[mycol]) - 1]


def automove():
    min_card = 0
    fromcand = 0
    tocand = 0
    for z1 in range(1, 9):
        if len(elements[z1]) == 0:
            continue
        for z2 in range(1, 9):
            if z1 == z2:
                continue
            if len(elements[z2]) == 0:
                continue
            thisdo = doable(z1, z2, 0)
            if thisdo > 0:
                if not can_put(elements[z1][len(elements[z1]) - thisdo], elements[z1][len(elements[z1]) - thisdo - 1]):
                    mincand = bot_card(z1) % 13
                    if mincand > min_card:
                        min_card = mincand
                        fromcand = z1
                        tocand = z2
    if fromcand > 0:
        myauto = str(fromcand) + str(tocand)
        print("Auto moved " + myauto)
        read_cmd(myauto)
        return 1
    return 0


def print_others():
    check_win()
    coolmoves = []
    foundmove = ''
    wackmove = ''
    emmove = ''
    latmove = ''
    canfwdmove = 0
    for z1 in range(1, 9):
        if len(elements[z1]) == 0:
            emmove = emmove + ' E' + str(z1)
            canfwdmove = 1
            continue
        if in_order(z1) and elements[z1][0] % 13 == 0:
            continue
        for z2 in range(1, 9):
            if z2 == z1:
                continue
            if len(elements[z2]) == 0:
                continue
            thisdo = doable(z1, z2, 0)
            if thisdo == -1:
                wackmove = wackmove + ' ' + str(z1) + str(z2)
            elif thisdo > 0:
                tempmove = str(z1) + str(z2)
                if thisdo >= len(elements[z1]):
                    canfwdmove = 1
                    coolmoves.append(tempmove)
                elif not can_put(elements[z1][len(elements[z1]) - thisdo],
                                 elements[z1][len(elements[z1]) - thisdo - 1]):
                    canfwdmove = 1
                    coolmoves.append(tempmove)
                else:
                    tempmove = ' ' + tempmove + '-'
                    latmove = latmove + tempmove
    for z1 in range(1, 9):
        if len(elements[z1]):
            for z2 in range(0, 4):
                if can_put(spares[z2], elements[z1][len(elements[z1]) - 1]):
                    foundmove = foundmove + ' ' + chr(z2 + 97) + str(z1)
                    canfwdmove = 1
    for z1 in range(0, 4):
        if spares[z1] == 0:
            foundmove = ' >' + chr(z1 + 97) + foundmove
            canfwdmove = 1
    if wackmove:
        print("Not enough room: " + str(wackmove))
    print("Possible moves:" + org_it(coolmoves) + foundmove + latmove + " (%d max shift" % (maxmove()) + (
        ", recdumprow=" + str(best_dump_row()) if best_dump_row() > 0 else "") + ")")
    if not canfwdmove:
        really_lost = 1
        for z in range(1, 9):
            if len(elements[z]) > 0 and foundable(elements[z][len(elements[z]) - 1]):
                really_lost = 0
        for z in range(0, 4):
            if foundable(spares[z]):
                really_lost = 0
        if really_lost == 1:
            print("Uh oh. You\'re probably lost.")
        else:
            print("You may have to dump stuff in the foundation.")
    sys.stdout.write('Empty slots: ')
    for y in range(0, 4):
        sys.stdout.write(to_card(spares[y]))
        for z in range(1, 9):
            if len(elements[z]) and can_put(spares[y], elements[z][len(elements[z]) - 1]):
                sys.stdout.write('<')
                break
        if spares[y] > 0 and (spares[y] - 1) % 13 == found[(spares[y] - 1) // 13]:
            sys.stdout.write('*')
        else:
            sys.stdout.write(' ')
    sys.stdout.write('\nFoundation: ')
    found_score = 0
    for y in [0, 2, 1, 3]:
        found_score += found[y]
        if found[y] == 0:
            sys.stdout.write(' ---')
        else:
            sys.stdout.write(' ' + to_card(found[y] + y * 13))
    sys.stdout.write(' (' + str(found_score) + ' point' + plur(found_score))
    global last_score
    if last_score < found_score:
        sys.stdout.write(', up ' + str(found_score - last_score))
    sys.stdout.write(', ' + str(chain_total()) + ' pairs in order, ' + str(chain_nope_big()) + ' out of order, ' + str(
        chain_nope_each()) + ' cols unordered')
    sys.stdout.write(')\n')
    last_score = found_score


def any_doable_limit(ii):
    temp_val = 0
    for y in range(1, 9):
        temp2 = doable(ii, y, 0)
        if len(elements[y]) > 0 and 0 < temp2 <= maxmove():
            if chains(ii) == temp2:
                return y
            temp_val = y
    return temp_val


def any_doable(ii, empty_ok):
    temp_ret = 0
    for y in range(1, 9):
        temp_val = doable(ii, y, 0)
        if empty_ok or len(elements[y]) > 0:
            if temp_val > 0:
                return y
        if len(elements[y]) > 0 and temp_val > 0:
            temp_ret = y
    return temp_ret


def doable(r1, r2, show_details):  # return value = # of cards to move. 0 = no match, -1 = asking too much
    from_line = 0
    loc_max_move = maxmove()
    if r1 < 1 or r2 < 1 or r1 > 8 or r2 > 8:
        print("This shouldn't have happened, but one of the rows is invalid.")
        # trackback.print_tb()
        return 0
    global only_move
    if len(elements[r2]) == 0:
        if len(elements[r1]) == 0:
            if show_details:
                print("Empty-empty move.")
            return 0
        if in_order(r1) and only_move == len(elements[r1]):
            if show_details:
                print('OK, moved the already-sorted row, though this doesn\'t really change the game state.')
            return len(elements[r1])
        loc_max_move /= 2
        if show_details and should_print():
            print("Only half moves here down to %d" % loc_max_move)
        for n in range(len(elements[r1]) - 1, -1, -1):
            from_line += 1
            # print '1 debug stuff:',to_card(elements[r1][n]),n,from_line
            if n == 0:
                break
            # print '2 debug stuff:',to_card(elements[r1][n]),n,from_line
            if can_put(elements[r1][n], elements[r1][n - 1]) == 0:
                break
                # print '3 debug stuff:',to_card(elements[r1][n]),n,from_line
    else:
        to_top_card = elements[r2][len(elements[r2]) - 1]
        # print str(elements[r2]) + "Row " + str(r2) + " Card " + to_card(to_top_card)
        for n in range(len(elements[r1]) - 1, -1, -1):
            from_line += 1
            if can_put(elements[r1][n], to_top_card):
                break
            if n == 0:
                return 0
            if can_put(elements[r1][n], elements[r1][n - 1]) == 0:
                return 0
    if only_move > loc_max_move:
        print("WARNING, %d is greater than the maximum of %d." % (only_move, loc_max_move))
        only_move = 0
    if len(elements[r1]) == 0:
        if show_details:
            print('Tried to move from empty.')
        return 0
    if only_move > 0:
        if only_move < loc_max_move:
            if show_details:
                if len(elements[r2]) > 0:
                    print('Can\'t move to that non-empty, even with force.')
                    return -1
                print_cond('Cutting down to ' + str(only_move))
                return only_move
        if only_move < from_line:
            return only_move
    if from_line > loc_max_move:
        if force == 1:
            if show_details:
                if len(elements[r2]) > 0:
                    print('Can\'t move to that non-empty, even with force.')
                    return -1
                print_cond("Cutting down to " + str(loc_max_move))
            return loc_max_move
        global cmd_churn
        if show_details and not cmd_churn:
            print("Not enough open. Have %d, need %d" % (loc_max_move, from_line))
        return -1
    return from_line


def max_move_mod():
    base = 2
    myexp = .5
    for y in range(0, 4):
        if spares[y] == 0:
            base += 1
    for y in range(1, 9):
        if len(elements[y]) == 0:
            myexp *= 2
    return base * myexp


def slip_under():
    slip_process = True
    ever_slip = False
    global cmd_churn
    while slip_process:
        fi = first_empty_row()
        slip_process = False
        if fi == 0:
            for i in range(1, 9):
                for j in range(0, 4):
                    if slip_process is False and\
                            (in_order(i) or (len(elements[i]) == 1)) and\
                            can_put(elements[i][0], spares[j]):
                        # print("Checking slip under %d %d %d %d %d" % (fi, i, j, elements[i][0], spares[j]))
                        if len(elements[i]) + spare_used() <= 4:
                            elements[i].insert(0, spares[j])
                            spares[j] = 0
                            slip_process = True
        else:
            for i in range(1, 9):
                if slip_process is False and ((len(elements[i]) > 0 and in_order(i)) or (len(elements[i]) == 1)):
                    # print("%d %d %d %d" % (i, len(elements[i]), in_order(i), slip_process))
                    for j in range(0, 4):
                        # print("%d %d %d %d" % (i, j, spares[j], can_put(elements[i][0], spares[j])))
                        if spares[j] > 0 and can_put(elements[i][0], spares[j]):
                            # print("OK, giving a look %d -> %d | %d %d" % (i, fi, len(elements[i]), max_move_mod()))
                            if len(elements[i]) <= max_move_mod():
                                reset_churn = not cmd_churn
                                cmd_churn = True
                                elements[fi].append(spares[j])
                                spares[j] = 0
                                shiftcards(i, fi, len(elements[i]))
                                if reset_churn:
                                    cmd_churn = False
                                slip_process = True
                                ever_slip = True
                                break
    return ever_slip


def dump_info(x):
    print("Uh oh, big error avoided")
    print(elements)
    print(backup)
    print(move_list)
    print(cmd_list)
    print(cmd_no_meta)
    print("Spares: " % spares)
    print("Found: " % found)
    if abs(x) == 2:
        print_vertical()
    if x < 0:
        exit()
    return


def shiftcards(r1, r2, amt):
    elements[r2].extend(elements[r1][int(-amt):])
    del elements[r1][int(-amt):]


def usage_game():
    print('========game moves========')
    print('r(1-8a-d) sends that card to the foundation. r alone forces everything it can.')
    print('p(1-8) moves a row as much as you can.')
    print('p on its own tries to force everything if you\'re near a win.')
    print('\\ tries all available moves starting with the highest card to match eg 10-9 comes before 7-6.')
    print('(1-8) attempts a \'smart move\' where the game tries progress, then shifting.')
    print('(1-8)(1-8) = move a row, standard move. You can also string moves together, or 646 goes back and forth.')
    print('(1-8a-d) (1-8a-d) move to spares and back.')
    print('f(1-8)(1-8) forces what you can (eg half of what can change between nonempty rows) onto an empty square.')
    print('(1-8)(1-8)-(#) forces # cards onto a row, if possible.')
    print('h slips a card under eg KH in spares would go under an ordered QC-JD.')
    print('- or = = a full board reset.')
    print('?/?g ?o ?m games options meta')


def usage_options():
    print('========options========')
    print('v toggles vertical, + toggles card size (only vertical right now).')
    print('cs toggles chain_show_all e.g. if 823 shows intermediate move.')
    print('sw/ws saves on win, sp/ps saves position.')
    print('+ = toggles double size, e = toggle autoshuffle.')
    print('?/?g ?o ?m games options meta, g is default.')


def usage_meta():
    print('========meta========')
    print('l=loads a game, s=saves, lp=load previous/latest saved')
    print('lo/so loads/saves options.')
    print('u = undo, u1-u10 undoes that many moves, undo does 11+, tu tracks undo.')
    print('ua = shows current move/undo array.')
    print('uc = shows current command list.')
    print('ux = shows current command list excluding meta-commands.')
    print('qu quits (q could be typed by accident).')
    print('? = usage (this).')
    print('empty command tries basic reshuffling and prints out the cards again.')
    print('? gives hints: /?g ?o ?m games options meta, g is default.')


def first_empty_spare():
    for i in range(0, 4):
        if spares[i] == 0:
            return i
    return -1


def undo_moves(to_undo):
    if to_undo == 0:
        print('No moves undone.')
        return 0
    global move_list
    global total_undo
    if len(move_list) == 0:
        print('Nothing to undo.')
        return 0
    global elements
    elements = [row[:] for row in backup]
    global found
    found = [0, 0, 0, 0]
    global spares
    spares = [0, 0, 0, 0]
    for _ in range(0, to_undo):
        move_list.pop()
        if total_undo > -1:
            total_undo += 1
    global in_undo
    in_undo = True
    global undo_idx
    for undo_idx in range(0, len(move_list)):
        read_cmd(str(move_list[undo_idx]))
        if track_undo == 1:
            in_undo = False
            print_cards()
            in_undo = True
    undo_idx = 0
    in_undo = False
    check_found()
    print_cards()
    return 1


def load_game(game_name):
    global total_undo
    global total_reset
    global start_time
    original = open(save_file, "r")
    start_time = -1
    while True:
        line = original.readline()
        if line.startswith('moves='):
            continue
        if game_name == line.strip():
            for y in range(1, 9):
                line = original.readline().strip()
                elements[y] = [int(i) for i in line.split()]
                backup[y] = [int(i) for i in line.split()]
            global move_list
            templine = original.readline()
            move_list = templine.strip().split()  # this is the list of moves
            global cmd_list
            global cmd_no_meta
            cmd_list = []
            cmd_no_meta = []
            line = original.readline().strip()
            while not re.search("^#end of", line):
                print(line + " read in")
                if re.search("^#cmd_no_meta", line):
                    cmd_no_meta = re.sub("^#cmd_no_meta=", "", line).split(',')
                if re.search("^#cmd_list", line):
                    cmd_list = re.sub("^#cmd_list=", "", line).split(',')
                line = original.readline().strip()
            original.close()
            if len(move_list) > 0:
                if len(cmd_no_meta) == 0:
                    cmd_no_meta = list(move_list)
                if len(cmd_list) == 0:
                    cmd_list = list(move_list)
            global in_undo
            in_undo = True
            init_side(0)
            global undo_idx
            for undo_idx in range(0, len(move_list)):
                read_cmd(str(move_list[undo_idx]))
                if track_undo == 1:
                    in_undo = False
                    print_cards()
                    in_undo = True
            in_undo = False
            check_found()
            print_cards()
            global totalFoundThisTime
            global cardlist
            totalFoundThisTime = 0
            cardlist = ''
            print("Successfully loaded " + game_name.replace(r'^.=', ''))
            # this was in unreachable code and is probably wrong but I can check to delete it later (?)
            # total_undo = -1
            # total_reset = -1
            return 1
        if not line:
            break
    print(re.sub(r'^.=', '', game_name) + ' save game not found.')
    original.close()
    return 0


def save_game(game_name):
    savfi = open(save_file, "r")
    linecount = 0
    for line in savfi:
        linecount += 1
        if line.strip() == game_name:
            print("Duplicate save game name found at line %d." % linecount)
            return
    savfi.close()
    with open(save_file, "a") as myfile:
        myfile.write(game_name + "\n")
        for y in range(1, 9):
            myfile.write(' '.join(str(x) for x in backup[y]) + "\n")
        myfile.write(' '.join(move_list) + "\n")
        if save_position:
            for y in range(1, 9):
                myfile.write('# '.join(str(x) for x in elements[y]) + "\n")
        myfile.write("###end of " + game_name + "\n")
        myfile.write("#cmd_no_meta=" + ', '.join(cmd_no_meta) + '\n')
        myfile.write("#cmd_list=" + ', '.join(cmd_list) + '\n')
    gn2 = game_name.replace(r'^.=', '')
    print("Successfully saved game as " + gn2)
    return 0


def reverse_card(my_card):
    ret_val = 0
    for i in range(0, 5):
        if i == 4:
            return -2
        if re.search(suits[i].lower(), my_card):
            ret_val = 13 * i
            break
    for i in range(0, 13):
        if re.search(cards[i].lower(), ' ' + my_card):
            ret_val += (i + 1)
            return ret_val
    return -1


def card_eval(my_cmd):
    ary = re.split('[ ,]', my_cmd)
    for word in ary:
        if word == 'e':
            continue
        sys.stdout.write(' ' + str(reverse_card(word)))
    print("")
    return


def go_bye():
    global cur_games
    global max_games
    if cur_games * 2 < max_games:
        print("Great job, leaving well before you played all you could've.")
    elif cur_games < max_games:
        print("Good job, leaving before you played all you could've.")
    else:
        print("Bye!")
    if time_matters:
        write_time_file()
    close_lock_file()
    exit()


def read_cmd(this_cmd):
    global debug
    global won_this_cmd
    global cmd_churn
    global vertical
    global dbl_sz_cards
    global auto_reshuf
    global elements
    global force
    global track_undo
    global total_reset
    global save_on_win
    global save_position
    global chain_show_all
    won_this_cmd = False
    prefix = ''
    force = 0
    check_found()
    if this_cmd == '':
        for _ in range(0, deliberate_nuisance_rows):
            print("DELIBERATE NUISANCE")
        try:
            name = input("Move:")
        except KeyboardInterrupt:
            print("\nCheaty cheaty. You should just quit instead.")
            exit()
        name = name.strip()
        if name == '/':  # special case for slash/backslash
            debug = 1 - debug
            print('debug', on_off[debug])
            cmd_list.append(name)
            return
        if name == '\\':
            temp = len(move_list)
            totalmoves = 0
            cmd_churn = 1
            while automove():
                totalmoves = totalmoves + 1
            cmd_churn = 0
            if temp == len(move_list):
                print("No moves done.")
            else:
                print_cards()
                print_found()
                print(totalmoves, "total moves.")
            cmd_no_meta.append(name)
            cmd_list.append(name)
            return
        name = re.sub('[\\\/]', '', name)
        cmd_no_meta.append(name)
        cmd_list.append(name)
        if name[:2] == 'e ':
            card_eval(name)
            return
        if name[:2] != 'l=' and name[:2] != 's=':
            name = name.replace(' ', '')
    else:
        name = this_cmd
    if name == '*':
        while reshuf(-1):
            pass
        return
    name = name.lower()
    if len(name) % 2 == 0 and len(name) >= 2:
        temp = int(len(name) / 2)
        if name[:] == name[temp:]:
            print("Looks like a duplicate command, so I'm cutting it in half.")
            name = name[temp:]
    if name == 'tu':
        track_undo = 1 - track_undo
        if not in_undo:
            print("track_undo now " + on_off[track_undo])
        cmd_no_meta.pop()
        return
    if len(name) == 0:
        any_reshuf = False
        while reshuf(-1):
            any_reshuf = True
        if any_reshuf:
            move_list.append('*')
        else:
            cmd_no_meta.pop()
        print_cards()
        return
    if name[0] == '>' and name[1:].isdigit:
        print(name[1:], "becomes", to_card(int(name[1:])))
        cmd_no_meta.pop()
        return
    global only_move
    only_move = 0
    if len(name) > 3:
        if name[2] == '-':
            only_move = re.sub(r'.*-', '', name)
            if not only_move.isdigit():
                print('Format is ##-#.')
                return
            only_move = int(only_move)
            name = re.sub(r'-.*', '', name)
    # saving/loading comes first.
    if name == 'lp':
        original = open(save_file, "r")
        o1 = re.compile(r'^s=')
        new_save = ""
        while True:
            line = original.readline()
            if o1.match(line):
                new_save = line
            if not line:
                break
        name = new_save.strip()
        name = "l" + name[1:]
        print("Loading " + name[2:])
    if name == 'l' or name == 's' or name == 'l=' or name == 's=':
        print("load/save needs = and then a name. lp loads the last in the save file.")
        cmd_no_meta.pop()
        return
    if len(name) > 1:
        if name[0] == 'l' and name[1] == '=':
            cmd_no_meta.pop()
            load_game(re.sub(r'^l=', 's=', name))
            return
        if name[0] == 's' and name[1] == '=':
            cmd_no_meta.pop()
            save_game(name.strip())
            return
    if name == "lo":
        cmd_no_meta.pop()
        read_opts()
        return
    if name == "so":
        cmd_no_meta.pop()
        send_opts()
        return
    if name == 'q':
        cmd_no_meta.pop()
        print("QU needed to quit, so you don't type Q accidentally.")
        return
    if name == 'qu':
        cmd_no_meta.pop()
        go_bye()
    if name == 'ws' or name == 'sw':
        cmd_no_meta.pop()
        save_on_win = not save_on_win
        print("Save on win is now %s." % ("on" if save_on_win else "off"))
        return
    if name == 'ps' or name == 'sp':
        cmd_no_meta.pop()
        save_position = not save_position
        print("Save position with moves/start is now %s." % ("on" if save_position else "off"))
        return
    if name == 'u':
        undo_moves(1)
        return
    if name == 'h':
        if not slip_under():
            cmd_no_meta.pop()
            print("No slip-unders found.")
        return
    if name == 'p':
        old_moves = len(move_list)
        any_dump = 0
        global break_macro
        while best_dump_row() > 0:
            any_dump = 1
            new_dump = best_dump_row()
            print("Dumping row " + str(new_dump))
            if chains(new_dump) == len(elements[new_dump]) and not cmd_churn:
                shufwarn()
                return
            rip_up(new_dump)
            if len(elements[new_dump]) > 0:
                if in_order(new_dump) != 1:  # or elements[new_dump][0] % 13 != 0
                    print("Row %d didn't unfold all the way." % new_dump)
                    break
            if break_macro == 1:
                break_macro = 0
                break
            check_found()
            if break_macro == 1:
                break_macro = 0
                break
            if debug:
                print("Check: " + " ".join(str(x) for x in found) + " <sp found> " + " ".join(str(x) for x in spares))
        cmd_churn = False
        if debug:
            print("Won this cmd: " + str(won_this_cmd))
        if any_dump == 0:
            print("No rows found to dump.")
        elif not won_this_cmd:
            print(str(len(move_list) - old_moves) + " moves total.")
            print_cards()
        elif sum(spares) == 52:
            print("Not sure why but I need to check for a win here.")
            check_win()
        won_this_cmd = False
        return
    if name[:1] == 'u':
        big_undo = False
        if name[:4] == 'undo':
            big_undo = True
            name = name[4:]
        else:
            name = name[1:]
        if name == 'a':
            cmd_no_meta.pop()
            if not in_undo:
                print('Move list,', len(move_list), 'moves so far:', move_list)
            return
        if name == 'c':
            cmd_no_meta.pop()
            if not in_undo:
                print('Command list,', len(cmd_list), 'commands so far:', cmd_list)
            return
        if name == 'x':
            cmd_no_meta.pop()
            if not in_undo:
                print('Trimmed command list,', len(cmd_no_meta), 'commands so far:', cmd_no_meta)
            return
        if name == 's':
            if len(move_list) == 0:
                print("You've made no moves yet.")
                return
            d1 = move_list[len(move_list) - 1][0]
            temp = 0
            while (temp < len(move_list) - 1) and (d1 == move_list[len(move_list) - temp - 1][0]):
                temp += 1
            undo_moves(temp)
            print("Last " + str(temp) + " moves started with " + d1)
            return
        if not name.isdigit():
            print("Need to undo a number, or A for a list, S for same row as most recent move, or nothing." +
                  " C=commands X=commands minus meta.")
            return
        if int(name) > len(move_list):
            print("Tried to do %d undo%s, can only undo %d." % (int(name), plur(int(name)), len(move_list)))
            return
        if int(name) > 10:
            if big_undo:
                print(
                    "This game doesn't allow undoing more than 10 at a time except with UND,"
                    " because u78 would be kind of bogus if you changed your mind from undoing to moving.")
                return
            print("UNDOing more than 10 moves.")
        undo_moves(int(name))
        return
    if name[0] == 'h':
        cmd_no_meta.pop()
        name = re.sub(r'^h', '', name)
        if name.isdigit() == 0:
            if name == 'q':
                name = 12
            elif name == 'j':
                name = 11
            elif name == 'k':
                name = 13
            elif name == 'a':
                name = 1
            else:
                print('Need a number, or AJQK.')
                return
        if int(name) < 1 or int(name) > 13:
            print('Need 1-13.')
            return
        global highlight
        highlight = int(name)
        if highlight == 0:
            print('Highlighting off.')
        else:
            print('Now highlighting', cards[highlight - 1])
        print_cards()
        return
    if name[0] == '?':
        cmd_no_meta.pop()
        if len(name) is 1 or name[1].lower() == 'g':
            usage_game()
        elif name[1].lower() == 'm':
            usage_meta()
        elif name[1].lower() == 'o':
            usage_options()
        else:
            print("Didn't recognize subflag", name[1].lower(), "so doing default of game command usage.")
            usage_game()
        return
    if name == "r" or name == "rr":
        force_foundation()
        return
    if name[0] == 'f' or (len(name) > 2 and name[2] == 'f'):
        name = name.replace("f", "")
        force = 1
        prefix = prefix + 'f'
        if len(name) == 0:
            print("You need a from/to, or at the very least, a from.")
            return
    if name == '-' or name == '=':
        if len(move_list) == 0:
            print("Nothing to undo.")
            return
        elements = [row[:] for row in backup]
        init_side(1)
        print_cards()
        check_found()
        total_reset += 1
        return
    if name == "?":
        cmd_no_meta.pop()
        print('Maximum card length moves: ', maxmove())
        return
    if name == "":
        print_cards()
        return
    if name == '+':
        cmd_no_meta.pop()
        dbl_sz_cards = not dbl_sz_cards
        print("Toggled dbl_sz_cards to %s." % (on_off[dbl_sz_cards]))
        print_cards()
        return
    if name == 'cs':
        cmd_no_meta.pop()
        chain_show_all = not chain_show_all
        print("Toggled chain_show_all to %s." % (on_off[chain_show_all]))
        print_cards()
        return
    if name == 'e':
        cmd_no_meta.pop()
        auto_reshuf = not auto_reshuf
        print("Toggled reshuffling to %s." % (on_off[auto_reshuf]))
        reshuf(-1)
        print_cards()
        return
    if name == 'v':
        cmd_no_meta.pop()
        vertical = not vertical
        print("Toggled vertical view to %s." % (on_off[vertical]))
        print_cards()
        return
    # mostly meta commands above here. Keep them there.
    preverified = 0
    if len(name) == 2:
        n1 = ord(name[0])
        n2 = ord(name[1])
        if (n1 > 96) and (n1 < 101):
            if (n2 > 96) and (n2 < 101):
                if n1 == n2:
                    print("Assuming you meant to do something with " + name[0] + ".")
                    name = name[0]
                elif spares[n1 - 97] > 0 and spares[n2 - 97] > 0:
                    cmd_no_meta.pop()
                    print("Neither cell is empty, though shuffling does nothing.")
                    return
                elif spares[n1 - 97] == 0 and spares[n2 - 97] == 0:
                    cmd_no_meta.pop()
                    print("Both cells are empty, so this does nothing.")
                    return
                else:
                    cmd_no_meta.pop()
                    print('Shuffling between empty squares does nothing, so I\'ll just pass here.')
                    return
    if len(name) == 1:
        if name.isdigit():
            i = int(name)
            if i > 8 or i < 1:
                print('Need 1-8.')
                return
            if len(elements[i]) is 0:
                cmd_no_meta.pop()
                print('Acting on an empty row.')
                return
            if any_doable_limit(i):
                name = name + str(any_doable_limit(i))
            elif any_doable(i, 0):
                name = name + str(any_doable(i, 0))
            elif chains(i) > 1 and can_dump(i):
                if chains(i) == len(elements[i]) and not cmd_churn:
                    shufwarn()
                    return
                name = name + str(can_dump(i))
                preverified = 1
            elif chains(i) == 1 and spare_used() < 4:
                name = name + "e"
            elif first_empty_row() and spare_used() == 4:
                if doable(i, first_empty_row(), 0) == len(elements[i]):
                    shufwarn()
                    return
                name = name + str(first_empty_row())
            elif any_doable(i, 1) and chains(i) < len(elements[i]):
                name = name + str(any_doable(i, 1))
            else:
                name = name + 'e'
            if should_print():
                print("New implied command %s." % name)
        elif 101 > ord(name[0]) > 96:
            if first_matchable_row(spares[ord(name[0]) - 97]) > 0:
                name = name + str(first_matchable_row(spares[ord(name[0]) - 97]))
            elif first_empty_row() > 0:
                name = name + str(first_empty_row())
            else:
                cmd_no_meta.pop()
                print('No empty row/column to drop from spares.')
                return
        else:
            cmd_no_meta.pop()
            print("Unknown 1-letter command.")
            return
    # two letter commands below here.
    if len(name) > 2:
        got_reversed = 0
        old_moves = len(move_list)
        if len(name) == 3 and name.isdigit:  # special case for reversing a move e.g. 64 46 can become 646
            if name[0] == name[2]:
                read_cmd(name[0] + name[1])
                read_cmd(name[1] + name[0])
                return
        if name.isdigit():  # for, say ,6873 to move 73 83 63
            got_reversed = 1
            cmd_churn = not chain_show_all
            old_turns = len(move_list)
            for jj in reversed(range(0, len(name) - 1)):
                if not won_this_cmd:
                    if name[jj] != name[jj + 1]:
                        temp = name[jj] + name[len(name) - 1]
                        print("Moving " + temp)
                        read_cmd(name[jj] + name[len(name) - 1])
            cmd_churn = False
            if len(move_list) > old_turns and not chain_show_all:
                print_cards()
            if name.isdigit() and won_this_cmd is False:
                print(
                    'Chained ' + str(len(move_list) - old_moves) + ' of ' + str(len(name) - 1) + ' moves successfully.')
        if got_reversed == 0:
            print('Only 2 chars per command.')
            cmd_no_meta.pop()
        return
    if len(name) < 2:
        print('Must have 2 chars per command, unless you are willing to use an implied command.')
        cmd_no_meta.pop()
        return
    if name[0] == 'r' or name[1] == 'r':
        tofound = name.replace("r", "")
        temprow = -1
        tempspare = -1
        if tofound.isdigit():
            temprow = int(tofound)
        elif (ord(tofound) > 96) and (ord(tofound) < 101):
            tempspare = ord(tofound) - 97
        else:
            print("1-8 a-d are needed with R, or (nothing) tries to force everything.")
            cmd_no_meta.pop()
            return
        if temprow > -1:
            if temprow > 8 or temprow < 1:
                print('Not a valid row.')
                cmd_no_meta.pop()
                return
            if len(elements[temprow]) == 0:
                print('Empty row.')
                cmd_no_meta.pop()
                return
            if foundable(elements[temprow][len(elements[temprow]) - 1]):
                found[(elements[temprow][len(elements[temprow]) - 1] - 1) // 13] += 1
                elements[temprow].pop()
                if not in_undo:
                    move_list.append(name)
                slip_under()
                check_found()
                reshuf(-1)
                print_cards()
                return
            print('Sorry, found nothing.')
            cmd_no_meta.pop()
            return
        if tempspare > -1:
            if foundable(spares[tempspare]):
                found[(spares[tempspare] - 1) // 13] += 1
                spares[tempspare] = 0
                print('Moving from spares.')
                if not in_undo:
                    move_list.append(name)
                check_again = True
                while check_again:
                    check_again = False
                    check_again |= check_found()
                    if force == 0:
                        check_again |= reshuf(-1)
                    pass
                check_found()
                reshuf(-1)
                print_cards()
            else:
                print('Can\'t move from spares.')  # /? 3s onto 2s with nothing else, all filled
                cmd_no_meta.pop()
            return
        print('Must move 1-8 or a-d.')
        cmd_no_meta.pop()
        return
    if len(name) == 2 and (name[0] == 'p' or name[1] == 'p'):
        q2 = (name.replace("p", ""))
        if not q2.isdigit():
            print("p command requires a digit.")
            cmd_no_meta.pop()
            return
        if rip_up(int(q2)):
            cmd_churn = False
            print_cards()
            print_found()
        else:
            cmd_churn = False
        return
    if name[0].isdigit() and name[1].isdigit():
        t1 = int(name[0])
        t2 = int(name[1])
        if t1 == t2:
            print('Moving a row to itself does nothing.')
            cmd_no_meta.pop()
            return
        if t1 < 1 or t2 < 1 or t1 > 8 or t2 > 8:
            print("Need digits from 1-8.")
            cmd_no_meta.pop()
            return  # don't put anything above this
        if len(elements[t1]) == 0 and not in_undo:
            print('Nothing to move from.')
            cmd_no_meta.pop()
            return
        if len(elements[t2]) == 0:
            if chains(t1) == len(elements[t1]) and not cmd_churn and force == 0 and only_move == 0:
                cmd_no_meta.pop()
                shufwarn()
                return
        temp_doab = doable(t1, t2, 1 - preverified)
        if temp_doab == -1:
            if not cmd_churn:
                print('Not enough space.')
                cmd_no_meta.pop()
            return
        if temp_doab == 0:
            if in_undo:
                # print "Move", str(undo_idx), "(", this_cmd, t1, t2, preverified, ") seems to have gone wrong. Use ua."
                if undo_idx == 15:
                    print_cards()
                    exit()
            else:
                print('Those cards don\'t match up.')
                cmd_no_meta.pop()
            return
        oldchain = chains(t1)
        shiftcards(t1, t2, temp_doab)
        if not in_undo:
            if temp_doab < oldchain and len(elements[t2]) == 0:
                move_list.append(str(t1) + str(t2) + "-" + str(temp_doab))
            elif only_move > 0:
                move_list.append(name + "-" + str(only_move))
            else:
                move_list.append(prefix + name)
        check_again = True
        while check_again:
            check_again = False
            check_again |= check_found()
            if force == 0:
                check_again |= reshuf(-1)
            check_again |= slip_under()
            pass
        print_cards()
        return
    if (ord(name[0]) > 96) and (ord(name[0]) < 101):  # a1 moves
        my_spare = ord(name[0]) - 97
        if spares[my_spare] == 0:
            print('Nothing in slot %d.' % (my_spare + 1))
            cmd_no_meta.pop()
            return
        if not name[1].isdigit():
            print('Second letter not recognized.')
            cmd_no_meta.pop()
            return
        my_row = int(name[1])
        if my_row < 1 or my_row > 8:
            print('To row must be between 1 and 8.')
            cmd_no_meta.pop()
            return
        if (len(elements[my_row]) == 0) or (can_put(spares[my_spare], elements[my_row][len(elements[my_row]) - 1])):
            elements[my_row].append(spares[my_spare])
            spares[my_spare] = 0
            if not in_undo:
                move_list.append(name)
            reshuf(-1)
            slip_under()
            check_found()
            print_cards()
            return
        print(
             "Can't put%s on%s." % (to_card_x(spares[my_spare]),
                                    to_card_x(elements[my_row][len(elements[my_row]) - 1])))
        cmd_no_meta.pop()
        return
    if (ord(name[1]) > 96) and (ord(name[1]) < 102):  # 1a moves, but also 1e can be A Thing
        if not name[0].isdigit():
            print('First letter not recognized as a digit.')
            return
        my_to_spare = first_empty_spare()
        if my_to_spare == -1:
            if not cmd_churn:
                print('Nothing empty to move to. To which to move.')
                cmd_no_meta.pop()
            return
        if name[1] != 'e':
            my_to_spare = ord(name[1]) - 97
        my_row = int(name[0])
        if my_row < 1 or my_row > 8:
            print('From row must be between 1 and 8.')
            cmd_no_meta.pop()
            return
        if len(elements[my_row]) == 0:
            print('Empty from-row.')
            cmd_no_meta.pop()
            return
        if spares[my_to_spare] > 0:
            my_first_empty = first_empty_row()
            if my_first_empty > 0:
                my_row = int(name[0])
                row_idx = len(elements[my_row]) - 1
                got_one = can_put(elements[my_row][row_idx], spares[my_to_spare])
                while row_idx > 0 and (
                                      can_put(elements[my_row][row_idx], spares[my_to_spare]) or
                                      can_put(elements[my_row][row_idx], elements[my_row][row_idx - 1])):
                    row_idx = row_idx - 1
                    got_one = True
                if got_one is True:
                    read_cmd(name[1] + str(my_first_empty))
                    read_cmd(name[0] + str(my_first_empty))
                    return
            for temp in range(0, 4):
                if spares[(my_to_spare + temp) % 4] <= 0:
                    print("Spare %d already filled, picking %d instead"
                          % (my_to_spare + 1, (my_to_spare + temp) % 4 + 1))
                    my_to_spare += temp
                    my_to_spare %= 4
                    break
            if spares[my_to_spare] > 0:
                print("Oops, I somehow see all-full and not all full at the same time.")
                cmd_no_meta.pop()
                return
        spares[my_to_spare] = elements[my_row].pop()
        if not in_undo:
            move_list.append(name)
        temp_move_size = -1
        while temp_move_size < len(move_list):
            temp_move_size = len(move_list)
            temp_row_size = len(elements[my_row])
            check_found()
            slip_under()
            if reshuf(my_to_spare) or len(elements[my_row]) < temp_row_size:
                reshuf(-1)
        print_cards()
        return
    print(name + ' not recognized, displaying usage.')
    cmd_no_meta.pop()
    usage_game()


# start main program

if disallow_write_source and os.access(__file__, os.W_OK):
    print("Source file should not have write access outside of the game. attrib +R " + __file__ + 
          " or chmod 333 to get things going.")
    exit()
    # zap above to debug

read_opts()

# note that the Cmd line overrides what is in the options file
parse_cmd_line()

if time_matters and os.path.exists(time_file) and os.stat(time_file).st_size > 0:
    read_time_file()

if annoying_nudge:
    pwd = input("Type TIME WASTING AM I, in reverse word order, in here.\n")
    pwd = pwd.strip()
    # if pwd != "i am wasting time":
    if pwd != "I aM wAsTiNg TiMe":
        if pwd.lower() == "i am wasting time":
            print("Remember to put it in alternate caps case! I did this on purpose, to make it that much harder.")
            exit()
        print("Type I am wasting time, or you can't play.")
        exit()

open_lock_file()

init_side(0)
init_cards()
print_cards()

while win == 0:
    read_cmd('')
