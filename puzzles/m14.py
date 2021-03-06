import sys

from collections import defaultdict
from fractions import Fraction
from itertools import permutations

op_str = [ '+', '-', '*', '/' ]

pl = list(permutations([0, 1, 2]))

idx = 0

my_puz = "14"

count = 1

def shuf(a, b, c):
    if b == 0: return a + c
    if b == 1: return a - c
    if b == 2: return a * c
    if b == 3: return a / c

class equat():
    def __init__(self, seed_num):
        self.seed = seed_num
        self.op1 = seed_num % 4
        self.op2 = (seed_num // 4) % 4
        self.rotate = pl[(seed_num // 16) % 6]
        self.paren23 = (seed_num // 96 == 1)
        self.val_array = [0, 0, 0]
    def make_new_vals(self, ary):
        self.val_array = ary
        self.adj_array = [self.val_array[x] for x in self.rotate]
    def print_eq(self): print(eq_str())
    def eq_str(self):
        return ("seed {:d}: ({:s}) {:s}{:d} {:s} {:s}{:d}{:s} {:s} {:d}{:s} = {:s}".format(self.seed, str(self.val_array), '' if self.paren23 else '(', self.adj_array[0], op_str[self.op1], '(' if self.paren23 else '', self.adj_array[1], '' if self.paren23 else ')', op_str[self.op2], self.adj_array[2], ')' if self.paren23 else '', str(Fraction(self.eval_expr()).limit_denominator())
        ))
        # print("{:s}{:d} {:s} {:s}{:d}{:s} {:s} {:d}{:s} = {:d}".format('' if self.paren23 else '(', self.val_array[0], op_str[self.op1], '' if not self.paren23 else '(', self.val_array[1], ')' if self.paren23 else '', op_str[self.op2], self.val_array[2]), ')' if self.paren23 else '', self.eval_expr())
    def eval_expr(self):
        try:
            if not self.paren23:
                temp = shuf(self.adj_array[0], self.op1, self.adj_array[1])
                return float(shuf(temp, self.op2, self.adj_array[2]))
            temp = shuf(self.adj_array[1], self.op2, self.adj_array[2])
            return float(shuf(self.adj_array[0], self.op1, temp))
        except:
            return float(9999)

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

only_one = False
got_one = False
print_all = False
equivalence_classes = True

firsts = defaultdict(int)
eqc = defaultdict(str)
sums = defaultdict(str)

if equivalence_classes:
    for q in range(0, 192):
        j = equat(q)
        j.make_new_vals([17, 83, 94])
        ev = j.eval_expr()
        if ev in eqc.keys():
            eqc[ev] += ", {:d}".format(q)
        else:
            eqc[ev] = str(q)
            firsts[q] = ev
    for x in sorted(firsts.keys()):
        if ',' not in eqc[firsts[x]]: print(x, "unique")
        else: print(firsts[x], '(', eqc[firsts[x]].count(',') + 1, ')', eqc[firsts[x]])
    exit()

for q in range(0,192):
    j = equat(q)
    okay = True
    print_str = ""
    cur_result = 0
    for z in range(0, len(combos)):
        j.make_new_vals(combos[z])
        res = j.eval_expr()
        if res != sols[z]: okay = False
        cur_result = res
        print_str += j.eq_str() + "\n"
    if okay:
        if not got_one: print("Got one!")
        else: print("Got another!")
        got_one = True
        j.make_new_vals(to_solve)
        print(print_str + j.eq_str())
        if only_one:
            exit()
    elif print_all:
        j.make_new_vals(to_solve)
        print(print_str + j.eq_str())

if not got_one: print("No patterns found. Rats.")
