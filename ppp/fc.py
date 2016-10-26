######################################
#fc.py
#
#no frills Python Freecell game
#

import re
import sys
from random import shuffle

savefile = "fcsav.txt"

onoff = ['off', 'on']

suits = ['C', 'd', 'S', 'h']

cards = [' A', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', ' J', ' Q', ' K']

top = ['CL', 'di', 'SP', 'he']
btm = ['UB', 'am', 'AD', 'ar']

moveList = []

win = 0
inUndo = 0

#options to define. How to do better?
vertical = 0
doubles = 0
autoReshuf = 0

lastscore = 0
highlight = 0

onlymove = 0

def canDump(mycol):
    if chains(mycol) > maxmove()/2:
        return 0
    for tocol in range (1,9):
        if len(elements[tocol]) == 0:
            return tocol
    return 0


def reshuf():
    if autoReshuf == 0:
        return 0
    retval = 0
    tryAgain = 1
    while tryAgain:
        tryAgain = 0
        for i in range(0,4):
            if spares[i]:
                for j in range(1,9):
                    if len(elements[j]):
                        if canPut(spares[i], elements[j][len(elements[j])-1]): #doesn't matter if there are 2. We can always switch
                            elements[j].append(spares[i])
                            spares[i] = 0
                            tryAgain = 1
                            retval = 1
                            #stupid bug here with if we change autoReshuf in the middle of the game
                            #solution is to create "ar(x)(y)" which only triggers if autoReshuf = 0
    return retval
            

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

def chainNope():
    retval = 0
    for i in range (0,9):
        for v in range (1,len(elements[i])):
            if not canPut(elements[i][v], elements[i][v-1]):
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
                autoReshuf = int(q)
            if "vertical".lower() in line.lower():
                vertical = int(q)
            if "doubles".lower() in line.lower():
                doubles = int(q)
    if gotOne:
        print "Options file read."
        f.close()
    else:
        print "Failed to read options file."
    return

def sendOpts():
    q = re.compile(r'^vertical=')
    r = re.compile(r'^doubles=')
    infile = "fcopt.txt"
    fileString = ""
    gotOne = 0
    with open(infile) as f:
        for line in f:
            gotOne = 1
            if (q.match(line)):
                fileString += "doubles=" + str(doubles) + "\n"
            elif (r.match(line)):
                fileString += "vertical=" + str(vertical) + "\n"
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

def initSide():
    global spares
    spares = [0, 0, 0, 0]
    global found
    found = [0, 0, 0, 0]
    global highlight
    highlight = 0
    if inUndo == 0:
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

def checkFound():
    retval = 0
    needToCheck = 1
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
                    needToCheck = 1;
                    retval = 1
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
                    retval = 1
    if totalFoundThisTime > 0 and inUndo == 0:
        sys.stdout.write(str(totalFoundThisTime) + ' card' + plur(totalFoundThisTime) + ' safely to foundation:' + cardlist + '\n')
    return retval

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
    if inUndo == 1:
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
    while True:
        finish = input("You win! Play again (Y/N, U to undo)?")
        if len(finish) > 0:
            if finish[0] == 'n' or finish[0] == 'N':
                print("Bye!")
                exit()
            if finish[0] == 'y' or finish[0] == 'Y':
                initCards()
                initSide()
                global backup
                backup = [row[:] for row in elements]
                return 1
            if finish[0] == 'u' or finish[0] == 'U':
                global inUndo
                inUndo = 1
                undoMoves(1)
                inUndo = 0
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
        sys.stdout.write('(' + str(chains(y)) + ') ')
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
                if ((elements[y][count]-1) % 13) == found[(elements[y][count]-1)//13]:
                    odds = (elements[y][count]-1)//13
                    if (elements[y][count]-1) % 13 < found[(odds+1)%4]+2 and (elements[y][count]-1) % 13 < found[(odds+3)%4]+2:
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
    canmove = ''
    wackmove = ''
    canfwdmove = 0
    for z1 in range (1,9):
        if len(elements[z1]) == 0:
            canmove = canmove + ' E' + str(z1)
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
                canmove = canmove + ' ' + str(z1)+str(z2)
                if thisdo >= len(elements[z1]):
                    canfwdmove = 1
                elif not canPut(elements[z1][len(elements[z1])-thisdo], elements[z1][len(elements[z1])-thisdo-1]):
                    canfwdmove = 1
                else:
                    canmove = canmove + '-'
    for z1 in range (1,9):
        if len(elements[z1]):
            for z2 in range (0,4):
                if canPut(spares[z2], elements[z1][len(elements[z1])-1]):
                    canmove = canmove + ' ' + chr(z2+97) + str(z1)
                    canfwdmove = 1
    for z1 in range (0,4):
        if spares[z1] == 0:
            canmove = canmove + ' >' + chr(z1+97)
            canfwdmove = 1
    if wackmove:
        print ("Not enough room: " + str(wackmove))
    if canmove:
        print ("Possible moves:" + canmove + " (%d longest, %d in order, %d out of order)" % (maxmove(), chainTotal(), chainNope()))
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
    sys.stdout.write(')\n')
    lastscore = foundscore

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
        if showDeets and not inUndo:
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
    print ('lo/so loads/saves options.')
    print ('1-8 1-8 = move a row, standard move.')
    print ('(1-8a-d) (1-8a-d) move to spares and back.')
    print ('f(1-8)(1-8) forces what you can (eg half of what can change between nonempty rows) onto an empty square.')
    print ('(1-8)(1-8)-(#) forces # cards onto a row, if possible.')
    print ('========options========')
    print ('v toggles vertical, + toggles card size (only vertical right now).')
    print ('u = usage (this).')

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

def undoMoves(toUndo):
    global moveList
    if len(moveList) == 0:
        print "Nothing to undo."
        return 0
    global elements
    elements = [row[:] for row in backup]
    global found
    found = [0, 0, 0, 0]
    global spares
    spares = [0, 0, 0, 0]
    for i in range (0,toUndo):
        moveList.pop()
    global inUndo
    inUndo = 1
    for myCmd in moveList:
        readCmd(str(myCmd))
    inUndo = 0
    checkFound()
    printCards()
    return 1
   

def loadGame(gameName):
    original = open(savefile, "r")
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
            inUndo = 1
            initSide()
            if len(line) > 0 and line[0] != '#':
                moveList = line.split()
            else:
                moveList = []
            for myCmd in moveList:
                readCmd(str(myCmd))
            inUndo = 0
            checkFound()
            printCards()
            return 1
        if not line:
            print (re.sub(r'^.=', '', gameName) + ' save game not found.')
            original.close()
            return 0
    gn2 = gameName.replace(r'^.=', '')
    print ("Successfully loaded " + gn2)
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
        myfile.write("###end of " + gameName + "\n")
    gn2 = gameName.replace(r'^.=', '')
    print ("Successfully saved game as " + gn2)
    return 0

def readCmd(thisCmd):
    global vertical
    global doubles
    global autoReshuf
    global elements
    global force
    force = 0
    checkFound()
    thisCmd = thisCmd.lower()
    if thisCmd == '':
        global input
        try: input = raw_input
        except NameError: pass
        name = input("Move:").strip()
    else:
        name = thisCmd
    if len(name) == 0:
        while reshuf():
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
    if name == "lo":
        readOpts()
        return
    if name == "so":
        sendOpts()
        return
    if name[0] == 'u':
        if len(name) == 1:
            undoMoves(1)
            return
        if name[1] == 'a':
            print (moveList)
            return
        temp = re.sub(r'^u', '', name)
        if not temp.isdigit:
            print "Need to undo a number, or nothing."
            return
        if int(temp) > len(moveList):
            print ("Tried to do %d undos, can only undo %d." % (int(temp), len(moveList)))
            return
        undoMoves(int(temp))
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
                print "Sending all to foundation."
                print ("Forced" + forceStr)
            reshuf()
            checkFound()
            printCards()
        else:
            print ("Nothing to force to foundation.")
        return
    if name[0] == 'f':
        name = name.replace("f", "")
        force = 1
        if len(name) == 0:
            print ("You need a from/to, or at the very least, a from.")
            return
    if name == "-":
        elements = [row[:] for row in backup]
        initSide()
        printCards()
        checkFound()
        return
    if name == "?":
        print ('Maximum card length moves: ', maxmove())
        return
    if name == "":
        printCards()
        return
    if name == '+':
        doubles = 1 - doubles
        print ("Toggled doubles to %s." % (onoff[doubles]))
        printCards()
        return
    if name == 'e':
        autoReshuf = 1 - autoReshuf
        print ("Toggled reshuffling to %s." % (onoff[autoReshuf]))
        reshuf()
        printCards()
        return
    if name == 'v':
        vertical = 1 - vertical
        print ("Toggled vertical view to %s." % (onoff[vertical]))
        printCards()
        return
    #### mostly meta commands above here. Keep them there.
    preverified = 0
    if len(name) == 1:
        if name.isdigit():
            i = int(name)
            if i > 8 or i < 1:
                print ('Need 1-8.')
                return
            if len(elements[i]) is 0:
                print ('Acting on an empty row.')
                return
            if anyDoable(i,0):
                name = name + str(anyDoable(i,0))
            elif chains(i) > 1 and canDump(i):
                if chains(i) == len(elements[i]):
                    print ("That's just useless shuffling.")
                    return
                name = name + str(canDump(i))
                preverified = 1
            elif chains(i) == 1 and spareUsed() < 4:
                name = name + "e"
            elif firstEmptyRow() and spareUsed() == 4:
                if doable(i, firstEmptyRow(), 0) == len(elements[i]):
                    print ("That's just useless shuffling.")
                    return
                name = name + str(firstEmptyRow())
            elif anyDoable(i,1) and chains(i) < len(elements[i]):
                name = name + str(anyDoable(i,1))
            else:
                name = name + 'e'
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
    if name[0] == 'l' and name[1] == '=':
        loadGame(re.sub(r'^l=', 's=', name))
        return
    if name[0] == 's' and name[1] == '=':
        saveGame(name.strip())
        return
    #### saving comes first.
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
                if inUndo == 0:
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
                if inUndo == 0:
                    moveList.append(name)
                checkFound()
                printCards()
            else:
                print ('Can\'t move from spares.') #/? 3s onto 2s with nothing else, all filled
            return
        print ('Must move 1-8 or a-d.')
        return
    if name[0].isdigit() and name[1].isdigit():
        t1 = int(name[0])
        t2 = int(name[1])
        if t1 == t2:
            print ('Moving a row to itself does nothing.')
            return
        if len(elements[t1]) == 0:
            print ('Nothing to move from.')
            return
        if t1 < 1 or t2 < 1 or t1 > 8 or t2 > 8:
            print ("Need digits from 1-8.")
            return
        tempdoab = doable(t1,t2,1 - preverified)
        if tempdoab == -1:
            #print 'Not enough space.'
            return
        if tempdoab == 0:
            print ('Those cards don\'t match up.')
            return
        oldchain = chains(t1)
        shiftcards(t1, t2, tempdoab)
        if inUndo == 0:
            if tempdoab < oldchain and len(elements[t2]) == 0:
                moveList.append(str(t1) + str(t2) + "-" + str(tempdoab))
            else:
                moveList.append(name)
        while reshuf() or checkFound():
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
            if inUndo == 0:
                moveList.append(name)
            reshuf()
            checkFound()
            printCards()
            return
        print ("Can't put%s on%s." % (tocardX(spares[mySpare]), tocardX(elements[myRow][len(elements[myRow])-1])))
        return
    if (ord(name[1]) > 96) and (ord(name[1]) < 102): #1a moves, but also 1e can be A Thing
        if name[1] == 'e':
            myToSpare = firstEmptySpare()
            if myToSpare == -1:
                print ('Nothing empty to move to. To which to move.')
                return
        else:
            myToSpare = ord(name[1]) - 97
        if not name[0].isdigit():
            print ('First letter not recognized.')
            return
        myRow = int(name[0])
        if spares[myToSpare] > 0:
            print ("Spare %d already filled" % (myToSpare + 1))
            return
        if myRow < 1 or myRow > 8:
            print ('From row must be between 1 and 8.')
            return
        if (len(elements[myRow]) == 0):
            print ('Empty from-row.')
            return
        spares[myToSpare] = elements[myRow].pop()
        if inUndo == 0:
            moveList.append(name)
        checkFound()
        printCards()
        return
    print (name,'not recognized, displaying usage.')
    usage()

while win == 0:
    readCmd('')
endwhile
