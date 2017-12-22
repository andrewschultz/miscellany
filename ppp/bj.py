###########################################################
#bj.py
#
#using argparse to get the Bill James safe lead coefficient
#
#usage: lead first, then time. Lead can be X or X-Y, time can be (seconds) or m:ss

import re
import sys
import argparse

def timesplit(x):
    temp = re.split('[:.]', x)
    if len(temp) > 2:
        print ('Too many colons.')
        exit()
    try:
        if not temp[0]:
            temp[0] = 0
        retval = int(temp[0])
        if len(temp) == 2:
            retval = retval * 60;
            retval = retval + int(temp[1])
    except:
        print("We need a number for time left, or a:b. Seconds are assumed without a colon.")
        exit()
    return retval

def parselead(x):
    temp = re.split('-', x)
    if len(temp) == 1:
        return int(temp[0])
    try:
        diff = int(temp[0]) - int(temp[1])
        if diff < 0:
            diff = 0 - diff
        return diff
    except:
        print("You need a score like 80-60 or a difference e.g. 20.")
        exit()
        return 0

def floatTime(x):
    return (float(x) - 3.5) ** 2

def leadPct(x, y, z):
    retval = (floatTime(x+z))
    if x < 4:
        return str(0)
    return float(retval * 100) / float(y)

parser = argparse.ArgumentParser()

parser.add_argument("lead", type=str, help="team's lead (or score)")
parser.add_argument("time", type=str, help="time left (can use colon/period to delimit minutes)")

args = parser.parse_args()

lead = parselead(args.lead)

timeint = timesplit(args.time)

if lead < 4:
    print("Lead is too small to matter. It should be at least 4.")
else:
    print('=' * 40)
    print("%.2f %% safe with ball" % leadPct(lead, timeint, 1))
    if leadPct(lead, timeint, 1) < 100:
        temp = floatTime(lead+1)
        print("%d:%02d cutoff time for with the ball" % (temp / 60, temp % 60))
        print ("%d:%02d til safe" % ( (timeint-temp+1)/60, (timeint-temp+1) % 60))
    print('=' * 40)
    print("%.2f %% safe without ball" % leadPct(lead, timeint, 0))
    if leadPct(lead, timeint, 0) < 100:
        temp = floatTime(lead)
        print("%d:%02d cutoff time for without the ball" % (temp / 60, temp % 60))
        print ("%d:%02d til safe" % ( (timeint-temp+1)/60, (timeint-temp+1) % 60))
