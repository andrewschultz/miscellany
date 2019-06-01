import os
import re
import sys
import time
import winsound

from urllib.request import Request, urlopen

log_file = "ca-todo.htm"

def launch_html_note(err_str, beep_freq, beep_dur):
    f = open(log_file, "w")
    f.write("<html><title>{:s}</title><body><center><font size=+5>CODECADEMY FOR TODAY, WELL UNTIL MIDNIGHT GMT: {:s}</font></center></body></html>".format(err_str, err_str))
    f.close()
    print(err_str)
    winsound.Beep(beep_freq, beep_dur)
    os.system(log_file)

def see_if_days_match(dy):
    streak_start = 1503187200 - 86400 # 2017-08-19 19:00:00
    eptime = int(time.time())
    days = (eptime - streak_start) // 86400
    rem = (eptime - streak_start) % 86400
    print('should have', days, 'days in a row', 'extra seconds', rem, 'of 86400')
    print("Current streak =", dy, "days")
    if days > dy: launch_html_note("Need something today", 500, 1500)
    elif days == dy: launch_html_note("All square", 1000, 500)
    else: launch_html_note("Oops! You did too much, somehow", 2000, 500)
    exit()

ignore_download = False
cmd_count = 0
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg == 'i':
        ignore_download = True
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
        see_if_days_match(dy)
    last = li
