import sys
import re
import numpy
from collections import defaultdict

count = defaultdict(int)

class tile:
    def __init__(self, is_h, digits, thru):
        self.is_h = is_h
        self.digits = digits
        self.in_puz = False
        self.puz_x = -1
        self.puz_y = -1
    def rm(self):
        self.in_puz = False
        self.puz_x = -1
        self.puz_y = -1
    def l(self):
        return len(self.digits)
    def pr(self):
        print(self.is_h, self.digits, self.in_puz, self.puz_x, self.puz_y)

board = [[0] * 5 for i in range(5)]
rights = [[False] * 5 for i in range(5)]
downs = [[False] * 5 for i in range(5)]

#mypuz = tile(True, [3, 7, 5])
#mypuz2 = tile(False, [2, 4, 6])
#mypuz.pr()
#mypuz2.pr()

pcs = []

def get_puzzle():
    global cur_walkthrough
    try:
        idx = input("Pick a puzzle(2, 18, ..., 194):")
    except KeyboardInterrupt:
        print("Bye!")
        exit()
    if not idx: idx = "2"
    count.clear()
    with open("puz.txt") as file:
        for line in file:
            # if line.startswith("#"): continue
            if not line.startswith(idx + ':'): continue
            ll = re.sub("^[0-9]+:", "", line.lower().strip()).split(',')
            n = 0
            cur_walkthrough = ""
            for x in range(0, len(ll)):
                if ll[x].startswith('h'):
                    horiz = True
                    any_yet = True
                elif ll[x].startswith('v'):
                    horiz = False
                    any_yet = True
                elif ll[x].startswith('s') or ll[x].startswith('w'):
                    cur_walkthrough = ll[x][1:]
                    if cur_walkthrough.startswith(':'): cur_walkthrough = cur_walkthrough[1:]
                    continue
                elif not ll[x][0].isdigit():
                    print("Tiles must start with h or v, a #, or s/w for a walkthrough:", x, ll[x])
                    exit()
                if not any_yet:
                    print("Must initialize with h or v.", line)
                    exit()
                j = ll[x]
                if not j[0].isdigit(): j = j[1:]
                nums = [int(q) for q in list(j)]
                for z in nums: count[z] = count[z] + 1
                n = n + len(j)
                print(x, n)
                q = tile(horiz, nums, cur_walkthrough)
                pcs.append(q)
            if n != 25:
                for x in range(0, 10): print(x, pcs[x].l(), pcs[x].digits)
                print("Have", n, "squares, need 25")
                exit()
            if len(pcs) != 10:
                print("Need ten total pieces in the puzzle group, have", len(ll))
                exit()
            return True
    print("Found no puzzles for", idx)
    return False

def check_win():
    for y in range(5):
        for x in range(5):
            if board[x][y] == -1: return False
    print_board()
    print("YOU WIN!")
    if not cur_walkthrough:
        wstr = ' '.join(['{:d}{:d}{:d}'.format(x, pcs[x].puz_x,pcs[x].puz_y) for x in range(0, 10)])
        print("Walkthrough:", wstr)

    return True

def reset_board():
    for y in range(5):
        for x in range(5):
            board[x][y] = -1
            rights[x][y] = False
            downs[x][y] = False
    for i in range(len(pcs)):
        pcs[i].rm()

def try_to_place(p, xi, yi):
    mn = pcs[p]
    if mn.in_puz:
        print("Already in puzzle.")
        return False
    if xi < 0 or xi > 4:
        print("Bad x-start.")
        return False
    if yi < 0 or yi > 4:
        print("Bad y-start.")
        return False
    if mn.is_h and xi + mn.l() > 5:
        print("End of piece", p, "goes off the right edge.")
        return False
    if not mn.is_h and yi + mn.l() > 5:
        print("End of piece", p, "goes off the bottom edge.")
        return False
    print(yi, 1 + yi + ((mn.l() - 1) * (not mn.is_h)), "/", xi, xi + (mn.l() * mn.is_h))
    for y in range (yi, 1 + yi + ((mn.l() - 1) * (not mn.is_h))):
        for x in range (xi, 1 + xi + ((mn.l() - 1) * mn.is_h)):
            if board[x][y] > 0:
                print("Oops, overlap at", x, y)
                return False
            if board[y][x] > 0 and board[y][x] != mn.digits[x-xi+y-yi]:
                print(mn.digits[x-xi+y-yi], "not", int(board[y][x]), "at", x, y, "vs", y, x, "so no symmetry.")
                return False
    mn.in_puz = True
    mn.puz_x = xi
    mn.puz_y = yi
    for j in range(0, mn.l()):
        board[xi + j * mn.is_h][yi + j * (not mn.is_h)] = mn.digits[j]
        if j < mn.l() - 1:
            if mn.is_h:
                rights[xi+j][yi] = True
            else:
                downs[xi][yi+j] = True
    return True

def print_odd_freq():
    print_str = "ODDS:"
    rares = "RARES:"
    for i in range (0, 10):
        if (count[i] % 2 == 1):
            print_str = "{:s} {:d} ({:d})".format(print_str, i, count[i])
        if count[i] < 3 and count[i] > 0:
            rares = "{:s} {:d} ({:d})".format(rares, i, count[i])
    print(print_str)
    print(rares)

def print_board():
    for j in range (0, 5):
        this_line = ""
        for i in range (0, 5):
            this_line = this_line + ('-' if board[i][j] == -1 else str(board[i][j])) + ("-" if rights[i][j] else " ")
        this_line = this_line + "| "
        for i in range (0, 5):
            if board[i][j] != -1:
                this_line = this_line + '*'
            elif board[i][j] == -1 and board[j][i] == -1:
                this_line = this_line + '-'
            else:
                this_line = this_line + ('*' if board[j][i] == -1 else str(board[j][i]))
            this_line = this_line + ("-" if rights[i][j] else " ")
        print(this_line)
        verts = ""
        for i in range (0, 5):
            verts = verts + ("|" if downs[i][j] else " ") + " "
        print(verts + "| " + verts)


def print_pieces():
    hstr = ""
    vstr = ""
    if len(pcs) == 0:
        print("OOPS no pieces.")
        return
    for i in range (0, len(pcs)):
        if pcs[i].in_puz: continue
        if pcs[i].is_h:
            if hstr:
                hstr = hstr + " / "
            else:
                hstr = "HORIZONTAL PIECES: "
            hstr = hstr + "{:d}={:s}".format(i, '-'.join([str(q) for q in pcs[i].digits]))
        else:
            vstr = vstr + "{:d} ".format(i)
    print(hstr)
    if vstr:
        vstr = vstr + "<<<<VERTICAL"
        print(vstr)
        print("=" * 40)
        for j in range(0, 3):
            print_string = ""
            for i in range (0, 10):
                if pcs[i].in_puz: continue
                #print(j, i, pcs[i].digits, pcs[i].l(), pcs[i].is_h)
                if pcs[i].is_h:
                    continue
                # print(j, i, pcs[i].digits, pcs[i].l())
                print_string = print_string + (" " if j >= pcs[i].l() else str(pcs[i].digits[j])) + " "
            print(print_string)

def play_one_game():
    refresh = True
    won = False
    while not won:
        if refresh:
            print_pieces()
            print_board()
            print_odd_freq()
        refresh = False
        try:
            mv = input("Move:")
        except KeyboardInterrupt:
            print("Bye!")
            exit()
        if not mv:
            refresh = True
            continue
        if mv is 'r':
            reset_board()
            continue
        if mv.startswith('w'):
            print("WALKTHROUGH:", cur_walkthrough)
            continue
        if mv.startswith('r'):
            try:
                b = int(mv[1:])
            except:
                print("r# needs a number.")
                continue
            if b > 9 or b < 0:
                print("r# needs a single digit number.")
                continue
            if not pcs[b].in_puz:
                print("Piece", b, "is not in the puzzle.")
                continue
            mn = pcs[b]
            for j in range(0, mn.l()):
                board[mn.puz_x + j * mn.is_h][mn.puz_y + j * (not mn.is_h)] = -1
                if j < mn.l() - 1:
                    if mn.is_h:
                        rights[mn.puz_x+j][mn.puz_y] = False
                    else:
                        downs[mn.puz_x][mn.puz_y+j] = False
            mn.rm()
            refresh = True
            continue
        mv = re.sub(" ", "", mv)
        if len(mv) < 3:
            print("Need 3 digits.")
            continue
        if mv[0].isdigit and mv[1].isdigit and mv[2].isdigit:
            print("Trying move...")
            refresh = try_to_place(int(mv[0]), int(mv[1]), int(mv[2]))
            won = check_win()

#######################################
# begin main bit of code
#

reset_board()

while True:
    pcs = []
    if not get_puzzle(): continue
    reset_board()
    play_one_game()
