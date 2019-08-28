import os
import re
import sys
import time
import winsound
import pendulum

from urllib.request import Request, urlopen

use_pendulum = True
log_file = "ca-todo.htm"
oops_file = "c:/coding/perl/proj/cad-oops.htm"

auto_launch = False
ignore_download = False
cmd_count = 1

def usage(x = "General usage"):
    print(x)
    print("=" * 50)
    print("a = auto launch")
    print("i = ignore download")
    print("p/pe/pen = use pendulum, g/gm/gmt/np/pn/npe = don't")
    print("A # > 0 gives a generic see-if-days-match. It assumes that the number on the command line is your current streak.")
    exit()

def launch_oops_bail_file(rewrite_string = "", last_code_string = ""):
    last_code_string_mod = last_code_string
    if last_code_string_mod: last_code_string_mod = "LAST CODED TIME DERIVED: " + last_code_string_mod
    if (rewrite_string) or not os.path.exists(oops_file):
        if not rewrite_string:
            rewrite_string = "GENERAL REWRITE"
        print("Rewriting oops file")
        with open(oops_file, "w") as file:
            file.write('<html><title>{}</title><body><center>{}<br />I couldn\'t find enough derivation text, so I\'ll force-open the LEARN page.<br /><a href="https://www.codecademy.com/learn"><font size=+4>LINK TO WHAT TO LEARN</font></a><br />{}</center></body></html>'.format(rewrite_string, rewrite_string, last_code_string_mod))
            file.close()
    os.system(oops_file)
    os.system("start https://www.codecademy.com/learn")
    os.system("start https://www.codecademy.com/AndrewSchultzChicago/")
    winsound.Beep(500, 500)
    winsound.Beep(500, 500)
    winsound.Beep(500, 500)
    exit()

def launch_html_note(err_str, beep_freq, beep_dur):
    f = open(log_file, "w")
    f.write("<html><title>{}</title><body><center><font size=+5>CODECADEMY FOR TODAY, WELL UNTIL MIDNIGHT {}: {}</font></center></body></html>".format(err_str, "CENTRAL" if use_pendulum else "GMT", err_str))
    f.close()
    print(err_str)
    winsound.Beep(beep_freq, beep_dur)
    os.system(log_file)

def process_day_deltas(actual_days, expected_days, extra_seconds, bail = False):
    print('should have', expected_days, 'days in a row')
    print("Current streak =", actual_days, "days with", extra_seconds, "extra seconds")
    if expected_days > actual_days: launch_html_note("Need something today", 500, 1500)
    elif expected_days == actual_days:
        print("Everything is square{0}!".format(", but launching to make sure" if auto_launch else ""))
        if auto_launch:
            launch_html_note("All square", 1000, 500)
    else: launch_html_note("Oops! You did too much, somehow", 2000, 500)
    if bail: sys.exit("Bailing in process_day_deltas.")

def see_if_days_match_pendulum(dy):
    this_day = pendulum.now()
    naive = this_day.naive()
    start_day = pendulum.from_format("2019-08-27 00:00", "YYYY-MM-DD HH:SS").naive() # technically start day is a day later
    day_period = naive - start_day
    day_streak_expected = day_period.days
    extra_seconds = day_period.seconds
    process_day_deltas(dy, day_streak_expected, extra_seconds)

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
    if arg[0] == '-': arg = arg[1:]
    if arg == 'i':
        ignore_download = True
    elif arg == 'a':
        auto_launch = True
    elif arg == 'p' or arg == 'pe' or arg == 'pen':
        use_pendulum = True
    elif arg == 'g' or arg == 'gm' or arg == 'gmt' or arg == 'np' or arg == 'pn' or arg == 'npe':
        use_pendulum = False
    elif arg.isdigit():
        see_if_days_match_generic(int(arg))
        exit()
    elif arg == '?':
        usage()
    else:
        usage("Bad parameter {}".format(arg))
    cmd_count += 1

doc_file = 'c:\coding\perl\proj\doc.html'
my_url = "https://www.codecademy.com/AndrewSchultzChicago"

if not ignore_download:
    print("(Re-)downloading from the web...")
    req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    lines = webpage.split(b'\n')
    f = open(doc_file, "wb")
    for l in lines:
        f.write(l)
        f.write(b"\n")
else:
    print("Ignoring download...")
    with open(doc_file, "rb") as fi:
        lines = fi.readlines()

days_ago_dawg = False
found_any = False
for li in lines:
    l2 = str(li)
    if 'last coded' in l2.lower():
        q = re.sub(".*last coded *", "", l2.lower())
        while q.startswith("<"):
            q = re.sub("^<.*?>", "", q)
        q = re.sub("<.*", "", q)
        if re.search("day(s)? ago", q) or re.search("2[0-9] hours ago", q):
            days_ago_dawg = True
            last_code_string = q
            print("Found abberant last code string")
        elif re.search("(hour|hours|minute|minutes) ago", q):
            print("Flagged ok since-last:", q)
    if 'current streak' in l2.lower():
        q = re.sub(".*current streak *", "", l2.lower())
        while q.startswith("<"):
            q = re.sub("^<.*?>", "", q)
        q = re.sub("<.*", "", q)
        try:
            web_streak = int(q)
        except:
            launch_oops_bail_file()
            exit()
        see_if_days_match_generic(web_streak)
        found_any = True
        break
    last = li

if not found_any:
    print("UH OH didn't find anything. Assuming the worst.")
    launch_oops_bail_file("COULDN'T FIND DERIVATION TEXT")
elif days_ago_dawg:
    print("UH OH it's been more than a day")
    launch_oops_bail_file("OVER A DAY SINCE I CODED", last_code_string)