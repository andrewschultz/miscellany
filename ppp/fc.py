import sys
from random import shuffle

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

win = 0

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
    retval = 0;
    for y in range (1,9):
        if len(elements[y]) > 0:
            while elements[y][len(elements[y])-1] % 13 == (1 + found[(elements[y][len(elements[y])-1]-1)/13]) % 13:
                retval = 1;
                print tocard(elements[y][len(elements[y])-1]), 'to foundation.'
                found[(elements[y][len(elements[y])-1]-1)/13] = found[(elements[y][len(elements[y])-1]-1)/13] + 1
                elements[y].pop();
                if len(elements[y]) == 0:
                    break;
    for y in range (0,4):
        if spares[y] > 0:
            if spares[y] % 13 == 1 + found[(spares[y]-1)/13]:
                found[(spares[y]-1)/13] = found[(spares[y]-1)/13] + 1
                spares[y] = 0
                print 'Popped', str(y+1), 'from spares.'
    return retval

def checkWin():
    for y in range (0,4):
        print y,found[y]
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
                break;
            elements[z].append(x.pop())

def tocard( cardnum ):
    if cardnum == 0:
        return '---'
    temp = cardnum - 1
    retval = '' + cards[temp % 13] + suits[temp / 13]
    return retval;

def printCards():
    for y in range (1,9):
        sys.stdout.write(str(y) + ':')
        for z in elements[y]:
             sys.stdout.write(' ' + tocard(z))
        print
    sys.stdout.write('Empty slots:')
    for y in range (0,4):
        sys.stdout.write(' ' + tocard(spares[y]))
    sys.stdout.write('\nFoundation:')
    for y in range (0,4):
        if found[y] == 0:
            sys.stdout.write(' ---');
        else:
            sys.stdout.write(' ' + tocard(found[y] + y * 13))
    print
    checkWin()

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
    if name == "":
        printCards()
        continue
    if len(name) > 2:
        print 'Only 2 chars per command.'
        continue
    if len(name) > 1:
        if name[0].isdigit() and name[1].isdigit():
            t1 = int(name[0])
            t2 = int(name[1])
            if len(elements[t1]) == 0:
                print 'Nothing to move from.'
                continue
            if len(elements[t2]) == 0 or canPut(elements[t1][len(elements[t1])-1], elements[t2][len(elements[t2])-1]):
                elements[t2].append(elements[t1][len(elements[t1])-1])
                elements[t1].pop()
                checkFound()
                printCards()
                continue
            print 'Can\'t do extended moves.'
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
        print name[0]
        print name[1]
endwhile
