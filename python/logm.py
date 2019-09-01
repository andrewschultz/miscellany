#
# logm.py
# modifies the log date
#
# no arguments needed ... 3 minutes before midnight is the default
# ! = random, so = seconds, max of 1 hour before
# daylight savings time is accounted for

import random
import re
import os
import sys
import time
import i7
import pendulum
import subprocess

base_dir_needed = "c:\\users\\andrew\\documents\\github"
set_author = True
set_commit = True
commit_message = ''
auto_date = False
auto_today_ok = False

def my_time(t):
    return time.strftime("%a %b %d %H:%M:%S", time.localtime(t))

def usage(arg = ""):
    if arg: print("Invalid command", arg)
    else: print("USAGE")
    my_time = pendulum.today().subtract(seconds=min_before * 60 + sec_before)
    time_str = my_time.format("HH:mm:ss ZZ")
    print("=" * 50)
    print("a tries for auto date, ao says today is okay")
    print("r or x executes the command")
    print("p(project name) specifies the project name e.g. pmisc")
    print("l at the end runs git log too")
    print("m# specifies minutes before midnight")
    print("nc/na sets no author or commit change, and am amends manually.")
    print("s# specifies seconds before midnight in addition to minutes")
    print("so# specifies *only* seconds before midnight, setting minutes to 0")
    print("! specifies a random number of seconds before midnight, from 1 to 600. Default is {:d} for a time of {:s}.".format(min_before * 60 + sec_before,
 time_str))
    print("A commit message can be put in quotes, and it needs a space.")
    print()
    print("Standard usage is probably logm.py rl (!) (3)")
    print()
    print("a number specifies the days back to look. If it is before midnight, nothing happens.")
    exit()

time_zone = 5

min_before = 3
sec_before = 0

days = 0
count = 1
run_cmd = False
run_log = False
proj_shift_yet = ""
bare_commit = False

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if ' ' in arg:
        commit_message = sys.argv[count]
        print("Commit message from cmd line:", commit_message)
    elif re.search("^[rxl]+", arg):
        run_cmd = 'r' in arg or 'x' in arg
        cmd_counts = arg.count('r') + arg.count('x')
        run_log = 'l' in arg
        if cmd_counts == 0: print("WARNING an L without an R or X means nothing.")
        elif cmd_counts > 1: print("WARNING extra r/x in the argument to run the command mean nothing.")
    elif arg.isdigit(): days = int(arg)
    elif i7.proj_exp(arg, False):
        if proj_shift_yet:
            print("WARNING shifting from project", proj_shift_yet)
        proj_shift_yet = i7.proj_exp(arg, False)
        if not proj_shift_yet:
            sys.exit("No such project or abbreviation {:s}".format(arg))
        print("Found project for {:s} as {:s} but -p is extra-super-proper usage.".format(arg, proj_shift_yet))
    elif arg == '!':
        min_before = 0
        sec_before = int(random.random()) * 600 + 1
        print("Random seconds before =", sec_before)
    elif arg[0] == 'p':
        if proj_shift_yet:
            print("WARNING shifting from project", proj_shift_yet)
        proj_shift_yet = i7.proj_exp(arg[1:])
        if not proj_shift_yet:
            sys.exit("No such project or abbreviation {:s}".format(arg[1:]))
    elif arg[0] == 'm':
        if arg[1:].isdigit(): min_before = int(arg[1:])
        else: sys.exit("-m must take a positive integer after!")
    elif arg[:2] == 'so':
        if arg[2:].isdigit():
            sec_before = int(arg[2:])
            min_before = 0
        else: sys.exit("-so must take a positive integer after!")
    elif arg[0] == 's':
        if arg[1:].isdigit(): sec_before = int(arg[1:])
        else: sys.exit("-s must take a positive integer after!")
    elif arg == 'a':
        auto_date = True
    elif arg == 'ao':
        auto_date = True
        auto_today_ok = True
    elif arg == 'na':
        set_author = False
        set_commit = True
    elif arg == 'nc':
        set_author = False
        set_commit = True
    elif arg == 'am':
        set_author = False
        set_commit = False
    elif arg == 'bc':
        bare_commit = True
    elif arg == '?': usage()
    else: usage()
    count += 1

my_time = pendulum.today()

bare_commit_cmd = "git commit -m \"{}\"".format(commit_message)

if auto_date:
    result=subprocess.run(["git", "show", "--summary"], stdout=subprocess.PIPE)
    lines = re.split("[\r\n]+", result.stdout.decode('utf-8'))
    for l in lines:
        if "Date:" in l:
            l = re.sub("Date: *", "", l)
            x = pendulum.parse(l, strict=False)
            day_diff = x.diff(my_time).in_days()
            if day_diff < 1:
                if bare_commit:
                    print("Just committing.")
                    print(bare_commit_cmd)
                    os.system(bare_commit_cmd)
                    sys.exit()
                sys.exit("LOGM has no use, since you already have a commit for today!\n    You can do a bare commit with -bc, no need for -r.\n    I'm making it a bit tricky for a reason, so you don't do so accidentally.")
            days = day_diff - 1
            if days == 0:
                print("You don't need logm--you can commit with the current time to keep your streak going!")
                if auto_today_ok:
                    set_author = False
                    set_commit = False
                    continue
                sys.exit("Set -ao to say auto-today is okay.")
            else:
                print("Last commit-space is back {} day{}.".format(days, '' if days == 1 else 's'))
            break

if proj_shift_yet:
    ghdir = os.path.join(base_dir_needed, proj_shift_yet if proj_shift_yet not in i7.i7gx.keys() else i7.i7gx[proj_shift_yet])
    print("Forcing to", ghdir)
    os.chdir(ghdir)

if base_dir_needed not in os.getcwd().lower():
    sys.exit("You need to go to {:s} or a child directory to edit a git log meaningfully, or you can use -p(project) or (project).".format(base_dir_needed))

if sec_before > 60 and min_before > 0: sys.exit(">60 seconds + minutes may be confusing. Use -so to remove this.")
if min_before > 60 or sec_before > 3600: sys.exit("Minutes and/or seconds are too high. 3600 sec is the limit, and you have {:d}.".format(min_before * 60 + sec_before))

mod_date = my_time.subtract(days=days-1)

sec_before += 60 * min_before
mod_date = mod_date.subtract(seconds=sec_before)

date_string = mod_date.format("ddd MMM DD YYYY HH:mm:ss ZZ")

if run_cmd:
    if auto_date and days == 0:
        print("Forcing message-only commit since auto_date is on and day_delta is zero.")
        os.system(bare_commit_cmd)
    else:
        if set_author:
            print("set GIT_AUTHOR_DATE=\"{}\"".format(date_string))
            os.environ["GIT_AUTHOR_DATE"] = date_string
        if set_commit:
            print("set GIT_COMMITTER_DATE=\"{}\"".format(date_string))
            os.environ["GIT_COMMITTER_DATE"] = date_string
        if set_author or set_commit:
            if not commit_message:
                sys.exit("You need either a commit message (something with spaces, in quotes) or to set -am to amend manually!")
            os.system("git commit -m \"{}\"".format(commit_message))
        if not (set_author or set_commit):
            print("Amending date via command line:", date_string)
            os.system("git commit --amend --date=\"{} {}\"".format(date_string, time_zone))
    if run_log:
        time.sleep(4)
        os.system("git log")
else:
    if auto_date and days == 0:
        print("No date adjustment will be necessary.")
    else:
        print("The date-string things will be sent to is", date_string)
    print("Use -r to run.")
    if not commit_message: print("Also, remember to set a commit message. Anything with a space counts as a commit message.")
