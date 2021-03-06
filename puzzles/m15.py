# combo lock touch all 49 squares in order, each sends you to another

import copy
import sys
import re

get_next = False
rows_got = 0
unreachable = 0
num = 15
brute_force = False
debug = False

argc = 1

def usage():
    print("b = brute force")
    print("b = debug")
    print("# = puzzle number (15+16x up to/including 191)")
    exit()

def print_got_yet():
    for y in range(0, height):
        print(' '.join([str(int(q)) for q in got_yet[y]]))

def square_before(y, x, dupe_search = False): # we could spruce this up by making an array but that is tinkering
    yr = -1
    xr = -1
    for w in range(height):
        if new_square(w, x) == (y, x) and not ignore_this[w][x]:
            if not got_yet[w][x]:
                if yr != -1:
                    print("Double solution to", x, y, "at", xr, yr, "and", x, w)
                    exit()
            elif dupe_search: return (w, x)
            yr = w
            xr = x
    for z in range(width):
        if new_square(y, z) == (y, x) and not ignore_this[y][z]:
            if not got_yet[y][z]:
                if yr != -1:
                    print("Double solution to", x, y, "at", xr, yr, "and", z, y)
                    exit()
            elif dupe_search: return (y, z)
            yr = y
            xr = z
    return (yr, xr)

def dirtxt(q):
    dist = int(q[0])
    dir = q[1]
    return txtdir[dir] * dist

def sol_show(y, x):
    count = 0
    while 'f' not in board[y][x]:
        count += 1
        str = "{:2d}: {:d}, {:d} ({:s}) {:s} to ".format(count, x, y, board[y][x], dirtxt(board[y][x]))
        (y, x) = new_square(y, x)
        str += "{:d}, {:d}".format(x, y)
        print(str)
    exit()

def gots():
    retval = 0
    for y in range(height):
        for x in range(width):
            retval += got_yet[y][x]
    return retval

def new_square(y, x):
    z = board[y][x]
    if z[0] == 'f': return (-2, -2)
    dist = int(z[0])
    dir = z[1]
    if dir == 'l':
        return (y, x - dist)
    if dir == 'r':
        return (y, x + dist)
    if dir == 'u':
        return (y - dist, x)
    if dir == 'd':
        return (y + dist, x)
    return (-1, -1)

def first_unfound(g):
    for y in range(height):
        for x in range(width):
            if not g[y][x]: return (y, x)
    return (-1, -1)

width = 6
height = 7

board = [[''] * width for i in range(height)]
got_yet = [[False] * width for i in range(height)]

fx = -1
fy = -1

while argc < len(sys.argv):
    arg = sys.argv[argc]
    if arg[0] == '-': arg = arg[1:]
    if arg.isdigit(): num = int(arg)
    elif arg == 'b': brute_force = True
    elif arg == 'd': debug = True
    else: usage()
    argc += 1

txtdir = { 'l': "<", 'r': ">", 'u': "^", 'd': "v" }

with open("m15.txt") as file:
    for line in file:
        if 'PROB' + str(num) in line:
            get_next = True
            continue
        if not get_next: continue
        if line.startswith("unreach="):
            unreachable = int(line[8:])
            continue
        board[rows_got] = re.split("[ ,]", line.lower().strip())
        # print(board[rows_got], len(board[rows_got]))
        for x in range(width):
            if 'f' in board[rows_got][x]:
                if fx > -1:
                    print("Uh-oh, two finishes.", fx, fy, "vs", x, rows_got)
                    exit()
                got_yet[rows_got][x] = True
                fx = x
                fy = rows_got
                last_x = fx
                last_y = fy
        rows_got += 1
        if rows_got == 7: break

so_far = 1;
# print(board)

ignore_this = copy.deepcopy(got_yet)

if brute_force:
    confusion = False
    while (gots() < 42):
        (y, x) = first_unfound(got_yet)
        if debug: print(gots(), 'tagged to start at', x, y)
        temp_y = y
        temp_x = x
        while not got_yet[y][x]:
            vtemp_y = y
            vtemp_x = x
            got_yet[y][x] = True
            (y, x) = new_square(y, x)
        if y != last_y or x != last_x:
            print("Uh oh!", vtemp_x, vtemp_y, "to", x, y, "got confusing:", square_before(y, x, True), "may be multiple solution.")
            if confusion: print("This may be a relic from the previous confusion.")
            confusion = True
        else:
            confusion = False
            last_y = temp_y
            last_x = temp_x
        if gots() == 42:
            print("We have a soluton!")
            sol_show(last_y, last_x)
            exit()
        elif debug: print(gots(), "tagged so far.")
else:
    if unreachable:
        isos = 0
        reachable = copy.deepcopy(got_yet)
        poss_dupe = copy.deepcopy(got_yet)
        for x in range(0, width):
            for y in range(0, height):
                (y1, x1) = new_square(y, x)
                if reachable[y1][x1]:
                    # print(x, y, 'may duplicate where something else goes')
                    poss_dupe[y][x] = True
                reachable[y1][x1] = True
        for x in range(0, width):
            for y in range(0, height):
                if poss_dupe[y][x] and not reachable[y][x]:
                    print(y, x, 'looks isolated.')
                    isos += 1
                    got_yet[y][x] = True
                    ignore_this[y][x] = True
        if isos != unreachable:
            sys.exit("{:d} isolated, {:d flagged as unreachable. The two should be equal. Bailing.".format(iso, unreachable))
        else:
            print("Found exactly", isos, "isolated, as expected.")
        for x in range(0, width):
            for y in range(0, height):
                if not reachable[y][x]:
                    continue
                    # print(x, y, "not reachable")
    count = 0
    (y, x) = (fy, fx)
    while (gots() < 42):
        old_y = y
        old_x = x
        (y, x) = square_before(y, x)
        count = count + 1
        print(count, old_x, old_y, "retrogrades to", x, y, board[y][x])
        if got_yet[y][x]:
            print(x, y, "was gotten before. I'm not sure how, but it was. Bailing.")
            exit()
        got_yet[y][x] = True
    print("And that wins!")
