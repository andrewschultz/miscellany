#
# nso.py: note sorter
#

import filecmp
from shutil import copy
import re
from collections import defaultdict
from mytools import nohy
import os
import i7
import sys

display_changes = False
copy_to_old = True
copy_smart = True

def unique_header(a, b):
    for x in b:
        if a == x: return x
        if 'xx' + a == x: return x
    temp_ret = ""
    for x in b:
        if x.startswith(a) or x.startswith('xx' + a):
            if temp_ret:
                print("Uh oh, {0} is ambiguous. It could be {1} or {2}.".format(a, x, temp_ret))
                return ""
            temp_ret = x
    return temp_ret

def copy_smart_ideas(pro, hdr_type = "ta"):
    notes_in = os.path.join(i7.proj2dir(pro), "notes.txt")
    notes_out = os.path.join(i7.proj2dir(pro), "notes-temp.txt")
    hdr_tmp = os.path.join(i7.extdir, "temp.i7x")
    hdr_to_change = i7.hdr(pro, hdr_type)
    markers = defaultdict(int)
    bail = False
    to_insert = defaultdict(str)
    with open(hdr_to_change) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("table of") and "[" in line and "\t" not in line:
                x = re.findall("\[([^\]]*)\]", line)
                for y in x:
                    y = re.sub("[\[\]]", "", y)
                    if y in markers:
                        bail = True
                        print("Uh oh double definition of {0}, lines {1} and {2}.".format(y, markers[y], line_count))
                    else:
                        markers[y] = line_count
    if bail: sys.exit()
    msort = sorted(markers)
    for y in range(0, len(msort)):
        for z in range(y+1, len(msort)):
            n1 = msort[y]
            n2 = msort[z]
            if n1.startswith(n2) or n2.startswith(n1):
                bail = True
                print("Uh oh overlapping {0} {1} {2} {3}.".format(n1, markers[n1], n2, markers[n2]))
    if bail: sys.exit()
    out_stream = open(notes_out, "w")
    uniques = 0
    with open(notes_in) as file:
        for (line_count, line) in enumerate(file, 1):
            print_this_line = True
            if re.search("^[a-zA-Z0-9]+:", line):
                left_bit = re.sub(":.*", "", line.lower().strip())
                uh = unique_header(left_bit, markers)
                if uh:
                    new_text = re.sub("^[a-zA-Z0-9]+:", "", line.rstrip()).strip()
                    if not new_text.startswith("\""): new_text = "\"" + new_text
                    if not new_text.endswith("\""): new_text = new_text + "\""
                    print_this_line = False
                    to_insert[uh] += new_text + "\n"
                    uniques += 1
                else:
                    if "#idea" not in line.lower():
                        print("Unrecognized colon starting with", left_bit, "at line", line_count, "full(er) text", line.strip()[:50])
                # print("Looking for uniques in {0}({1}): {2}".format(line.strip(), uh, print_this_line))
            if print_this_line: out_stream.write(line)
    out_stream.close()
    print(uniques, "uniques found to send to header.")
    if uniques:
        print_after_next = False
        out_stream = open(hdr_tmp, "w", newline="\n")
        last_blank = False
        with open(hdr_to_change) as file:
            for (line_count, line) in enumerate(file, 1):
                if last_blank and not line.strip(): continue
                out_stream.write(line)
                last_blank = not line.strip()
                if line.startswith("table of") and "\t" not in line:
                    x = re.findall("\[([^\]]*)\]", line)
                    print_after_next = True
                    continue
                if print_after_next:
                    print_after_next = False
                    if len(x):
                        for j in x:
                            if j in to_insert:
                                out_stream.write(to_insert[j])
                                to_insert.pop(j)
        out_stream.close()
    else:
        print("No commands to shuffle table rows over.")
        return
    if len(to_insert):
        print("Uh oh! We didn't clear everything.", to_insert)
    if display_changes:
        i7.wm(notes_in, notes_out)
        i7.wm(hdr_to_change, hdr_tmp)
    else:
        copy(notes_out, notes_in)
        copy(hdr_tmp, hdr_to_change)
    os.remove(notes_out)
    os.remove(hdr_tmp)
    if display_changes: sys.exit()

def move_old_ideas(pro):
    notes_in = os.path.join(i7.proj2dir(pro), "notes.txt")
    notes_out = os.path.join(i7.proj2dir(pro), "notes-old.txt")
    notes_temp = os.path.join(i7.proj2dir(pro), "notes-temp.txt")
    no = open(notes_out, "a")
    nt = open(notes_temp, "w")
    got_one = 0
    blanks = 0
    last_blank = False
    with open(notes_in) as file:
        for (line_count, line) in enumerate(file, 1):
            if not line.strip():
                blanks += 1
                if last_blank: continue
            last_blank = not line.strip()
            if line.startswith("##"):
                got_one += 1
                no.write(line)
            else: nt.write(line)
    print(blanks, "of", line_count, "total blank lines.")
    no.close()
    nt.close()
    if got_one:
        if display_changes: i7.wm(notes_in, notes_temp)
        else:
            print(got_one, "lines zapped from notes.")
            copy(notes_temp, notes_in)
    else:
        print("No ##'s found")
    os.remove(notes_temp)


cmd_proj = ""
default_proj = i7.dir2proj()

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = nohy(sys.argv[len])
    if i7.proj_exp(arg):
        if cmd_proj:
            sys.exit("Redefined command project on the command line.")
        cmd_proj = i7.proj_exp(arg)
    elif l == 'co':
        copy_to_old = True
    elif l == 'cs' or l == 'sc':
        copy_smart = True
    elif l == 'ca' or l == 'ac' or l == 'bc' or l == 'cb':
        copy_smart = True
        copy_to_old = True
    elif l == 'dc':
        display_changes = True
    elif l == 'dcn' or l == 'ndc' or l == 'nc' or l == 'nd':
        display_changes = False
    cmd_count += 1

if not cmd_proj:
    if default_proj:
        print("No project in parameters. Going with default project", default_proj)
        my_proj = default_proj
    else:
        sys.exit("I couldn't find a project in the directory path or on the command line. Bailing.")
else: my_proj = cmd_proj

if copy_smart or copy_to_old:
    print(copy_smart, copy_to_old)
    if copy_smart: copy_smart_ideas(my_proj)
    if copy_to_old: move_old_ideas(my_proj)
    show_nonblanks(os.path.join(i7.proj2dir(my_proj), "notes.txt"))
    sys.exit()

