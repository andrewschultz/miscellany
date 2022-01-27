############################################
#hrcheck.py (formerly hrcheck.pl/sov.pl for stack overflow stuff)
#
#scheduling stuff, and stuff
#hrcheck.txt edited for what, when
#
#example of one line:
#
#11|http://www.thefreedictionary.com
#
#Twice-weekly thing, half past noon
#d2,5/12h|http://www.ebay.com
#
#Twice-monthly thing
#m=2,17/12|http://www.discovercard.com
#
#tphb = quarter hours
#:(0-5) = 0 past, 10 past, etc.
#
#0 = monday
#
# put tasks that are once a day at my discretion, any time, to check off
# todo: hrcheck use taskscheduler ~1 hour after
#
# How to set up on a new computer to run every half hour:
# schtasks /create /SC MINUTE /MO 30 /TN hrcheck /TR py c:\writing\scripts\hrcheck.py 0:33 /st 06:03

import sys
import os
import datetime
import re
import calendar
import time
import pendulum
import mytools as mt

retired_file = 'c:/writing/scripts/hrcheck.txt'
hrcheck_list = 'c:/writing/scripts/hrcheck-list.txt'

dupes = ['', 's']

from collections import defaultdict

init_delay = 0
hour_parts = 4

of_day = defaultdict(str)
of_neg_day = defaultdict(list)
quarter_mod_shift = defaultdict(str)
of_week = defaultdict(lambda: defaultdict(str))
of_month = defaultdict(lambda: defaultdict(str))

bookmark_dict = defaultdict(list)
bookmark_file = defaultdict(list)
extra_bookmark = defaultdict(list)
backbkmk = defaultdict(str)

lock_file   = "c:\\writing\\scripts\\hrchecklock.txt";
queue_file   = "c:\\writing\\scripts\\hrcheckqueue.txt";

code   = "c:\\writing\\scripts\\hrcheck.py";

bailFile   = "c:\\writing\\scripts\\hrcheck-bailfile.txt";
forgotFile = "c:\\writing\\scripts\\hrcheck-forgotfile.txt";
anyExtra   = 0;
extraFiles = [];

cmds_to_ignore = []

show_warnings = False

verbose = False

only_check_expired = False
found_expiry = False

# thanks to https://stackoverflow.com/questions/42950/get-last-day-of-the-month-in-python

def find_in_one_checkfile(my_string, f, find_comments):
    base_name = os.path.basename(f)
    with open(f) as file:
        for (line_count, line) in enumerate (file, 1):
            if not find_comments and line.startswith("#"):
                continue
            if my_string in line.lower():
                print("Found instance of <<{}>> at line {} of {}.".format(my_string, line_count, base_name))
                mt.add_postopen(f, line_count)
    return

def find_in_checkfiles(my_string, find_comments_first_pass, ignore_comments):
    if find_comments_first_pass and ignore_comments:
        print("WARNING: conflicting options C and I to both find comments and ignore them. Finding comments (C) overrides ignoring comments (I).")
    for x in hrcheck_array:
        find_in_one_checkfile(my_string, x, find_comments_first_pass)
    if not find_comments_first_pass and not ignore_comments: # second pass through, this time looking for comments, assuming we ignored them first time
        for x in hrcheck_array:
            find_in_one_checkfile(my_string, x, find_comments_first_pass)
    mt.postopen()
    print("Nothing found for <<{}>>.".format(my_string))
    sys.exit()

def is_time(t, bail = False):
    x = t.count(":")
    if x != 1:
        if bail: sys.exit("Time must have 1 colon")
        return False
    y = t.split(":")
    return y[0].isdigit() and y[1].isdigit()

def last_day_of_month(date):
    x = pendulum.now()
    y = x.add(months=1)
    return (y-x).days

def usage():
    print("=" * 50)
    print("hh = normalizes to half hour e.g. :12 or :18 look for both :00 and :15 tipoffs. nh/hn turns it off.")
    print("rp/p/r decides whether to print or run current commands")
    print("l/ul/lu = lock the lockfile, u = unlock the lockfile, q = run the queue file, lq = list queue, kq/qk=keep queue file, qm = max to run in queue")
    print("id specifies initial delay")
    print("e=edit main file, ea=edit all ex=edit extra ep=edit private")
    print("b= = bookmarks to run, bp prints bookmarks")
    print("0 = Monday, 6 = Sunday for days of week. 1-31 for days of month.")
    print("v = verbose")
    print("f/s(c):(string) = find string in file, c = look in comments too")
    sys.exit()

def get_file_list_by_priority():
    temp_array = []
    with open(hrcheck_list) as file:
        for (line_count, line) in enumerate (file, 1):
            temp_array.extend(line.strip().split(","))
    return temp_array

def print_all_bookmarks():
    for x in sorted(extra_bookmark):
        print("    ===={}{} in {} ({} cmds): {}\n".format(x, "({})".format('/'.join(extra_bookmark[x])) if extra_bookmark[x] else "", os.path.basename(bookmark_file[x]), len(bookmark_dict[x]), ', '.join(bookmark_dict[x])))
    sys.exit()

def garbage_collect(x):
    y = re.sub("^\\\\", "", x) # stuff that needs to go first or last
    return y

def my_time(x):
    if x[0] == '-': return int(x)
    hr = { 'h': 2, 'p': 3, 'b': 1, 't': 0 }
    for q in hr:
        if x[-1] == q:
            return int(x[:-1]) * 4 + hr[q]
    return int(x) * 4

def make_time_array(j, k, line_count):
    quarter_delta = 0
    my_weekday = 0
    my_monthday = 0
    monthday_array = []
    weekday_array = []
    day_array = []
    j = garbage_collect(j)
    slash_array = j.split("/")
    kn = k + "\n"
    for q in slash_array:
        if q.startswith("m="):
            monthday_array = q[2:].split(",")
        elif q.startswith("d="):
            weekday_array = q[2:].split(",")
        elif q.startswith("q="):
            quarter_delta = int(q[2:])
        elif q.startswith("m") or q.startswith("d") or q.startswith("q"):
            print("Uh oh, line {0} has time starting with m/d/q and not m=/d=/q=. Fix this.".format(line_count), j, q)
            return
        else:
            hour_array = [my_time(x) for x in q.split(",")]
    if not hour_array:
        print("Uh oh, line {} does not define an hour array along with a month or day: {}".format(line_count, j))
    if len(monthday_array):
        for m in monthday_array:
            for h in hour_array:
                if verbose:
                    print("Monthday/hour adding", m, h)
                of_month[int(h)][int(m)] += kn
    if len(weekday_array):
        for w in weekday_array:
            for h in hour_array:
                if verbose:
                    print("Weekday/hour adding", w, h, j, k)
                of_week[int(h)][int(w)] += kn
    if not len(monthday_array) and not len(weekday_array):
        for h in hour_array:
            hi = int(h)
            if hi >= 0:
                of_day[int(h)] += kn
            else:
                quarter_mod_shift[kn.strip()] = quarter_delta
                of_neg_day[-hi].append(kn.strip())
    return

def read_hourly_check(a):
    global found_expiry
    old_line = ""
    old_cmd = ""
    one_line_only = False
    bookmark_string = ""
    bookmark_last_line = 0
    ab = os.path.basename(a)
    if show_warnings > -1: print("reading", ab)
    with open(a) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"):
                if line_count < 6:
                    print("WARNING: {} may have had a semicolon near the top (line {}) for testing/skipping purposes.".format(a, line_count))
                    mt.add_post(a, line_count)
                break
            if line.startswith("#"): continue
            line = line.strip()
            if line.startswith("X:"):
                l2 = re.sub("\|.*", "", line[2:])
                line = re.sub("^.*?\|", "", line)
                try:
                    expiry_date = pendulum.from_format(l2, 'YYYY-MM-DD', tz = pendulum.now().timezone_name).add(days = 1)
                except:
                    print("Invalid expiry date {} after X: in {} at line {}. ".format(l2, a, line_count))
                    expiry_date = pendulum.now(pendulum.now()).add(days = 1)
                if pendulum.now() >= expiry_date:
                    print("WARNING: daily task at line {} of {} has expired as of {}.".format(line_count, a, l2))
                    if only_check_expired:
                        mt.add_post(a, line_count, priority = 8)
                        found_expiry = True
            if line.count("|") > 1:
                print("WARNING: too many OR pipes (replace with slash?) {} line {}: {}".format(ab, line_count, line.strip()))
                mt.add_post(a, line_count)
            if line.startswith("="):
                bookmark_past = bookmark_string
                bookmark_string = re.sub("^=*", "", line.lower().strip())
                bookmark_string = re.sub(" *#[^#]$", "", bookmark_string)
                if bookmark_past and bookmark_string:
                    print("WARNING bookmark {} opened at line {} file {} was not closed before opening new bookmark {} at line {}.".format(bookmark_past, bookmark_last_line, ab, bookmark_string, line_count))
                bookmark_last_line = line_count
                if not bookmark_string: continue
                if bookmark_string.startswith(">"):
                    one_line_only = True
                    bookmark_string = bookmark_string[1:]
                temp_bookmark_ary = bookmark_string.split(",")
                bookmark_ary = []
                for b in temp_bookmark_ary:
                    if b in bookmark_dict:
                        if show_warnings: print("WARNING line {} bookmark {} redefined".format(line_count, bookmark_string))
                    else:
                        bookmark_ary.append(b)
                if len(bookmark_ary) > 1:
                    bookmark_string = re.sub(",.*", "", bookmark_string)
                    if verbose:
                        print(bookmark_ary[0])
                        print(bookmark_ary[1:])
                    extra_bookmark[bookmark_ary[0]] = bookmark_ary[1:]
                    for u in bookmark_ary[1:]:
                        backbkmk[u] = bookmark_ary[0]
                continue
            if "|" not in line:
                if show_warnings: print("WARNING odd line {:d}:\n    {:s}".format(line_count, line.lower().strip()))
                continue
            line = line.strip()
            if line[0] == '"':
                line = old_cmd + line[1:]
                if verbose:
                    print("Line {:d} of {:s} uses quotes to copy previous line and is {:s}.".format(line_count, ab, line.strip()))
            a1 = line.split("|")
            if len(a1) > 2:
                if show_warnings:
                    print("WARNING too many variables, can't yet parse {0} line {1} (maybe you want a forward slash instead of |):\n    {:2}".format(bn, line_count, line))
                    mt.add_post(a, line_count)
                continue
            a3 = re.sub("\t", "\n", a1[-1])
            make_time_array(a1[0].lower(), a3, line_count)
            if bookmark_string:
                bookmark_file[bookmark_string] = a
                bookmark_dict[bookmark_string] += a1[-1].split("\t")
                if one_line_only:
                    bookmark_string = ""
                    one_line_only = False
            old_line = line
            old_cmd = re.sub("\|[^\|]*$", "", old_line)
    if bookmark_string:
        print("WARNING file {} ends with bookmark string {} invoked at line {}.".format(a, bookmark_string, bookmark_line))
        mt.add_post(a, bookmark_last_line)

def check_print_run(x, msg="(no message)"):
    if not x: return 0
    if print_cmd: print("***running", msg, x)
    if run_cmd:
        if x.startswith("+host"):
            mt.hosts_file_toggle(re.sub(".*[ \t]", "", x), allow_website_access = True)
        elif x.startswith("-host"):
            mt.hosts_file_toggle(re.sub(".*[ \t]", "", x), allow_website_access = False)
        elif x.startswith("http"):
            if '^&' in x:
                x = x.replace('^&', '&')
                print("WARNING: get rid of ^& and replace with &, as we are using os.startfile for websites and not os.system.")
            os.startfile(x)
        else:
            for y in cmds_to_ignore:
                if y in x:
                    return 0
            os.system(x)
    return 1

def carve_up(q, msg):
    if not q: return 0
    retval = 0
    ary = q.strip().split("\n")
    for x in ary:
        retval += check_print_run(x, msg)
    return retval

def carve_neg(ti):
    retval = 0
    for delta_group in of_neg_day.keys():
        for neg_cmd in of_neg_day[delta_group]:
            if ti % delta_group == quarter_mod_shift[neg_cmd]:
                retval += check_print_run(neg_cmd, "every-x-hours {:d} {:d}-per-hour units".format(delta_group, hour_parts))
    return retval

def see_what_to_run(ti, wd, md, hh):
    print(ti, "= time index", wd, "= weekday index", md, "= monthday index")
    print(hh, "= whether to cover the full half-hour or just the fifteen-minute sector")
    totals = 0
    totals += carve_neg(ti ^ hh)
    totals += carve_up(of_day[ti ^ hh], "daily run on")
    totals += carve_up(of_week[ti ^ hh][wd], "weekly run on")
    totals += carve_up(of_month[ti ^ hh][md], "monthly run on")
    if md < 0:
        totals += carve_up(of_month[ti ^ hh][last_of_month-md+1], "monthly run on")
    print("Ran", totals, "scripts for {:d}h/{:d}w/{:d}m".format(ti,wd,md))

def list_queue():
    hours_processed = defaultdict(bool)
    got_any = False
    total_dupes = 0
    with open(queue_file) as file:
        for (line_count, line) in enumerate(file, 1):
            l = line.strip()
            if l in hours_processed:
                total_dupes += 1
                continue
            hours_processed[l] = True
            if l.startswith(";"): break
            if l.startswith("#"): continue
            try:
                l0 = [int(q) for q in l.split(",")]
                print("Time={:d}:{:02d} Day of week={:s} Day of month={:d}".format(l0[0]//4, 15*(l0[0] % 4), calendar.day_name[l0[1]], l0[2]))
                got_any = True
            except:
                print("Bad line", line_count, "needs #,#,#, has", l)
    if not got_any: print("Nothing in the queue.")
    if total_dupes:
        print(len(hours_processed), "duplicate time" + dupes[not len(hours_processed)], total_dupes, "additional duplicate line" + dupes[not total_dupes])
    sys.exit()

def file_lock():
    if not os.path.exists(lock_file): return False
    with open(lock_file) as file:
        for line in file:
            if line.startswith("locked"): return True
    return False

def lock_lock_file(print_warning = True):
    if os.path.exists(lock_file) and print_warning:
        with open(lock_file) as file:
            for line in file:
                if line.strip().lower() == 'locked':
                    print(lock_file, "already locked")
                    return
    f = open(lock_file, "w")
    f.write("locked")
    f.close()
    print("Locked", lock_file)

def unlock_lock_file(print_warning = True):
    if os.path.exists(lock_file and print_warning):
        with open(lock_file) as file:
            for line in file:
                if line.strip().lower() == 'unlocked':
                    print(lock_file, "already unlocked")
                    return
    f = open(lock_file, "w")
    f.write("unlocked")
    f.close()
    print("Unlocked", lock_file)

def run_queue_file():
    got_one = False
    hours_processed = defaultdict(bool)
    triples_for_later = defaultdict(bool)
    cmd_array = []
    with open(queue_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            l0 = line.lower().strip()
            lhr = l0.split(",")[0]
            hours_processed[lhr] = True
            if queue_max and len(hours_processed) > queue_max:
                triples_for_later[l0] = True
                continue
            my_list = [int(x) for x in l0.split(",")]
            if len(my_list) != 3:
                print("WARNING line {:d} needs time index, day of week, day of month in {:s}: {:s}".format(line_count, queue_file, line.strip()))
                continue
            print("Going with", '/'.join([str(x) for x in my_list]))
            if of_day[my_list[0]]: cmd_array += of_day[my_list[0]].strip().split("\n")
            if of_week[my_list[0]][my_list[1]]: cmd_array += of_week[my_list[0]][my_list[1]].strip().split("\n")
            if of_week[my_list[0]][my_list[1]]: cmd_array += of_week[my_list[0]][my_list[1]].strip().split("\n")
            if of_month[my_list[0]][my_list[2]]: cmd_array += of_month[my_list[0]][my_list[2]].strip().split("\n")
            got_one = True
    if len(cmd_array):
        cmd_array = [x for i, x in enumerate(cmd_array) if cmd_array.index(x) == i]
        for c in cmd_array:
            check_print_run(c)
    if not got_one:
        print("Didn't find anything to run.")
        return got_one
    tfl = sorted(triples_for_later, key=lambda x: [int(y) for y in x.split(",")])
    if not queue_keep:
        f = open(queue_file, "w")
        f.write("#queue file format = (time index),(day of week),(day of month)\n")
        for j in tfl:
            f.write("{:s}\n".format(j))
        f.close()
    return got_one

queue_run = 0
queue_keep = False

count = 1
half_hour = False
run_cmd = True
print_cmd = True
time_array = []
minute_delta = 0
mday = -1
wkday = -1

queue_max = 4

my_bookmarks = []
print_bookmarks = False

if 1:
    hrcheck_array = get_file_list_by_priority()
else:
    sys.exit("Could not retrieve list of HRCHECK files. Bailing.")

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-' and not arg[1:].isdigit():
        arg = arg[1:]
    if arg == 'hh':
        half_hour = True
    elif arg in ( 'nh', 'hn' ):
        half_hour = False
    elif re.search("^[pr]+$", arg):
        run_cmd = 'r' in arg
        print_cmd = 'p' in arg
    elif arg == 'l':
        lock_lock_file()
        sys.exit()
    elif arg in ( 'u', 'ul', 'lu' ):
        unlock_lock_file()
        sys.exit()
    elif arg == 'q':
        unlock_lock_file(False)
        queue_run = 1
    elif arg[0] == 'q' and arg[1:].isdigit():
        unlock_lock_file(False)
        queue_run = 1
        queue_max = int(arg[1:])
    elif arg[:2] == 'mq' or arg[:2] == 'qm':
        queue_run = 1
        queue_max = int(arg[2:])
    elif arg in ( 'qk', 'kq' ):
        unlock_lock_file(False)
        queue_run = 1
        queue_keep = True
    elif arg in ( 'ql', 'lq' ):
        list_queue()
        sys.exit()
    elif arg == 'qe':
        os.system(queue_file)
        sys.exit()
    elif arg == 'cx':
        only_check_expired = True
    elif arg[:2] == 'id':
        init_delay = int(arg[2:])
    elif arg[0] == 'm':
        mday = int(arg[1:])
    elif arg[0] == 'w':
        wkday = int(arg[1:])
    elif is_time(arg):
        time_array = [int(q) for q in arg.split(":")]
    elif arg in ( 'ra', 'ar' ):
        if retired_file in hrcheck_array:
            print("Tried to add retired file twice.")
        else:
            hrcheck_array.append(retired_file)
    elif arg == 'e':
        mt.npo(hrcheck_array[0])
    elif arg == 'e?':
        print("List of indices")
        for x in range (0, len(hrcheck_array)):
            print("{:2d} {}".format(x, hrchech_array[x]))
        sys.exit()
    elif arg[:2] == 'e-':
        mt.npo(retired_file)
    elif arg[0] == 'e' and arg[1].isdigit():
        print_at_end = False
        for x in arg[1:].split(","):
            try:
                mt.npo(hrcheck_array[int(x)], bail=False)
            except:
                print("Bad index", x, "range is 0 to", len(hrcheck_array) - 1)
                print_at_end = True
        if print_at_end:
            print("e? shows indices with files they point to.")
        sys.exit()
    elif arg.startswith("b="):
        my_bookmarks += arg[2:].split(",")
    elif arg == "bp":
        print_bookmarks = True
    elif arg == 'v':
        verbose = True
    elif re.search('^[fs]([ci]?)[:=]', arg):
        this_array = re.split("[:=]", arg, 1)
        find_in_checkfiles(this_array[1], 'c' in this_array[0], 'i' in this_array[0])
    elif arg[:2] == 'i:':
        ignore_string = arg[2:].lower()
        for z in ignore_string.split(','):
            if len(z) == 0:
                sys.exit("Need a string to ignore.")
            cmds_to_ignore.append(z)
    elif arg == '?':
        usage()
        sys.exit()
    else:
        print("Bad argument", count, arg)
        usage()
        sys.exit()
    count += 1

n = pendulum.now()

for f in hrcheck_array:
    read_hourly_check(f)

if only_check_expired:
    mt.post_open(blank_message = 'No expired dates found in hrcheck.txt.')
    sys.exit()

if len(my_bookmarks):
    ran_any = False
    for x in my_bookmarks:
        x0 = x
        if x not in bookmark_dict:
            if x not in backbkmk:
                print("No bookmark named {}, not running anything.".format(x))
                continue
            x0 = backbkmk[x0]
        for y in bookmark_dict[x0]:
            check_print_run(y)
            ran_any = True
    if not ran_any:
        sys.exit("Failed to run any bookmarks from command line.")
    sys.exit()

if print_bookmarks == True:
    print_all_bookmarks()
    sys.exit()

if len(time_array):
    time_index = time_array[0] * hour_parts + (time_array[1] * hour_parts) // 60
else:
    n.subtract(minutes=minute_delta)
    if minute_delta:
        print("WARNING shifting", minute_delta, "back" if minute_delta < 0 else "forward")
    time_index = n.hour * 4 + (n.minute * hour_parts) // 60

if mday == -1: mday = n.day
if wkday == -1: wkday = n.weekday()

last_of_month = last_day_of_month(n)

if file_lock():
    f = open(queue_file, "a")
    string_to_write = "{:d},{:d},{:d}".format(time_index,wkday,mday)
    f.write(string_to_write + "\n")
    print("Wrote", string_to_write, "to", queue_file, "since it is locked.")
    sys.exit()

if init_delay: time.sleep(init_delay)

if queue_run == 1:
    run_queue_file()
else:
    print("Running time-index", time_index)
    see_what_to_run(time_index, wkday, mday, half_hour)

mt.post_open()