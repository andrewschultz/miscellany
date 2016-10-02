import sys
from random import shuffle

suits = ['C', 'D', 'H', 'S'];

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

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

spares = [0, 0, 0, 0]

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