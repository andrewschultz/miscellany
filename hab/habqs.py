# todo: add Wikipedia link for TZ
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
# make a default write_to_quest_file that people can adjust
# allow people to edit the name and location of the quest file/cfg file as well?
# option to print what is pasted to the clipboard (pp/npp)
# put our_zones into the config file

import re
from collections import defaultdict
import pyperclip
import pendulum
import sys
import os

write_to_quest_file = False

quest_hours = quest_default_hours = 24

timezone_list = defaultdict(list)

quest_details = defaultdict(str)
quest_nag = "c:/scripts/start-quest.htm"

overwrite_html = True
execute_command = True

# it's okay to have duplicate-ish time zones below.
our_zones = [ 'America/Chicago', 'America/New_York', 'America/Denver', 'America/Los_Angeles', 'Europe/Sofia', 'Australia/Sydney', "America/El_Salvador" ]

def usage():
    print("Options include w / nw / wn to write to a quest file or not. The default is not to write to it.")
    print("You can also enter a quest name e.g. cow. The program will try to match anything over 1 character long.")
    exit()

def extract_copy():
    to_parse = pyperclip.paste()
    parse_lines = re.split("\r\n+", to_parse)
    for x in parse_lines:
        u = bytes(x, encoding='utf-8')
        if 0xe2 not in u: continue
        if "Level" not in x: continue
        v = re.sub(".Level .*", "", x)
        print(v)
    exit()


def local_area(x):
    return re.sub("^.*/", "", x).replace('_', ' ') # we want a greedy match since there is stuff like, say, America/Kentucky/Louisville

def slash_join(ary):
    ary2 = [ local_area(x) for x in ary ]
    return ' / '.join(ary2)

def hab_format(tm, tz):
    temp = tm.in_timezone(tz)
    return temp.format("dddd MMMM DD HH:mm (h:mm A)")

os.chdir("c:/scripts")

with open("habqs.txt") as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith("#"): continue
        if line.startswith(";"): break
        ary = line.strip().split("\t")
        if len(ary) < 2:
            print("Need tab in line", line_count)
            if '  ' in line:
                print("You likely forgot to convert multiple spaces to a tab.")
            continue
        if ary[0] in quest_details:
            print(ary[0], "is a duplicate pet at line", line_count)
        quest_details[ary[0]] = ary[1]

quest_details['<NULL>'] = "<PLACEHOLDER>"

poss_match = []

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg == 'w':
        write_to_quest_file = True
    elif arg == 'wn' or arg == 'nw':
        write_to_quest_file = False
    elif arg in quest_details:
        poss_match.append(arg)
    elif arg.isdigit():
        atemp = abs(int(arg))
        if atemp > 2:
            quest_hours = int(atemp)
        else:
            quest_hours = 24 * int(atemp)
    elif arg == 'xc':
        extract_copy()
        exit()
    elif arg == '?':
        usage()
    else:
        prev = len(poss_match)
        for x in quest_details:
            if x.startswith(arg):
                poss_match.append(x)
        if not len(poss_match):
            for x in quest_details:
                if arg in x:
                    poss_match.append(x)
        if prev == len(poss_match):
            print("{} didn't match any quests or recognized command line parameters.".format(arg))
            usage()
    cmd_count += 1

if len(poss_match) > 1:
    print("Multiple matches found. Delete the extraneous one(s) before posting to the group.")

if not len(poss_match):
    poss_match = ['<NULL>']
    
paste_string = ""

my_time = pendulum.now()
quest_start_time = my_time.add(hours=quest_hours)

for x in our_zones:
    try:
        if ' ' in x:
            print("WARNING: IANA timezones require underscores. <<{}>> has a space. I can fix this, but I'm still going to throw this nag out.".format(x))
            x = x.replace(' ', '_')
        y = hab_format(quest_start_time, x)
    except:
        if "/" not in x:
            print("Uh oh. {} needs a slash to be a valid IANA time zone. Skipping -- please verify.")
        print("Uh oh. {} may not have been a valid IANA time zone. Skipping -- please verify.".format(x))
    timezone_list[y].append(x)

for x in poss_match:
    paste_string += "Habitica {} quest ({} pet) invites sent {}. Quest starts by time zone:\n".format(x, quest_details[x], hab_format(my_time, our_zones[0]))

for q in sorted(timezone_list): # the sorting is so times will be sorted from the international date line (top) east around the globe. This seems like the best way to do things, though it doesn't feel perfect.
    paste_string += "* {} for the {} timezone{}\n".format(q, slash_join(timezone_list[q]), "" if len(timezone_list[q]) == 1 else "s")

pyperclip.copy(paste_string)

print("PASTED===================")
print(paste_string)

alert_date = quest_start_time.format("MM/DD/YYYY")
alert_time = quest_start_time.format("HH:mm")

my_cmd = 'schtasks /f /create /sc ONCE /tn hman /tr "c:\\scripts\\start-quest.htm" /st {} /sd {}'.format(alert_time, alert_date)

if overwrite_html:
    f = open(quest_nag, "a")
    f.write("<html>\n<title>\nStart quest nag</title>\n<body>\n<center>\nSTART QUEST NAG AT {} {}</center>\n</body>\n</html>\n")
    f.close()
    print("Rewrote", quest_nag)
else:
    print("Did not overwrite html.")

if write_to_quest_file:
    with open("c:/scripts/habqlog.txt", "a") as file:
        file.write(paste_string)

print(my_cmd)
if execute_command:
    os.system(my_cmd)
else:
    print("Remember to execute the command.")