######################################
#fc.py
#
#no frills Python Freecell game
#

import sys
from random import shuffle

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

win = 0

vertical = 0

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
            if spares[y] > 0:
                if (spares[y]-1) % 13 == found[(spares[y]-1)/13]:
                    sparesuit = (spares[y]-1)/13
                    print 'position', y, 'suit' ,suits[(spares[y]-1)/13], 'card' ,tocard(spares[y])
                    if found[(sparesuit+3)%4] < found[sparesuit] - 1:
                        break
                    if found[(sparesuit+1)%4] < found[sparesuit] - 1:
                        break
                    cardlist = cardlist + tocardX(spares[y])
                    found[(spares[y]-1)/13] = found[(spares[y]-1)/13] + 1
                    spares[y] = 0
                    needToCheck = 1
    if totalFoundThisTime == 1:
        print totalFoundThisTime, 'card safely to foundation:',cardlist
    elif totalFoundThisTime > 0:
        print totalFoundThisTime, 'cards safely to foundation:',cardlist

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
    if vertical == 1:
        printVertical()
    else:
        printHorizontal()
 
def printVertical():
    count = 0
    for y in range (1,9):
        sys.stdout.write('  ' + str(y) + ' ')
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
    sys.stdout.write('Empty slots:')
    for y in range (0,4):
        sys.stdout.write(' ' + tocard(spares[y]))
    sys.stdout.write('\nFoundation: ')
    for y in [0, 2, 1, 3]:
        if found[y] == 0:
            sys.stdout.write(' ---');
        else:
            sys.stdout.write(' ' + tocard(found[y] + y * 13))
    print
    checkWin()

def doable (r1, r2):
    cardsToMove = 0
    fromline = 0
    locmaxmove = maxmove()
    if len(elements[r1]) == 0:
        print 'Tried to move from empty.'
        return 0
    if len(elements[r2]) == 0:
        locmaxmove /= 2
        print 'Only half moves here down to', locmaxmove
        for n in range(len(elements[r1])-1, 0, -1):
            fromline += 1
            if n == 0:
                break
            if canPut(elements[r1][n], elements[r1][n-1]) == 0:
                break
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
        print 'Not enough open. Have',locmaxmove,'need', fromline
        return -1
    return fromline
    return 0

def shiftcards(r1, r2, amt):
    elements[r2].extend(elements[r1][-amt:])
    del elements[r1][-amt:]

spares = [0, 0, 0, 0]
found = [0, 0, 0, 0]


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


initCards()
printCards()

name = ""

while win == 0:
    checkFound()
    name = raw_input("Move:")
    if name == "?":
        print 'Maximum card length moves: ', maxmove()
        continue
    if name == "":
        printCards()
        continue
    if name == 'v':
        vertical = 1 - vertical
        printCards()
        continue
    if len(name) > 2:
        print 'Only 2 chars per command.'
        continue
    if len(name) < 2:
        print 'Must have 2 chars per command.'
        continue
    if name[0] == 'r' or name[1] == 'r':
        tofound = name.replace("r", "")
        temprow = -1
        if name[1].isdigit():
            temprow = int(name[1])
        elif name[0].isdigit():
            temprow = int(name[0])
        elif (ord(name[0]) > 96) and (ord(name[0]) < 101):
            tempspare = ord(name[0]) - 97
        elif (ord(name[1]) > 96) and (ord(name[1]) < 101):
            tempspare = ord(name[1]) - 97
        if temprow > -1:
            if temprow > 8 or temprow < 1:
                print 'Not a valid row.'
                continue
            if len(elements[temprow]) == 0:
                print 'Empty row.'
                continue
            if foundable(elements[temprow][len(elements[temprow])-1]) == 1:
                found[(elements[temprow][len(elements[temprow])-1]-1)/13]+= 1
                elements[temprow].pop()
                checkFound()
                printCards()
                continue
            print 'Sorry, found nothing.'
            continue
        if tempspare > -1:
            if foundable(spares[tempspare]):
                found[(spares[tempspare]-1)/13]+= 1
                spares[tempspare] = 0;
                print 'Moving from spares.'
            else:
                print 'Can\'t move from spares.' #/? 3s onto 2s with nothing else, all filled
            continue
        print 'Must move 1-8 or a-d.'
        continue
    if name[0].isdigit() and name[1].isdigit():
        t1 = int(name[0])
        t2 = int(name[1])
        if len(elements[t1]) == 0:
            print 'Nothing to move from.'
            continue
        tempdoab = doable(t1,t2)
        if tempdoab == -1:
            print 'Not enough space.'
            continue
        if tempdoab == 0:
            print 'Those cards don\'t match up.'
            continue
        shiftcards(t1, t2, tempdoab)
        checkFound()
        printCards()
        continue
    if (ord(name[0]) > 96) and (ord(name[0]) < 101): #a1 moves
        mySpare = ord(name[0]) - 97
        if spares[mySpare] == 0:
            print 'Nothing in slot' , name[0]
            continue
        myRow = int(name[1])
        if myRow < 1 or myRow > 8:
            print 'To row must be between 1 and 8.'
            continue
        if (len(elements[myRow]) == 0) or (canPut(spares[mySpare], elements[myRow][len(elements[myRow])-1])):
            elements[myRow].append(spares[mySpare])
            spares[mySpare] = 0
            checkFound()
            printCards()
            continue
        print 'Can\'t put ', spares[mySpare], 'on', elements[myRow][len(elements[myRow])-1]
        continue;
    if (ord(name[1]) > 96) and (ord(name[1]) < 101):
        myRow = int(name[0])
        if spares[ord(name[1]) - 97] > 0:
            print 'Already filled.'
            continue
        if myRow < 1 or myRow > 8:
            print 'From row must be between 1 and 8.'
            continue
        if (len(elements[myRow]) == 0):
            print 'Empty from-row.'
            continue
        spares[ord(name[1]) - 97] = elements[myRow].pop()
        checkFound()
        printCards()
endwhile
