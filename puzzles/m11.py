import sys

board = [[0] * 5 for i in range(5)]
init = [[False] * 5 for i in range(5)]

def check_won(a):
    for y in range(5):
        for x in range(5):
            if a[x][y] == -1: return False
    return True

def mirror(a):
    l = []
    for y in range(5):
        l.append([a[x][y] for x in range(5)])
    return l

def print_board(b):
    print("=" * 21)
    for y in range(5):
        my_line = ""
        for x in range(5):
            my_line = "{:s}{:>2s}{:s} ".format(my_line, str(b[y][x]) if b[y][x] > -1 else "--", ' ' if init[y][x] or b[y][x] == -1 else '*')
        print(my_line)


def reset_board():
    board = [[0] * 5 for i in range(5)]

problem = '11'

if len(sys.argv) > 1: problem = sys.argv[1]

f = open("m11.txt", "r")
reading_puzzle = False
row = 0

while (True):
    x = f.readline().lower()
    if not x: break
    if x.startswith('puz' + problem):
        reading_puzzle = True
        continue
    if not reading_puzzle:
        continue
    if x.startswith('s=') or x.startswith('m='):
        mnum = int(x[2:])
        continue
    if ',' in x:
        board[row] = [int(y) for y in x.strip().split(',')]
        for j in range(5):
            if board[row][j] > -1: init[row][j] = True
        row = row + 1
        if row == 5: break

look_again = True

print_board(board)
#print("=" * 40)
#print_board(mirror(board))
#print("=" * 40)

while look_again and not check_won(board):
    look_again = False
    q = mirror(board)
    for x in range(5):
        y = board[x].count(-1)
        if y == 1:
            # print("Row", x+1, "can be zapped")
            s = 0
            for z in range(5):
                if board[x][z] == -1:
                    replace = z
                else:
                    s = s + board[x][z]
            # print("Row", x+1, "replace", replace, z, '->', mnum - s)
            board[x][replace] = mnum - s
            print_board(board)
            look_again = True
            q = mirror(board)
        y = q[x].count(-1)
        if y == 1:
            s = 0
            for z in range(5):
                # print(z, x, board[z][x])
                if board[z][x] == -1:
                    replace = z
                else:
                    s = s + board[z][x]
            # print("Column", x+1, "replace", replace, z, '->', mnum - s)
            board[replace][x] = mnum - s
            print_board(board)
            look_again = True
            q = mirror(board)
    opens = 0
    s = 0
    for x in range(5):
        if board[x][x] == -1:
            opens += 1
            replace = x
        else:
            s = s + board[x][x]
    if opens == 1:
        board[replace][replace] = mnum - s
        print("UL DR diag", replace, replace, '->', mnum - s)
        print_board(board)
    opens = 0
    s = 0
    for x in range(5):
        if board[x][4-x] == -1:
            opens += 1
            replace = x
        else:
            s = s + board[x][4-x]
    if opens == 1:
        board[replace][4-replace] = mnum - s
        print("DL UR diag", replace, 4-replace, '->', mnum - s)
        print_board(board)
        look_again = True
        q = mirror(board)

cw = check_won(board)

if check_won(board):
    print("GOT EM ALL!")
else:
    print("Need to get some more.")
