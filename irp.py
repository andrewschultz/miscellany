import i7
import sys
import mytools as mt

insteads_global = 0

def usage():
    print("Only project names now.")
    exit()

def find_instead(q):
    in_instead = False
    out_string = ""
    insteads = 0
    global insteads_global
    with open(q) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("instead of"):
                insteads += 1
                insteads_global += 1
                out_string += "({:d}/{:d}) ".format(insteads, insteads_global) + line
                in_instead = True
                continue
            if in_instead:
                out_string += line
                if not line.strip(): in_instead = False
                continue
    if out_string:
        print("====", q, "====")
        print(out_string)
        print(insteads, "total insteads for", q)
    else: print("No INSTEADS string for", q)

my_project = "ailihphilia"
cmd_proj = ""

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if i7.proj_exp(arg):
        if cmd_proj: sys.exit("Defined two command line projects. Bailing.")
        cmd_proj = i7.proj_exp(arg)
    else:
        usage()
    cmd_count += 1

if cmd_proj: my_project = cmd_proj
else:
    print("Going with default project", my_project)

q = []

for j in i7.i7nonhdr.values():
    if j not in q: q.append(j)

for k in i7.i7f[my_project]:
    find_instead(k)

pdir = i7.proj2dir(my_project)

for k in q:
    find_instead(k)
