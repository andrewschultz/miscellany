#
# hbl.py = hosts block list
#

from collections import defaultdict
from shutil import copy
import time
import sys
import os
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from filecmp import cmp
import re

allow_write = False
see_diffs = False
force_copy = False
#see_diffs = True
open_hosts = False
open_data = False

def usage():
    print("-w = allow write")
    print("-d = see differences")
    print("-f = force copy")
    print("-e = edit sites file")
    print("-h = edit hosts file")
    print("To restore access -f -w -h")
    exit()

def modify_hosts_data(my_data_file):
    out_str = ""
    changes = 0
    with open(my_data_file) as file:
        for (line_count, line) in enumerate(file, 1):
            out_line = line
            for uc in uncomment:
                if uc in line.lower():
                    out_line = re.sub("^#", "", line, 0, re.IGNORECASE)
                    print("Uncommented", uc, "line", line_count)
            for c in comment_out:
                if c in line.lower():
                    out_line = "#" + re.sub("^#", "", line, 0, re.IGNORECASE)
                    print("Commented out", c, "line", line_count)
            changes += out_line != line
            out_str += out_line
    if not changes:
        print("No changes.")
    else:
        print(changes, "changes. Bailing after rewrite.")
        os.chmod(hosts, S_IWUSR|S_IREAD)
        f = open(my_data_file, "w")
        f.write(out_str)
        f.close()
        os.chmod(hosts, S_IREAD|S_IRGRP|S_IROTH)
    exit()

def read_hosts_data(my_data_file):
    with open(my_data_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if line.strip():
                tary = line.strip().split("\t")
                blockables[tary[0]] = int(tary[1])

reset = defaultdict(bool)
blockables = defaultdict(int)

hosts = 'C:\Windows\System32\drivers\etc\hosts'
hosts_temp = 'c:\scripts\hosts-temp.txt'
hosts_data = 'c:\scripts\hosts-data.txt'

count = 1

comment_out = []
uncomment = []

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    neg = arg[0] == '-'
    if neg: arg = arg[1:]
    if arg == 'w':
        allow_write = True
    elif arg == 'wo':
        print("Oh, all right.")
        os.chmod(hosts, S_IWUSR|S_IREAD)
        exit()
    elif arg == 'd':
        see_diffs = True
    elif arg == 'f':
        force_copy = True
    elif arg == 'e':
        open_data = True
    elif arg == 'h':
        open_hosts = True
    elif "." in arg:
        if neg:
            comment_out.append(arg)
        else:
            uncomment.append(arg)
    else:
        print("Invalid flag", sys.argv[count])
        usage()
    count = count + 1

if len(comment_out) + len(uncomment):
    modify_hosts_data(hosts)

read_hosts_data(hosts_data)

hostout = open(hosts_temp, "w")

cur_time = int(time.time())
comment_next = in_timing_check = False
check_timed = True

with open(hosts) as file:
    for (line_count, line) in enumerate(file, 1):
        ll = line
        if check_timed:
            if '#timeout blocking' in line:
                in_timing_check = True
                hostout.write(line)
                continue
        if in_timing_check:
            if not ll.strip(): in_timing_check = False
            elif comment_next:
                comment_next = False
                print(ll)
                if not ll.startswith("#"):
                    print("Commenting", ll)
                    ll = "#" + ll
            elif line.startswith("#last"):
                tmpa = line[1:].split("/")
                if reset[tmpa[1]]:
                    hostout.write("#last/{:s}/{:d}/{:d}".format(tmpa[1], cur_time, blockables[tmpa[1]]))
                time_to_disable = int(tmpa[2]) + int(tmpa[3])
                if time_to_disable < cur_time:
                    comment_next = True
        else:
            for b in blockables.keys():
                if b in line and line.startswith('#') and not line.startswith("#last/"):
                    print('blockable found:', b, "=string, line=", line)
                    ll = ll[1:]
        hostout.write(ll)

hostout.close()

# comment to see what changed
if see_diffs:
    os.system("wm {:s} {:s}".format(hosts, hosts_temp))
    os.system(hosts_temp)
    exit()


do_i_copy = True

if cmp(hosts_temp, hosts):
    if not force_copy:
        print("Nothing changed. No copying.")
        do_i_copy = False
    else:
        os.chmod(hosts, S_IWUSR|S_IREAD)
        print("Nothing changed, but copying over anyway.")

os.chmod(hosts, S_IWUSR|S_IREAD)

if do_i_copy:
    copy(hosts_temp, hosts)
    print("Copied", hosts_temp, "successfully back to", hosts)

if not allow_write:
    print("Setting to read only.")
    os.chmod(hosts, S_IREAD|S_IRGRP|S_IROTH)

if open_data: os.system(hosts_data)
if open_hosts: os.system("\"c:\\program files (x86)\\notepad++\\notepad++.exe\" " + hosts)