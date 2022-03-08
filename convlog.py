# logfile's format is 0=file 1=errors 2=time run finished 3=time taken

import mytools as mt
import re
import os
import pendulum
import i7
import glob
import sys
from collections import defaultdict

last_success = defaultdict(int)
last_success_time_taken = defaultdict(int)
last_run = defaultdict(int)
last_run_time_taken = defaultdict(int)
last_errs = defaultdict(int)
blank = defaultdict(int)
raw_link = defaultdict(str)
mod_link = defaultdict(str)
timestamp = defaultdict(int)
gone_files = defaultdict(int)

wild_cards = ''

write_to_file = False

my_binary = ''
my_proj = ''

def find_binary_in(a_file):
    with open(a_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if 'game:' in line.lower():
                raw = re.sub(".*: *", "", line.strip())
                raw = re.sub(".*prt", i7.prt, raw)
                return raw
    print("Warning no game file found in {}".format(a_file))
    return ''

def center_write(my_text):
    f.write("<center><font size=+4>{}</font></center>".format(my_text))

def html_table_make(val_array, array_of_dict):
    if len(val_array) == 0:
        f.write("<center><font size=+4>(nothing found, no table created)</font></center>\n")
    f.write("<center><table border=1>")
    for x in sorted(val_array):
        f.write("<tr><td>{}</td>".format(x))
        for y in array_of_dict:
            f.write("<td>{}</td>".format(y[x]))
        f.write("</tr>\n")
    f.write("</table></center>")

def now_of(my_time):
    my_time_int = round(float(my_time))
    return pendulum.from_timestamp(my_time_int, tz='local').format("YYYY/MM/DD HH:mm:ss")

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    temp_proj = i7.main_abb(arg)
    if temp_proj:
        my_proj = temp_proj
    elif arg == 'w':
        write_to_file = True
    elif arg.startswith("w="):
        write_to_file = True
        wild_cards = arg[2:]
    cmd_count += 1

if not my_proj:
    my_proj = i7.main_abb(i7.dir2proj())
    if not my_proj:
        sys.exit("Specify project or move to a directory with a project.")
    print("Pulling default project", my_proj)

out_file = os.path.join(i7.prt, "logpy-{}.htm".format(my_proj))

prefix = "reg-{}".format(my_proj)

os.chdir(i7.prt)

with open(os.path.join(i7.prt, "logfile.txt")) as file:
    for (line_count, line) in enumerate (file, 1):
        if not line.startswith(prefix):
            continue
        ary = line.strip().split("\t")
        if ary[1] == '0':
            last_success[ary[0]] = now_of(ary[2])
            last_success_time_taken[ary[0]] = ary[3]
        last_run[ary[0]] = now_of(ary[2])
        timestamp[ary[0]] = round(float(ary[2]))
        last_run_time_taken[ary[0]] = ary[3]
        last_errs[ary[0]] = int(ary[1])
        if not my_binary:
            my_binary = find_binary_in(ary[0])

never_pass = [x for x in last_errs if x not in last_success]
still_errs = [x for x in last_errs if x in last_success and last_run[x] > last_success[x]]
passed = [x for x in last_errs if x in last_success and last_run[x] == last_success[x]]

for l in last_run:
    l_mod = l.replace(".txt", "-mod.txt")
    raw_link[l] = '<a href="latest/trans-{}">{} original</a>'.format(l, l)
    mod_link[l] = '<a href="latest/trans-{}">{} modified</a>'.format(l_mod, l)

f = open(out_file, "w")

f.write("<html><title>LOG RUNS FOR {}</title>\n<body>\n".format(my_proj))

if len(never_pass) == 0:
    f.write("All files have passed at one time or another.\n")
else:
    html_table_make(never_pass, [ raw_link, last_run, last_errs, mod_link ])

center_write("Still errors")
html_table_make(still_errs, [ raw_link, last_success, last_success_time_taken, last_run, last_run_time_taken, last_errs, mod_link ])
center_write("Passing")
html_table_make(passed, [ raw_link, last_run, last_run_time_taken, mod_link ])

f.write("</body>\n</html>\n".format(my_proj))

for x in last_run:
    x0 = os.path.realpath(x)
    if not os.path.exists(x0):
        if x0 not in gone_files:
            print(x0, "could not be found. If it was moved, you may wish to delete it from the data.")
            gone_files[x0] += 1
        continue
    if os.stat(x).st_mtime > timestamp[x]:
        f.write("{} modified after test run {:.2f} seconds.<br />\n".format(x, os.stat(x).st_mtime - timestamp[x]))
    elif os.stat(my_binary).st_mtime > timestamp[x]:
        f.write("{} modified after binary file {:.2f} seconds.<br />\n".format(x, os.stat(my_binary).st_mtime - timestamp[x]))

f.close()

print("Spoiler alert: {} never passed, {} still have errors, {} passed.".format(len(never_pass), len(still_errs), len(passed)))

total_errs = len(still_errs) + len(never_pass)

if len(still_errs):
    my_max = max(still_errs, key=last_errs.get)
    print("Most still-errs is {} with {}".format(my_max, last_errs[my_max]))

if len(never_pass):
    my_max = max(never_pass, key=last_errs.get)
    print("Most never-pass is {} with {}".format(my_max, last_errs[my_max]))

if write_to_file:
    if total_errs == 0:
        sys.exit("No script to write.")
    else:
        total_commands = 0
        td = pendulum.now()
        todays_date = td.format("YYYYMMDD")
        f = open(todays_date, "w", newline='\n')
        for x in still_errs:
            if not wild_cards or re.search(wild_cards, x):
                f.write("r1a {}\n".format(x))
                total_commands += 1
        f.write("##################still has errors above, never passed below\n")
        for x in never_pass:
            if not wild_cards or re.search(wild_cards, x):
                f.write("r1a {}\n".format(x))
                total_commands += 1
        f.close()
        print("Wrote re-run script to", todays_date)
        if total_commands == 0:
            print("No commands were sent to the command file with wildcard {}, even though error files were found.".format(wild_cards))

os.system(out_file)
#g = glob.glob("c:/games/inform/prt/reg-{}-*.txt".format(my_proj))

#print(g)