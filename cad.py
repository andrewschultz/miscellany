import os
import re
import sys
import time
import winsound
import pendulum

from urllib.request import Request, urlopen

use_pendulum = True
log_file = "ca-todo.htm"

auto_launch = False
ignore_download = False
cmd_count = 0

def launch_html_note(err_str, beep_freq, beep_dur):
    f = open(log_file, "w")
    f.write("<html><title>{:s}</title><body><center><font size=+5>CODECADEMY FOR TODAY, WELL UNTIL MIDNIGHT GMT: {:s}</font></center></body></html>".format(err_str, err_str))
    f.close()
    print(err_str)
    winsound.Beep(beep_freq, beep_dur)
    os.system(log_file)

def process_day_deltas(actual_days, expected_days, extra_seconds):
    print('should have', expected_days, 'days in a row')
    print("Current streak =", actual_days, "days with", extra_seconds, "extra seconds")
    if expected_days > actual_days: launch_html_note("Need something today", 500, 1500)
    elif expected_days == actual_days:
        print("Everything is square{0}!".format(", but launching to make sure" if auto_launch else ""))
        if auto_launch:
            launch_html_note("All square", 1000, 500)
    else: launch_html_note("Oops! You did too much, somehow", 2000, 500)
    exit()

def see_if_days_match_pendulum(dy):
    this_day = pendulum.now()
    naive = this_day.naive()
    start_day = pendulum.from_format("2017-08-19 00:00", "YYYY-MM-DD HH:SS").naive()
    day_period = naive - start_day
    day_streak_expected = day_period.days
    extra_seconds = day_period.seconds
    process_day_deltas(dy, day_streak_expected, extra_seconds)
    exit()

def see_if_days_match_gmt(dy):
    streak_start = 1503187200 - 86400 # 2017-08-19 19:00:00
    eptime = int(time.time())
    days = (eptime - streak_start) // 86400
    rem = (eptime - streak_start) % 86400
    process_day_deltas(dy, days, extra_seconds)
    exit()

def see_if_days_match_generic(dy):
    if use_pendulum:
        see_if_days_match_pendulum(dy)
    else:
        see_if_days_match_gmt(dy)

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg == 'i':
        ignore_download = True
    elif arg == 'a':
        auto_launch = True
    elif arg == 'p' or arg == 'pe' or arg == 'pen':
        use_pendulum = True
    elif arg == 'g' or arg == 'gm' or arg == 'gmt' or arg == 'np' or arg == 'pn' or arg == 'npe':
        use_pendulum = False
    elif arg.isdigit() and int(arg) > 100:
        see_if_days_match_generic(int(arg))
    cmd_count += 1

doc_file = 'c:\coding\perl\proj\doc.html'
my_url = "https://www.codecademy.com/AndrewSchultzChicago"

if not ignore_download:
    req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    lines = webpage.split(b'\n')
    f = open(doc_file, "wb")
    for l in lines:
        f.write(l)
        f.write(b"\n")
else:
    with open(doc_file, "rb") as fi:
        lines = fi.readlines()

last = ""
for li in lines:
    if '<small>day streak</small>' in str(li):
        q = str(last)
        q = re.sub("<\/.*", "", q)
        q = re.sub(".*>", "", q)
        dy = int(q)
        see_if_days_match_generic(dy)
    last = li
