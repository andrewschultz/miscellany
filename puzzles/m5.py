# X: (numbers), (# they sum to)

import sys

get_next = False
got_any = False

be_fast = True
#be_fast = False

c1 = 0

num_to_get = '5'
if len(sys.argv) > 1:
    num_to_get = sys.argv[1]

def print_sums(nums_left, sum_left, cur_index, cur_array):
    global c1
    c1 += 1
    global j
    global count
    if nums_left == 0 and sum_left == 0:
        count += 1
        print(count, ":", sum, '=', ' + '.join([str(q) for q in cur_array]))
        return
    if nums_left == 0: return
    if sum_left < 0: return
    for i in range (cur_index, j):
        if be_fast and areas[i] < sum_left / nums_left: break
        print_sums(nums_left - 1, sum_left - areas[i], i, cur_array + [ areas[i] ])


with open("m5.txt") as file:
    for line in file:
        if line.startswith('puz') and num_to_get in line:
            get_next = True
            continue
        if get_next:
            get_next = False
            got_any = True
            to_add = int(line[0])
            areas = line[2:].lower().strip().split(",")
            sum = int(areas[-1])
            areas = sorted(int(x) for x in areas[:-1])
            break

if not got_any:
    sys.exit("Couldn't get any project named", num_to_get)


areas = sorted(areas, reverse=True)
j = len(areas)
count = 0

print_sums(to_add, sum, 0, [])
print(c1)