import sys

debug = True
puz_num = '1'

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
    if x == 4 and y == 0 and rm == 0: return [walkstr]
    return thru_path(ary, sols, y, x+1, rm, walkstr + 'R') + thru_path(ary, sols, y-1, x, rm, walkstr + 'U')

f=open("m1.txt", "r")

sols = []

adj = 0
total_needed = 0
cur_row = 0

ary = [[0] * 5 for i in range(5)]

reading_my_puzzle = False
read_my_puzzle = False

if len(sys.argv) > 1:
    puz_num = sys.argv[1]
puz_str = 'puz' + puz_num

while True:
    x = f.readline().lower()
    if not x: break
    if x.startswith(puz_str):
        reading_my_puzzle = True
        read_my_puzzle = False
        continue
    if not reading_my_puzzle: continue
    if x.startswith('puz'): break
    if x.startswith("x="):
        adj = int(x[2:])
    elif x.startswith("g="):
        total_needed = int(x[2:])
    else:
        ary[cur_row] = sortit(x, adj)
        cur_row += 1

alls = thru_path(ary, sols, 4, 0, total_needed, "")

print(ary)
print(alls, "for", ["{:s}={:s}".format(x, nums(x)) for x in alls], total_needed)