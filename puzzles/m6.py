import os
import sys
from copy import deepcopy
import numpy

x = numpy.zeros(shape=(4, 3))
solv = []
lc = 0
dumbstr = ""
my_col = -1

horiz = []
verts = []

my_puz = "6" if len(sys.argv) == 1 else sys.argv[1]
puz_str = "puz" + my_puz

puzzled = False

to_solve = []
known_eq = []
sols = []

def abc_2_vars(x):
    return [ x.count('a'), x.count('b'), x.count('c') ]

with open("m6.txt") as file:
    for line in file:
        if line.startswith(";"): break
        if line.startswith(puz_str):
            puzzled = True
            continue
        if puzzled and line.startswith('puz'): break
        if not puzzled: continue
        if lc == 4:
            sols = line.strip().split(',')
            continue
        if lc > 5: sys.exit("You can only have 5 lines for the 4x4.")
        temp = abc_2_vars(line)
        horiz.append(line[:4].strip())
        if '?' in line:
            to_solve.append(temp)
        else:
            q = int(line[5:])
            temp.append(q)
            print("Adding", temp)
            known_eq.append(temp)
        lc = lc + 1

if not puzzled: raise Exception("Couldn't find " + puz_str)
if not puzzled: sys.exit("Didn't find " + puz_str)

for a in range(0, 4):
    vert = abc_2_vars([x[a] for x in horiz])
    if sols[a].isdigit():
        vert.append(int(sols[a]))
        known_eq.append(vert)
    else:
        to_solve.append(vert)
    print(vert)

print ('to solve', to_solve)
print ('known', known_eq)

my_matrix = []

solve_matrix = []

for x in known_eq:
    print(x)
    solve_matrix.append(x)
    if numpy.linalg.matrix_rank(numpy.row_stack(solve_matrix)) != len(solve_matrix):
        solve_matrix.pop()
        continue
    print(numpy.linalg.matrix_rank(numpy.row_stack(solve_matrix)), len(solve_matrix), solve_matrix)

vals = []
for j in solve_matrix:
    vals.append(j.pop())

q = numpy.linalg.solve(solve_matrix, vals)
print(q)
for x in to_solve:
    print(q, '*', x, '=', numpy.dot(q, x))
exit()

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