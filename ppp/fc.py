######################################
## fc.py
##
## no frills Python Freecell game
##
## this deliberately blocks me from playing. If you just want to, replace the variables below as necessary.
##
## 1) time_matters = 86400 2) deliberateNuisanceRows = 3 3) deliberateNuisanceIncrease = 2
## 4) annoyingNudge = False (set to 0 or false)

import re
import sys
import os
from random import shuffle, randint
import time
import traceback
import configparser
import argparse
from math import sqrt

## need vc14 for below to work
## from gmpy import invert

config_opt = configparser.SafeConfigParser()
config_time = configparser.SafeConfigParser()

opt_file = "fcopt.txt"
save_file = "fcsav.txt"
win_file = "fcwins.txt"
time_file = "fctime.txt"
lockfile = "fclock.txt"

onOff = ['off', 'on']

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

top = ['CL', 'di', 'SP', 'he']
btm = ['UB', 'am', 'AD', 'ar']

moveList = []

win = 0

total_undo = 0
total_reset = 0

cmd_churn = False
in_undo = False

wonThisCmd = False

lastReset = 0
startTime = 0

## time before next play variables

time_matters = 1
nagDelay = 86400  # set this to zero if you don't want to restrict the games you can play
minDelay = 70000  # if we can cheat one time
highTime = 0
maxDelay = 0
curGames = 0
maxGames = 5

## options to define. How to do better?
chainShowAll = False
vertical = True
dblSzCards = False
autoReshuf = True
savePosition = False
saveOnWin = False
quickBail = False
## this is an experimental feature to annoy me
deliberateNuisanceRows = 3
deliberateNuisanceIncrease = 2
## this can't be toggled in game but you can beforehand
annoyingNudge = True

## easy mode = A/2 on top. Cheat index tells how many cards of each suit are sorted to the bottom.
cheatIndex = 0

## making the game extra secure, not playing 2 at once or tinkering with timing file
haveLockFile = True
disallowWriteSource = True

lastScore = 0
highlight = 0

onlymove = 0

trackUndo = 0

breakMacro = 0

undo_idx = 0

debug = False

cmdList = []
cmdNoMeta = []

backup = []
elements = [[], [], [], [], [], [], [], [], []]

name = ""


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
        print ("That won't make progress. F(##) or ##-# let you move part of an in-order stack over.")


def dump_total(q):  # Negative q means you print. Mostly for debugging.
    retval = 0
    do_print = False
    if q < 0:
        q = 0 - q
        do_print = True
    for z in range(0, len(elements[q])):
        if foundable(elements[q][z]):
            if do_print:
                print (tocard(elements[q][z]), elements[q][z], 'foundable')
            retval += 1
            if elements[q][z] % 13 == 2:  # aces/2's get a special bonus
                retval += 1
            if elements[q][z] % 13 == 1:  # aces/2's get a special bonus
                retval += 2
        if nexties(elements[q][z]):  # not an elif as foundable deserves an extra point
            retval += 1
            if do_print:
                print (tocard(elements[q][z]), elements[q][z], 'nexties')
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
        print ("Column/row needs to be 1-8.")
        return False
    if len(elements[q]) == 0:
        print ("Already no elements.")
        return True
    go_again = 1
    global cmd_churn
    cmd_churn = True
    movesize = len(moveList)
    max_run = 0
    while go_again == 1 and len(elements[q]) > 0 and max_run < 25 and not in_order(q):
        should_reshuf = True
        if len(elements[q]) > 1:
            if can_put(elements[q][len(elements[q]) - 1], elements[q][len(elements[q]) - 2]):
                should_reshuf = False
        max_run += 1
        go_again = 0
        temp_ary_size = len(moveList)
        read_cmd(str(q))
        if len(moveList) > temp_ary_size:
            go_again = 1
            made_one = True
        checkFound()
        if should_reshuf:
            reshuf(-1)
        forceFoundation()
        slipUnder()
    if max_run == 25:
        print ("Oops potential hang at " + str(q))
    checkFound()
    if len(moveList) == movesize:
        print ("Nothing moved.")
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
    if chains(mycol) > maxmove() / 2:
        return 0
    for tocol in range(1, 9):
        if len(elements[tocol]) == 0:
            return tocol
    return 0


def reshuf(xyz):  # this reshuffles the empty cards
    if not autoReshuf:
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
                            # stupid bug here with if we change autoReshuf in the middle of the game
                            # solution is to create "ar(x)(y)" which only triggers if autoReshuf = 0
    shifties = 0
    if force == 1 or onlymove > 0:
        return retval
    while auto_shift():
        shifties += 1
        if shifties == 12:
            print ('Oops, broke an infinite loop.')
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
                        print ("Autoshifted " + str(i) + " to " + str(j) + ".")
                    shiftcards(i, j, len(elements[i]))
                    return True
    return False


def in_order(rowNum):
    if len(elements[rowNum]) < 2:
        return 0
    for i in range(1, len(elements[rowNum])):
        if not can_put(elements[rowNum][i], elements[rowNum][i - 1]):
            return 0
    return 1


def chainTotal():
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


def spareUsed():
    retval = 0
    for i in range(0, 4):
        if spares[i]:
            retval += 1
    return retval


def firstEmptyRow():
    for i in range(1, 9):
        if len(elements[i]) == 0:
            return i
    return 0


def firstMatchableRow(cardval):
    for i in range(1, 9):
        if len(elements[i]) > 0:
            if can_put(cardval, elements[i][len(elements[i]) - 1]):
                return i
    return 0


def openLockFile():
    if os.path.exists(lockfile):
        print ('There seems to be another game running. Close it first, or if necessary, delete', lockfile)
        exit()
    f = open(lockfile, 'w')
    f.write('This is a lockfile')
    f.close()
    os.system("attrib +r " + lockfile)


def closeLockFile():
    os.system("attrib -r " + lockfile)
    os.remove(lockfile)
    if os.path.exists(lockfile):
        print ('I wasn\'t able to delete', lockfile)


def parseCmdLine():
    global vertical
    global debug
    global saveOnWin
    global cheatIndex
    global annoyingNudge
    global quickBail
    global nagDelay
    global maxGames
    openAnyFile = False
    parser = argparse.ArgumentParser(description='Play FreeCell.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-o', '--opt_file', action='store_true', dest='opt_file', help='open options file')
    parser.add_argument('-l', '--loadsaveFile', action='store_true', dest='save_file', help='open save file')
    parser.add_argument('-p', '--pythonfile', action='store_true', dest='pythonfile', help='open python source file')
    parser.add_argument('-t', '--textfile', action='store_true', dest='time_file', help='open text/time file\n\n')
    parser.add_argument('-r', '--resettime', action='store_true', dest='resettime', help='open text/time file\n\n')
    parser.add_argument('--getridofthetimewastenag', action='store_false', dest='annoyingNudge')
    parser.add_argument('-c', '--cheatindex', action='store', dest='cheatIndex', help='specify cheat index 1-13',
                        type=int)
    parser.add_argument('-e', '--easy', action='store_true', dest='easy', help='easy mode on (A and 2 on top)\n\n')
    parser.add_argument('-d', '--debug', action='store_true', dest='debugOn', help='debug on')
    parser.add_argument('-nd', '--nodebug', action='store_true', dest='debugOff', help='debug off')
    parser.add_argument('-v', '--vertical', action='store_true', dest='verticalOn', help='vertical on')
    parser.add_argument('-nv', '--novertical', action='store_true', dest='verticalOff', help='vertical off')
    parser.add_argument('-s', '--saveonwin', action='store_true', dest='saveOnWinOn', help='save-on-win on')
    parser.add_argument('-ns', '--nosaveonwin', action='store_true', dest='saveOnWinOff', help='save-on-win off')
    parser.add_argument('-q', '--quickbail', action='store_true', dest='quickBail', help='quick bail after one win')
    parser.add_argument("--waittilnext", dest='nagDelay', type=int, help='adjust nagDelay')
    parser.add_argument('-mg', '--maxgames', nargs=1, dest='maxGames', type=int, help='adjust maxGames')
    args = parser.parse_args()
    # let's see if we tried to open any files, first
    if args.resettime is True:
        print ("Resetting the time file", time_file)
        writeTimeFile()
        exit()
    if args.opt_file is True:
        os.system(opt_file)
        openAnyFile = True
    if args.save_file is True:
        os.system("fcsav.txt")
        openAnyFile = True
    if args.pythonfile is True:
        os.system("\"c:\\Program Files (x86)\\Notepad++\\notepad++\" fc.py")
        openAnyFile = True
    if args.time_file is True:
        os.system("fctime.txt")
        openAnyFile = True
    if openAnyFile:
        exit()
    # then let's see about the annoying nudge and cheating
    if args.annoyingNudge is not None:
        annoyingNudge = args.annoyingNudge
    if args.cheatIndex is not None:
        if args.cheatIndex < 1:
            print("Too low. The cheat index must be between 1 and 13.")
            sys.exit()
        elif args.cheatIndex > 13:
            print("Too high. The cheat index must be between 1 and 13.")
            sys.exit()
        cheatIndex = args.cheatIndex
    elif args.easy is True:
        cheatIndex = 2
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
    if args.saveOnWinOn:
        if args.saveOnWinOff:
            print("Save both ways set both ways on command line. Bailing.")
            exit()
        saveOnWin = True
    if args.saveOnWinOff:
        saveOnWin = False
    if args.quickBail:
        quickBail = True
    if args.nagDelay and args.nagDelay > 0:
        if args.nagDelay < minDelay:
            print('Too soon, need >', minDelay)
            exit()
        if args.nagDelay > nagDelay:
            print("Whoah, going above the default!")
        nagDelay = args.nagDelay
    if args.maxGames and args.maxGames > 0:
            maxGames = args.maxGames
    return


def readTimeFile():
    global nagDelay
    global maxDelay
    if os.access(time_file, os.W_OK):
        print ("Time file should not have write access outside of the game. attrib +R " + time_file + \
              " or chmod 333 to get things going.")
        exit()
    if not os.path.isfile(time_file):
        print ("You need to create fctime.txt with (sample)\n[Section1]\nlasttime = 1491562931" \
              "\nmaxdelay = 0\nmodulus = 178067\nremainder = 73739.")
        exit()
    config_time.read(time_file)
    modulus = modinv(config_time.getint('Section1', 'modulus'), 200003)
    remainder = config_time.getint('Section1', 'remainder')
    maxDelay = config_time.getint('Section1', 'maxdelay')
    lasttime = config_time.getint('Section1', 'lasttime')
    curtime = time.time()
    delta = int(curtime - lasttime)
    if delta < nagDelay:
        print('Only', str(delta), 'seconds elapsed of', nagDelay)
        exit()
    if delta > 90000000:
        print("Save file probably edited to start playing a bit early. I'm not going to judge.")
    elif delta > maxDelay:
        print('New high delay', delta, 'old was', maxDelay)
        maxDelay = delta
    else:
        print('Delay', delta, 'did not exceed record of', maxDelay)
    if lasttime % modulus != remainder:
        print ("Save file is corrupted. If you need to reset it, choose a modulus of 125000 and do things manually.")
        print (lasttime, modulus, remainder, lasttime % modulus)
        exit()
    if modulus < 100001 or modulus > 199999:
        print ("Modulus is not in range in fctime.txt.")
        exit()
    if not is_prime(modulus):
        print ("Modulus", modulus, "is not prime.")
        exit()
    return


def writeTimeFile():
    os.system("attrib -r " + time_file)
    if not config_time.has_section('Section1'):
        config_time.add_section("Section1")
    lasttime = int(time.time())
    modulus = rand_prime()
    remainder = lasttime % modulus
    global maxDelay
    config_time.set('Section1', 'modulus', str(modinv(modulus, 200003)))  # 200003 is prime. I checked!
    config_time.set('Section1', 'remainder', str(remainder))
    config_time.set('Section1', 'maxdelay', str(maxDelay))
    config_time.set('Section1', 'lasttime', str(lasttime))
    with open(time_file, 'w') as configfile:
        config_time.write(configfile)
    os.system("attrib +r " + time_file)
    return


def readOpts():
    if not os.path.isfile(opt_file):
        print ("No", opt_file, "so using default options.")
        return
    config_opt.read(opt_file)
    global vertical
    vertical = config_opt.getboolean('Section1', 'vertical')
    global autoReshuf
    autoReshuf = config_opt.getboolean('Section1', 'autoReshuf')
    global dblSzCards
    dblSzCards = config_opt.getboolean('Section1', 'dblSzCards')
    global saveOnWin
    saveOnWin = config_opt.getboolean('Section1', 'saveOnWin')
    global savePosition
    savePosition = config_opt.getboolean('Section1', 'savePosition')
    global annoyingNudge
    annoyingNudge = config_opt.getboolean('Section1', 'annoyingNudge')
    global chainShowAll
    chainShowAll = config_opt.getboolean('Section1', 'chainShowAll')
    return


def sendOpts():
    if not config_opt.has_section('Section1'):
        config_opt.add_section("Section1")
    config_opt.set('Section1', 'vertical', str(vertical))
    config_opt.set('Section1', 'autoReshuf', str(autoReshuf))
    config_opt.set('Section1', 'dblSzCards', str(dblSzCards))
    config_opt.set('Section1', 'saveOnWin', str(saveOnWin))
    config_opt.set('Section1', 'savePosition', str(savePosition))
    config_opt.set('Section1', 'annoyingNudge', str(annoyingNudge))
    config_opt.set('Section1', 'annoyingNudge', str(chainShowAll))
    with open(opt_file, 'w') as configfile:
        config_opt.write(configfile)
    print("Saved options.")
    return


def initSide(inGameReset):
    global spares
    spares = [0, 0, 0, 0]
    global found
    found = [0, 0, 0, 0]
    global highlight
    global startTime
    global lastReset
    highlight = 0
    if not in_undo:
        lastReset = time.time()
        if inGameReset != 1:
            startTime = lastReset
        global win
        win = 0
        global moveList
        moveList = []
        global cmdList
        cmdList = []
        global cmdNoMeta
        cmdNoMeta = []
    global breakMacro
    breakMacro = 0


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


def checkFound():
    retval = False
    needToCheck = 1
    global totalFoundThisTime
    global cardlist
    if not cmd_churn:
        totalFoundThisTime = 0
        cardlist = ''
    while needToCheck:
        needToCheck = 0
        for y in range(1, 9):
            if len(elements[y]) > 0:
                while elements[y][len(elements[y]) - 1] % 13 == (
                            1 + found[(elements[y][len(elements[y]) - 1] - 1) // 13]) % 13:
                    basesuit = (elements[y][len(elements[y]) - 1] - 1) // 13
                    if found[(basesuit + 1) % 4] < found[basesuit] - 1:
                        break
                    if found[(basesuit + 3) % 4] < found[basesuit] - 1:
                        break
                    needToCheck = 1
                    retval = True
                    totalFoundThisTime += 1
                    found[(elements[y][len(elements[y]) - 1] - 1) // 13] = found[(elements[y][len(
                        elements[y]) - 1] - 1) // 13] + 1
                    cardlist = cardlist + tocardX(elements[y][len(elements[y]) - 1])
                    elements[y].pop()
                    if len(elements[y]) == 0:
                        break
        for y in range(0, 4):
            # print 'checking ',y,tocard(spares[y])
            if spares[y] > 0:
                if (spares[y] - 1) % 13 == found[(spares[y] - 1) // 13]:
                    sparesuit = (spares[y] - 1) // 13
                    if debug:
                        print ('position', y, 'suit', suits[(spares[y] - 1) / 13], 'card', tocard(spares[y]))
                    if found[(sparesuit + 3) % 4] < found[sparesuit] - 1:
                        continue
                    if found[(sparesuit + 1) % 4] < found[sparesuit] - 1:
                        continue
                    cardlist = cardlist + tocardX(spares[y])
                    totalFoundThisTime += 1
                    found[(spares[y] - 1) // 13] += 1
                    spares[y] = 0
                    needToCheck = 1
                    retval = True
    # print (str(totalFoundThisTime) + " undo " + str(in_undo) + " churn " + str(cmd_churn) + " " + str(should_print()))
    # traceback.print_stack()
    printFound()
    return retval


def printFound():
    global totalFoundThisTime
    global cardlist
    if totalFoundThisTime > 0 and should_print():
        sys.stdout.write(
            str(totalFoundThisTime) + ' card' + plur(totalFoundThisTime) + ' safely to foundation:' + cardlist + '\n')
        totalFoundThisTime = 0
        cardlist = ''


def forceFoundation():
    global in_undo
    checkAgain = 1
    forceStr = ""
    global cardlist
    global totalFoundThisTime
    while checkAgain:
        checkAgain = 0
        for row in range(1, 9):
            if len(elements[row]) > 0:
                if foundable(elements[row][len(elements[row]) - 1]) == 1:
                    found[(elements[row][len(elements[row]) - 1] - 1) // 13] += 1
                    forceStr = forceStr + tocardX(elements[row][len(elements[row]) - 1])
                    if not in_undo:
                        cardlist = cardlist + tocardX(elements[row][len(elements[row]) - 1])
                        totalFoundThisTime += 1
                    elements[row].pop()
                    checkAgain = 1
        for xx in range(0, 4):
            if spares[xx]:
                # print ("Checking" + tocardX(spares[xx]))
                if foundable(spares[xx]):
                    forceStr = forceStr + tocardX(spares[xx])
                    if not in_undo:
                        cardlist = cardlist + tocardX(spares[xx])
                        totalFoundThisTime += 1
                    found[(spares[xx] - 1) // 13] += 1
                    spares[xx] = 0
                    checkAgain = 1
    if forceStr:
        if not in_undo:
            moveList.append("r")
            print_cond("Sending all to foundation.")
            print_cond("Forced" + forceStr)
        reshuf(-1)
        checkFound()
        printCards()
    else:
        print_cond("Nothing to force to foundation.")
    return


def checkWin():
    for y in range(0, 4):
        # print y,found[y]
        if found[y] != 13:
            return 0
    checkWinning()


def initCards():
    x = []
    global elements
    if cheatIndex > 0:
        x = list(range(cheatIndex + 1, 14)) + list(range(cheatIndex + 14, 27)) + list(
            range(cheatIndex + 27, 40)) + list(range(cheatIndex + 40, 53))
        shuffle(x)
        for y in reversed(range(1, cheatIndex + 1)):
            x[:0] = [y, y + 13, y + 26, y + 39]
    else:
        x = list(range(1, 53))
        shuffle(x)
    for z in range(0, 52):
        elements[z % 8 + 1].append(x.pop())
    global backup
    backup = [row[:] for row in elements]


def tocard(cardnum):
    if cardnum == 0:
        return '---'
    temp = cardnum - 1
    retval = '' + cards[temp % 13] + suits[temp // 13]
    return retval


def tocardX(cnum):
    if cnum % 13 == 10:
        return ' ' + tocard(cnum)
    return tocard(cnum)


def printCards():
    if cmd_churn:
        return
    if in_undo:
        return
    if sum(found) == 52:
        if not checkWinning():
            return
    if vertical:
        printVertical()
    else:
        printHorizontal()


def checkWinning():
    global input
    try:
        input = raw_input
    except NameError:
        pass
    global cmd_churn
    # print ("Churn now false (checkWinning).")
    cmd_churn = False
    printFound()
    global startTime
    global lastReset
    if startTime != -1:
        curTime = time.time()
        timeTaken = curTime - startTime
        print ("%.2f seconds taken." % timeTaken)
        if lastReset > startTime:
            print ("%.2f seconds taken since last reset." % (curTime - lastReset))
    else:
        print ("No time data kept for loaded game.")
    global total_reset
    global total_undo
    if total_reset > 0:
        print ("%d reset used." % total_reset)
    if total_undo > 0:
        print ("%d undo used." % total_undo)
    if total_undo == -1:
        print ("No undo data from loaded game.")
    if saveOnWin:
        with open(win_file, "a") as myfile:
            winstring = time.strftime("sw=%Y-%m-%d-%H-%M-%S", time.localtime())
            myfile.write(winstring)
            myfile.write("\n#START NEW SAVED POSITION\n")
            global backup
            for i in range(1, 9):
                myfile.write(' '.join(str(x) for x in backup[i]) + "\n")
        print ("Saved " + winstring)
    global breakMacro
    breakMacro = 1
    if maxGames > 0:
        global curGames
        curGames = curGames + 1
        print ('Won', curGames, 'of', maxGames, 'so far.')
        if curGames == maxGames:
            print ("Well, that's it. Looks like you've played all your games.")
            goBye()
    global wonThisCmd
    wonThisCmd = True
    while True:
        finish = input("You win in %d commands (%d including extraneous) and %d moves! Play again (Y/N, U to undo)?" % (
            len(cmdNoMeta), len(cmdList), len(moveList))).lower()
        finish = re.sub(r'^ *', '', finish)
        if len(finish) > 0:
            if finish[0] == 'n' or finish[0] == 'q':
                goBye()
            if finish[0] == 'y':
                if quickBail:
                    print ("Oops! Quick bailing.")
                    goBye()
                global deliberateNuisanceRows
                if deliberateNuisanceRows > 0:
                    deliberateNuisanceRows += deliberateNuisanceIncrease
                initCards()
                initSide(0)
                total_undo = 0
                total_reset = 0
                return 1
            if finish[0] == 'u':
                curGames -= 1
                cmdNoMeta.pop()
                global in_undo
                in_undo = True
                undo_moves(1)
                in_undo = False
                return 0
        print ("Y or N (or U to undo). Case insensitive, cuz I'm a sensitive guy.")


# this detects how long a chain is, e.g. how many in a row
# 10d-9s-8d-7s is 4 not 3
def chains(myrow):
    if len(elements[myrow]) == 0:
        return 0
    retval = 1
    mytemp = len(elements[myrow]) - 1
    while mytemp > 0:
        if can_put(elements[myrow][mytemp], elements[myrow][mytemp - 1]):
            retval += 1
            mytemp = mytemp - 1
        else:
            return retval
    return retval


def onedig(y):
    if y < 10:
        return str(y)
    return "+"


def printVertical():
    count = 0
    for y in range(1, 9):
        if chain_nope(y) == 0:
            sys.stdout.write(' *' + onedig(chains(y)) + '*')
        else:
            sys.stdout.write(' ' + onedig(chains(y)) + '/' + str(chain_nope(y)))
        if dblSzCards:
            sys.stdout.write(' ')
    print ("")
    for y in range(1, 9):
        sys.stdout.write(' ' + str(y) + ': ')
        if dblSzCards:
            sys.stdout.write(' ')
    print ("")
    oneMoreTry = 1
    while oneMoreTry:
        thisline = ''
        secondLine = ''
        oneMoreTry = 0
        for y in range(1, 9):
            if len(elements[y]) > count:
                oneMoreTry = 1
                if dblSzCards:
                    temp = str(tocard(elements[y][count]))
                    if tocard(elements[y][count])[0] == ' ':
                        thisline += temp[1]
                        secondLine += temp[0]
                    else:
                        thisline += temp[0]
                        secondLine += temp[1]
                    thisline += top[(elements[y][count] - 1) // 13]
                    secondLine += btm[(elements[y][count] - 1) // 13] + ' '
                else:
                    thisline += str(tocard(elements[y][count]))
                if foundable(elements[y][count]):
                    if nexties(elements[y][count]):
                        thisline += '!'
                    else:
                        thisline += '*'
                elif highlight and (((elements[y][count] - 1) % 13) == highlight - 1):
                    thisline += '+'
                else:
                    thisline += ' '
                if dblSzCards:
                    thisline += ' '
                    secondLine += ' '
            else:
                thisline += '    '
                if dblSzCards:
                    thisline += ' '
                    secondLine += '     '
        if oneMoreTry:
            print (thisline)
            if secondLine:
                print (secondLine)
        count += 1
    printOthers()
    # traceback.print_stack()


def printHorizontal():
    for y in range(1, 9):
        sys.stdout.write(str(y) + ':')
        for z in elements[y]:
            sys.stdout.write(' ' + tocard(z))
        print
    printOthers()


def org_it(myList):
    globbed = 1
    while globbed:
        globbed = 0
        for x1 in range(0, len(myList)):
            for x2 in range(0, len(myList)):
                if globbed == 0:
                    if myList[x1][0] == myList[x2][-1]:
                        globbed = 1
                        temp = myList[x2] + myList[x1][1:]
                        del myList[x2]
                        if x1 > x2:
                            del myList[x1 - 1]
                        else:
                            del myList[x1]
                        myList.insert(0, temp)
    return ' ' + ' '.join(myList)


def botcard(mycol):
    return elements[mycol][len(elements[mycol]) - 1]


def automove():
    mincard = 0
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
                    mincand = botcard(z1) % 13
                    if mincand > mincard:
                        mincard = mincand
                        fromcand = z1
                        tocand = z2
    if fromcand > 0:
        myauto = str(fromcand) + str(tocand)
        print ("Auto moved " + myauto)
        read_cmd(myauto)
        return 1
    return 0


def printOthers():
    checkWin()
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
        print ("Not enough room: " + str(wackmove))
    print ("Possible moves:" + org_it(coolmoves) + foundmove + latmove + " (%d max shift" % (maxmove()) + (
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
            print ("Uh oh. You\'re probably lost.")
        else:
            print ("You may have to dump stuff in the foundation.")
    sys.stdout.write('Empty slots: ')
    for y in range(0, 4):
        sys.stdout.write(tocard(spares[y]))
        for z in range(1, 9):
            if len(elements[z]) and can_put(spares[y], elements[z][len(elements[z]) - 1]):
                sys.stdout.write('<')
                break
        if spares[y] > 0 and (spares[y] - 1) % 13 == found[(spares[y] - 1) // 13]:
            sys.stdout.write('*')
        else:
            sys.stdout.write(' ')
    sys.stdout.write('\nFoundation: ')
    foundScore = 0
    for y in [0, 2, 1, 3]:
        foundScore += found[y]
        if found[y] == 0:
            sys.stdout.write(' ---')
        else:
            sys.stdout.write(' ' + tocard(found[y] + y * 13))
    sys.stdout.write(' (' + str(foundScore) + ' point' + plur(foundScore))
    global lastScore
    if lastScore < foundScore:
        sys.stdout.write(', up ' + str(foundScore - lastScore))
    sys.stdout.write(', ' + str(chainTotal()) + ' pairs in order, ' + str(chain_nope_big()) + ' out of order, ' + str(
        chain_nope_each()) + ' cols unordered')
    sys.stdout.write(')\n')
    lastScore = foundScore


def any_doable_limit(ii):
    tempval = 0
    for y in range(1, 9):
        temp2 = doable(ii, y, 0)
        if len(elements[y]) > 0 and 0 < temp2 <= maxmove():
            if chains(ii) == temp2:
                return y
            tempval = y
    return tempval


def anyDoable(ii, emptyOK):
    tempret = 0
    for y in range(1, 9):
        tempval = doable(ii, y, 0)
        if emptyOK or len(elements[y]) > 0:
            if tempval > 0:
                return y
        if len(elements[y]) > 0 and tempval > 0:
            tempret = y
    return tempret


def doable(r1, r2, showDeets):  # return value = # of cards to move. 0 = no match, -1 = asking too much
    fromline = 0
    locmaxmove = maxmove()
    if r1 < 1 or r2 < 1 or r1 > 8 or r2 > 8:
        print ("This shouldn't have happened, but one of the rows is invalid.")
        trackback.print_tb()
        return 0
    global onlymove
    if len(elements[r2]) == 0:
        if len(elements[r1]) == 0:
            if showDeets:
                print ("Empty-empty move.")
            return 0
        if in_order(r1) and onlymove == len(elements[r1]):
            if showDeets:
                print ('OK, moved the already-sorted row, though this doesn\'t really change the game state.')
            return len(elements[r1])
        locmaxmove /= 2
        if showDeets and should_print():
            print ("Only half moves here down to %d" % locmaxmove)
        for n in range(len(elements[r1]) - 1, -1, -1):
            fromline += 1
            # print '1 debug stuff:',tocard(elements[r1][n]),n,fromline
            if n == 0:
                break
            # print '2 debug stuff:',tocard(elements[r1][n]),n,fromline
            if can_put(elements[r1][n], elements[r1][n - 1]) == 0:
                break
                # print '3 debug stuff:',tocard(elements[r1][n]),n,fromline
    else:
        toTopCard = elements[r2][len(elements[r2]) - 1]
        # print str(elements[r2]) + "Row " + str(r2) + " Card " + tocard(toTopCard)
        for n in range(len(elements[r1]) - 1, -1, -1):
            fromline += 1
            if can_put(elements[r1][n], toTopCard):
                break
            if n == 0:
                return 0
            if can_put(elements[r1][n], elements[r1][n - 1]) == 0:
                return 0
    if onlymove > locmaxmove:
        print ("WARNING, %d is greater than the maximum of %d." % (onlymove, locmaxmove))
        onlymove = 0
    if len(elements[r1]) == 0:
        if showDeets:
            print ('Tried to move from empty.')
        return 0
    if onlymove > 0:
        if onlymove < locmaxmove:
            if showDeets:
                if len(elements[r2]) > 0:
                    print ('Can\'t move to that non-empty, even with force.')
                    return -1
                print_cond('Cutting down to ' + str(onlymove))
                return onlymove
        if onlymove < fromline:
            return onlymove
    if fromline > locmaxmove:
        if force == 1:
            if showDeets:
                if len(elements[r2]) > 0:
                    print ('Can\'t move to that non-empty, even with force.')
                    return -1
                print_cond("Cutting down to " + str(locmaxmove))
            return locmaxmove
        global cmd_churn
        if showDeets and not cmd_churn:
            print ("Not enough open. Have %d, need %d" % (locmaxmove, fromline))
        return -1
    return fromline


def maxMoveMod():
    base = 2
    myexp = .5
    for y in range(0, 4):
        if spares[y] == 0:
            base += 1
    for y in range(1, 9):
        if len(elements[y]) == 0:
            myexp *= 2
    return base * myexp


def slipUnder():
    slipProcess = True
    everSlip = False
    global cmd_churn
    while slipProcess:
        fi = firstEmptyRow()
        slipProcess = False
        if fi == 0:
            for i in range(1, 9):
                for j in range(0, 4):
                    if slipProcess is False and (in_order(i) or (len(elements[i]) == 1)) and can_put(elements[i][0],
                                                                                                     spares[j]):
                        # print ("Checking slip under %d %d %d %d %d" % (fi, i, j, elements[i][0], spares[j]))
                        if len(elements[i]) + spareUsed() <= 4:
                            elements[i].insert(0, spares[j])
                            spares[j] = 0
                            slipProcess = True
        else:
            for i in range(1, 9):
                if slipProcess is False and ((len(elements[i]) > 0 and in_order(i)) or (len(elements[i]) == 1)):
                    # print ("%d %d %d %d" % (i, len(elements[i]), in_order(i), slipProcess))
                    for j in range(0, 4):
                        # print ("%d %d %d %d" % (i, j, spares[j], can_put(elements[i][0], spares[j])))
                        if spares[j] > 0 and can_put(elements[i][0], spares[j]):
                            # print ("OK, giving a look %d -> %d | %d %d" % (i, fi, len(elements[i]), maxMoveMod()))
                            if len(elements[i]) <= maxMoveMod():
                                resetChurn = not cmd_churn
                                cmd_churn = True
                                elements[fi].append(spares[j])
                                spares[j] = 0
                                shiftcards(i, fi, len(elements[i]))
                                if resetChurn:
                                    cmd_churn = False
                                slipProcess = True
                                everSlip = True
                                break
    return everSlip


def dumpInfo(x):
    print ("Uh oh, big error avoided")
    print (elements)
    print (backup)
    print (moveList)
    print (cmdList)
    print (cmdNoMeta)
    print ("Spares: " % spares)
    print ("Found: " % found)
    if abs(x) == 2:
        printVertical()
    if x < 0:
        exit()
    return


def shiftcards(r1, r2, amt):
    elements[r2].extend(elements[r1][int(-amt):])
    del elements[r1][int(-amt):]


def usageGame():
    print ('========game moves========')
    print ('r(1-8a-d) sends that card to the foundation. r alone forces everything it can.')
    print ('p(1-8) moves a row as much as you can.')
    print ('p on its own tries to force everything if you\'re near a win.')
    print ('\\ tries all available moves starting with the highest card to match eg 10-9 comes before 7-6.')
    print ('(1-8) attempts a \'smart move\' where the game tries progress, then shifting.')
    print ('(1-8)(1-8) = move a row, standard move. You can also string moves together, or 646 goes back and forth.')
    print ('(1-8a-d) (1-8a-d) move to spares and back.')
    print ('f(1-8)(1-8) forces what you can (eg half of what can change between nonempty rows) onto an empty square.')
    print ('(1-8)(1-8)-(#) forces # cards onto a row, if possible.')
    print ('h slips a card under eg KH in spares would go under an ordered QC-JD.')
    print ('- or = = a full board reset.')
    print ('?/?g ?o ?m games options meta')


def usageOptions():
    print ('========options========')
    print ('v toggles vertical, + toggles card size (only vertical right now).')
    print ('cs toggles chainShowAll e.g. if 823 shows intermediate move.')
    print ('sw/ws saves on win, sp/ps saves position.')
    print ('+ = toggles double size, e = toggle autoshuffle.')
    print ('?/?g ?o ?m games options meta, g is default.')


def usage_meta():
    print ('========meta========')
    print ('l=loads a game, s=saves, lp=load previous/latest saved')
    print ('lo/so loads/saves options.')
    print ('u = undo, u1-u10 undoes that many moves, undo does 11+, tu tracks undo.')
    print ('ua = shows current move/undo array.')
    print ('uc = shows current command list.')
    print ('ux = shows current command list excluding meta-commands.')
    print ('qu quits (q could be typed by accident).')
    print ('? = usage (this).')
    print ('empty command tries basic reshuffling and prints out the cards again.')
    print ('? gives hints: /?g ?o ?m games options meta, g is default.')


def first_empty_spare():
    for i in range(0, 4):
        if spares[i] == 0:
            return i
    return -1


def undo_moves(to_undo):
    if to_undo == 0:
        print('No moves undone.')
        return 0
    global moveList
    global total_undo
    if len(moveList) == 0:
        print ('Nothing to undo.')
        return 0
    global elements
    elements = [row[:] for row in backup]
    global found
    found = [0, 0, 0, 0]
    global spares
    spares = [0, 0, 0, 0]
    for _ in range(0, to_undo):
        moveList.pop()
        if total_undo > -1:
            total_undo += 1
    global in_undo
    in_undo = True
    global undo_idx
    for undo_idx in range(0, len(moveList)):
        read_cmd(str(moveList[undo_idx]))
        if trackUndo == 1:
            in_undo = False
            printCards()
            in_undo = True
    undo_idx = 0
    in_undo = False
    checkFound()
    printCards()
    return 1


def load_game(game_name):
    global time
    global total_undo
    global total_reset
    global startTime
    original = open(save_file, "r")
    startTime = -1
    while True:
        line = original.readline()
        if line.startswith('moves='):
            continue
        if game_name == line.strip():
            for y in range(1, 9):
                line = original.readline().strip()
                elements[y] = [int(i) for i in line.split()]
                backup[y] = [int(i) for i in line.split()]
            global moveList
            templine = original.readline()
            moveList = templine.strip().split() # this is the list of moves
            global cmdList
            global cmdNoMeta
            cmdList = []
            cmdNoMeta = []
            line = original.readline().strip()
            while (re.search("^#end of", line) == False):
                print(line + " read in")
                if re.search("^#cmdNoMeta", line):
                    cmdNoMeta = re.sub("^#cmdNoMeta=", "", line).split(',')
                if re.search("^#cmdList", line):
                    cmdList = re.sub("^#cmdList=", "", line).split(',')
                line = original.readline().strip()
            original.close()
            if len(moveList) > 0:
                if len(cmdNoMeta) == 0:
                    cmdNoMeta = list(moveList)
                if len(cmdList) == 0:
                    cmdList = list(moveList)
            global in_undo
            in_undo = True
            initSide(0)
            global undo_idx
            for undo_idx in range(0, len(moveList)):
                read_cmd(str(moveList[undo_idx]))
                if trackUndo == 1:
                    in_undo = False
                    printCards()
                    in_undo = True
            in_undo = False
            checkFound()
            printCards()
            global totalFoundThisTime
            global cardlist
            totalFoundThisTime = 0
            cardlist = ''
            print ("Successfully loaded " + game_name.replace(r'^.=', ''))
            # this was in unreachable code and is probably wrong but I can check to delete it later (?)
            # total_undo = -1
            # total_reset = -1
            return 1
        if not line:
            break
    print (re.sub(r'^.=', '', game_name) + ' save game not found.')
    original.close()
    return 0


def saveGame(game_name):
    savfi = open(save_file, "r")
    linecount = 0
    for line in savfi:
        linecount += 1
        if line.strip() == game_name:
            print ("Duplicate save game name found at line %d." % linecount)
            return
    savfi.close()
    with open(save_file, "a") as myfile:
        myfile.write(game_name + "\n")
        for y in range(1, 9):
            myfile.write(' '.join(str(x) for x in backup[y]) + "\n")
        myfile.write(' '.join(moveList) + "\n")
        if savePosition:
            for y in range(1, 9):
                myfile.write('# '.join(str(x) for x in elements[y]) + "\n")
        myfile.write("###end of " + game_name + "\n")
        myfile.write("#cmdNoMeta=" + ', '.join(cmdNoMeta) + '\n')
        myfile.write("#cmdList=" + ', '.join(cmdList) + '\n')
    gn2 = game_name.replace(r'^.=', '')
    print ("Successfully saved game as " + gn2)
    return 0


def reverseCard(myCard):
    retVal = 0
    for i in range(0, 5):
        if i == 4:
            return -2
        if re.search(suits[i].lower(), myCard):
            retVal = 13 * i
            break
    for i in range(0, 13):
        if re.search(cards[i].lower(), ' ' + myCard):
            retVal += (i + 1)
            return retVal
    return -1


def cardEval(myCmd):
    ary = re.split('[ ,]', myCmd)
    for word in ary:
        if word == 'e':
            continue
        sys.stdout.write(' ' + str(reverseCard(word)))
    print ("")
    return


def goBye():
    global curGames
    global maxGames
    if curGames * 2 < maxGames:
        print ("Great job, leaving well before you played all you could've.")
    elif curGames < maxGames:
        print ("Good job, leaving before you played all you could've.")
    else:
        print ("Bye!")
    if time_matters:
        writeTimeFile()
    closeLockFile()
    exit()


def read_cmd(thisCmd):
    global debug
    global wonThisCmd
    global cmd_churn
    global vertical
    global dblSzCards
    global autoReshuf
    global elements
    global force
    global trackUndo
    global total_reset
    global saveOnWin
    global savePosition
    global chainShowAll
    wonThisCmd = False
    prefix = ''
    force = 0
    checkFound()
    if thisCmd == '':
        for _ in range(0, deliberateNuisanceRows):
            print("DELIBERATE NUISANCE")
        global input
        try:
            input = raw_input
        except NameError:
            pass
        name = input("Move:").strip()
        if name == '/':  # special case for slash/backslash
            debug = 1 - debug
            print ('debug', onOff[debug])
            cmdList.append(name)
            return
        if name == '\\':
            temp = len(moveList)
            totalmoves = 0
            cmd_churn = 1
            while automove():
                totalmoves = totalmoves + 1
            cmd_churn = 0
            if temp == len(moveList):
                print("No moves done.")
            else:
                printCards()
                printFound()
                print (totalmoves, "total moves.")
            cmdNoMeta.append(name)
            cmdList.append(name)
            return
        name = re.sub('[\\\/]', '', name)
        cmdNoMeta.append(name)
        cmdList.append(name)
        if name[:2] == 'e ':
            cardEval(name)
            return
        if name[:2] != 'l=' and name[:2] != 's=':
            name = name.replace(' ', '')
    else:
        name = thisCmd
    if name == '*':
        while reshuf(-1):
            pass
        return
    name = name.lower()
    if len(name) % 2 == 0 and len(name) >= 2:
        temp = int(len(name) / 2)
        if name[:] == name[temp:]:
            print ("Looks like a duplicate command, so I'm cutting it in half.")
            name = name[temp:]
    if name == 'tu':
        trackUndo = 1 - trackUndo
        if not in_undo:
            print ("trackUndo now " + onOff[trackUndo])
        cmdNoMeta.pop()
        return
    if len(name) == 0:
        anyReshuf = False
        while reshuf(-1):
            anyReshuf = True
        if anyReshuf:
            moveList.append('*')
        else:
            cmdNoMeta.pop()
        printCards()
        return
    if name[0] == '>' and name[1:].isdigit:
        print (name[1:], "becomes", tocard(int(name[1:])))
        cmdNoMeta.pop()
        return
    global onlymove
    onlymove = 0
    if len(name) > 3:
        if name[2] == '-':
            onlymove = re.sub(r'.*-', '', name)
            if not onlymove.isdigit():
                print ('Format is ##-#.')
                return
            onlymove = int(onlymove)
            name = re.sub(r'-.*', '', name)
    #### saving/loading comes first.
    if name == 'lp':
        original = open(save_file, "r")
        o1 = re.compile(r'^s=')
        newSave = ""
        while True:
            line = original.readline()
            if o1.match(line):
                newSave = line
            if not line:
                break
        name = newSave.strip()
        name = "l" + name[1:]
        print ("Loading " + name[2:])
    if name == 'l' or name == 's' or name == 'l=' or name == 's=':
        print ("load/save needs = and then a name. lp loads the last in the save file.")
        cmdNoMeta.pop()
        return
    if len(name) > 1:
        if name[0] == 'l' and name[1] == '=':
            cmdNoMeta.pop()
            load_game(re.sub(r'^l=', 's=', name))
            return
        if name[0] == 's' and name[1] == '=':
            cmdNoMeta.pop()
            saveGame(name.strip())
            return
    if name == "lo":
        cmdNoMeta.pop()
        readOpts()
        return
    if name == "so":
        cmdNoMeta.pop()
        sendOpts()
        return
    if name == 'q':
        cmdNoMeta.pop()
        print ("QU needed to quit, so you don't type Q accidentally.")
        return
    if name == 'qu':
        cmdNoMeta.pop()
        goBye()
    if name == 'ws' or name == 'sw':
        cmdNoMeta.pop()
        saveOnWin = not saveOnWin
        print ("Save on win is now %s." % ("on" if saveOnWin else "off"))
        return
    if name == 'ps' or name == 'sp':
        cmdNoMeta.pop()
        savePosition = not savePosition
        print ("Save position with moves/start is now %s." % ("on" if savePosition else "off"))
        return
    if name == 'u':
        undo_moves(1)
        return
    if name == 'h':
        if not slipUnder():
            cmdNoMeta.pop()
            print ("No slip-unders found.")
        return
    if name == 'p':
        oldMoves = len(moveList)
        anyDump = 0
        global breakMacro
        while best_dump_row() > 0:
            anyDump = 1
            newDump = best_dump_row()
            print ("Dumping row " + str(newDump))
            if chains(newDump) == len(elements[newDump]) and not cmd_churn:
                shufwarn()
                return
            rip_up(newDump)
            if len(elements[newDump]) > 0:
                if in_order(newDump) != 1:  # or elements[newDump][0] % 13 != 0
                    print ("Row %d didn't unfold all the way." % newDump)
                    break
            if breakMacro == 1:
                breakMacro = 0
                break
            checkFound()
            if breakMacro == 1:
                breakMacro = 0
                break
            if debug:
                print("Check: " + " ".join(str(x) for x in found) + " <sp found> " + " ".join(str(x) for x in spares))
        cmd_churn = False
        if debug:
            print ("Won this cmd: " + str(wonThisCmd))
        if anyDump == 0:
            print ("No rows found to dump.")
        elif not wonThisCmd:
            print (str(len(moveList) - oldMoves) + " moves total.")
            printCards()
        elif spares.sum == 52:
            print ("Not sure why but I need to check for a win here.")
            checkWin()
        wonThisCmd = False
        return
    if name[:1] == 'u':
        bigUndo = False
        if name[:4] == 'undo':
            bigUndo = True
            name = name[4:]
        else:
            name = name[1:]
        if name == 'a':
            cmdNoMeta.pop()
            if not in_undo:
                print ('Move list,', len(moveList), 'moves so far:', (moveList))
            return
        if name == 'c':
            cmdNoMeta.pop()
            if not in_undo:
                print ('Command list,', len(cmdList), 'commands so far:', (cmdList))
            return
        if name == 'x':
            cmdNoMeta.pop()
            if not in_undo:
                print ('Trimmed command list,', len(cmdNoMeta), 'commands so far:', (cmdNoMeta))
            return
        if name == 's':
            if len(moveList) == 0:
                print ("You've made no moves yet.")
                return
            d1 = moveList[len(moveList) - 1][0]
            temp = 0
            while (temp < len(moveList) - 1) and (d1 == moveList[len(moveList) - temp - 1][0]):
                temp += 1
            undo_moves(temp)
            print ("Last " + str(temp) + " moves started with " + d1)
            return
        if not name.isdigit():
            print ("Need to undo a number, or A for a list, S for same row as most recent move, or nothing." \
                  " C=commands X=commands minus meta.")
            return
        if int(name) > len(moveList):
            print ("Tried to do %d undo%s, can only undo %d." % (int(name), plur(int(name)), len(moveList)))
            return
        if int(name) > 10:
            if bigUndo:
                print (
                    "This game doesn't allow undoing more than 10 at a time except with UND,"
                    " because u78 would be kind of bogus if you changed your mind from undoing to moving.")
                return
            print ("UNDOing more than 10 moves.")
        undo_moves(int(name))
        return
    if name[0] == 'h':
        cmdNoMeta.pop()
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
                print ('Need a number, or AJQK.')
                return
        if int(name) < 1 or int(name) > 13:
            print ('Need 1-13.')
            return
        global highlight
        highlight = int(name)
        if highlight == 0:
            print ('Highlighting off.')
        else:
            print ('Now highlighting', cards[highlight - 1])
        printCards()
        return
    if name[0] == '?':
        cmdNoMeta.pop()
        if len(name) is 1 or name[1].lower() == 'g':
            usageGame()
        elif name[1].lower() == 'm':
            usage_meta()
        elif name[1].lower() == 'o':
            usageOptions()
        else:
            print ("Didn't recognize subflag", name[1].lower(), "so doing default of game command usage.")
            usageGame()
        return
    if name == "r" or name == "rr":
        forceFoundation()
        return
    if name[0] == 'f' or (len(name) > 2 and name[2] == 'f'):
        name = name.replace("f", "")
        force = 1
        prefix = prefix + 'f'
        if len(name) == 0:
            print ("You need a from/to, or at the very least, a from.")
            return
    if name == '-' or name == '=':
        if len(moveList) == 0:
            print ("Nothing to undo.")
            return
        elements = [row[:] for row in backup]
        initSide(1)
        printCards()
        checkFound()
        total_reset += 1
        return
    if name == "?":
        cmdNoMeta.pop()
        print ('Maximum card length moves: ', maxmove())
        return
    if name == "":
        printCards()
        return
    if name == '+':
        cmdNoMeta.pop()
        dblSzCards = not dblSzCards
        print ("Toggled dblSzCards to %s." % (onOff[dblSzCards]))
        printCards()
        return
    if name == 'cs':
        cmdNoMeta.pop()
        chainShowAll = not chainShowAll
        print ("Toggled chainShowAll to %s." % (onOff[chainShowAll]))
        printCards()
        return
    if name == 'e':
        cmdNoMeta.pop()
        autoReshuf = not autoReshuf
        print ("Toggled reshuffling to %s." % (onOff[autoReshuf]))
        reshuf(-1)
        printCards()
        return
    if name == 'v':
        cmdNoMeta.pop()
        vertical = not vertical
        print ("Toggled vertical view to %s." % (onOff[vertical]))
        printCards()
        return
    #### mostly meta commands above here. Keep them there.
    preverified = 0
    if len(name) == 2:
        n1 = ord(name[0])
        n2 = ord(name[1])
        if (n1 > 96) and (n1 < 101):
            if (n2 > 96) and (n2 < 101):
                if n1 == n2:
                    print ("Assuming you meant to do something with " + name[0] + ".")
                    name = name[0]
                elif spares[n1 - 97] > 0 and spares[n2 - 97] > 0:
                    cmdNoMeta.pop()
                    print ("Neither cell is empty, though shuffling does nothing.")
                    return
                elif spares[n1 - 97] == 0 and spares[n2 - 97] == 0:
                    cmdNoMeta.pop()
                    print ("Both cells are empty, so this does nothing.")
                    return
                else:
                    cmdNoMeta.pop()
                    print ('Shuffling between empty squares does nothing, so I\'ll just pass here.')
                    return
    if len(name) == 1:
        if name.isdigit():
            i = int(name)
            if i > 8 or i < 1:
                print ('Need 1-8.')
                return
            if len(elements[i]) is 0:
                cmdNoMeta.pop()
                print ('Acting on an empty row.')
                return
            if any_doable_limit(i):
                name = name + str(any_doable_limit(i))
            elif anyDoable(i, 0):
                name = name + str(anyDoable(i, 0))
            elif chains(i) > 1 and can_dump(i):
                if chains(i) == len(elements[i]) and not cmd_churn:
                    shufwarn()
                    return
                name = name + str(can_dump(i))
                preverified = 1
            elif chains(i) == 1 and spareUsed() < 4:
                name = name + "e"
            elif firstEmptyRow() and spareUsed() == 4:
                if doable(i, firstEmptyRow(), 0) == len(elements[i]):
                    shufwarn()
                    return
                name = name + str(firstEmptyRow())
            elif anyDoable(i, 1) and chains(i) < len(elements[i]):
                name = name + str(anyDoable(i, 1))
            else:
                name = name + 'e'
            if should_print():
                print ("New implied command %s." % name)
        elif 101 > ord(name[0]) > 96:
            if firstMatchableRow(spares[ord(name[0]) - 97]) > 0:
                name = name + str(firstMatchableRow(spares[ord(name[0]) - 97]))
            elif firstEmptyRow() > 0:
                name = name + str(firstEmptyRow())
            else:
                cmdNoMeta.pop()
                print ('No empty row/column to drop from spares.')
                return
        else:
            cmdNoMeta.pop()
            print ("Unknown 1-letter command.")
            return
    #### two letter commands below here.
    if len(name) > 2:
        gotReversed = 0
        oldMoves = len(moveList)
        if len(name) == 3 and name.isdigit:  # special case for reversing a move e.g. 64 46 can become 646
            if name[0] == name[2]:
                read_cmd(name[0] + name[1])
                read_cmd(name[1] + name[0])
                return
        if name.isdigit():  # for, say ,6873 to move 73 83 63
            gotReversed = 1
            cmd_churn = not chainShowAll
            oldTurns = len(moveList)
            for jj in reversed(range(0, len(name) - 1)):
                if not wonThisCmd:
                    if name[jj] != name[jj + 1]:
                        temp = name[jj] + name[len(name) - 1]
                        print ("Moving " + temp)
                        read_cmd(name[jj] + name[len(name) - 1])
            cmd_churn = False
            if len(moveList) > oldTurns and not chainShowAll:
                printCards()
            if name.isdigit() and wonThisCmd is False:
                print (
                    'Chained ' + str(len(moveList) - oldMoves) + ' of ' + str(len(name) - 1) + ' moves successfully.')
        if gotReversed == 0:
            print ('Only 2 chars per command.')
            cmdNoMeta.pop()
        return
    if len(name) < 2:
        print ('Must have 2 chars per command, unless you are willing to use an implied command.')
        cmdNoMeta.pop()
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
            print ("1-8 a-d are needed with R, or (nothing) tries to force everything.")
            cmdNoMeta.pop()
            return
        if temprow > -1:
            if temprow > 8 or temprow < 1:
                print ('Not a valid row.')
                cmdNoMeta.pop()
                return
            if len(elements[temprow]) == 0:
                print ('Empty row.')
                cmdNoMeta.pop()
                return
            if foundable(elements[temprow][len(elements[temprow]) - 1]):
                found[(elements[temprow][len(elements[temprow]) - 1] - 1) // 13] += 1
                elements[temprow].pop()
                if not in_undo:
                    moveList.append(name)
                slipUnder()
                checkFound()
                reshuf(-1)
                printCards()
                return
            print ('Sorry, found nothing.')
            cmdNoMeta.pop()
            return
        if tempspare > -1:
            if foundable(spares[tempspare]):
                found[(spares[tempspare] - 1) // 13] += 1
                spares[tempspare] = 0
                print ('Moving from spares.')
                if not in_undo:
                    moveList.append(name)
                checkAgain = True
                while checkAgain:
                    checkAgain = False
                    checkAgain |= checkFound()
                    if force == 0:
                        checkAgain |= reshuf(-1)
                    pass
                checkFound()
                reshuf(-1)
                printCards()
            else:
                print ('Can\'t move from spares.')  # /? 3s onto 2s with nothing else, all filled
                cmdNoMeta.pop()
            return
        print ('Must move 1-8 or a-d.')
        cmdNoMeta.pop()
        return
    if len(name) == 2 and (name[0] == 'p' or name[1] == 'p'):
        q2 = (name.replace("p", ""))
        if not q2.isdigit():
            print ("p command requires a digit.")
            cmdNoMeta.pop()
            return
        if rip_up(int(q2)):
            cmd_churn = False
            printCards()
            printFound()
        else:
            cmd_churn = False
        return
    if name[0].isdigit() and name[1].isdigit():
        t1 = int(name[0])
        t2 = int(name[1])
        if t1 == t2:
            print ('Moving a row to itself does nothing.')
            cmdNoMeta.pop()
            return
        if t1 < 1 or t2 < 1 or t1 > 8 or t2 > 8:
            print ("Need digits from 1-8.")
            cmdNoMeta.pop()
            return  # don't put anything above this
        if len(elements[t1]) == 0 and not in_undo:
            print ('Nothing to move from.')
            cmdNoMeta.pop()
            return
        if len(elements[t2]) == 0:
            if chains(t1) == len(elements[t1]) and not cmd_churn and force == 0 and onlymove == 0:
                cmdNoMeta.pop()
                shufwarn()
                return
        tempdoab = doable(t1, t2, 1 - preverified)
        if tempdoab == -1:
            if not cmd_churn:
                print ('Not enough space.')
                cmdNoMeta.pop()
            return
        if tempdoab == 0:
            if in_undo:
                # print "Move", str(undo_idx), "(", thisCmd, t1, t2, preverified, ") seems to have gone wrong. Use ua."
                if undo_idx == 15:
                    printCards()
                    exit()
            else:
                print ('Those cards don\'t match up.')
                cmdNoMeta.pop()
            return
        oldchain = chains(t1)
        shiftcards(t1, t2, tempdoab)
        if not in_undo:
            if tempdoab < oldchain and len(elements[t2]) == 0:
                moveList.append(str(t1) + str(t2) + "-" + str(tempdoab))
            elif onlymove > 0:
                moveList.append(name + "-" + str(onlymove))
            else:
                moveList.append(prefix + name)
        checkAgain = True
        while checkAgain:
            checkAgain = False
            checkAgain |= checkFound()
            if force == 0:
                checkAgain |= reshuf(-1)
            checkAgain |= slipUnder()
            pass
        printCards()
        return
    if (ord(name[0]) > 96) and (ord(name[0]) < 101):  # a1 moves
        mySpare = ord(name[0]) - 97
        if spares[mySpare] == 0:
            print ('Nothing in slot %d.' % (mySpare + 1))
            cmdNoMeta.pop()
            return
        if not name[1].isdigit():
            print ('Second letter not recognized.')
            cmdNoMeta.pop()
            return
        myRow = int(name[1])
        if myRow < 1 or myRow > 8:
            print ('To row must be between 1 and 8.')
            cmdNoMeta.pop()
            return
        if (len(elements[myRow]) == 0) or (can_put(spares[mySpare], elements[myRow][len(elements[myRow]) - 1])):
            elements[myRow].append(spares[mySpare])
            spares[mySpare] = 0
            if not in_undo:
                moveList.append(name)
            reshuf(-1)
            slipUnder()
            checkFound()
            printCards()
            return
        print ("Can't put%s on%s." % (tocardX(spares[mySpare]), tocardX(elements[myRow][len(elements[myRow]) - 1])))
        cmdNoMeta.pop()
        return
    if (ord(name[1]) > 96) and (ord(name[1]) < 102):  # 1a moves, but also 1e can be A Thing
        if not name[0].isdigit():
            print ('First letter not recognized as a digit.')
            return
        myToSpare = first_empty_spare()
        if myToSpare == -1:
            if not cmd_churn:
                print ('Nothing empty to move to. To which to move.')
                cmdNoMeta.pop()
            return
        if name[1] != 'e':
            myToSpare = ord(name[1]) - 97
        myRow = int(name[0])
        if myRow < 1 or myRow > 8:
            print ('From row must be between 1 and 8.')
            cmdNoMeta.pop()
            return
        if len(elements[myRow]) == 0:
            print ('Empty from-row.')
            cmdNoMeta.pop()
            return
        if spares[myToSpare] > 0:
            myFirstE = firstEmptyRow()
            if myFirstE > 0:
                myRow = int(name[0])
                rowIdx = len(elements[myRow]) - 1
                gotOne = can_put(elements[myRow][rowIdx], spares[myToSpare])
                while rowIdx > 0 and (
                            can_put(elements[myRow][rowIdx], spares[myToSpare]) or can_put(elements[myRow][rowIdx],
                                                                                           elements[myRow][
                                                                                                   rowIdx - 1])):
                    rowIdx = rowIdx - 1
                    gotOne = True
                if gotOne is True:
                    read_cmd(name[1] + str(myFirstE))
                    read_cmd(name[0] + str(myFirstE))
                    return
            for temp in range(0, 4):
                if spares[(myToSpare + temp) % 4] <= 0:
                    print ("Spare %d already filled, picking %d instead" % (myToSpare + 1, (myToSpare + temp) % 4 + 1))
                    myToSpare += temp
                    myToSpare %= 4
                    break
            if spares[myToSpare] > 0:
                print ("Oops, I somehow see all-full and not all full at the same time.")
                cmdNoMeta.pop()
                return
        spares[myToSpare] = elements[myRow].pop()
        if not in_undo:
            moveList.append(name)
        tempMoveSize = -1
        while tempMoveSize < len(moveList):
            tempMoveSize = len(moveList)
            tempRowSize = len(elements[myRow])
            checkFound()
            slipUnder()
            if reshuf(myToSpare) or len(elements[myRow]) < tempRowSize:
                reshuf(-1)
        printCards()
        return
    print (name + ' not recognized, displaying usage.')
    cmdNoMeta.pop()
    usageGame()


# start main program

if disallowWriteSource and os.access(__file__, os.W_OK):
    print ("Source file should not have write access outside of the game. attrib -R " + __file__ + \
          " or chmod 333 to get things going.")
    exit()

readOpts()

# note that the Cmd line overrides what is in the options file
parseCmdLine()

if time_matters and os.path.exists(time_file) and os.stat(time_file).st_size > 0:
    readTimeFile()

if annoyingNudge:
    try:
        input = raw_input
    except NameError:
        pass
    pwd = input("Type TIME WASTING AM I, in reverse word order, in here.\n").strip()
    # if pwd != "i am wasting time":
    if pwd != "I aM wAsTiNg TiMe":
        if pwd.lower() == "i am wasting time":
            print ("Remember to put it in alternate caps case! I did this on purpose, to make it that much harder.")
            exit()
        print ("Type I am wasting time, or you can't play.")
        # exit()

openLockFile()

initSide(0)
initCards()
printCards()

while win == 0:
    read_cmd('')
