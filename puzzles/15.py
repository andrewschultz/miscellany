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

def read_15_file():
    board = []
    with open(read_file) as file:
        for line in file:
            l0 = line.strip().split(",")
            board.append(peg_hole(int(l0[0]), int(l0[1]), int(l0[2]), l0[3] == 'y'))
    return board

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
    for x in range(0, len(board)):
        x.is_full = x.reset_val
    if reprint_board: print_board(board)
    return board

board = read_15_file()

print_board(board)

while True:
    my_move = input("Your move:")
    if my_move == 'q': exit()
    if my_move == 'r':
        board = reset_board(board, reprint=True)
        continue
    j = my_move.split(",")
    if len(j) < 2:
        print("Need from and to")
        continue
    if len(j) > 2:
        print("Need only two numbers")
        continue
    if not j[0].isdigit() or not j[1].isdigit():
        print("Each argument must be a digit.")
    any_fatal = False
    mr = len(board)
    for q in range (0, 2):
        if j(q) < 1:
            print(q, j[q], "must be between 1 and", mr)
            any_fatal = True
            break
        if j(q) > mr:
            print(q, j[q], "must be between 1 and", mr)
            any_fatal = True
            break
    if any_fatal: continue
    if not valid_distance(board, j[0], j[1]):
        print("No valid distance between", j[0], "and", j[1])
        continue
    if not board[j[0]-1].is_full:
        print("Tried to move from empty peg", j[0])
        continue
    if board[j[0]-1].is_full:
        print("Tried to move to full peg", j[0])
        continue
    mp = midpoint(board, j[0], j[1])
    if not board[mp].is_full:
        print("Tried to jump over empty peg", j[0])
        continue
    print("Yay valid move")
    board[j[0]-1].is_full = False
    board[j[1]-1].is_full = True
    board[mp] = False
