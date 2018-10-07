import re

from collections import defaultdict

caps = [ "THINK", "TIP IT", "DEVED", "DEV ED", "SMH MS", "GUY UG", "TOOLS LOOT", "NI WIN", "N I WIN", "META", "SHUTTUHS", "LO VOL", "LOVE VOL", "DEEP SPEED", "REV OVER", "ROT", "REI", "REV", "MM" ]

caps_par = "|".join(caps)

def skipit(a):
    if '"' not in a: return True
    if re.search(": *print", a): return True
    if a.startswith("["): return True
    if a.startswith("USE / GOOD"): return True
    if 'REV OVER doesn\'t think' in a: return True
    return False

def bruteforce():
    print("Brute force run:")
    count = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            for q in caps:
                if q in line and "[b]{:s}[r]".format(q) not in line:
                    if skipit(line): continue
                    count += 1
                    print(line.rstrip())
    if count == 0: print("NO ERRORS! Yay!")

def sophisticated():
    finerr = defaultdict(str)
    print("Sophisticated run:")
    count = 0
    countall = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            q = re.findall(r"(?<!(\[b\]))\b({:s})\b(?!(\[r\]))".format(caps_par), line)
            if q:
                if skipit(line): continue
                count += 1
                countall += len(q)
                adds = [x[1] for x in q]
                print(count, "/", countall, "Need bold in", line_count, line, ', '.join(adds))
                for j in adds: finerr[j] += " {:05d}".format(line_count)
    if count == 0: print("NO ERRORS! Yay!")
    else:
        for q in sorted(finerr.keys(), key=lambda x: (len(finerr[x]), finerr[x])):
            print(q, finerr[q])

def find_caps():
    capfind = defaultdict(int)
    print("Find caps:")
    count = 0
    countall = 0
    with open("story.ni") as file:
        for (line_count, line) in enumerate (file, 1):
            if skipit(line): continue
            q = re.findall(r"([A-Z])([A-Z ]*[A-Z])".format(caps_par), line)
            for l in q: capfind[l[0]+l[1]] += 1
    for q in sorted(capfind.keys(), key=capfind.get):
        print(q, capfind[q])

#find_caps()
#bruteforce()
sophisticated()
