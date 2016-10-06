######################################
#fc.py
#
#no frills Python Freecell game
#

import re
import sys
from random import shuffle

onoff = ['off', 'on']

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

moveList = []

win = 0
inUndo = 0

#options to define. How to do better?
vertical = 0

highlight = 0

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
    infile = "fcopt.txt";
    with open(infile) as f:
        for line in f:
            q=re.sub(r'.*=', '', line.rstrip())
            if "vertical" in line:
                vertical = int(q)
                return
    exit()

def initSide():
    global spares
    spares = [0, 0, 0, 0]
    global found
    found = [0, 0, 0, 0]
    global highlight
    highlight = 0
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
    whichsuit = (thiscard - 1) / 13
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
    if ((temp2 / 13) + (temp1 / 13)) % 2 == 1:
        return 1;
    return 0;

def checkFound():
    retval = 0
    needToCheck = 1
    totalFoundThisTime = 0
    cardlist = '';
    while needToCheck:
        needToCheck = 0
        for y in range (1,9):
            if len(elements[y]) > 0:
                while elements[y][len(elements[y])-1] % 13 == (1 + found[(elements[y][len(elements[y])-1]-1)/13]) % 13:
                    basesuit = (elements[y][len(elements[y])-1]-1)/13
                    if found[(basesuit+1) % 4] < found[basesuit] - 1:
                        break
                    if found[(basesuit+3) % 4] < found[basesuit] - 1:
                        break
                    needToCheck = 1;
                    totalFoundThisTime += 1
                    found[(elements[y][len(elements[y])-1]-1)/13] = found[(elements[y][len(elements[y])-1]-1)/13] + 1
                    cardlist = cardlist + tocardX(elements[y][len(elements[y])-1])
                    elements[y].pop();
                    if len(elements[y]) == 0:
                        break
        for y in range (0,4):
            #print 'checking ',y,tocard(spares[y])
            if spares[y] > 0:
                if (spares[y]-1) % 13 == found[(spares[y]-1)/13]:
                    sparesuit = (spares[y]-1)/13
                    if debug:
                        print 'position', y, 'suit' ,suits[(spares[y]-1)/13], 'card' ,tocard(spares[y])
                    if found[(sparesuit+3)%4] < found[sparesuit] - 1:
                        continue
                    if found[(sparesuit+1)%4] < found[sparesuit] - 1:
                        continue
                    cardlist = cardlist + tocardX(spares[y])
                    found[(spares[y]-1)/13] = found[(spares[y]-1)/13] + 1
                    spares[y] = 0
                    needToCheck = 1
    if totalFoundThisTime > 0 and inUndo == 0:
        sys.stdout.write(str(totalFoundThisTime) + ' card' + plur(totalFoundThisTime) + ' safely to foundation: ' + cardlist + '\n')

def checkWin():
    for y in range (0,4):
        #print y,found[y]
        if found[y] != 13:
            return 0;
    print 'You win!'
    exit()
    
def initCards():
    x = range(1,53)
    shuffle(x)
    for y in range(0,7):
        for z in range(1,9):
            if len(x) == 0:
                break
            elements[z].append(x.pop())

def tocard( cardnum ):
    if cardnum == 0:
        return '---'
    temp = cardnum - 1
    retval = '' + cards[temp % 13] + suits[temp / 13]
    return retval;

def tocardX (cnum):
    if (cnum % 13 == 10):
        return ' ' + tocard(cnum)
    return tocard(cnum)

def printCards():
    if inUndo == 1:
        return
    if vertical == 1:
        printVertical()
    else:
        printHorizontal()
 
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
        sys.stdout.write('(' + str(chains(y)) + ') ')
    print
    for y in range (1,9):
        sys.stdout.write(' ' + str(y) + ': ')
    print
    oneMoreTry = 1
    while oneMoreTry:
        thisline = ''
        oneMoreTry = 0;
        for y in range (1,9):
            if len(elements[y]) > count:
                thisline += str(tocard(elements[y][count]))
                if ((elements[y][count]-1) % 13) == found[(elements[y][count]-1)/13]:
                    thisline += '*'
                elif highlight and (((elements[y][count]-1) % 13) == highlight - 1):
                    thisline += '+'
                else:
                    thisline += ' '
                oneMoreTry = 1
            else:
                thisline += '    '
        if oneMoreTry:
            print thisline
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
    canmove = ''
    wackmove = ''
    for z1 in range (1,9):
        if len(elements[z1]) == 0:
            canmove = canmove + ' E' + str(z1)
            continue
        for z2 in range (1,9):
            if z2 == z1:
                continue
            if len(elements[z2]) == 0:
                continue
            if doable(z1,z2,0) == -1:
                wackmove = wackmove + ' ' + str(z1)+str(z2)
            elif doable(z1,z2,0):
                canmove = canmove + ' ' + str(z1)+str(z2)
    for z1 in range (1,9):
        if len(elements[z1]):
            for z2 in range (0,4):
                if canPut(spares[z2], elements[z1][len(elements[z1])-1]):
                    canmove = canmove + ' ' + chr(z2+97) + str(z1)
    for z1 in range (0,4):
        if spares[z1] == 0:
            canmove = canmove + ' r' + chr(z1+97)
    if wackmove:
        print 'Not enough room:', str(wackmove)
    if canmove:
        sys.stdout.write('Possible moves: ' + str(canmove) + ' (' + str(maxmove()) + ')\n')
    else:
        print 'Uh oh. You\'re probably lost.'
    sys.stdout.write('Empty slots:')
    for y in range (0,4):
        sys.stdout.write(' ' + tocard(spares[y]))
    sys.stdout.write('\nFoundation: ')
    foundscore = 0
    for y in [0, 2, 1, 3]:
        foundscore += found[y]
        if found[y] == 0:
            sys.stdout.write(' ---');
        else:
            sys.stdout.write(' ' + tocard(found[y] + y * 13))
    print ' (' + str(foundscore) + ' points)'

def doable (r1, r2, showDeets):
    cardsToMove = 0
    fromline = 0
    locmaxmove = maxmove()
    if len(elements[r1]) == 0:
        if showDeets:
            print 'Tried to move from empty.'
        return 0
    if len(elements[r2]) == 0:
        locmaxmove /= 2
        if showDeets:
            print 'Only half moves here down to', locmaxmove
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
    if fromline > locmaxmove:
        if force == 1:
            if showDeets:
                print 'Cutting down to ', locmaxmove
            return locmaxmove
        if showDeets:
            print 'Not enough open. Have',locmaxmove,'need', fromline
        return -1
    return fromline
    return 0

def shiftcards(r1, r2, amt):
    elements[r2].extend(elements[r1][-amt:])
    del elements[r1][-amt:]

def usage():
    print 'r (1-8a-d) sends that card to the foundation'
    print '1-8 1-8 = move a row, standard move'
    print '(1-8a-d) (1-8a-d) move to spares and back'
    print 'u = usage (this)'

def firstEmptySpare():
    for i in range(0,4):
        if spares[i] == 0:
            return i
    return -1

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

readOpts()
initSide()
initCards()
printCards()

debug = 0

backup = [row[:] for row in elements]

name = ""

def loadGame(gameName):
    #print 'looking for', gameName
    original = open("fcsav.txt", "r")
    while True:
        line=original.readline()
        if gameName == line.strip():
            for y in range (1,9):
                line=original.readline().strip()
                elements[y] = [int(i) for i in line.split()]
                backup[y] = [int(i) for i in line.split()]
            line=original.readline().strip()
            moveList = line.split()
            global inUndo
            inUndo = 1
            for myCmd in moveList:
                readCmd(str(myCmd))
            inUndo = 0
            printCards()
            return 1
        if not line:
            print re.sub(r'^.=', '', gameName) , 'save game not found.'
            return 0
    return 0

def saveGame(gameName):
    with open("fcsav.txt", "a") as myfile:
        myfile.write(gameName + "\n")
        for y in range (1,9):
            myfile.write(' '.join(str(x) for x in backup[y]) + "\n")
        myfile.write(' '.join(moveList) + "\n")
        myfile.write("###end of " + gameName + "\n")
    return 0

def readCmd(thisCmd):
    global vertical
    global elements
    global force
    force = 0
    checkFound()
    if thisCmd == '':
        name = raw_input("Move:").strip()
    else:
        name = thisCmd
    if len(name) == 0:
        printCards()
        return
    if name[0] == '/':
        debug = 1 - debug
        print 'debug', onoff[debug]
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
                print 'Need a number, or AJQK.'
                return
        if int(name) < 1 or int(name) > 13:
            print 'Need 1-13.'
            return
        global highlight
        highlight = int(name)
        if highlight == 0:
            print 'Highlighting off.'
        else:
            print 'Now highlighting', cards[highlight-1]
        printCards()
        return
    if name[0] == 'u':
        usage()
        return
    if name[0] == 'f':
        name = name.replace("f", "")
        force = 1
    if name == "-":
        elements = [row[:] for row in backup]
        initSide()
        printCards()
        checkFound()
        return
    if name == "?":
        print 'Maximum card length moves: ', maxmove()
        return
    if name == "":
        printCards()
        return
    if name == 'v':
        vertical = 1 - vertical
        printCards()
        return
    #### mostly meta commands above here. Keep them there.
    if len(name) == 1:
        if name.isdigit():
            i = int(name)
            if i > 8 or i < 1:
                print 'Need 1-8.'
                return
            if len(elements[i]) is 0:
                print 'Acting on an empty row.'
                return
            if chains(i) > 1 and firstMatchableRow(elements[i][len(elements[i])-1]):
                name = name + str(firstMatchableRow(elements[i][len(elements[i])-1]))
            elif firstEmptyRow() and spareUsed() == 4:
                if doable(i, firstEmptyRow(), 0) == len(elements[i])
                    print "That's just useless shuffling."
                    return
                name = name + str(firstEmptyRow())
            else:
                name = name + 'e'
            print 'New implied command', name
        elif ord(name[0]) < 101 and ord(name[0]) > 96:
            if firstMatchableRow(spares[ord(name[0]) - 97]) > 0:
                name = name + str(firstMatchableRow(spares[ord(name[0]) - 97]))
            elif firstEmptyRow() > 0:
                name = name + str(firstEmptyRow())
            else:
                print 'No empty row/column to drop from spares.'
                return
        else:
            print "Unknown 1-letter command."
            return
    #### two letter commands below here.
    if name[0] == 'l' and name[1] == '=':
        loadGame(re.sub(r'^l=', 's=', name))
        return
    if name[0] == 's' and name[1] == '=':
        saveGame(name.strip())
        return
    #### saving comes first.
    if name == "ua":
        print moveList
        return
    if len(name) > 2:
        print 'Only 2 chars per command.'
        return
    if len(name) < 2:
        print 'Must have 2 chars per command.'
        return
    if name[0] == 'r' or name[1] == 'r':
        tofound = name.replace("r", "")
        temprow = -1
        if tofound.isdigit():
            temprow = int(tofound)
        elif (ord(tofound) > 96) and (ord(tofound) < 101):
            tempspare = ord(tofound) - 97
        if temprow > -1:
            if temprow > 8 or temprow < 1:
                print 'Not a valid row.'
                return
            if len(elements[temprow]) == 0:
                print 'Empty row.'
                return
            if foundable(elements[temprow][len(elements[temprow])-1]) == 1:
                found[(elements[temprow][len(elements[temprow])-1]-1)/13]+= 1
                elements[temprow].pop()
                moveList.append(name)
                checkFound()
                printCards()
                return
            print 'Sorry, found nothing.'
            return
        if tempspare > -1:
            if foundable(spares[tempspare]):
                found[(spares[tempspare]-1)/13]+= 1
                spares[tempspare] = 0;
                print 'Moving from spares.'
                moveList.append(name)
                checkFound()
                printCards()
            else:
                print 'Can\'t move from spares.' #/? 3s onto 2s with nothing else, all filled
            return
        print 'Must move 1-8 or a-d.'
        return
    if name[0].isdigit() and name[1].isdigit():
        t1 = int(name[0])
        t2 = int(name[1])
        if len(elements[t1]) == 0:
            print 'Nothing to move from.'
            return
        tempdoab = doable(t1,t2,1)
        if tempdoab == -1:
            #print 'Not enough space.'
            return
        if tempdoab == 0:
            print 'Those cards don\'t match up.'
            return
        shiftcards(t1, t2, tempdoab)
        moveList.append(name)
        checkFound()
        printCards()
        return
    if (ord(name[0]) > 96) and (ord(name[0]) < 101): #a1 moves
        mySpare = ord(name[0]) - 97
        if spares[mySpare] == 0:
            print 'Nothing in slot' , name[0]
            return
        if not name[1].isdigit():
            print 'Second letter not recognized.'
            return
        myRow = int(name[1])
        if myRow < 1 or myRow > 8:
            print 'To row must be between 1 and 8.'
            return
        if (len(elements[myRow]) == 0) or (canPut(spares[mySpare], elements[myRow][len(elements[myRow])-1])):
            elements[myRow].append(spares[mySpare])
            spares[mySpare] = 0
            moveList.append(name)
            checkFound()
            printCards()
            return
        print 'Can\'t put ', spares[mySpare], 'on', elements[myRow][len(elements[myRow])-1]
        return
    if (ord(name[1]) > 96) and (ord(name[1]) < 102): #1a moves, but also 1e can be A Thing
        if name[1] == 'e':
            myToSpare = firstEmptySpare()
            if myToSpare == -1:
                print 'Nothing empty to move to. To which to move.'
                return
        else:
            myToSpare = ord(name[1]) - 97
        if not name[0].isdigit():
            print 'First letter not recognized.'
            return
        myRow = int(name[0])
        if spares[myToSpare] > 0:
            print 'Spare', myToSpare, 'already filled.'
            return
        if myRow < 1 or myRow > 8:
            print 'From row must be between 1 and 8.'
            return
        if (len(elements[myRow]) == 0):
            print 'Empty from-row.'
            return
        spares[myToSpare] = elements[myRow].pop()
        moveList.append(name)
        checkFound()
        printCards()
        return
    print name,'not recognized, displaying usage.'
    usage()

while win == 0:
    readCmd('')
endwhile


#?? possible moves show restricted, put in new line 