import sys
from collections import defaultdict

puzzles = defaultdict(bool)
freqs = defaultdict(int)

debug = False
default_puz = '1'

cur_low = 9999
cur_high = 0

calc_sum_freq = False

high_array = []
low_array = []

def print_board(q):
    for j in range (0,5):
        print(' '.join('{:3d}'.format(q[i][j]) for i in range (0,5)))

def nums(j):
    x = 0
    y = 4
    sums = ary[y][x]
    retstr = str(ary[y][x])
    for k in j:
        if ary[y][x] < 0: return ""
        if k == 'U':
            y -= 1
            retstr += str(ary[y][x])
            sums += ary[y][x]
        elif k == 'R':
            x += 1
            retstr += str(ary[y][x])
            sums += ary[y][x]
        else:
            print(j, "blew up nums.")
            exit()
    return retstr

def sortit(a, b):
    return [b if 'x' in y else int(y) for y in a.split(',')]

def thru_path(ary, sols, y, x, remaining, walkstr):
    if x > 4 or x < 0 or y > 4 or y < 0: return []
    rm = remaining - ary[y][x]
    if debug: print("Trying", x, y, "left", rm, "str", walkstr)
    if x == 4 and y == 0:
        if calc_sum_freq: freqs[-rm] += 1
        if rm == 0: return [walkstr]
        if not total_needed:
            global cur_low
            global cur_high
            global high_array
            global low_array
            rmn = - rm
            if rmn < cur_low:
                cur_low = rmn
                low_array = [ walkstr ]
            elif rmn == cur_low:
                cur_low = rmn
                low_array.append(walkstr)
            if rmn > cur_high:
                cur_high = rmn
                high_array = [ walkstr ]
            elif rmn == cur_high:
                cur_high = rmn
                high_array.append(walkstr)
    return thru_path(ary, sols, y, x+1, rm, walkstr + 'R') + thru_path(ary, sols, y-1, x, rm, walkstr + 'U')

f=open("m1-8.txt", "r")

sols = []

adj = 0
total_needed = 0
cur_row = 0

ary = [[0] * 5 for i in range(5)]

got_puz = False
reading_my_puzzle = False
read_my_puzzle = False

count = 1
puz_num = -1

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg.isdigit():
        if got_puz: sys.exit("Already got a puzzle number.")
        puz_num = sys.argv[1]
        got_puz = True
    elif arg == 'l': find_lowest = True
    elif arg == 'h': find_highest = True
    elif arg == 'd': debug = True
    count += 1

if not got_puz:
    print("Going with default puzzle", puz_num)
    puz_num = default_puz

puz_str = 'puz' + puz_num

while True:
    x = f.readline().lower()
    if not x: break
    if x.startswith(';'): break
    if x.startswith('#'): continue
    if x.startswith('puz'):
        puzzles[int(x[3:])] = True
    if x.startswith(puz_str):
        reading_my_puzzle = True
        read_my_puzzle = False
        continue
    if not reading_my_puzzle: continue
    if x.startswith('puz'): break
    if x.startswith("x="): adj = int(x[2:])
    elif x.startswith('sums'): calc_sum_freq = True
    elif x.startswith("g="): total_needed = int(x[2:])
    else:
        ary[cur_row] = sortit(x, adj)
        cur_row += 1

for j in range(0, 201):
    if j % 16 == 1 or j % 16 == 8:
        if j is 129: print("129 is in m3.")
        elif j not in puzzles.keys(): print ("Need to write up", j)

alls = thru_path(ary, sols, 4, 0, total_needed, "")

print_board(ary)

if not total_needed:
    print("low", cur_low, low_array)
    print("high", cur_high, high_array)

if calc_sum_freq:
    for x in sorted(freqs.keys()): print(x, freqs[x])

print(len(alls), 'ways:', alls, "for", ["{:s}={:s}".format(x, nums(x)) for x in alls], total_needed)