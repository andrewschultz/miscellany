# logfile's format is 0=file 1=errors 2=time run finished 3=time taken

import mytools as mt
import re
import os
import pendulum
import i7
import glob
import sys
from collections import defaultdict
from shutil import copy

last_success = defaultdict(int)
last_success_time_taken = defaultdict(int)
last_run = defaultdict(int)
last_run_time_taken = defaultdict(int)
last_errs = defaultdict(int)
blank = defaultdict(int)
raw_link = defaultdict(str)
mod_link = defaultdict(str)
timestamp = defaultdict(int)
orphaned_files = defaultdict(int)

extra_data_file_flags = 3

wild_cards = ''

write_errors_to_script = False
write_current_project = False
read_i7_default_project = False
save_old_copy = False

delete_array = []
runs_logfile = 'logfile.txt'
logfile_temp = 'logfile-temp.txt'

my_binary = ''
my_proj = ''

def usage(header = 'usage'):
    print('=' * 20 + header + '=' * 20)
    print("w = write to file")
    print("w= = wild card")
    print("wp/pw = write current project to i7 data file")
    print("o# = orphaned file flags, 1=warn 2=don't process, oa=all")
    sys.exit()

def find_orphans(my_array):
    for x in last_run:
        x0 = os.path.realpath(x)
        if not os.path.exists(x0):
            if x0 not in orphaned_files:
                print(x0, "is orphaned (in the PRT directory but not the source directory. If it was moved, you may wish to delete it from the data.")
                del_cmd += "    erase {}\n".format(x)
                orphaned_files[x0] += 1
            continue
        if os.stat(x).st_mtime > timestamp[x]:
            f.write("{} modified after test run {:.2f} seconds.<br />\n".format(x, os.stat(x).st_mtime - timestamp[x]))
        elif os.stat(my_binary).st_mtime > timestamp[x]:
            f.write("{} modified after binary file {:.2f} seconds.<br />\n".format(x, os.stat(my_binary).st_mtime - timestamp[x]))

def zap_files(del_array):
    f = open(runs_logfile)
    ary = f.readlines()
    out_string = ""
    count = 0
    my_dels = defaultdict(int)
    for x in ary:
        temp = x.split("\t")
        if temp[0] in del_array:
            my_dels[temp[0]] += 1
            continue
        out_string += x
        count += 1
    f.close()
    if not count:
        sys.exit("Didn't find any lines to delete.")
    f = open(logfile_temp, 'w', newline='\n')
    f.write(out_string)
    f.close()
    print("How much got erased, where:")
    for x in sorted(my_dels):
        print(x, my_dels[x])
    copy(logfile_temp, runs_logfile)
    sys.exit()

def float_stub(x):
    temp = re.sub(" .*", "", x)
    try:
        return float(temp)
    except:
        print("Unable to get a float from", temp)
        return 0

def find_binary_in(a_file):
    with open(a_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if 'game:' in line.lower():
                raw = re.sub(".*: *", "", line.strip())
                raw = re.sub(".*prt", i7.prt, raw)
                return raw
    print("Warning no game file found in {}".format(a_file))
    return ''

def center_write(my_text, my_num = 0):
    f.write("<center><font size=+4>{}{}</font></center>".format(my_text, '' if my_num == 0 else '({})'.format(my_num)))


def html_table_make(val_array, array_of_dict, header_array = [ 'Name', 'Original', 'Last time of day', 'Errors', 'Last test run length', 'Modified' ]):
    if len(val_array) == 0:
        f.write("<center><font size=+4>(nothing found, no table created)</font></center>\n")
    f.write("<center><table border=1>")
    header_string = ""
    for h in header_array:
        header_string += "<th>{}</th>".format(h)
    f.write(header_string + "\n")
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
    (arg, num, valid_num) = mt.parnum(sys.argv[cmd_count], allow_float = True)
    temp_proj = i7.main_abb(arg)
    if temp_proj:
        my_proj = temp_proj
    elif arg[:2] == 'd=':
        delete_array = arg[2:].split(',')
    elif arg == 'w':
        write_errors_to_script = True
    elif arg.startswith("w="):
        write_errors_to_script = True
        wild_cards = arg[2:]
    elif arg in ( 'so', 'os' ):
        save_old_copy = True
    elif mt.alfmatch('nso', arg):
        save_old_copy = False
    elif arg in ( 'wp', 'pw' ):
        write_current_project = True
    elif arg == 'o':
        if not valid_num:
            extra_data_file_flags = -1
        else:
            extra_data_file_flags = num
    elif arg == 'oa':
        extra_data_file_flags = -1
    elif arg == '?':
        usage()
    else:
        usage('invalid command {}'.format(arg))
    cmd_count += 1

if not my_proj:
    my_proj = i7.main_abb(i7.dir2proj())
    if not my_proj:
        my_proj = i7.read_latest_proj()[0]
        read_i7_default_project = True
        if not my_proj:
            sys.exit("No temporary current project specified in i7d.txt. Specify a project or move to a directory with a project.")
        print("Pulling project from CFG", my_proj)
    else:
        print("Pulling project from current directory", my_proj)

out_file = os.path.join(i7.prt, "logpy-{}.htm".format(my_proj))

prefix = "reg-{}".format(my_proj)

os.chdir(i7.prt)

if delete_array:
    zap_files(delete_array)

extra_data_files = []
original_dir = i7.proj2dir(my_proj)

EXTRA_DATA_WARN = 1
EXTRA_DATA_SKIPCHECKING = 2

orphan_count = 0

del_cmd = ''

if save_old_copy:
    old_file = os.path.join(i7.prt, "logpy-old-{}.htm".format(my_proj))
    try:
        shutil.copy(out_file, old_file)
    except:
        print("Could not find {} to back up.".format(out_file))

with open(os.path.join(i7.prt, runs_logfile)) as file:
    for (line_count, line) in enumerate (file, 1):
        if not line.startswith(prefix):
            continue
        ary = line.strip().split("\t")
        if extra_data_file_flags:
            original_file = os.path.join(original_dir, ary[0])
            if not os.path.exists(original_file):
                if original_file not in extra_data_files:
                    extra_data_files.append(original_file)
                    if extra_data_file_flags | EXTRA_DATA_WARN:
                        orphan_count += 1
                        print("Found extra-data file (data, but not in original source directory) {} line {} of {}: {}".format(orphan_count, line_count, runs_logfile, ary[0]))
                        del_cmd += "    convlog.py d={}\n".format(ary[0])
                        prt_file = os.path.normpath(os.path.join(i7.prt, ary[0]))
                        if os.path.exists(prt_file):
                            print("You may also wish to erase {}".format(prt_file))
                            del_cmd += "    erase {}\n".format(prt_file)
                if extra_data_file_flags | EXTRA_DATA_SKIPCHECKING:
                    continue
        if ary[1] == '0':
            last_success[ary[0]] = now_of(ary[2])
            last_success_time_taken[ary[0]] = ary[3]
        last_run[ary[0]] = now_of(ary[2])
        timestamp[ary[0]] = round(float(ary[2]))
        last_run_time_taken[ary[0]] = "{:.2f} sec".format(float(ary[3]))
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
    f.write("<center><font size=+3>All files have passed at one time or another.</font></center>\n")
else:
    center_write("Never passed", len(never_pass))
    html_table_make(never_pass, [ raw_link, last_run, last_errs, last_run_time_taken, mod_link ])

center_write("Still errors", len(still_errs))
html_table_make(still_errs, [ raw_link, last_success, last_success_time_taken, last_run, last_run_time_taken, last_errs, mod_link ])
center_write("Passing", len(passed))
html_table_make(passed, [ raw_link, last_run, last_run_time_taken, mod_link ])

if len(extra_data_files):
    f.write("\n<font size=+4>ORPHANED FILES ({}):</font>\n<ul>\n".format(len(extra_data_files)))
    for x in extra_data_files:
        f.write("<li>{}</li>\n".format(x))
    f.write("</ul>\n")

f.write("</body>\n</html>\n".format(my_proj))

find_orphans(last_run)

f.close()

if del_cmd:
    print("Delete command:")
    print(del_cmd)

print("Spoiler alert: {} never passed, {} still have errors, {} passed.".format(len(never_pass), len(still_errs), len(passed)))

total_errs = len(still_errs) + len(never_pass)

still_times = never_times = 0

if len(still_errs):
    my_max = max(still_errs, key=last_errs.get)
    print("Most still-errs is {} with {}".format(my_max, last_errs[my_max]))

if len(never_pass):
    my_max = max(never_pass, key=last_errs.get)
    print("Most never-pass is {} with {}".format(my_max, last_errs[my_max]))

if write_errors_to_script:
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
                still_times += float_stub(last_run_time_taken[x])
        f.write("##################still has errors above, never passed below\n")
        for x in never_pass:
            if not wild_cards or re.search(wild_cards, x):
                f.write("r1a {}\n".format(x))
                total_commands += 1
                never_times += float_stub(last_run_time_taken[x])
        if still_times:
            f.write("# time for files still left: {}\n".format(still_times))
        if never_times:
            f.write("# time for files never passed: {}\n".format(never_times))
        if still_times and never_times:
            f.write("# total time for files still to pass: {}\n".format(still_times + never_times))
        f.close()
        print("Wrote re-run script to", todays_date)
        if total_commands == 0:
            print("No commands were sent to the command file with wildcard {}, even though error files were found.".format(wild_cards))

if still_times:
    print("# time for files still left: {}".format(still_times))
if never_times:
    print("# time for files never passed: {}".format(never_times))
if still_times and never_times:
    print("# total time for files still to pass: {}".format(still_times + never_times))

if write_current_project:
    i7.write_latest_project(my_proj, give_success_feedback = True)
elif read_i7_default_project:
    print("Note we can write a new default project with -wp or -pw.")

os.system(out_file)
#g = glob.glob("c:/games/inform/prt/reg-{}-*.txt".format(my_proj))

#print(g)