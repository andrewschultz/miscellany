# m7.py
# traverse 5 nodes of a graph for maximum or actual score
#
# starting at the corners
#
# a-b-------c-d
#   |\     /|
#   | e---f |
#   | |\ /| |
#   | | g | |
#   | |/ \| |
#   | h---i |
#   |/     \|
# j-k-------l-m
#

import copy
import sys

less_than_wanted = 0
cur_max = 0
cur_low = 1000
puz_num = 7
exact_wanted = 0
from collections import defaultdict

exact_array = []
less_than_array = []
worst_array = []
best_array = []
vals = defaultdict(int)

def sift_thru(node, cur_value, jumps, trav_string, graph):
    global best_array
    global cur_max
    global exact_array
    global worst_array
    global cur_low
    # print(node, cur_value, jumps, trav_string, graph[node].keys())
    cur_value = cur_value + vals[node]
    if jumps == 0 or node not in graph.keys():
        if cur_value == exact_wanted:
            exact_array.append(trav_string)
        if cur_value < less_than_wanted:
            less_than_array.append(trav_string + '=' + str(cur_value))
        if cur_value > cur_max:
            best_array = [trav_string]
            cur_max = cur_value
        elif cur_value == cur_max:
            best_array.append(trav_string)
        if jumps == 0:
            if cur_value < cur_low:
                worst_array = [trav_string]
                cur_low = cur_value
            elif cur_value == cur_low:
                worst_array.append(trav_string)
        return
    for j in graph[node].keys():
        if graph[node][j] == False: continue
        g2 = copy.deepcopy(graph)
        g2[node][j] = False
        for j2 in g2.keys():
            if j in g2[j2].keys():
                g2[j2][j] = False
        sift_thru(j, cur_value, jumps - 1, trav_string + j, g2)

def check_dict(ary, jumps):
    for node in ary:
        print("Starting at", node)
        graf = copy.deepcopy(big_graph)
        # print(graf)
        sift_thru(node, 0, 4, node, graf)

big_graph = defaultdict(lambda: defaultdict(bool))

graph1 = {
  "a": ["b"], "b": ["c", "e", "k"], "c": ["d", "f", "l"], "e": ["f", "g", "h"],
  "f": ["i"], "g": ["h", "i"], "h": ["i", "k"], "i": ["l"], "j": ["k"], "k": ["l"], "l": ["m"]
}

for y in graph1.keys():
    for z in graph1[y]:
        big_graph[z][y] = True
        big_graph[y][z] = True

# for y in sorted(big_graph.keys()): print(y, sorted(big_graph[y].keys()))

if len(sys.argv) > 1:
    puz_num = int(sys.argv[1])

puz = "puz{:d}:".format(puz_num)

got_puz = False

with open("m7.txt") as file:
    for line in file:
        if line.lower().startswith(puz):
            line = line.lower().strip()[len(puz):]
            va = line.split(",")
            count = 0
            got_puz = True
            for a in range(len(va)):
                if va[a].startswith('e'):
                    exact_wanted = int(va[a][1:])
                    continue
                if va[a].startswith('<'):
                    less_than_wanted = int(va[a][1:])
                    continue
                vals[chr(count+97)] = int(va[a])
                count += 1
                # print(chr(a+97), a, va[a])


if not got_puz:
    print("No puzzle. Try 7+16x up to 199.")
    exit()

print("a           d")
print("{:d}-{:d}-------{:d}-{:d}".format(vals['a'], vals['b'], vals['c'], vals['d']))
print("  |\     /|")
print("  | {:d}---{:d} |".format(vals['e'], vals['f']))
print("  | |\ /| |")
print("  | | {:d} | |".format(vals['g']))
print("  | |/ \| |")
print("  | {:d}---{:d} |".format(vals['h'], vals['i']))
print("  |/     \|")
print("{:d}-{:d}-------{:d}-{:d}".format(vals['j'], vals['k'], vals['l'], vals['m']))
print("j           m")

# a-b-------c-d
#   |\     /|
#   | e---f |
#   | |\ /| |
#   | | g | |
#   | |/ \| |
#   | h---i |
#   |/     \|
# j-k-------l-m


check_dict(['a', 'd', 'j', 'm'], 4)
print("BEST", best_array, cur_max)
if cur_low < 1000: print("WORST", worst_array, cur_low)

if exact_wanted:
    print(exact_wanted, exact_array, len(exact_array), "times")

if less_than_wanted:
    print(less_than_wanted, less_than_array, len(less_than_array), "times")
