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
import mytools as mt

base_dir_needed = "c:\\users\\andrew\\documents\\github"
set_author = True
set_commit = True
commit_message = ''
auto_date = True
auto_today_ok = False
days_back = 0
push_after_commit = False
no_verify = False
actual_time_commit_stamp = False
suppress_batch_nudge = False
only_show_last = False

by_end_of_month = False
by_end_of_week = False
by_end_of_year = False

def commit_maybe_push(cmd):
    os.system(cmd)
    if push_after_commit:
        mt.warn("Pushing changes after... (-np/-pn disables)")
        os.system("git push")
    else:
        mt.warn("Use -p to push changes after...")
    if not suppress_batch_nudge:
        mt.warn("You may wish to use LBA.BAT instead. Did you forget?")

def my_time(t):
    return time.strftime("%a %b %d %H:%M:%S", time.localtime(t))

def is_valid_time(my_string):
    ary = my_string.split(":")
    if len(ary) not in (2, 3):
        return False
    for x in ary:
        if not x.isdigit():
            return False
    return True

def usage(arg = ""):
    if arg: print("Invalid command", arg)
    else: print("USAGE")
    my_time = pendulum.today().subtract(seconds=min_before * 60 + sec_before)
    time_str = my_time.format("HH:mm:ss ZZ")
    print("=" * 50)
    mt.okay("a tries for auto date, ao says today is okay")
    mt.okay("at puts actual timestamp on a past-dated commit")
    mt.okay("r or x executes the command")
    print("p(project name) specifies the project name e.g. pmisc, though p = git push after git commit")
    print("l at the end runs git log too")
    print("fl gets the next missing date from the log. For instance, if the last commit is on October 14, it will be October 15.")
    print("m# specifies minutes before midnight")
    print("nc/na sets no author or commit change, and am amends manually.")
    print("nv = --no-verify as sometimes I may not want to copy over the very latest changes")
    print("s# specifies seconds before midnight in addition to minutes")
    print("so# specifies *only* seconds before midnight, setting minutes to 0")
    mt.okay("osl/ol only shows the last")
    print("! specifies a random number of seconds before midnight, from 1 to 600. Default is {:d} for a time of {:s}.".format(min_before * 60 + sec_before,
 time_str))
    print("A commit message can be put in quotes, and it needs a space.")
    print()
    print("emy/eym = end of month and year goals displayed. eoy/eom = end of year or month.")
    print()
    print("Previous standard usage is probably logm.py r(l) (!) (3)")
    print("Standard usage now is probably logm.py r(l) a \"commit-message\"")
    print("    Also logm.py -lf -r 'commit message' for serious backdating.")
    print()
    print("A number specifies the days back to look. If it is before midnight, nothing happens.")
    print()
    mt.warn("LBA (string) fast-tracks logm.py -r -at with lba.bat, the most common usage (note to self: batch file uses %~1 for string with spaces)")
    exit()

def per_day_metrics(days, end_goal = 'month'):
    import calendar
    d = pendulum.now()
    last_day = calendar.monthrange(d.year, d.month)[1]
    if end_goal == 'month':
        a1 = pendulum.local(d.year, d.month, last_day).timestamp() + 86400
    elif end_goal == 'year':
        a1 = pendulum.local(d.year + 1, 1, 1).timestamp()
    elif end_goal == 'week':
        a1 = pendulum.today().add(days = 7 - d.day_of_week).timestamp()
    a2 = d.timestamp()
    days_left = (a1-a2)/86400
    commits_per_day_total = (days + days_left - 1) / days_left
    commits_per_day_catchup = days / days_left
    if commits_per_day_total > 0:
        print("To get caught up by the end of the {}, you actually need {}-{} commits.".format(end_goal, int(days + days_left - 1), int(days + days_left)))
        print("That makes {:.3f}/{:.3f} commits per day current/actual commits. {:.3f} days left in the {}. Each commit shaves off {} per-day.".format(
            commits_per_day_total, commits_per_day_catchup, days_left, end_goal, mt.decimal_only(1 / days_left)))
    else:
        print("You don't need any specific goals.")

def bail_if_not_auto_ok():
    global set_author
    global set_commit
    if auto_today_ok:
        set_author = False
        set_commit = False
        return
    sys.exit("Set -ao to say auto-today is okay and commit with the current time.")

def get_date_delt(x, throw_error = False):
    if x.count(' ') > 1: return False
    ary = re.split("[-/]", x)
    if len(ary) < 2 or len(ary) > 3:
        if throw_error:
            sys.exit("Need array length of 2 or 3.")
        return 0
    dspace = ' '.join(ary)
    tdy = pendulum.today()
    if len(ary) == 2:
        y = pendulum.from_format(dspace, 'MM DD')
        if y > tdy:
            y = y.subtract(years=1)
            print(y, "subtracting a year", pendulum.today())
    else:
        try:
            y = pendulum.from_format(dspace, 'MM DD YY')
        except:
            sys.exit("Need format MM-DD-YY.")
        if tdy < y:
            sys.exit("The date you input is far ahead.")
    if abs(y.diff(tdy).in_years()) > 0:
        sys.exit("Can't have difference of a year or more.")
    return y.diff(tdy).in_days()

def days_since():
    result=subprocess.run(["git", "log", "-1"], stdout=subprocess.PIPE).stdout.decode("utf-8")
    ary = result.split('\n')
    day_start = my_time.start_of('day')
    for my in ary:
        if my.lower().startswith("date"):
            my = re.sub("^date: *", "", my, 0, re.IGNORECASE)
            x = pendulum.from_format(my, 'ddd MMM DD')
            temp = day_start.diff(x).in_days()
            if temp < 2:
                bail_if_not_auto_ok()
            return temp
    sys.exit("Could not differ git log -1 from current datetime.")

def add_my_files(files_to_add):
    if not files_to_add: return
    my_cmd = "git add {}".format(' '.join([mt.add_quotes_if_space(x) for x in files_to_add]))
    os.system(my_cmd)

def check_bare_commit(bare_commit, files_to_add, bail=False):
    if not bare_commit: return
    add_my_files(files_to_add)
    print("Just committing with -bc/bare commit flag.")
    commit_maybe_push(bare_commit_cmd)
    if bail: sys.exit()

time_zone = 5

min_before = 3
sec_before = 0

days = 0
count = 1
run_cmd = False
run_log = False
proj_shift_yet = ""
bare_commit = False
files_to_add = []
get_from_log = False
add_commands = []
force_time = []

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    arg_no_num = re.sub("[0-9]+$", "", arg)
    if not arg: usage("<blank parameter>")
    if arg.startswith("f:") or arg.startswith("a:"):
        files_to_add.append(arg[2:])
        print("Files to add:", arg[2:])
    elif os.path.exists(arg) or '*' in arg:
        print("Detecting {} as file(s)-to-add.".format(arg))
        files_to_add.append(arg)
    elif get_date_delt(arg):
        days_back = get_date_delt(arg) # do date delta
        auto_date = False
    elif ' ' in arg:
        if commit_message: sys.exit("Duplicate commit message {} vs {}".format(sys.argv[count].strip(), commit_message))
        commit_message = sys.argv[count].strip()
    elif re.search("^[rxl]+$", arg):
        run_cmd = 'r' in arg or 'x' in arg
        cmd_counts = arg.count('r') + arg.count('x')
        run_log = 'l' in arg
        if cmd_counts == 0: print("WARNING an L without an R or X means nothing.")
        elif cmd_counts > 1: print("WARNING extra r/x in the argument to run the command mean nothing.")
    elif arg.isdigit():
        days = int(arg)
        auto_date = False
    elif i7.proj_exp(arg, False):
        if proj_shift_yet:
            print("WARNING shifting from project", proj_shift_yet)
        proj_shift_yet = i7.proj_exp(arg, False)
        if not proj_shift_yet:
            sys.exit("No such project or abbreviation {:s}".format(arg))
        print("Found project for {:s} as {:s} but -p is extra-super-proper usage.".format(arg, proj_shift_yet))
    elif arg == '!':
        min_before = 0
        sec_before = int(random.random() * 600) + 1
        print("Random seconds before =", sec_before)
    elif is_valid_time(arg):
        force_time = [int(x) for x in arg.split(":")]
        if len(force_time) == 2:
            force_time.append(0)
    elif arg == 'p':
        push_after_commit = True
    elif arg == 'np' or arg == 'pn':
        push_after_commit = False
    elif arg[0] == 'p':
        if proj_shift_yet:
            mt.warn("WARNING re-shifting from project", proj_shift_yet)
        proj_shift_yet = i7.proj_exp(arg[1:])
        if not proj_shift_yet:
            mt.bailfail("No such project or abbreviation {:s}".format(arg[1:]))
    elif arg_no_num == 'm':
        try:
            min_before = int(arg[1:])
        except:
            sys.exit("-m (minutes) must take a positive integer after! \n(NOTE: -m for message would be redundant. Anything that looks like a message is flagged as such.)")
    elif arg[:2] == 'so' and arg[2:].isdigit():
        sec_before = int(arg[2:])
        min_before = 0
        #sys.exit("-so must take a positive integer after!")
    elif arg[0] == 's' and arg[1:].isdigit():
        sec_before = int(arg[1:])
        #sys.exit("-s (seconds) must take a positive integer after!")
    elif arg == 'a':
        auto_date = True
    elif arg == 'ao':
        auto_date = True
        auto_today_ok = True
    elif arg == 'at':
        actual_time_commit_stamp = True
    elif arg == 'fl' or arg == 'lf':
        get_from_log = True
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
    elif arg == 'nv':
        no_verify = True
    elif arg == 'ea':
        by_end_of_week = by_end_of_month = by_end_of_year = True
    elif arg in ( 'ol', 'osl' ):
        only_show_last = True
    elif re.search(r'e(o?)[wmy]+', arg):
        by_end_of_week = 'w' in arg
        by_end_of_month = 'm' in arg
        by_end_of_year = 'y' in arg
    elif arg == 'sn':
        suppress_batch_nudge = True
    elif arg == '?': usage()
    else: usage(arg)
    count += 1

if base_dir_needed not in os.getcwd().lower():
    mt.bailfail("You need to go to {:s} or a child directory to edit a git log meaningfully, or you can use -p(project) or (project).".format(base_dir_needed))

my_time = pendulum.today()

if actual_time_commit_stamp:
    cur_date_time = pendulum.now().format("YY/MM/DD HH:mm:ss")
    commit_message = "{} {}".format(cur_date_time, commit_message)

if commit_message:
    print("Commit message from cmd line:", commit_message)

bare_commit_cmd = "git commit{} -m \"{}\"".format(" --no-verify" if no_verify else "", commit_message)

if get_from_log:
    days = days_since()
    if days == 0: sys.exit("Can't use FL flag since we already have a commit today.")
    print("Days_since in log is", days, "So next commit will be", days - 1)
    days -= 1

if auto_date:
    result = subprocess.run(["git", "show", "--summary"], stdout=subprocess.PIPE)
    change_list = subprocess.run(["git", "status"], stdout=subprocess.PIPE)
    valid_commit = 'to be committed' in change_list.stdout.decode('utf-8')
    lines = re.split("[\r\n]+", result.stdout.decode('utf-8'))
    for l in lines:
        if "Date:" in l:
            l = re.sub("Date: *", "", l)
            x = pendulum.parse(l, strict=False)
            day_diff = x.diff(my_time).in_days()
            if day_diff < 1:
                check_bare_commit(bare_commit, files_to_add, bail=True)
                sys.exit("LOGM has no use, since you already have a commit for today!\n    You can do a bare commit with -bc, no need for -r.\n    I'm making it a bit tricky for a reason, so you don't do so accidentally.")
            days = day_diff - valid_commit
            if days == 0:
                print("You don't need logm--you can commit with the current time to keep your streak going!")
                bail_if_not_auto_ok()
            else:
                print("Last commit-space is back {} day{}.".format(days, '' if days == 1 else 's'))
                if days == 0: break
                if only_show_last:
                    sys.exit()
                if not (by_end_of_week or by_end_of_month or by_end_of_year): break
                if by_end_of_week:
                    per_day_metrics(days, 'week')
                if by_end_of_month:
                    per_day_metrics(days, 'month')
                if by_end_of_year:
                    per_day_metrics(days, 'year')
            break
    if not actual_time_commit_stamp:
        print("Reminder: if you want a time-stamp, you can add the -at flag.")

if proj_shift_yet:
    ghdir = os.path.join(base_dir_needed, proj_shift_yet if proj_shift_yet not in i7.i7gx.keys() else i7.i7gx[proj_shift_yet])
    print("Forcing to", ghdir)
    os.chdir(ghdir)

if sec_before > 60 and min_before > 0: sys.exit(">60 seconds + minutes may be confusing. Use -so to remove this.")
if min_before > 60 or sec_before > 3600: sys.exit("Minutes and/or seconds are too high. 3600 sec is the limit, and you have {:d}.".format(min_before * 60 + sec_before))

mod_date = my_time.subtract(days=days-1)

sec_before += 60 * min_before
mod_date = mod_date.subtract(seconds=sec_before)
if days_back: mod_date = mod_date.subtract(days=days_back)

if force_time:
    mod_date = mod_date.set(hour = force_time[0], minute = force_time[1], second = force_time[2])

date_string = mod_date.format("ddd MMM DD YYYY HH:mm:ss ZZ")

if run_cmd:
    add_my_files(files_to_add)
    if auto_date and days == 0:
        print("Forcing message-only commit since auto_date is on and day_delta is zero.")
        commit_maybe_push(bare_commit_cmd)
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
            commit_maybe_push("git commit -m \"{}\"".format(commit_message))
        if not (set_author or set_commit):
            print("Amending date via command line:", date_string)
            commit_maybe_push("git commit --amend --date=\"{} {}\"".format(date_string, time_zone))
    if run_log:
        time.sleep(4)
        os.system("git log")
else:
    if auto_date and days == 0:
        print("No date adjustment will be necessary.")
    else:
        print("The date-string things will be sent to is", date_string)
    print("Use -r to run.")
    if not commit_message: print("Also, remember to set a commit message. Any string with a space (use quotes) counts as a commit message.")
