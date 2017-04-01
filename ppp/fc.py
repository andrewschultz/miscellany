######################################
#fc.py
#
#no frills Python Freecell game
#

#?? P (all) doesn't show what went to foundation
#> and < to bookend macro-type undoables. Skip if in Undo

# reshuf after, say, 5r (?)
import re
import sys
import os
from random import shuffle, randint
import time
import traceback
import ConfigParser
import optparse

configOpt = ConfigParser.SafeConfigParser()
configTime = ConfigParser.SafeConfigParser()

savefile = "fcsav.txt"
winFile = "fcwins.txt"
timefile = "fctime.txt"

onoff = ['off', 'on']

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

top = ['CL', 'di', 'SP', 'he']
btm = ['UB', 'am', 'AD', 'ar']

moveList = []

win = 0

totalUndo = 0
totalReset = 0

cmdChurn = False
inUndo = False

wonThisCmd = False

lastReset = 0
startTime = 0

#time before next play variables
timeMatters = 1
nagDelay = 30000
highTime = 0
maxDelay = 0

#options to define. How to do better?
vertical = True
dblSzCards = False
autoReshuf = True
savePosition = False
saveOnWin = False
# this is an experimental feature to annoy me
deliberateNuisanceRows = 3
deliberateNuisanceIncrease = 2
# this can't be toggled in game
annoyingNudge = True
#easy mode = A/2 on top
cheatIndex = 0

lastscore = 0
highlight = 0

onlymove = 0

trackUndo = 0

breakMacro = 0

undoIdx = 0

debug = False

cmdList = []
cmdNoMeta = []

backup = []
elements = [ [], [], [], [], [], [], [], [], [] ]

name = ""

def TOrF(x):
    if x == "False" or x == "0":
        return False
    return True

def printCond(myString, z):
    if not inUndo and not cmdChurn:
        print(myString)
    return

def shufwarn():
    if not cmdChurn and not inUndo:
        print ("That won't make progress. F(##) or ##-# let you move part of an in-order stack over.")

def dumpTotal(q): # the doPrint is for debugging purposes. A negative number input means you print. This is not great code but there were so many dumpTotal calls I just got lazy and made a small hack.
    retval = 0
    doPrint = False
    if q < 0:
        q = 0 - q
        doPrint = True
    for z in range(0,len(elements[q])):
        if foundable(elements[q][z]):
            if doPrint:
                print tocard(elements[q][z]), elements[q][z], 'foundable'
            retval += 1
            if elements[q][z] % 13 == 2: #aces/2's get a special bonus
                retval += 1
            if elements[q][z] % 13 == 1: #aces/2's get a special bonus
                retval += 2
        if nexties(elements[q][z]): # not an elif as foundable deserves an extra point
            retval += 1
            if doPrint:
                print tocard(elements[q][z]), elements[q][z], 'nexties'
    return retval

def bestDumpRow():
    bestScore = -1
    bestRow = 0
    bestChains = 10
    for y in range (1,9):
        if chainNope(y) == 0: # if there is nothing to move or dump, then skip this e.g. empty or already in order
            continue
        if dumpTotal(y) + YNCanDump(y) > bestScore or (dumpTotal(y) == bestScore and chainNope(y) < bestChains):
            bestRow = y
            bestChains = chainNope(y)
            bestScore = dumpTotal(y)
    if bestRow > 0:
        return bestRow
    maxShifts = 10
    for y in range (1,9):
        if chainNope(y) == 0:
            continue
        if chainNope(y) < maxShifts:
            for z in range (1,9):
                if doable(y, z, 0) > 0:
                    maxShifts = chainNope(y)
                    bestRow = y
    return bestRow

def foundable(myc):
    if (myc-1) % 13 == found[(myc-1)//13]:
        return True
    return False

def nexties(myc): #note that this may be a bit warped looking if you have 5S 5C 2h 2d for instance
    odds = (myc-1)//13
    cardval = (myc-1) % 13
    if cardval < found[(odds+1)%4]+2 and cardval < found[(odds+3)%4]+2:
        return True
    return False

def ripUp(q):
    madeOne = False
    if q < 1 or q > 8:
        print ("Column/row needs to be 1-8.")
        return False
    if len(elements[q]) == 0:
        print ("Already no elements.")
        return True
    goAgain = 1
    global cmdChurn
    cmdChurn = True
    movesize = len(moveList)
    maxRun = 0
    while goAgain == 1 and len(elements[q]) > 0 and maxRun < 25 and not inOrder(q):
        shouldReshuf = True
        if len(elements[q]) > 1:
            if canPut(elements[q][len(elements[q])-1], elements[q][len(elements[q])-2]):
                shouldReshuf = False
        maxRun += 1
        goAgain = 0
        tempArySize = len(moveList)
        readCmd(str(q))
        if len(moveList) > tempArySize:
            goAgain = 1
            madeOne = True
        checkFound()
        if shouldReshuf:
            reshuf(-1)
        forceFoundation()
        slipUnder()
    if maxRun == 25:
        print ("Oops potential hang at " + str(q))
    checkFound()
    if (len(moveList) == movesize):
        print ("Nothing moved.")
    return madeOne

def shouldPrint():
    global inUndo
    global cmdChurn
    if inUndo or cmdChurn:
        return False
    return True

def YNCanDump(mycol): # could also be (int)(not not canDump(myCol)) but that's a bit odd looking
    if canDump(mycol) > 0:
        return 1
    return 0

def canDump(mycol): # returns column you can dump to
    for thatcol in range (1,9):
        if doable(mycol, thatcol, 0) > 0:
            return thatcol
    dumpSpace = 0
    for thiscol in range (1,9):
        if len(elements[thiscol]) == 0:
            dumpSpace = dumpSpace + 1
    if dumpSpace == 0:
        return 0
    dumpSpace *= 2
    dumpSpace -= 1
    for x in range (0,4):
        if found[x] == 0:
            dumpSpace = dumpSpace + 1
    if chains(mycol) > maxmove()/2:
        return 0
    for tocol in range (1,9):
        if len(elements[tocol]) == 0:
            return tocol
    return 0

def reshuf(xyz): # this reshuffles the empty cards
    if not autoReshuf:
        return False
    retval = False
    tryAgain = 1
    movesBefore = len(moveList)
    while tryAgain:
        tryAgain = 0
        for i in range(0,4):
            if i == xyz:
                continue
            if xyz > -1 and spares[i] and abs(spares[i] - spares[xyz]) == 26:
                continue #this is a very special case for if we put 3C to spares and 3S is there
            if spares[i]:
                for j in range(1,9):
                    if len(elements[j]):
                        if canPut(spares[i], elements[j][len(elements[j])-1]): #doesn't matter if there are 2. We can always switch
                            elements[j].append(spares[i])
                            spares[i] = 0
                            tryAgain = 1
                            retval = True
                            #stupid bug here with if we change autoReshuf in the middle of the game
                            #solution is to create "ar(x)(y)" which only triggers if autoReshuf = 0
    shifties = 0
    if force == 1 or onlymove > 0:
        return retval
    while autoShift():
        shifties += 1
        if shifties == 12:
            print ('Oops, broke an infinite loop.')
            return False
    return retval

def autoShift(): # this shifts rows
    for i in range (1,9): # this is to check for in-order columns that can be restacked
        if len(elements[i]) == 0 or chainNope(i) > 0:
            continue
        for j in range (1,9):
            if len(elements[j]) > 0 and len(elements[i]) <= maxmove():
                if canPut(elements[i][0], elements[j][len(elements[j])-1]):
                    if not cmdChurn and not inUndo:
                        print ("Autoshifted " + str(i) + " to " + str(j) + ".")
                    shiftcards(i, j, len(elements[i]))
                    return True
    return False

def inOrder2(rowNum):
    if len(elements[rowNum]) < 2:
        return 0
    return inOrder(rowNum)

def inOrder(rowNum):
    if len(elements[rowNum]) < 2:
        return 0
    for i in range(1,len(elements[rowNum])):
        if not canPut(elements[rowNum][i], elements[rowNum][i-1]):
            return 0
    return 1

def chainTotal():
    retval = 0
    for i in range (0,9):
        for v in range (1,len(elements[i])):
            if canPut(elements[i][v], elements[i][v-1]):
                retval += 1
    return retval

def chainNopeBig():
    retval = 0
    for i in range (0,9):
        retval += chainNope(i)
    return retval

def chainNopeEach():
    retval = 0
    for i in range (0,9):
        if chainNope(i) > 0:
            retval += 1
    return retval

def chainNope(rowcand):
    retval = 0 #note this doesn't consider if we have, say, 7C-Ah-6D
    for v in range (1,len(elements[rowcand])):
        if canPut(elements[rowcand][v], elements[rowcand][v-1]) == 0: # make sure it is not a (!)
            retval += 1
    return retval

def spareUsed():
    retval = 0
    for i in range (0,4):
        if spares[i]:
            retval += 1
    return retval

def firstEmptyRow():
    for i in range(1,9):
        if len(elements[i]) == 0:
            return i
    return 0

def firstMatchableRow(cardval):
    for i in range (1,9):
        if len(elements[i]) > 0:
            if canPut(cardval, elements[i][len(elements[i])-1]):
                return i
    return 0

def parseCmdLine():
    global vertical
    global debug
    global saveOnWin
    global cheatIndex
    openAnyFile = False
    parser = optparse.OptionParser(description='Play FreeCell.')
    parser.add_option('--getridofthetimewastenag', action='store_false', dest='annoyingNudge', help='delete annoying nudge')
    parser.add_option('-e', '--easy', action='store_true', dest='easy', help='easy mode on (A and 2 on top)')
    parser.add_option('-c', '--cheatindex', action='store', dest='cheatIndex', help='specify cheat index 1-13', type='int')
    parser.add_option('-d', '--debug', action='store_true', dest='debug', help='debug on')
    parser.add_option('-D', '--nodebug', action='store_false', dest='debug', help='debug off')
    parser.add_option('-v', '--vertical', action='store_true', dest='vertical', help='vertical on')
    parser.add_option('-V', '--novertical', action='store_false', dest='vertical', help='vertical off')
    parser.add_option('-s', '--saveonwin', action='store_true', dest='saveOnWin', help='save-on-win on')
    parser.add_option('-S', '--nosaveonwin', action='store_false', dest='saveOnWin', help='save-on-win off')
    parser.add_option('-t', '--textfile', action='store_true', dest='timefile', help='open text/time file')
    parser.add_option('-o', '--optfile', action='store_true', dest='optfile', help='open options file')
    parser.add_option('-l', '--loadsavefile', action='store_true', dest='savefile', help='open save file')
    parser.add_option('-p', '--pythonfile', action='store_true', dest='pythonfile', help='open python file')
    (opts, args) = parser.parse_args()
    if opts.timefile is True:
        os.system("fctime.txt")
        openAnyFile = True
    if opts.optfile is True:
        os.system("fcopt.txt")
        openAnyFile = True
    if opts.savefile is True:
        os.system("fcsav.txt")
        openAnyFile = True
    if opts.pythonfile is True:
        os.system("\"c:\\Program Files (x86)\\Notepad++\\notepad++\" fc.py")
        openAnyFile = True
    if openAnyFile:
        exit()
    if opts.annoyingNudge is not None:
        annoyingNudge=opts.annoyingNudge
    if opts.vertical is not None:
        vertical=opts.vertical
    if opts.debug is not None:
        debug=opts.debug
    if opts.saveOnWin is not None:
        saveOnWin=opts.saveOnWin
    if opts.cheatIndex is not None:
        if opts.cheatIndex < 1:
            print "Too low. The cheat index must be between 1 and 13."
            sys.exit()
        elif opts.cheatIndex > 13:
            print "Too high. The cheat index must be between 1 and 13."
            sys.exit()        
        cheatIndex = opts.cheatIndex
    elif opts.easy is True:
        cheatIndex = 2
    return

def readTimeFile():
    global nagDelay
    global maxDelay
    configTime.read("fctime.txt")
    modulus = configTime.getint('Section1', 'modulus')
    remainder = configTime.getint('Section1', 'remainder')
    maxDelay = configTime.getint('Section1', 'maxdelay')
    lasttime = configTime.getint('Section1', 'lasttime')
    curtime = time.time()
    delta = int(curtime - lasttime)
    if delta < nagDelay:
        print 'Only', str(delta), 'seconds elapsed of',nagDelay
        exit()
    if delta > 90000000:
        print "Save file probably edited to start playing a bit early. I'm not going to judge."
    elif delta > maxDelay:
        print 'New high delay', delta, 'old was', maxDelay
        maxDelay = delta
    else:
        print 'Delay', delta, 'did not exceed record of', maxDelay
    if lasttime % modulus != remainder:
        print "Save file is corrupted. If you need to reset it, choose a modulus of 125000 and do things manually."
        print lasttime,modulus,remainder,lasttime%modulus
        exit()
    if modulus < 100001 or modulus > 199999:
        print "Modulus is not in range in fctime.txt."
        exit()
    return

def writeTimeFile():
    if not configTime.has_section('Section1'):
        configTime.add_section("Section1")
    lasttime = int(time.time())
    modulus = randint(100001,199999)
    remainder = lasttime % modulus
    global maxDelay
    configTime.set('Section1', 'modulus', str(modulus))
    configTime.set('Section1', 'remainder', str(remainder))
    configTime.set('Section1', 'maxdelay', str(maxDelay))
    configTime.set('Section1', 'lasttime', str(lasttime))
    with open('fctime.txt', 'w') as configfile:
        configTime.write(configfile)
    return

def readOpts():
    configOpt.read("fcopt.txt")
    global vertical
    vertical = configOpt.getboolean('Section1', 'vertical')
    global autoReshuf
    autoReshuf = configOpt.getboolean('Section1', 'autoReshuf')
    global dblSzCards
    dblSzCards = configOpt.getboolean('Section1', 'dblSzCards')
    global saveOnWin
    saveOnWin = configOpt.getboolean('Section1', 'saveOnWin')
    global savePosition
    savePosition = configOpt.getboolean('Section1', 'savePosition')
    global annoyingNudge
    annoyingNudge = configOpt.getboolean('Section1', 'annoyingNudge')
    return

def sendOpts():
    if not configOpt.has_section('Section1'):
        configOpt.add_section("Section1")
    configOpt.set('Section1', 'vertical', str(vertical))
    configOpt.set('Section1', 'autoReshuf', str(autoReshuf))
    configOpt.set('Section1', 'dblSzCards', str(dblSzCards))
    configOpt.set('Section1', 'saveOnWin', str(saveOnWin))
    configOpt.set('Section1', 'savePosition', str(savePosition))
    configOpt.set('Section1', 'annoyingNudge', str(annoyingNudge))
    with open('fcopt.txt', 'w') as configfile:
        configOpt.write(configfile)
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
    if not inUndo:
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
    for y in range (0,4):
        if (spares[y] == 0):
            base += 1
    for y in range (1,9):
        if (len(elements[y]) == 0):
            myexp *= 2
    return base * myexp

def canPut(lower, higher):
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
    if not cmdChurn:
        totalFoundThisTime = 0
        cardlist = ''
    while needToCheck:
        needToCheck = 0
        for y in range (1,9):
            if len(elements[y]) > 0:
                while elements[y][len(elements[y])-1] % 13 == (1 + found[(elements[y][len(elements[y])-1]-1)//13]) % 13:
                    basesuit = (elements[y][len(elements[y])-1]-1)//13
                    if found[(basesuit+1) % 4] < found[basesuit] - 1:
                        break
                    if found[(basesuit+3) % 4] < found[basesuit] - 1:
                        break
                    needToCheck = 1
                    retval = True
                    totalFoundThisTime += 1
                    found[(elements[y][len(elements[y])-1]-1)//13] = found[(elements[y][len(elements[y])-1]-1)//13] + 1
                    cardlist = cardlist + tocardX(elements[y][len(elements[y])-1])
                    elements[y].pop()
                    if len(elements[y]) == 0:
                        break
        for y in range (0,4):
            #print 'checking ',y,tocard(spares[y])
            if spares[y] > 0:
                if (spares[y]-1) % 13 == found[(spares[y]-1)//13]:
                    sparesuit = (spares[y]-1)//13
                    if debug:
                        print ('position', y, 'suit' ,suits[(spares[y]-1)/13], 'card' ,tocard(spares[y]))
                    if found[(sparesuit+3)%4] < found[sparesuit] - 1:
                        continue
                    if found[(sparesuit+1)%4] < found[sparesuit] - 1:
                        continue
                    cardlist = cardlist + tocardX(spares[y])
                    totalFoundThisTime += 1
                    found[(spares[y]-1)//13] += 1
                    spares[y] = 0
                    needToCheck = 1
                    retval = True
    #print (str(totalFoundThisTime) + " undo " + str(inUndo) + " churn " + str(cmdChurn) + " " + str(shouldPrint()))
    #traceback.print_stack()
    printFound()
    return retval

def printFound():
    global totalFoundThisTime
    global cardlist
    if totalFoundThisTime > 0 and shouldPrint():
        sys.stdout.write(str(totalFoundThisTime) + ' card' + plur(totalFoundThisTime) + ' safely to foundation:' + cardlist + '\n')
        totalFoundThisTime = 0
        cardlist = ''

def forceFoundation():
    global inUndo
    checkAgain = 1
    forceStr = ""
    global cardlist
    global totalFoundThisTime
    while checkAgain:
        checkAgain = 0
        for row in range (1,9):
            if len(elements[row]) > 0:
                if foundable(elements[row][len(elements[row])-1]) == 1:
                    found[(elements[row][len(elements[row])-1]-1)//13]+= 1
                    forceStr = forceStr + tocardX(elements[row][len(elements[row])-1])
                    if not inUndo:
                        cardlist = cardlist + tocardX(elements[row][len(elements[row])-1])
                        totalFoundThisTime += 1
                    elements[row].pop()
                    checkAgain = 1
        for xx in range (0,4):
            if spares[xx]:
                #print ("Checking" + tocardX(spares[xx]))
                if foundable(spares[xx]):
                    forceStr = forceStr + tocardX(spares[xx])
                    if not inUndo:
                        cardlist = cardlist + tocardX(spares[xx])
                        totalFoundThisTime += 1
                    found[(spares[xx]-1)//13] += 1
                    spares[xx] = 0
                    checkAgain = 1
    if forceStr:
        if not inUndo:
            moveList.append("r")
            printCond("Sending all to foundation.", False)
            printCond("Forced" + forceStr, False)
        reshuf(-1)
        checkFound()
        printCards()
    else:
        printCond("Nothing to force to foundation.", False)
    return

def checkWin():
    for y in range (0,4):
        #print y,found[y]
        if found[y] != 13:
            return 0
    checkWinning()

def initCards():
    x = []
    if cheatIndex > 0:
        x = list(range(cheatIndex+1, 14)) + list(range(cheatIndex+14, 27)) + list(range(cheatIndex+27, 40)) + list(range(cheatIndex+40, 53))
        shuffle(x)
        for y in reversed(range(1,cheatIndex+1)):
            x[:0] = [y,y+13,y+26,y+39]
    else:
        x = list(range(1,53))
        shuffle(x)
    global elements
    for y in range(0,7):
        for z in range(1,9):
            if len(x) == 0:
                break
            elements[z].append(x.pop())
    global backup
    backup = [row[:] for row in elements]

def tocard( cardnum ):
    if cardnum == 0:
        return '---'
    temp = cardnum - 1
    retval = '' + cards[temp % 13] + suits[temp // 13]
    return retval

def tocardX (cnum):
    if (cnum % 13 == 10):
        return ' ' + tocard(cnum)
    return tocard(cnum)

def printCards():
    if cmdChurn:
        return
    if inUndo:
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
    try: input = raw_input
    except NameError: pass
    finish = ""
    global cmdChurn
    #print ("Churn now false (checkWinning).")
    cmdChurn = False
    printFound()
    global startTime
    global lastReset
    if startTime != -1:
        curTime = time.time()
        timeTaken = curTime - startTime
        print ("%.2f seconds taken." % (timeTaken))
        if lastReset > startTime:
            print ("%.2f seconds taken since last reset." % (curTime - lastReset))
    else:
        print ("No time data kept for loaded game.")
    global totalReset
    global totalUndo
    if totalReset > 0:
        print ("%d reset used." % (totalReset))
    if totalUndo > 0:
        print ("%d undo used." % (totalUndo))
    if totalUndo == -1:
        print ("No undo data from loaded game.")
    if saveOnWin:
        with open(winFile, "a") as myfile:
            winstring = time.strftime("sw=%Y-%m-%d-%H-%M-%S", time.localtime())
            myfile.write(winstring)
            myfile.write("\n#START NEW SAVED POSITION\n")
            global backup
            for i in range (1,9):
                myfile.write(' '.join(str(x) for x in backup[i]) + "\n")
        print ("Saved " + winstring)
    global breakMacro
    breakMacro = 1
    global wonThisCmd
    wonThisCmd = True
    while True:
        finish = input("You win in %d commands (%d including extraneous) and %d moves! Play again (Y/N, U to undo)?" % (len(cmdNoMeta), len(cmdList), len(moveList))).lower()
        finish = re.sub(r'^ *', '', finish)
        if len(finish) > 0:
            if finish[0] == 'n' or finish[0] == 'q':
                goBye()
            if finish[0] == 'y':
                global deliberateNuisanceRows
                if deliberateNuisanceRows > 0:
                    deliberateNuisanceRows += deliberateNuisanceIncrease
                initCards()
                initSide(0)
                totalUndo = 0
                totalReset = 0
                return 1
            if finish[0] == 'u':
                cmdNoMeta.pop()
                global inUndo
                inUndo = True
                undoMoves(1)
                inUndo = False
                return 0
        print ("Y or N (or U to undo). Case insensitive, cuz I'm a sensitive guy.")

# this detects how long a chain is, e.g. how many in a row
#10d-9s-8d-7s is 4 not 3
def chains(myrow):
    if len(elements[myrow]) == 0:
        return 0
    retval = 1
    mytemp = len(elements[myrow]) - 1
    while mytemp > 0:
        if canPut(elements[myrow][mytemp], elements[myrow][mytemp-1]):
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
    for y in range (1,9):
        if chainNope(y) == 0:
            sys.stdout.write(' *' + onedig(chains(y)) + '*')
        else:
            sys.stdout.write(' ' + onedig(chains(y)) + '/' + str(chainNope(y)))
        if dblSzCards:
            sys.stdout.write(' ')
    print ("")
    for y in range (1,9):
        sys.stdout.write(' ' + str(y) + ': ')
        if dblSzCards:
            sys.stdout.write(' ')
    print ("")
    oneMoreTry = 1
    while oneMoreTry:
        thisline = ''
        secondLine = ''
        oneMoreTry = 0
        for y in range (1,9):
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
                    thisline += top[(elements[y][count]-1)//13]
                    secondLine += btm[(elements[y][count]-1)//13] + ' '
                else:
                    thisline += str(tocard(elements[y][count]))
                if foundable(elements[y][count]):
                    if nexties(elements[y][count]):
                        thisline += '!'
                    else:
                        thisline += '*'
                elif highlight and (((elements[y][count]-1) % 13) == highlight - 1):
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
        count+=1
    printOthers()
    #traceback.print_stack()

def printHorizontal():
    for y in range (1,9):
        sys.stdout.write(str(y) + ':')
        for z in elements[y]:
             sys.stdout.write(' ' + tocard(z))
        print
    printOthers()

def orgit(myList = []):
    globbed = 1
    while globbed:
        globbed = 0
        for x1 in range (0,len(myList)):
            for x2 in range (0,len(myList)):
                if globbed == 0:
                    if myList[x1][0] == myList[x2][-1]:
                        globbed = 1
                        temp = myList[x2] + myList[x1][1:]
                        del myList[x2]
                        if x1 > x2:
                            del myList[x1-1]
                        else:
                            del myList[x1]
                        myList.insert(0, temp)
    return  ' ' + ' '.join(myList)

def printOthers():
    checkWin()
    coolmoves = []
    coolmove = ''
    foundmove = ''
    canmove = ''
    wackmove = ''
    emmove = ''
    latmove = ''
    canfwdmove = 0
    for z1 in range (1,9):
        if len(elements[z1]) == 0:
            emmove = emmove + ' E' + str(z1)
            canfwdmove = 1
            continue
        if inOrder(z1) and elements[z1][0] % 13 == 0:
            continue
        for z2 in range (1,9):
            if z2 == z1:
                continue
            if len(elements[z2]) == 0:
                continue
            thisdo  = doable(z1,z2,0)
            if thisdo == -1:
                wackmove = wackmove + ' ' + str(z1)+str(z2)
            elif thisdo > 0:
                tempmove = str(z1)+str(z2)
                if thisdo >= len(elements[z1]):
                    canfwdmove = 1
                    coolmoves.append(tempmove)
                elif not canPut(elements[z1][len(elements[z1])-thisdo], elements[z1][len(elements[z1])-thisdo-1]):
                    canfwdmove = 1
                    coolmoves.append(tempmove)
                else:
                    tempmove = ' ' + tempmove + '-'
                    latmove = latmove + tempmove
    for z1 in range (1,9):
        if len(elements[z1]):
            for z2 in range (0,4):
                if canPut(spares[z2], elements[z1][len(elements[z1])-1]):
                    foundmove = foundmove + ' ' + chr(z2+97) + str(z1)
                    canfwdmove = 1
    for z1 in range (0,4):
        if spares[z1] == 0:
            foundmove = ' >' + chr(z1+97) + foundmove
            canfwdmove = 1
    if wackmove:
        print ("Not enough room: " + str(wackmove))
    if coolmove and latmove:
        coolmove = coolmove + ' |'
    if (coolmove or latmove) and emmove:
        emmove = ' |' + emmove
    elif not coolmove and not latmove:
        coolmove = '(no row switches)'
    print ("Possible moves:" + orgit(coolmoves) + foundmove + latmove + " (%d max shift" % (maxmove()) + (", recdumprow=" + str(bestDumpRow()) if bestDumpRow() > 0 else "") + ")" )
    if not canfwdmove:
        reallylost = 1
        for z in range (1,9):
            if len(elements[z]) > 0 and foundable(elements[z][len(elements[z])-1]):
                reallylost = 0
        for z in range (0,4):
            if foundable(spares[z]):
                reallylost = 0
        if reallylost == 1:
            print ("Uh oh. You\'re probably lost.")
        else:
            print ("You may have to dump stuff in the foundation.")
    sys.stdout.write('Empty slots: ')
    for y in range (0,4):
        sys.stdout.write(tocard(spares[y]))
        for z in range(1,9):
            if len(elements[z]) and canPut(spares[y], elements[z][len(elements[z])-1]):
                sys.stdout.write('<')
                break
        if spares[y] > 0 and (spares[y] - 1) % 13 == found[(spares[y] - 1) // 13]:
            sys.stdout.write('*')
        else:
            sys.stdout.write(' ')
    sys.stdout.write('\nFoundation: ')
    foundscore = 0
    for y in [0, 2, 1, 3]:
        foundscore += found[y]
        if found[y] == 0:
            sys.stdout.write(' ---')
        else:
            sys.stdout.write(' ' + tocard(found[y] + y * 13))
    sys.stdout.write(' (' + str(foundscore) + ' point' + plur(foundscore))
    global lastscore
    if (lastscore < foundscore):
        sys.stdout.write(', up ' + str(foundscore - lastscore))
    sys.stdout.write(', ' + str(chainTotal()) + ' pairs in order, ' + str(chainNopeBig()) + ' out of order, ' + str(chainNopeEach()) + ' cols unordered')
    sys.stdout.write(')\n')
    lastscore = foundscore

def anyDoableLimit (ii):
    tempval = 0
    for y in range (1,9):
        temp2 = doable(ii, y, 0)
        if len(elements[y]) > 0 and temp2 > 0 and temp2 <= maxmove():
            if chains(ii) == temp2:
                return y
            tempval = y
    return tempval

def anyDoable (ii, emptyOK):
    tempret = 0
    for y in range (1,9):
        tempval = doable(ii, y, 0);
        if emptyOK or len(elements[y]) > 0:
            if tempval > 0:
                return y
        if len(elements[y]) > 0 and tempval > 0:
            tempret = y
    return tempret

def doable (r1, r2, showDeets): # return value = # of cards to move. 0 = no match, -1 = asking too much
    cardsToMove = 0
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
        if inOrder(r1) and onlymove == len(elements[r1]):
            if showDeets:
                print ('OK, moved the already-sorted row, though this doesn\'t really change the game state.')
            return len(elements[r1])
        locmaxmove /= 2
        if showDeets and shouldPrint():
            print ("Only half moves here down to %d" % (locmaxmove))
        for n in range(len(elements[r1])-1, -1, -1):
            fromline += 1
            #print '1 debug stuff:',tocard(elements[r1][n]),n,fromline
            if n == 0:
                break
            #print '2 debug stuff:',tocard(elements[r1][n]),n,fromline
            if canPut(elements[r1][n], elements[r1][n-1]) == 0:
                break
            #print '3 debug stuff:',tocard(elements[r1][n]),n,fromline
    else:
        toTopCard = elements[r2][len(elements[r2])-1]
        #print str(elements[r2]) + "Row " + str(r2) + " Card " + tocard(toTopCard)
        for n in range(len(elements[r1])-1, -1, -1):
            fromline += 1
            if canPut(elements[r1][n], toTopCard):
                break
            if n == 0:
                return 0
            if canPut(elements[r1][n], elements[r1][n-1]) == 0:
                #print ("Can't put " + tocard(elements[r1][n]) + " on " + tocard(elements[r1][n-1]) + " or " + tocard(toTopCard));
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
                printCond ('Cutting down to ' + str(onlymove), False)
                return onlymove
        if onlymove < fromline:
            return onlymove
    if fromline > locmaxmove:
        if force == 1:
            if showDeets:
                if len(elements[r2]) > 0:
                    print ('Can\'t move to that non-empty, even with force.')
                    return -1
                printCond ("Cutting down to " + str(locmaxmove), False)
            return locmaxmove
        global cmdChurn
        if showDeets and not cmdChurn:
            print ("Not enough open. Have %d, need %d" % (locmaxmove, fromline))
        return -1
    return fromline

def maxMoveMod():
    base = 2
    myexp = .5
    for y in range (0,4):
        if (spares[y] == 0):
            base += 1
    for y in range (1,9):
        if (len(elements[y]) == 0):
            myexp *= 2
    return base * myexp

def slipUnder():
    slipProcess = True
    everSlip = False
    global cmdChurn
    while slipProcess:
        fi = firstEmptyRow()
        slipProcess = False
        curMove = len(moveList)
        if (fi == 0):
            for i in range (1,9):
                for j in range (0,4):
                    if slipProcess == False and (inOrder(i) or (len(elements[i]) == 1)) and canPut(elements[i][0], spares[j]):
                        #print ("Checking slip under %d %d %d %d %d" % (fi, i, j, elements[i][0], spares[j]))
                        if len(elements[i]) + spareUsed() <= 4:
                            temp = 0
                            elements[i].insert(0, spares[j])
                            spares[j] = 0
                            slipProcess = True
        else:
            for i in range(1,9):
                if slipProcess == False and ((len(elements[i]) > 0 and inOrder(i)) or (len(elements[i]) == 1)):
                    #print ("%d %d %d %d" % (i, len(elements[i]), inOrder(i), slipProcess))
                    for j in range (0,4):
                        #print ("%d %d %d %d" % (i, j, spares[j], canPut(elements[i][0], spares[j])))
                        if spares[j] > 0 and canPut(elements[i][0], spares[j]):
                            #print ("OK, giving a look %d -> %d | %d %d" % (i, fi, len(elements[i]), maxMoveMod()))
                            if len(elements[i]) <= maxMoveMod():
                                tst = chr(97+j) + str(fi)
                                resetChurn = not cmdChurn
                                cmdChurn = True
                                elements[fi].append(spares[j])
                                spares[j] = 0
                                shiftcards(i, fi, len(elements[i]))
                                if resetChurn:
                                    cmdChurn = False
                                slipProcess = True
                                everSlip = True #note the below is tricky because we sort of record the move and sort of don't. The best way to do this is to have, say "slip-" + tst as the move and it's only activated if slip (not an option right now) is turned off. Similarly for other options. But that's a lot of work.
                                #if curMove == len(moveList):
                                    #cmdChurn = False
                                    #print ("Tried move" + tst + ", failed.")
                                    #dumpInfo(-1)
                                    #printVertical()
                                break
    return everSlip

def dumpInfo(x):
    print ("Uh oh, big error avoided")
    print elements
    print backup
    print moveList
    print cmdList
    print cmdNoMeta
    print ("Spares: "% (spares));
    print ("Found: "% (found));
    if abs(x) == 2:
        printVertical()
    if x < 0:
        exit()
    return

def shiftcards(r1, r2, amt):
    elements[r2].extend(elements[r1][-amt:])
    del elements[r1][-amt:]

def usageGame():
    print ('========game moves========')
    print ('r(1-8a-d) sends that card to the foundation. r alone forces everything it can.')
    print ('p(1-8) moves a row as much as you can.')
    print ('p on its own tries to force everything if you\'re near a win.')
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
    print ('sw/ws saves on win, sp/ps saves position.')
    print ('+ = toggles double size, e = toggle autoshuffle.')
    print ('?/?g ?o ?m games options meta')
    
def usageMeta():
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
    print ('?/?g ?o ?m games options meta')

def firstEmptySpare():
    for i in range(0,4):
        if spares[i] == 0:
            return i
    return -1

def undoMoves(toUndo):
    if toUndo == 0:
        print('No moves undone.')
        return 0
    global moveList
    global totalUndo
    if len(moveList) == 0:
        print ('Nothing to undo.')
        return 0
    global elements
    elements = [row[:] for row in backup]
    global found
    found = [0, 0, 0, 0]
    global spares
    spares = [0, 0, 0, 0]
    for i in range (0,toUndo):
        moveList.pop()
        if totalUndo > -1:
            totalUndo += 1
    global inUndo
    inUndo = True
    global undoIdx
    for undoIdx in range (0,len(moveList)):
        readCmd(str(moveList[undoIdx]))
        if trackUndo == 1:
            inUndo = False
            printCards()
            inUndo = True
    undoIdx = 0
    inUndo = False
    checkFound()
    printCards()
    return 1

def loadGame(gameName):
    global time
    global totalUndo
    global totalReset
    global startTime
    original = open(savefile, "r")
    startTime = -1
    while True:
        line=original.readline()
        if line.startswith('moves='):
            continue
        if gameName == line.strip():
            for y in range (1,9):
                line=original.readline().strip()
                elements[y] = [int(i) for i in line.split()]
                backup[y] = [int(i) for i in line.split()]
            line=original.readline().strip()
            original.close()
            global moveList
            global inUndo
            inUndo = True
            initSide(0)
            if len(line) > 0 and line[0] != '#':
                moveList = line.split()
            else:
                moveList = []
            global undoIdx
            for undoIdx in range(0,len(moveList)):
                readCmd(str(moveList[undoIdx]))
                if trackUndo == 1:
                    inUndo = False
                    printCards()
                    inUndo = True
            inUndo = False
            checkFound()
            printCards()
            global totalFoundThisTime
            global cardlist
            totalFoundThisTime = 0
            cardlist = ''
            return 1
        if not line:
            print (re.sub(r'^.=', '', gameName) + ' save game not found.')
            original.close()
            return 0
    gn2 = gameName.replace(r'^.=', '')
    print ("Successfully loaded " + gn2)
    totalUndo = -1
    totalReset = -1
    return 0

def saveGame(gameName):
    savfi = open(savefile, "r")
    linecount = 0
    for line in savfi:
        linecount += 1
        if line.strip() == gameName:
            print ("Duplicate save game name found at line %d." % linecount)
            return
    savfi.close()
    with open(savefile, "a") as myfile:
        myfile.write(gameName + "\n")
        for y in range (1,9):
            myfile.write(' '.join(str(x) for x in backup[y]) + "\n")
        myfile.write(' '.join(moveList) + "\n")
        if savePosition:
            for y in range (1,9):
                myfile.write('# '.join(str(x) for x in elements[y]) + "\n")
        myfile.write("###end of " + gameName + "\n")
        myfile.write("#cmdNoMeta=" + ', '.join(cmdNoMeta) + '\n')
        myfile.write("#cmdList=" + ', '.join(cmdList) + '\n')
    gn2 = gameName.replace(r'^.=', '')
    print ("Successfully saved game as " + gn2)
    return 0

def reverseCard(myCard):
    retVal = 0
    for i in range(0,5):
        if i == 4:
            return -2
        if re.search(suits[i].lower(), myCard):
            retVal = 13 * i
            break
    for i in range (0,13):
        if re.search(cards[i].lower(), ' ' + myCard):
            retVal += (i + 1)
            return retVal
    return -1

def cardEval(myCmd):
    ary = re.split(' |,', myCmd)
    for word in ary:
        if word == 'e':
            continue
        sys.stdout.write(' ' + str(reverseCard(word)))
    print ("")
    return

def goBye():
    print ("Bye!")
    writeTimeFile()
    exit()

def readCmd(thisCmd):
    global debug
    global wonThisCmd
    global cmdChurn
    global vertical
    global dblSzCards
    global autoReshuf
    global elements
    global force
    global trackUndo
    global totalReset
    global saveOnWin
    global savePosition
    wonThisCmd = False
    prefix = ''
    force = 0
    checkFound()
    if thisCmd == '':
        for i in range (0,deliberateNuisanceRows):
            print "DELIBERATE NUISANCE"
        global input
        try: input = raw_input
        except NameError: pass
        name = input("Move:").strip()
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
            next
        return
    name = name.lower()
    if len(name) % 2 == 0 and len(name) >= 2:
        temp = len(name) / 2
        if name[:temp] == name[temp:]:
            print ("Looks like a duplicate command, so I'm cutting it in half.")
            name = name[temp:]
    if name == 'tu':
        trackUndo = 1 - trackUndo
        if not inUndo:
            print ("trackUndo now " + onoff[trackUndo])
        cmdNoMeta.pop()
        return
    if len(name) == 0:
        anyReshuf = False
        while reshuf(-1):
            anyReshuf = True
            next
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
        original = open(savefile, "r")
        o1 = re.compile(r'^s=')
        while True:
            line=original.readline()
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
            loadGame(re.sub(r'^l=', 's=', name))
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
        print ("Save on win is now %s." %("on" if saveOnWin else "off"))
        return
    if name == 'ps' or name == 'sp':
        cmdNoMeta.pop()
        savePosition = not savePosition
        print ("Save position with moves/start is now %s." %("on" if savePosition else "off"))
        return
    if name == 'u':
        undoMoves(1)
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
        while bestDumpRow() > 0:
            anyDump = 1
            newDump = bestDumpRow()
            print ("Dumping row " + str(newDump))
            if chains(newDump) == len(elements[newDump]) and not cmdChurn:
                shufwarn()
                return
            ripUp(newDump)
            if len(elements[newDump]) > 0:
                if inOrder(newDump) != 1: #or elements[newDump][0] % 13 != 0
                    print ("Row %d didn't unfold all the way." % (newDump))
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
        cmdChurn = False
        if debug:
            print ("Won this cmd: " + str(wonThisCmd))
        if anyDump == 0:
            print ("No rows found to dump.")
        elif not wonThisCmd:
            print (str(len(moveList)-oldMoves) + " moves total.")
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
            if not inUndo:
                print 'Move list,', len(moveList), 'moves so far:', (moveList)
            return
        if name == 'c':
            cmdNoMeta.pop()
            if not inUndo:
                print 'Command list,', len(cmdList), 'commands so far:', (cmdList)
            return
        if name == 'x':
            cmdNoMeta.pop()
            if not inUndo:
                print 'Trimmed command list,', len(cmdNoMeta), 'commands so far:', (cmdNoMeta)
            return
        if name == 's':
            if len(moveList) == 0:
                print ("You've made no moves yet.")
                return
            d1 = moveList[len(moveList)-1][0]
            temp = 0
            while (temp < len(moveList) - 1) and (d1 == moveList[len(moveList)-temp-1][0]):
                temp += 1
            undoMoves(temp)
            print ("Last " + str(temp) + " moves started with " + d1)
            return
        if not name.isdigit():
            print "Need to undo a number, or A for a list, S for same row as most recent move, or nothing. C=commands X=commands minus meta."
            return
        if int(name) > len(moveList):
            print ("Tried to do %d undo%s, can only undo %d." % (int(name), plur(int(name)), len(moveList)))
            return
        if int(name) > 10:
            if bigUndo:
                print ("This game doesn't allow undoing more than 10 at a time except with UND, because u78 would be kind of bogus if you changed your mind from undoing to moving.")
                return
            print ("UNDOing more than 10 moves.")
        undoMoves(int(name))
        return
    if name[0] == '/':
        debug = 1 - debug
        print ('debug', onoff[debug])
        cmdNoMeta.pop()
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
            print ('Now highlighting', cards[highlight-1])
        printCards()
        return
    if name[0] == '?':
        cmdNoMeta.pop()
        if len(name) is 1 or name[1].lower() == 'g':
            usageGame()
        elif name[1].lower() == 'm':
            usageMeta()
        elif name[1].lower() == 'o':
            usageOptions()
        else:
            print "Didn't recognize subflag", name[1].lower(), "so doing default of game command usage."
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
        totalReset += 1
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
        print ("Toggled dblSzCards to %s." % (onoff[dblSzCards]))
        printCards()
        return
    if name == 'e':
        cmdNoMeta.pop()
        autoReshuf = not autoReshuf
        print ("Toggled reshuffling to %s." % (onoff[autoReshuf]))
        reshuf(-1)
        printCards()
        return
    if name == 'v':
        cmdNoMeta.pop()
        vertical = not vertical
        print ("Toggled vertical view to %s." % (onoff[vertical]))
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
                elif spares[n1-97] > 0 and spares[n2-97] > 0:
                    cmdNoMeta.pop()
                    print ("Neither cell is empty, though shuffling does nothing.")
                    return
                elif spares[n1-97] == 0 and spares[n2-97] == 0:
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
            if anyDoableLimit(i):
                name = name + str(anyDoableLimit(i))
            elif anyDoable(i,0):
                name = name + str(anyDoable(i,0))
            elif chains(i) > 1 and canDump(i):
                if chains(i) == len(elements[i]) and not cmdChurn:
                    shufwarn()
                    return
                name = name + str(canDump(i))
                preverified = 1
            elif chains(i) == 1 and spareUsed() < 4:
                name = name + "e"
            elif firstEmptyRow() and spareUsed() == 4:
                if doable(i, firstEmptyRow(), 0) == len(elements[i]):
                    shufwarn()
                    return
                name = name + str(firstEmptyRow())
            elif anyDoable(i,1) and chains(i) < len(elements[i]):
                name = name + str(anyDoable(i,1))
            else:
                name = name + 'e'
            if shouldPrint():
                print ("New implied command %s." % (name))
        elif ord(name[0]) < 101 and ord(name[0]) > 96:
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
        if len(name) == 3 and name.isdigit: #special case for reversing a move e.g. 64 46 can become 646
            if name[0] == name[2]:
                readCmd(name[0] + name[1])
                readCmd(name[1] + name[0])
                return
        if name.isdigit():
            gotReversed = 1
            for jj in reversed(range(0,len(name)-1)):
                if wonThisCmd == False:
                    if name[jj] != name[jj+1]:
                        temp = name[jj] + name[len(name)-1]
                        print "Moving " + temp
                        readCmd(name[jj] + name[len(name)-1])
            if name.isdigit() and wonThisCmd == False:
                print ('Chained ' + str(len(moveList) - oldMoves) + ' of ' + str(len(name)-1) + ' moves successfully.')
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
        if tofound.isdigit():
            temprow = int(tofound)
        elif (ord(tofound) > 96) and (ord(tofound) < 101):
            tempspare = ord(tofound) - 97
        else:
            print "1-8 a-d are needed with R, or (nothing) tries to force everything."
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
            if foundable(elements[temprow][len(elements[temprow])-1]):
                found[(elements[temprow][len(elements[temprow])-1]-1)//13]+= 1
                elements[temprow].pop()
                if not inUndo:
                    moveList.append(name)
                slipUnder()
                checkFound()
                printCards()
                return
            print ('Sorry, found nothing.')
            cmdNoMeta.pop()
            return
        if tempspare > -1:
            if foundable(spares[tempspare]):
                found[(spares[tempspare]-1)//13]+= 1
                spares[tempspare] = 0
                print ('Moving from spares.')
                if not inUndo:
                    moveList.append(name)
                checkAgain = True
                while checkAgain:
                    checkAgain = False
                    checkAgain |= checkFound()
                    if force == 0:
                        checkAgain |= reshuf(-1)
                    pass
                checkFound()
                printCards()
            else:
                print ('Can\'t move from spares.') #/? 3s onto 2s with nothing else, all filled
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
        if ripUp(int(q2)):
            cmdChurn = False
            printCards()
            printFound()
        else:
            cmdChurn = False
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
            return ##### don't put anything above this
        if len(elements[t1]) == 0 and not inUndo:
            print ('Nothing to move from.')
            cmdNoMeta.pop()
            return
        if len(elements[t2]) == 0:
            if chains(t1) == len(elements[t1]) and not cmdChurn and force == 0 and onlymove == 0:
                cmdNoMeta.pop()
                shufwarn()
                return
        tempdoab = doable(t1,t2,1 - preverified)
        if tempdoab == -1:
            if not cmdChurn:
                print 'Not enough space.'
                cmdNoMeta.pop()
            return
        if tempdoab == 0:
            if inUndo:
                #print "Move", str(undoIdx), "(", thisCmd, t1, t2, preverified, ") seems to have gone wrong. Use ua."
                if undoIdx == 15:
                    printVertical()
                    exit
            else:
                print ('Those cards don\'t match up.')
                cmdNoMeta.pop()
            return
        oldchain = chains(t1)
        shiftcards(t1, t2, tempdoab)
        if not inUndo:
            if tempdoab < oldchain and len(elements[t2]) == 0:
                moveList.append(str(t1) + str(t2) + "-" + str(tempdoab))
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
    if (ord(name[0]) > 96) and (ord(name[0]) < 101): #a1 moves
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
        if (len(elements[myRow]) == 0) or (canPut(spares[mySpare], elements[myRow][len(elements[myRow])-1])):
            elements[myRow].append(spares[mySpare])
            spares[mySpare] = 0
            if not inUndo:
                moveList.append(name)
            reshuf(-1)
            slipUnder()
            checkFound()
            printCards()
            return
        print ("Can't put%s on%s." % (tocardX(spares[mySpare]), tocardX(elements[myRow][len(elements[myRow])-1])))
        cmdNoMeta.pop()
        return
    if (ord(name[1]) > 96) and (ord(name[1]) < 102): #1a moves, but also 1e can be A Thing
        if not name[0].isdigit():
            cmdNoMeta.pop()
            print ('First letter not recognized as a digit.')
            return
        myToSpare = firstEmptySpare()
        if myToSpare == -1:
            if not cmdChurn:
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
        if (len(elements[myRow]) == 0):
            print ('Empty from-row.')
            cmdNoMeta.pop()
            return
        if spares[myToSpare] > 0:
            for temp in range (0,4):
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
        if not inUndo:
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

###################################start main program

parseCmdLine()

if timeMatters and os.path.exists(timefile) and os.stat(timefile).st_size > 0:
    readTimeFile()

readOpts()

if annoyingNudge:
    try: input = raw_input
    except NameError: pass
    pwd = input("Type TIME WASTING AM I, in reverse word order, in here.\n").strip()
    #if pwd != "i am wasting time":
    if pwd != "I aM wAsTiNg TiMe":
        if pwd.lower() == "i am wasting time":
            print ("Remember to put it in alternate caps case! I did this on purpose, to make it that much harder.")
            exit()
        print ("Type I am wasting time, or you can't play.")
        exit()

initSide(0)
initCards()
printCards()

while win == 0:
    readCmd('')
endwhile
