import sys

puz_num = '3'

if len(sys.argv) > 1:
    puz_num = sys.argv[1]

totals = []
read_ever = False
reading = False

puz_str = 'puz' + puz_num

rows = []
row = 0
total = 0
print(puz_str)

with open("m3.txt") as file:
    for line in file:
        ll = line.lower().strip()
        if ll.startswith(puz_str):
            reading = True
            read_ever = True
            continue
        if ll.startswith('puz'):
            continue
        if reading:
            if line.startswith('t='):
                total = int(line[2:])
                continue
            q = [int(x) for x in ll.split(',')]
            if len(q) < 7:
                if len(q) % 2 == 0:
                    print("Oops bad line even # of items", q)
                x = [0] * ((7-len(q))//2)
                q = x + q + x
            rows.append(q)
            row = row + 1
            if row == 7: break

if not read_ever:
    print(puz_str, "not found")
    exit()
if not total:
    print("T= total not found")
    exit()

for i in range(7):
    q = [' -' if j == 0 else "{:>2d}".format(j) for j in rows[i]]
    print(' '.join(q))

moves = 3

def no_backtracks(str):
    if 'DU' in str or 'UD' in str or 'LR' in str or 'RL' in str: return False
    # bad hack that works only because 3 moves. With more, we need to plot points out.
    return True
    j = defaultdict(bool)
    j['0-0'] = True
    x = 0
    y = 0
    for a in str:
        if a == 'D': y = y + 1
        if a == 'U': y = y - 1
        if a == 'L': x = x - 1
        if a == 'R': x = x + 1
        q = '{:d}-{:d}'.format(x,y)
        if q in j.keys(): return False
        j[q] = True
    return True

def find_values(total, cur_tot, moves, y, x, move_str):
    if rows[y][x] == 0: return
    cur_tot = cur_tot + rows[y][x]
    if moves == 0:
        if cur_tot == total:
            global totals
            totals.append(move_str)
        return
    find_values(total, cur_tot, moves - 1, y + 1, x, move_str + 'D')
    find_values(total, cur_tot, moves - 1, y - 1, x, move_str + 'U')
    find_values(total, cur_tot, moves - 1, y, x - 1, move_str + 'L')
    find_values(total, cur_tot, moves - 1, y, x + 1, move_str + 'R')

find_values(total, 0, moves, 3, 3, "")
print("Ways to", total, "are", totals, len(totals))

retotals = []

for x in totals:
    if no_backtracks(x): retotals.append(x)

print("Without backtracks:", retotals, len(retotals))