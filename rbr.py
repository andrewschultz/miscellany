import re
import os

file_list = []
file_array = []

line_count = 0

with open("rbr-ail-thru.txt") as file:
    for line in file:
        line_count = line_count + 1
        if len(file_array) == 0:
            file_array = line.lower().strip().split(',')
            actives = [False] * len(file_array)
            for x in file_array:
                f = open(x, 'w')
                file_list.append(f)
            continue
        if len(actives) == 0: continue
        if line.startswith("==+"):
            ll = line.lower().strip()[3:]
            for x in ll.split(','):
                if x.isdigit():
                    actives[int(x)] = True
        if line.startswith("==-"):
            ll = line.lower().strip()[3:]
            for x in ll.split(','):
                if x.isdigit():
                    actives[int(x)] = False
        if line.startswith("==="):
            ll = re.sub("^=+", "", line.lower().strip())
            la = ll.split(',')
            actives = [False] * len(file_array)
            for x in la:
                if x.isdigit(): actives[int(x)] = True
            continue
        for ct in range(0, len(file_list)):
            if actives[ct]:
                file_list[ct].write(line)

for ct in range(0, len(file_array)):
    file_list[ct].close()

print("Wrote files:", ', '.join(file_array))
