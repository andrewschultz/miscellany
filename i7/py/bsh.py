#
# bsh.py
#
# battleship "solver" / algorithm tryer
#

import sys

verbose = False

square2txt = [ '.', '-', '*', 'x' ]

def guesses_array(guess_type, guess_subtype):
    ret_ary = []
    mod = 0
    if guess_type == 0:
        mod = guess_subtype
        for j in range(0, 10):
            for i in range(0, 10):
                if (i + j) % 2 == mod: ret_ary.append((i, j))
        return ret_ary
    if guess_type == 1:
        mod = guess_subtype
        for j in range(0, 10):
            for i in range(0, 10):
                if (i + j) % 3 == mod: ret_ary.append((i, j))
        return ret_ary
    if guess_type == 2:
        mod = guess_subtype
        for j in range(0, 10):
            for i in range(0, 10):
                if (i - j) % 3 == mod: ret_ary.append((i, j))
        return ret_ary
    sys.exit("Bad value for", guesses_array)

print(guesses_array(1, 0))
print(guesses_array(2, 0))
exit()

def first_hit(bsb):
    for j in range (0, 10):
        for i in range (0, 10):
            if bsb.guess_board[i][j] == '*':
                return (i, j)
    return (-1, -1)

class battleship_ship:
    def __init__(self, length, name, abbr):
        self.vertical = False
        self.x = -1
        self.y = -1
        self.name = name
        self.abbr = abbr
        self.length = length
        self.hits = [0] * length
        self.sunk = False

class battleship_board:
    def __init__(self):
        self.guess_board = []
        self.placings_board = []
        for i in range (0, 10): self.guess_board.append([0] * 10)
        for i in range (0, 10): self.placings_board.append(['.'] * 10)
        self.ship = [battleship_ship(5, 'carrier', 'C'), battleship_ship(4, 'battleship', 'B'), battleship_ship(3, 'cruiser', 'U'),
          battleship_ship(3, 'submarine', 'S'), battleship_ship(2, 'destroyer', 'D') ]
    def pr_board(self):
        print("GUESSES MAP")
        for i in self.ship:
            if i.x == -1:
                print("You haven't placed the {:s} (length {:d}).".format(i.name, i.length))
            else:
                if verbose: print(i.x, i.y, i.vertical, i.length, i.hits, i.sunk)
        for i in range (0, 10):
            print(' '.join([square2txt[q] for q in self.guess_board[i]]))
    def pr_placings(self):
        print("PLACINGS MAP")
        for i in self.ship:
            if i.x == -1:
                print("You haven't placed the {:s} (length {:d}).".format(i.name, i.length))
            else:
                if verbose: print(i.x, i.y, i.vertical, i.length, i.hits, i.sunk)
        for i in range (0, 10):
            print(' '.join(self.placings_board[i]))
    def place(self, ary):
        if len(ary) != len(self.ship):
            sys.exit("Tried to place the wrong number of ships. It should be {:d}.".format(len(self.ship)))
        self.placings_board[9][9] = 'X'
        for j in range(0, len(ary)):
            if verbose:
                print("Placing", j, ary[j])
                print("Start", ary[j][0], ary[j][1], "End", ary[j][0] + ary[j][2] * (self.ship[j].length - 1), ary[j][0] + (not ary[j][2]) * (self.ship[j].length - 1))
            if ary[j][0] < 0 or ary[j][0] > 9: sys.exit("Bad horizontal start.")
            if ary[j][1] < 0 or ary[j][1] > 9: sys.exit("Bad vertical start.")
            if ary[j][2]: # e.g. place the ship vertically
                if ary[j][1] + self.ship[j].length > 10: sys.exit("Bad vertical end {:d} {:d} for {:s}.".format(ary[j][0], ary[j][1] + self.ship[j].length - 1, self.ship[j].name))
                for k in range (ary[j][1], ary[j][1] + self.ship[j].length):
                    if self.placings_board[ary[j][0]][k] != '.':
                        sys.exit("Oops! (V) Double-placing at ({:d}, {:d}) {:s}.".format(k, ary[j][0], self.placings_board[ary[j][0]][k]))
                    self.placings_board[ary[j][0]][k] = self.ship[j].abbr
            else: # e.g. place the ship horizontally
                if ary[j][0] + self.ship[j].length > 10: sys.exit("Bad horizontal end {:d} {:d} for {:s}.".format(ary[j][0] + self.ship[j].length - 1, ary[j][1], self.ship[j].name))
                for k in range (ary[j][0], ary[j][0] + self.ship[j].length):
                    if self.placings_board[k][ary[j][1]] != '.': sys.exit("Oops! (H) Double-placing at ({:d}, {:d}) {:s}.".format(k, ary[j][1]))
                    self.placings_board[k][ary[j][1]] = self.ship[j].abbr
            self.ship[j].x = ary[j][0]
            self.ship[j].y = ary[j][1]
            self.ship[j].vertical = ary[j][2]

def try_every_other(odds = False):
    guess_list = []
    for i in range(0, 100):
        if i % 2 == odds:
            guess_list.append((i % 10, i // 10))
    print(guess_list)

count = 1
while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg == 'v': verbose = True
    elif arg == 'nv' or arg == 'vn': verbose = False
    else: sys.exit("Unknown flag {:s}.".format(arg))
    count += 1

x = battleship_board()
x.place([[7, 7, False], [2, 2, False], [4, 4, False], [6, 6, False], [8, 8, False]])
x.pr_board()
x.pr_placings()

#try_every_other(False)
#try_every_other(True)

