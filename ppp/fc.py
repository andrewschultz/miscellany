import sys
from random import shuffle

suits = ['C', 'D', 'H', 'S']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

win = 0

def checkFound():
    retval = 0;
    for y in range (0,8):
        while elements[y][len(elements[y])-1] % 13 == 1 + found[(elements[y][len(elements[y])-1]-1)/13]:
            retval = 1;
            print tocard(elements[y][len(elements[y])-1]), 'to foundation.'
            found[(elements[y][len(elements[y])-1]-1)/13] = found[(elements[y][len(elements[y])-1]-1)/13] + 1
            elements[y].pop();
    return retval

def initCards():
    x = range(1,53)
    shuffle(x)
    for y in range(0,7):
        for z in range(0,8):
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
    for y in range (0,8):
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


initCards()
printCards()

name = ""

while win == 0:
    checkFound()
    name = raw_input("Move:")
    if name == "":
        printCards()
        next
    if len(name) > 1:
        if (ord(name[1]) > 96) and (ord(name[1]) < 101):
            if spares[ord(name[1]) - 97] > 0:
                print 'Already filled.'
                next
            if name[0] < 1 or name[0] > 8:
                print 'Between 1 and 8.'
                next
            spares[ord(name[1]) - 97] = elements[int(name[0]-1)].pop()
            checkFound()
        print name[0]
        print name[1]
endwhile
