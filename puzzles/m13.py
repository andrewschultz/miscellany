# note that the suits are inaccurate: it goes clubs, diamonds, spades (not counting whatever suit I'm trying to solve for) in the arrays in m13.txt

import numpy as np

reading = False
last_puz = "NONE"

with open("m13.txt") as file:
    for line in file:
        if line.startswith('puz'):
            last_puz = line.strip()
            clu = []
            ary = []
            reading = True
            count = 0
            continue
        if reading:
            if count == 3:
                reading = False
                break
            la = line.lower().strip().split(',')
            if count == 2:
                df = la[0]
                sf = la[1]
                x = np.array(ary)
                y = np.array(clu)
                z = np.linalg.solve(x, y)
                print("======================", last_puz)
                print(x, y, z)
                print(z[0], z[1])
                print (float(df), z[0], float(sf), z[1], float(df) * z[0] + float(sf) * z[1])
            else:
                ary.append([int(x) for x in la[:2]])
                clu.append(int(la[2]))
            count = count + 1