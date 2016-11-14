######################################
#fc.py
#
#no frills Python Freecell game
#

#?? P (all) doesn't show what went to foundation
#> and < to bookend macro-type undoables. Skip if in Undo

import re
import sys
from random import shuffle
import time
import traceback

savefile = "fcsav.txt"
winFile = "fcwins.txt"

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

lastReset = 0
startTime = 0

#options to define. How to do better?
vertical = False
doubles = False
autoReshuf = False
savePosition = False
saveOnWin = False

lastscore = 0
highlight = 0

onlymove = 0

trackUndo = 0

breakMacro = 0

debug = 0

backup = []
elements = []

elements.append([])
elements.append([])
elements.append([])
elements.append([])
elements.append([])
elements.append([])
elements.append([])
elements.append([])
elements.append([])

name = ""

def tobool(x):
    if x == "False":
        return False
    return True

def printCond(myString, z):
    if not inUndo and not cmdChurn:
        print(myString)
    return

def shufwarn():
    if not cmdChurn and not inUndo:
        print ("That's just useless shuffling.")

def dumpTotal(q):
    retval = 0
    for z in range(0,len(elements[q])):
        if foundable(z):
            retval += 1
        if nexties(z):
            retval += 1
    return retval

def bestDumpRow():
    bestScore = -1
    bestRow = 0
    bestChains = 10
    for y in range (1,9):
        if chainNope(y) == 0:
            continue
        if canDump(y):
            if dumpTotal(y) > bestScore or (dumpTotal(y) == bestScore and chainTotal(y) < bestChains):
                bestRow = y
                bestChains = chainNope(y)
    return bestRow

def foundable(myc):
    if (myc-1) % 13 == found[(myc-1)//13]:
        return True
    return False

def nexties(myc):
    odds = (myc-1)//13
    if (myc-1) % 13 < found[(odds+1)%4]+2 and (myc-1) % 13 < found[(odds+3)%4]+2:
        return True
    return False

def ripUp(q):
    if q < 1 or q > 8:
        print ("Column/row needs to be 1-8.")
        return
    if len(elements[q]) == 0:
        print ("Already no elements.")
        return
    goAgain = 1
    global cmdChurn
    cmdChurn = True
    movesize = len(moveList)
    maxRun = 0
    while goAgain == 1 and len(elements[q]) > 0 and maxRun < 25:
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
        checkFound()
        if shouldReshuf:
            reshuf(-1)
        forceFoundation()
    if maxRun == 25:
        print ("Oops potential hang at " + str(q))
    checkFound()
    cmdChurn = False
    printCards()
    printFound()
    if (len(moveList) == movesize):
        print ("Nothing moved.")

def shouldPrint():
    global inUndo
    global cmdChurn
    if inUndo or cmdChurn:
        return False
    return True

def canDump(mycol):
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
    while tryAgain:
        tryAgain = 0
        for i in range(0,4):
            if i == xyz:
                continue
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
            

def inOrder(rowNum):
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
    retval = 0;
    for i in range (0,9):
        if chainNope(i) > 0:
            retval += 1
    return retval
    
def chainNope(rowcand):
    retval = 0
    thelast = 0
    for v in range (1,len(elements[rowcand])):
        mye = elements[rowcand][thelast]
        if nexties(elements[rowcand][v]) and foundable(elements[rowcand][v]):
            continue
        if not canPut(elements[rowcand][v], mye): # make sure it is not a (!)
            retval += 1
        thelast = v
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
                return i;
    return 0

def readOpts():
    global vertical
    global autoReshuf
    global doubles
    infile = "fcopt.txt";
    with open(infile) as f:
        for line in f:
            gotOne = 1
            if line[0] == '#': #ignore comments
                continue
            q=re.sub(r'.*=', '', line.rstrip())
            if "autoReshuf".lower() in line.lower():
                autoReshuf = tobool(q)
            if "savePosition".lower() in line.lower():
                savePosition = tobool(q)
            if "saveOnWin".lower() in line.lower():
                saveOnWin = tobool(q)
            if "vertical".lower() in line.lower():
                vertical = tobool(q)
            if "doubles".lower() in line.lower():
                doubles = tobool(q)
    if gotOne:
        print "Options file read."
        f.close()
    else:
        print "Failed to read options file."
    return

def sendOpts():
    o1 = re.compile(r'^vertical=')
    o2 = re.compile(r'^doubles=')
    o3 = re.compile(r'^autoReshuf=')
    o4 = re.compile(r'^saveOnWin=')
    o5 = re.compile(r'^savePosition=')
    infile = "fcopt.txt"
    fileString = ""
    gotOne = 0
    with open(infile) as f:
        for line in f:
            gotOne = 1
            if (o1.match(line)):
                fileString += "vertical=" + str(int(vertical)) + "\n"
            elif (o2.match(line)):
                fileString += "doubles=" + str(int(doubles)) + "\n"
            elif (o3.match(line)):
                fileString += "autoReshuf=" + str(int(autoReshuf)) + "\n"
            elif (o4.match(line)):
                fileString += "saveOnWin=" + str(int(saveOnWin)) + "\n"
            elif (o5.match(line)):
                fileString += "savePosition=" + str(int(savePosition)) + "\n"
            else:
                fileString += line
    if gotOne:
        f.close()
        f2 = open(infile, 'w')
        f2.write(fileString)
        print "Got options file, rewrote it."
        f2.close()
    else:
        print "Failed to get options file."
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

def foundable(thiscard):
    whichsuit = (thiscard - 1) // 13
    whichface = ((thiscard  - 1) % 13) + 1    
    if found[whichsuit] == whichface - 1:
        return 1
    return 0

def canPut(lower, higher):
    temp1 = lower - 1
    temp2 = higher - 1
    if temp1 % 13 == 0:
        return 0;
    if temp2 % 13 - temp1 % 13 != 1:
        return 0;
    if ((temp2 // 13) + (temp1 // 13)) % 2 == 1:
        return 1;
    return 0;

totalFoundThisTime = 0
cardlist = ''

def checkFound():
    retval = False
    needToCheck = 1
    global totalFoundThisTime
    global cardlist
    if not cmdChurn:
        totalFoundThisTime = 0
        cardlist = '';
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
                    elements[y].pop();
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
    if totalFoundThisTime > 0 and shouldPrint():
        sys.stdout.write(str(totalFoundThisTime) + ' card' + plur(totalFoundThisTime) + ' safely to foundation:' + cardlist + '\n')

def forceFoundation():
    global inUndo
    checkAgain = 1
    forceStr = ""
    while checkAgain:
        checkAgain = 0
        for row in range (1,9):
            if len(elements[row]) > 0:
                if foundable(elements[row][len(elements[row])-1]) == 1:
                    found[(elements[row][len(elements[row])-1]-1)//13]+= 1
                    forceStr = forceStr + tocardX(elements[row][len(elements[row])-1])
                    elements[row].pop()
                    checkAgain = 1
        for xx in range (0,4):
            if spares[xx]:
                #print ("Checking" + tocardX(spares[xx]))
                if foundable(spares[xx]):
                    forceStr = forceStr + tocardX(spares[xx])
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
    return retval;

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
    if vertical == 1:
        printVertical()
    else:
        printHorizontal()

def checkWinning():
    global input
    try: input = raw_input
    except NameError: pass
    finish = ""
    global cmdChurn
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
    while True:
        finish = input("You win! Play again (Y/N, U to undo)?").lower()
        if len(finish) > 0:
            if finish[0] == 'n':
                print("Bye!")
                exit()
            if finish[0] == 'y':
                initCards()
                initSide(0)
                totalUndo = 0
                totalReset = 0
                return 1
            if finish[0] == 'u':
                global inUndo
                inUndo = True
                undoMoves(1)
                inUndo = False
                return 0
        print ("Y or N (or U to undo). Case insensitive, cuz I'm a sensitive guy.")
        
def chains(myrow):
    if len(elements[myrow]) == 0:
        return 0;
    retval = 1
    mytemp = len(elements[myrow]) - 1
    while mytemp > 0:
        if canPut(elements[myrow][mytemp], elements[myrow][mytemp-1]):
            retval += 1
            if retval == 10:
                return "+"
            mytemp = mytemp - 1
        else:
            return retval
    return retval

def printVertical():
    count = 0
    for y in range (1,9):
        if chainNope(y) == 0:
            sys.stdout.write(' *' + str(chains(y)) + '*')
        else:
            sys.stdout.write(' ' + str(chains(y)) + '/' + str(chainNope(y)))
        if doubles:
            sys.stdout.write(' ')
    print ("")
    for y in range (1,9):
        sys.stdout.write(' ' + str(y) + ': ')
        if doubles:
            sys.stdout.write(' ')
    print ("")
    oneMoreTry = 1
    while oneMoreTry:
        thisline = ''
        secondLine = ''
        oneMoreTry = 0;
        for y in range (1,9):
            if len(elements[y]) > count:
                oneMoreTry = 1
                if doubles:
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
                if doubles:
                    thisline += ' '
                    secondLine += ' '
            else:
                thisline += '    '
                if doubles:
                    thisline += ' '
                    secondLine += '     '
        if oneMoreTry:
            print (thisline)
            if secondLine:
                print (secondLine)
        count+=1
    printOthers()

def printHorizontal():
    for y in range (1,9):
        sys.stdout.write(str(y) + ':')
        for z in elements[y]:
             sys.stdout.write(' ' + tocard(z))
        print
    printOthers()
    
def printOthers():
    checkWin()
    coolmove = ''
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
        for z2 in range (1,9):
            if z2 == z1:
                continue
            if len(elements[z2]) == 0:
                continue
            thisdo  = doable(z1,z2,0)
            if thisdo == -1:
                wackmove = wackmove + ' ' + str(z1)+str(z2)
            elif thisdo:
                tempmove = ' ' + str(z1)+str(z2)
                if thisdo >= len(elements[z1]):
                    canfwdmove = 1
                    coolmove = coolmove + tempmove
                elif not canPut(elements[z1][len(elements[z1])-thisdo], elements[z1][len(elements[z1])-thisdo-1]):
                    canfwdmove = 1
                    coolmove = coolmove + tempmove
                else:
                    tempmove = tempmove + '-'
                    latmove = latmove + tempmove
    for z1 in range (1,9):
        if len(elements[z1]):
            for z2 in range (0,4):
                if canPut(spares[z2], elements[z1][len(elements[z1])-1]):
                    coolmove = coolmove + ' ' + chr(z2+97) + str(z1)
                    canfwdmove = 1
    for z1 in range (0,4):
        if spares[z1] == 0:
            coolmove = coolmove + ' >' + chr(z1+97)
            canfwdmove = 1
    if wackmove:
        print ("Not enough room: " + str(wackmove))
    if coolmove and latmove:
        coolmove = coolmove + ' |'
    if (coolmove or latmove) and emmove:
        emmove = ' |' + emmove
    elif not coolmove and not latmove:
        coolmove = '(no row switches)'
    print ("Possible moves:" + coolmove + latmove + " (%d longest)" % (maxmove()))
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
            sys.stdout.write(' ---');
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
    for y in range (1,9):
        if len(elements[y]) > 0 and doable(ii, y, 0) > 0 and doable(ii, y, 0) < maxmove:
            return y
    return 0

def anyDoable (ii, emptyOK):
    for y in range (1,9):
        if doable(ii, y, 0):
            if emptyOK or len(elements[y]) > 0:
                return y
    return 0

def doable (r1, r2, showDeets): # return value = # of cards to move. 0 = no match, -1 = asking too much
    cardsToMove = 0
    fromline = 0
    locmaxmove = maxmove()
    if r1 < 1 or r2 < 1 or r1 > 8 or r2 > 8:
        print ("This shouldn't have happened, but one of the rows is invalid.")
        trackback.print_tb()
        return
    global onlymove
    if len(elements[r2]) == 0:
        if inOrder(r1) and onlymove > 0:
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
        for n in range(len(elements[r1])-1, -1, -1):
            fromline += 1
            if canPut(elements[r1][n], toTopCard):
                break
            if n == 0:
                return 0
            if canPut(elements[r1][n], elements[r1][n-1]) == 0:
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
                print ('Cutting down to', onlymove)
                return onlymove
        if onlymove < fromline:
            return onlymove
    if fromline > locmaxmove:
        if force == 1:
            if showDeets:
                if len(elements[r2]) > 0:
                    print ('Can\'t move to that non-empty, even with force.')
                    return -1
                print ("Cutting down to " + str(locmaxmove))
            return locmaxmove
        if showDeets:
            print ("Not enough open. Have %d, need %d" % (locmaxmove, fromline))
        return -1
    return fromline

def shiftcards(r1, r2, amt):
    elements[r2].extend(elements[r1][-amt:])
    del elements[r1][-amt:]

def usage():
    print ('r (1-8a-d) sends that card to the foundation. r alone forces everything it can.')
    print ('p (1-8) moves a row as much as you can.')
    print ('p on its own tries to force everything if you\'re near a win.')
    print ('lo/so loads/saves options.')
    print ('(1-8) attempts a \'smart move\' where the game tries progress, then shifting.')
    print ('(1-8)(1-8) = move a row, standard move.')
    print ('(1-8a-d) (1-8a-d) move to spares and back.')
    print ('f(1-8)(1-8) forces what you can (eg half of what can change between nonempty rows) onto an empty square.')
    print ('(1-8)(1-8)-(#) forces # cards onto a row, if possible.')
    print ('========options========')
    print ('v toggles vertical, + toggles card size (only vertical right now).')
    print ('u = undo, u1-u9 undoes that many moves.')
    print ('ua = shows current move/undo array.')
    print ('? = usage (this).')
    print ('empty command tries basic reshuffling and prints out the cards again.')

def firstEmptySpare():
    for i in range(0,4):
        if spares[i] == 0:
            return i
    return -1

readOpts()
initSide(0)
initCards()
printCards()

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
    for myCmd in moveList:
        readCmd(str(myCmd))
        if trackUndo == 1:
            inUndo = False
            printCards()
            inUndo = True
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
            for myCmd in moveList:
                readCmd(str(myCmd))
                if trackUndo == 1:
                    inUndo = False
                    printCards()
                    inUndo = True
            inUndo = False
            checkFound()
            printCards()
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

def readCmd(thisCmd):
    global cmdChurn
    global vertical
    global doubles
    global autoReshuf
    global elements
    global force
    global trackUndo
    global totalReset
    global saveOnWin
    prefix = ''
    force = 0
    checkFound()
    if thisCmd == '':
        global input
        try: input = raw_input
        except NameError: pass
        name = input("Move:").strip()
        if name[:2] == 'e ':
            cardEval(name)
            return
        if name[:2] != 'l=' and name[:2] != 's=':
            name = name.replace(' ', '')
    else:
        name = thisCmd
    name = name.lower()
    if len(name) % 2 == 0 and len(name) >= 2:
        temp = len(name) / 2
        if name[:temp] == name[temp:]:
            print ("Looks like a duplicate command, so I'm cutting it in half.")
            name = name[temp:]
    if name == 'tu':
        trackUndo = 1 - trackUndo
        print ("trackUndo now " + onoff[trackUndo])
        return
    if len(name) == 0:
        while reshuf(-1):
            next
        printCards()
        return
    global onlymove
    onlymove = 0
    if len(name) > 3:
        if name[2] == '-':
            onlymove = re.sub(r'.*-', '', name)
            if not onlymove.isdigit:
                print ('Format is ##-#.')
                return
            onlymove = int(onlymove)
            name = re.sub(r'-.*', '', name)
    #### saving/loading comes first.
    if name[0] == 'l' and name[1] == '=':
        loadGame(re.sub(r'^l=', 's=', name))
        return
    if name[0] == 's' and name[1] == '=':
        saveGame(name.strip())
        return
    if name == "lo":
        readOpts()
        return
    if name == "so":
        sendOpts()
        return
    if name == 'q':
        print ("QU needed to quit.")
        return
    if name == 'qu':
        print ("Bye!")
        exit()
    if name == 'ws' or name == 'sw':
        saveOnWin = not saveOnWin
        print ("Save on win is now %s." %("on" if saveOnWin else "off"))
        return
    if name == 'ps' or name == 'sp':
        savePosition = not savePosition
        print ("Save position with moves/start is now %s." %("on" if savePosition else "off"))
        return
    if name == 'u':
        undoMoves(1)
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
            if breakMacro == 1:
                breakMacro = 0
                break
            checkFound()
        if anyDump == 0:
            print ("No rows found to dump.")
        else:
            print (str(len(moveList)-oldMoves) + " moves total.")
        return
    if "u" in name:
        name = name.replace("u", "")
        if name == 'a':
            print (moveList)
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
        if not name.isdigit:
            print "Need to undo a number, or A for a list, S for same row as most recent move, or nothing."
            return
        if int(name) > len(moveList):
            print ("Tried to do %d undos, can only undo %d." % (int(temp), len(moveList)))
            return
        undoMoves(int(name))
        return
    if name[0] == '/':
        debug = 1 - debug
        print ('debug', onoff[debug])
        return
    if name[0] == 'h':
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
        usage()
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
    if name == "-":
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
        print ('Maximum card length moves: ', maxmove())
        return
    if name == "":
        printCards()
        return
    if name == '+':
        doubles = not doubles
        print ("Toggled doubles to %s." % (onoff[doubles]))
        printCards()
        return
    if name == 'e':
        autoReshuf = not autoReshuf
        print ("Toggled reshuffling to %s." % (onoff[autoReshuf]))
        reshuf(-1)
        printCards()
        return
    if name == 'v':
        vertical = 1 - vertical
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
                    print ("Neither cell is empty, though shuffling does nothing.")
                    return
                elif spares[n1-97] == 0 and spares[n2-97] == 0:
                    print ("Both cells are empty, so this does nothing.")
                    return
                else:
                    print ('Shuffling between empty squares does nothing, so I\'ll just pass here.')
                    return
    if len(name) == 1:
        if name.isdigit():
            i = int(name)
            if i > 8 or i < 1:
                print ('Need 1-8.')
                return
            if len(elements[i]) is 0:
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
                print ('No empty row/column to drop from spares.')
                return
        else:
            print ("Unknown 1-letter command.")
            return
    #### two letter commands below here.
    if len(name) > 2:
        print ('Only 2 chars per command.')
        return
    if len(name) < 2:
        print ('Must have 2 chars per command.')
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
            return
        if temprow > -1:
            if temprow > 8 or temprow < 1:
                print ('Not a valid row.')
                return
            if len(elements[temprow]) == 0:
                print ('Empty row.')
                return
            if foundable(elements[temprow][len(elements[temprow])-1]) == 1:
                found[(elements[temprow][len(elements[temprow])-1]-1)//13]+= 1
                elements[temprow].pop()
                if not inUndo:
                    moveList.append(name)
                checkFound()
                printCards()
                return
            print ('Sorry, found nothing.')
            return
        if tempspare > -1:
            if foundable(spares[tempspare]):
                found[(spares[tempspare]-1)//13]+= 1
                spares[tempspare] = 0;
                print ('Moving from spares.')
                if not inUndo:
                    moveList.append(name)
                checkFound()
                printCards()
            else:
                print ('Can\'t move from spares.') #/? 3s onto 2s with nothing else, all filled
            return
        print ('Must move 1-8 or a-d.')
        return
    if name[0] == 'p' or name[1] == 'p':
        q2 = (name.replace("p", ""))
        if not q2.isdigit():
            print ("p command requires a digit.")
            return
        ripUp(int(q2))
        return
    if name[0].isdigit() and name[1].isdigit():
        t1 = int(name[0])
        t2 = int(name[1])
        if t1 == t2:
            print ('Moving a row to itself does nothing.')
            return
        if len(elements[t1]) == 0 and not inUndo:
            print ('Nothing to move from.')
            return
        if len(elements[t2]) == 0:
            if chains(t1) == len(elements[t1]) and not cmdChurn:
                shufwarn()
                return
        if t1 < 1 or t2 < 1 or t1 > 8 or t2 > 8:
            print ("Need digits from 1-8.")
            return
        tempdoab = doable(t1,t2,1 - preverified)
        if tempdoab == -1:
            #print 'Not enough space.'
            return
        if tempdoab == 0:
            if inUndo:
                print ("Move " + str(len(moveList)) + " seems to have gone wrong. Use ua.")
            else:
                print ('Those cards don\'t match up.')
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
            pass
        printCards()
        return
    if (ord(name[0]) > 96) and (ord(name[0]) < 101): #a1 moves
        mySpare = ord(name[0]) - 97
        if spares[mySpare] == 0:
            print ('Nothing in slot %d.' % (mySpare + 1))
            return
        if not name[1].isdigit():
            print ('Second letter not recognized.')
            return
        myRow = int(name[1])
        if myRow < 1 or myRow > 8:
            print ('To row must be between 1 and 8.')
            return
        if (len(elements[myRow]) == 0) or (canPut(spares[mySpare], elements[myRow][len(elements[myRow])-1])):
            elements[myRow].append(spares[mySpare])
            spares[mySpare] = 0
            if not inUndo:
                moveList.append(name)
            reshuf(-1)
            checkFound()
            printCards()
            return
        print ("Can't put%s on%s." % (tocardX(spares[mySpare]), tocardX(elements[myRow][len(elements[myRow])-1])))
        return
    if (ord(name[1]) > 96) and (ord(name[1]) < 102): #1a moves, but also 1e can be A Thing
        if not name[0].isdigit():
            print ('First letter not recognized as a digit.')
            return
        myToSpare = firstEmptySpare()
        if myToSpare == -1:
            if not cmdChurn:
                print ('Nothing empty to move to. To which to move.')
            return
        if name[1] != 'e':
            myToSpare = ord(name[1]) - 97
        myRow = int(name[0])
        if myRow < 1 or myRow > 8:
            print ('From row must be between 1 and 8.')
            return
        if (len(elements[myRow]) == 0):
            print ('Empty from-row.')
            return
        if spares[myToSpare] > 0:
            for temp in range (0,4):
                if spares[(myToSpare + temp) % 4] <= 0:
                    print ("Spare %d already filled, picking %d instead" % (myToSpare + 1, (myToSpare + temp) % 4 + 1))
                    myToSpare += temp
                    break
            if spares[myToSpare] > 0:
                print ("Oops, I somehow see all-full and not all full at the same time.")
                return
        spares[myToSpare] = elements[myRow].pop()
        if not inUndo:
            moveList.append(name)
        tempMoveSize = -1
        while tempMoveSize < len(moveList):
            tempMoveSize = len(moveList)
            checkFound()
            reshuf(myToSpare)
        printCards()
        return
    print (name + ' not recognized, displaying usage.')
    usage()

while win == 0:
    readCmd('')
endwhile
