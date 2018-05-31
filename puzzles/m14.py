import sys

from itertools import permutations
from enum import Enum

op_str = [ '+', '-', '*', '/' ]
class ops(Enum):
    plus = 1
    minus = 2
    times = 3
    div = 4

pl = list(permutations([0, 1, 2]))

idx = 0

my_puz = "14"

count = 1

while count < len(sys.argv):
    arg = sys.argv[count]
    if not arg.isdigit(): sys.exit("Need a digit as arg, otherwise default to puzzle " + my_puz)
    my_puz = arg
    count += 1

puz_str = 'puz' + my_puz
read_puz = False

combos = []
sols = []
to_solve = []

with open("m14.txt") as file:
    for line in file:
        if puz_str in line:
            read_puz = True
            continue
        if not read_puz: continue
        if 'puz' in line: break
        ll = line.strip()
        if ll.endswith('?'):
            to_solve = [int(x) for x in ll[:-1].split(',')]
        if '=' in ll:
            l2 = ll.split('=')
            combos.append([int(x) for x in l2[0].split(',')])
            sols.append(int(l2[1]))

#print(read_puz)
#print(combos)
#print(sols)
#print(to_solve)

def shuf(a, b, c):
    if b == 0: return a + c
    if b == 1: return a - c
    if b == 2: return a * c
    if b == 3: return a / c

def check_combos(a):
    op1 = (a // 4) % 4
    op2 = a % 4
    ord = pl[a//16]
    for x in range(0, len(combos)):
        temp = combos[x][0]
        temp = shuf(temp, op1, combos[x][1])
        temp = shuf(temp, op2, combos[x][2])
        if temp != sols[x]: return False
    return True

def show_poss():
    for a in range(0, 96):
        if check_combos(a):
            print(to_solve[0], op_str[(a//4)%4], to_solve[1], op_str[(a%4)], to_solve[2], "may be a solution")

show_poss()