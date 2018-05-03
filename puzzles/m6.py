import os
import sys
from copy import deepcopy
import numpy

x = numpy.zeros(shape=(4, 3))
solv = []
lc = 0
dumbstr = ""
my_col = 0

my_puz = "6" if len(sys.argv) == 1 else sys.argv[1]
puz_str = "puz" + my_puz

puzzled = False

with open("m6.txt") as file:
    for line in file:
        if line.startswith(";"): break
        if line.startswith(puz_str):
            puzzled = True
            continue
        if not puzzled: continue
        if line.startswith("col"):
            my_col = int(line[4:]) - 1
            continue
        temp = [line.count('a'), line.count('b'), line.count('c')]
        dumbstr = dumbstr + line[my_col]
        x[lc] = temp
        solv.append(int(line[5:].strip()))
        lc = lc + 1
        if lc == 4: break

if not puzzled: raise Exception("Couldn't find " + puz_str)
if not puzzled: sys.exit("Didn't find " + puz_str)

got_one = False

for i in range(4):
    temp1 = list(x)
    temp2 = list(solv)
    del temp1[i]
    del temp2[i]
    t1 = numpy.array(temp1)
    t2 = numpy.array(temp2)
    try:
        q = numpy.linalg.solve(t1, t2)
        print(q)
        my_sum = dumbstr.count('a') * int(q[0]) + dumbstr.count('b') * int(q[1]) + dumbstr.count('c') * int(q[2])
        print(my_sum, '= the sum we wanted')
        got_one = True
        break
    except:
        print("Removing", i, "doesn't give solvable equation")

if not got_one: sys.exit("Found no solutions.")