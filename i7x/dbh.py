#
# dbh.py
#
# debug hacker python file
#

import i7
import re

# i7.i7x

dbh = "c:/writing/scripts/dbh.txt"

my_project = "pu"

reading_operators = False
firsts = {}
lasts = {}

def process_operators(infile, outfile):
    in_mod = infile
    out_mod = outfile
    in_noxt = re.sub("\.[^\.]*$", "", in_mod)
    out_noxt = re.sub("\.[^\.]*$", "", out_mod)
    if 'i7x' in in_mod and 'i7x' in out_mod:
        in_mod = i7.i7xd + in_mod
        out_mod = i7.i7xd + out_mod
    to_go = 0
    in_table = False
    line_count = 0
    fk = list(firsts.keys())
    fout=open(out_mod, "w")
    with open(in_mod) as file:
        for line in file:
            line_count = line_count + 1
            if line_count == 1:
                new_line = re.sub(in_noxt, out_noxt, line, 0, re.IGNORECASE)
                fout.write(new_line)
                continue
            if line.strip().endswith("ends here."):
                new_line = re.sub(in_noxt, out_noxt, line, 0, re.IGNORECASE)
                fout.write(new_line)
                continue
            if not line.strip():
                in_table = False
            if line.startswith("table"):
                for x in fk:
                    if line.startswith(x):
                        to_go = firsts[x] + 1
                        in_table = True
            if in_table:
                if to_go < 0:
                    continue
                to_go = to_go - 1
            fout.write(line)
    fout.close()
    return

with open(dbh) as file:
    for line in file:
        if reading_operators:
            if not line.strip() or line.startswith(";"):
                reading_operators = False
                process_operators(read_file, write_file)
                continue
            t = line.strip().split("\t")
            if line.startswith("first"):
                firsts[t[2]] = int(t[1])
                print("Take first", t[1], "of", t[2])
        if line.startswith(my_project) and "->" in line:
            firsts = {}
            lasts = {}
            y = re.sub("^[^:]*:", "", line.strip())
            x = y.split("->")
            read_file = x[0]
            write_file = x[1]
            print("Sending" ,x[0], "to", x[1])
            reading_operators = True