import sys
import re
import numpy
from collections import defaultdict

read_file = "15.txt"

class peg_hole:
    def __init__(self, orig_num, x, y, is_full):
        self.orig_num = orig_num
        self.x = x
        self.y = y
        self.is_full = is_full
        self.reset_val = is_full

def valid_distance(board, p1, p2):
    return True

def read_15_file():
    board = []
    with open(read_file) as file:
        for line in file:
            l0 = line.strip().split(",")
            board.append(peg_hole(int(l0[0]), int(l0[1]), int(l0[2]), l0[3] == 'y'))
    return board

def midpoint(board, p1, p2):
    x = (board[p1].x + board[p2].x) / 2
    y = (board[p1].y + board[p2].y) / 2
    for q in range(0, len(board)):
        if board[q].x == x and board[q].y == y: return q
    return -1

def print_board(board):
    last_row = -1
    last_x = -1
    out_string = ""
    for x in range(0, len(board)):
        bx = board[x]
        yn = ['n', 'y']
        if bx.y > last_row:
            last_row = bx.y
            if x > 0: out_string += "\n"
            out_string += ' ' * bx.x
            out_string += yn[bx.is_full]
            last_x = bx.x
        else:
            out_string += ' ' * (bx.x - last_x - 1) + yn[bx.is_full]
            last_x = bx.x
    print(out_string)
    return

def reset_board(board, reprint_board = False):
    global moves
    moves = []
    for x in range(0, len(board)):
        board[x].is_full = board[x].reset_val
    if reprint_board: print_board(board)
    return board

moves = []

board = read_15_file()

print_board(board)

while True:
    my_move = input("Your move:")
    if my_move == 'q': exit()
    if my_move == 'r':
        board = reset_board(board, reprint_board=True)
        continue
    if my_move == 'm':
        if length(moves): print("Moves:", ' / '.join(moves))
        else: print("No moves yet.")
        continue
    if my_move == '?':
        print("q=exit r=reset board m=move list #,#=move")
    j = my_move.split(",")
    if len(j) < 2:
        print("Need from and to. ? for commands.")
        continue
    if len(j) > 2:
        print("Need only two numbers. ? for commands.")
        continue
    if not j[0].isdigit() or not j[1].isdigit():
        print("Each argument must be a digit.")
    js = int(j[0])
    je = int(j[1])
    any_fatal = False
    mr = len(board)
    for q in range (0, 2):
        if js < 1 or je < 1:
            print(q, js, je, "must be between 1 and", mr)
            any_fatal = True
            break
        if js > mr or je > mr:
            print(q, js, je, "must be between 1 and", mr)
            any_fatal = True
            break
    if any_fatal: continue
    if not valid_distance(board, js-1, je-1):
        print("No valid distance between", js, "and", je)
        continue
    if not board[js-1].is_full:
        print("Tried to move from empty peg", js)
        continue
    if board[je-1].is_full:
        print("Tried to move to full peg", je)
        continue
    mp = midpoint(board, js-1, je-1)
    if mp == -1:
        print("No clear midpoint between", js, "and", je)
        continue
    if not board[mp].is_full:
        print("Tried to jump over empty peg", js)
        continue
    print("Yay valid move")
    board[js-1].is_full = False
    board[je-1].is_full = True
    board[mp].is_full = False
    moves.append(j)
    print_board(board)
    if len(moves) == 14: print("YOU WIN! YAY!")